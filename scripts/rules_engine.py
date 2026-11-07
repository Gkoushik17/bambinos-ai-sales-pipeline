#!/usr/bin/env python3
"""
Bambinos.live: Post-Demo Call Intelligence rules engine.

The LLM (prompts/01, prompts/02) makes *judgements* with evidence.
This script makes everything *deterministic*:
  1. Verifies every evidence quote really exists in the transcript / demo notes (anti-hallucination)
  2. Converts 0-4 dimension scores into a 100-pt audit score, applies compliance caps
  3. Computes the lead intent score (1-10) from evidence-backed signals + order/demo data
  4. Runs data guardrails: paid gate, discount cap, catalog coverage, duplicates, SLA, follow-up hygiene
  5. Assigns CRM stage + priority, and the final approval tier for every WhatsApp touch
  6. Writes cleaned CRM rows (CSV/JSON) and markdown reports to outputs/final/

Standard library only. Run:  python3 scripts/rules_engine.py
"""
import csv, json, re, unicodedata
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
LLM = ROOT / "outputs" / "llm_raw"
OUT = ROOT / "outputs" / "final"
CFG = json.loads((ROOT / "config" / "scoring_config.json").read_text())
SNAPSHOT = datetime.strptime(CFG["snapshot_time_ist"], "%Y-%m-%d %H:%M")
SEV_RANK = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}


# ---------------------------------------------------------------- loading
def load_csv(name):
    with open(RAW / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def nul(v):
    return None if v in (None, "", "NULL") else v

def ts(v):
    v = nul(v)
    return datetime.strptime(v, "%Y-%m-%d %H:%M:%S") if v else None

leads = load_csv("1_crm_leads.csv")
demos = {r["lead_id"]: r for r in load_csv("2_demo_class_evaluations.csv")}
calls = {r["lead_id"]: r for r in load_csv("3_sales_call_logs.csv")}
orders = {r["lead_id"]: r for r in load_csv("4_live_orders_and_invoices.csv")}
catalog = {r["class_id"]: r for r in load_csv("reference_courses_pricing_and_compliance_policy.csv")}
FEE_COL = {"INR": "standard_fee_india_inr", "AED": "standard_fee_gcc_aed", "USD": "standard_fee_usa_usd"}

llm_calls = {}
for p in sorted(LLM.glob("call_*.json")):
    d = json.loads(p.read_text())
    llm_calls[d["lead_id"]] = d
demo_only = {d["lead_id"]: d for d in json.loads((LLM / "demo_only_signals.json").read_text())["leads"]}
followups = {d["lead_id"]: d for d in json.loads((LLM / "followups.json").read_text())["sequences"]}


# ---------------------------------------------------------------- evidence verification
def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", s).strip().lower()

def quote_in(quote, source):
    """Exact (normalised) substring match, else fuzzy word-window match >= 0.9."""
    q, s = norm(quote), norm(source)
    if not q:
        return False, 0.0
    if q in s:
        return True, 1.0
    qw, sw = q.split(), s.split()
    n, best = len(qw), 0.0
    for i in range(0, max(1, len(sw) - n + 1)):
        r = SequenceMatcher(None, q, " ".join(sw[i:i + n])).ratio()
        best = max(best, r)
    return best >= 0.9, round(best, 3)

verification_log = []

def verify(lead_id, where, ev, source):
    ok, score = quote_in(ev.get("quote", ""), source)
    verification_log.append({"lead_id": lead_id, "where": where, "ts": ev.get("ts", ""),
                             "quote": ev.get("quote", ""), "verified": ok, "match": score})
    return ok


# ---------------------------------------------------------------- helpers
def disc_cap(class_id):
    m = re.search(r"(\d+)%", catalog[class_id]["max_rep_discount_allowed_pct"])
    return int(m.group(1)) / 100

def catalog_fee(class_id, currency):
    col = FEE_COL.get(currency)
    if class_id not in catalog or not col:
        return None
    return float(catalog[class_id][col])

def label_for(score):
    for thr, lab in CFG["intent"]["labels"]:
        if score >= thr:
            return lab
    return "Cold"

def grade_for(total):
    for thr, g in CFG["scorecard"]["grades"]:
        if total >= thr:
            return g
    return "D - At risk"

def flag(code, sev, why, source="rules_engine"):
    return {"code": code, "severity": sev, "why": why, "source": source}


# ---------------------------------------------------------------- 1. call audits
audits = {}
for lead_id, d in llm_calls.items():
    tr = (RAW / "call_transcripts" / calls[lead_id.split("-")[1]]["transcript_filename"]).read_text(encoding="utf-8")
    review = list(d.get("review_reasons", []))
    dims, total = [], 0.0
    gaming = d["audit"]["rubric_gaming_detected"]
    for dim in d["audit"]["dimensions"]:
        did, score = dim["id"], dim["score"]
        verified = [verify(lead_id, f"audit.{did}", ev, tr) for ev in dim.get("evidence", [])]
        note = ""
        if score > 0 and not any(verified):
            score, note = 0, "zeroed: no verified evidence"
            review.append(f"{did} evidence not verified")
        if gaming and did in ("D1", "D2"):
            score, note = 0, "zeroed: rubric gaming"
        w = CFG["scorecard"]["dimensions"][did]["weight"]
        pts = round(score / 4 * w, 2)
        total += pts
        dims.append({"id": did, "name": CFG["scorecard"]["dimensions"][did]["name"], "score_0_4": score,
                     "weight": w, "points": pts, "rationale": dim["rationale"], "note": note,
                     "evidence": dim.get("evidence", [])})
    for ev in d["audit"].get("gaming_evidence", []):
        verify(lead_id, "audit.gaming", ev, tr)
    flags = []
    for f in d["compliance_flags"]:
        ok = verify(lead_id, f"flag.{f['code']}", f, tr)
        if not ok:
            review.append(f"flag {f['code']} quote not verified")
        flags.append({**f, "verified": ok, "source": "llm_call_audit"})
    raw_total = round(total, 1)
    max_sev = max([SEV_RANK[f["severity"]] for f in flags if f["verified"]] or [0])
    cap, final = None, raw_total
    if max_sev >= 4:
        cap = CFG["scorecard"]["caps"]["CRITICAL"]
    elif max_sev == 3:
        cap = CFG["scorecard"]["caps"]["HIGH"]
    if cap is not None:
        final = min(raw_total, cap)
    grade = "AUTO-FAIL (Compliance)" if max_sev >= 4 else grade_for(final)
    for k, sig in d["crm"]["intent_signals"].items():
        if sig.get("value") and sig.get("quote"):
            if not verify(lead_id, f"signal.{k}", sig, tr):
                sig["value"] = False
                review.append(f"signal {k} not verified")
    for key in ("primary_objection",):
        verify(lead_id, "crm.primary_objection", d["crm"][key], tr)
    for so in d["crm"]["secondary_objections"]:
        verify(lead_id, "crm.secondary_objection", so, tr)
    audits[lead_id] = {"call_id": d["call_id"], "counsellor": calls[lead_id.split("-")[1]]["counsellor_name"],
                       "rep_talk_pct": int(calls[lead_id.split("-")[1]]["rep_talk_time_pct"]), "language": d["language"],
                       "dimensions": dims, "raw_total": raw_total, "cap_applied": cap, "final_score": final,
                       "grade": grade, "rubric_gaming": gaming, "flags": flags, "coaching": d["coaching"],
                       "needs_human_review": d["needs_human_review"] or bool(review) or max_sev >= 4,
                       "review_reasons": sorted(set(review)), "confidence": d["confidence"]}

for lead_id, d in demo_only.items():
    src = json.dumps(demos.get(lead_id.split("-")[1], {})) + json.dumps(
        next((l for l in leads if l["lead_code"] == lead_id), {}))
    for k, sig in d["intent_signals"].items():
        if sig.get("value") and not verify(lead_id, f"demo_signal.{k}", sig, src):
            sig["value"] = False


# ---------------------------------------------------------------- 2. data guardrails (no LLM)
system_flags = []
seen = {}
dup_of = {}
for l in sorted(leads, key=lambda r: r["created_at"]):
    keys = [("student_id", l["student_id"]), ("mobile", l["mobile"])]
    for k in keys:
        if k in seen and seen[k] != l["lead_code"]:
            dup_of[l["lead_code"]] = seen[k]
        seen.setdefault(k, l["lead_code"])

gateway_mismatch_reported = False
lead_flags = {l["lead_code"]: [] for l in leads}
for l in leads:
    lid, num = l["lead_code"], l["id"]
    F = lead_flags[lid]
    o, dm, c = orders.get(num), demos.get(num), calls.get(num)
    if l["class_id"] not in catalog:
        F.append(flag("CLASS_NOT_IN_CATALOG", "MEDIUM", f"class_id {l['class_id']} ({l['course_pitched']}) missing from pricing/compliance catalog; no price may be messaged."))
    if lid in dup_of:
        F.append(flag("DUPLICATE_LEAD", "HIGH", f"Same student_id/mobile as {dup_of[lid]}; merge, keep original owner, suppress messages."))
    if any(ord(ch) > 127 for ch in l["student_name"] + l["parent_name"]):
        bad = "".join(sorted({ch for ch in l["student_name"] + l["parent_name"] if ord(ch) > 127}))
        F.append(flag("NON_ASCII_HOMOGLYPH", "LOW", f"Name contains non-ASCII characters {bad!r} (e.g. Cyrillic); breaks dedup/matching. Normalise."))
    if o:
        st = o["payment_link_status"]
        if st == "Paid" and l["crm_lead_stage"] != "Enrolled_Paid":
            F.append(flag("PAID_STAGE_NOT_UPDATED", "CRITICAL", f"Order {o['order_id']} Paid at {o['paid_at']} but CRM stage = {l['crm_lead_stage']}. Block sales cadence; start onboarding."))
        if st == "Payment_Failed":
            F.append(flag("PAYMENT_FAILED", "HIGH", f"Order {o['order_id']} failed: {o['gateway_error_reason']}. Trigger payment-recovery touch."))
        if st == "Unpaid_Link_Opened_Twice":
            F.append(flag("PAYMENT_LINK_OPENED", "INFO", f"Order {o['order_id']} link opened twice: buying signal."))
        fee = catalog_fee(o["class_id"], o["currency"])
        if fee is None:
            F.append(flag("CURRENCY_NOT_IN_CATALOG", "MEDIUM", f"{o['currency']} price for class {o['class_id']} not in catalog (order shows {o['currency']} {o['net_payable_amount']}); ops must confirm before re-issuing link."))
        else:
            if abs(float(o["standard_amount"]) - fee) > 0.01:
                F.append(flag("ORDER_AMOUNT_MISMATCH", "MEDIUM", f"Order {o['order_id']} standard_amount {o['standard_amount']} {o['currency']} vs catalog {fee:.0f}. Invoice data error."))
            disc = float(o["discount_applied"])
            pct = disc / fee
            if pct > disc_cap(o["class_id"]) + 1e-9:
                F.append(flag("DISCOUNT_ABOVE_CAP", "CRITICAL", f"Order {o['order_id']} discount {o['currency']} {disc:.0f} = {pct:.1%} of catalog fee (cap {disc_cap(o['class_id']):.0%}). Void link."))
        m = re.search(r">\s*(\d+)%", o["gateway_error_reason"] or "")
        if m and int(m.group(1)) / 100 > disc_cap(o["class_id"]) and not gateway_mismatch_reported:
            system_flags.append(flag("GATEWAY_THRESHOLD_MISMATCH", "HIGH", f"Payment gateway anomaly rule fires at >{m.group(1)}% but policy cap is {disc_cap(o['class_id']):.0%}; discounts of 10-15% currently pass silently. Fix gateway rule."))
            gateway_mismatch_reported = True
    if l["crm_lead_stage"] == "Demo_Completed_Uncalled" and dm and dm["attended_demo"] == "Yes":
        hrs = (SNAPSHOT - ts(dm["demo_completed_at"])).total_seconds() / 3600
        if hrs > CFG["sla"]["uncalled_demo_hours"]:
            F.append(flag("UNCALLED_SLA_BREACH", "HIGH", f"Demo attended {hrs:.1f}h ago (engagement {dm['child_engagement_score_1_to_5']}/5), never called. SLA = {CFG['sla']['uncalled_demo_hours']}h."))
    called = nul(l["last_call_at"]) is not None
    if called and lid not in dup_of and not (o and o["payment_link_status"] == "Paid"):
        nf, lc = ts(l["next_followup_at"]), ts(l["last_call_at"])
        if nf is None:
            F.append(flag("MISSING_FOLLOWUP_DATE", "MEDIUM", "Called lead with no next_followup_at: will silently go cold."))
        elif nf < lc:
            F.append(flag("STALE_FOLLOWUP_DATE", "MEDIUM", f"next_followup_at {nf} is before last_call_at {lc}."))
        note = (nul(l["manual_rep_notes"]) or "").strip().lower()
        if note in CFG["vague_dispositions"] or len(note) < 15:
            F.append(flag("VAGUE_DISPOSITION", "MEDIUM", f"Rep note '{l['manual_rep_notes']}' / disposition '{l['manual_rep_disposition']}' carries no buying-intent information."))
if not any(f["code"] == "TIMEZONE" for f in system_flags):
    system_flags.append(flag("MIXED_TIMEZONES", "LOW", "Timestamps are stored in local time without offsets (IST rows mixed with a PST paid_at). Store UTC + parent timezone."))


# ---------------------------------------------------------------- 3. intent scoring + stage
IC = CFG["intent"]

def intent_for(lid, num):
    pts, parts = IC["base"], [f"base {IC['base']:+d}"]
    dm, o = demos.get(num), orders.get(num)
    if dm:
        e = IC["demo_engagement_points"][dm["child_engagement_score_1_to_5"]]
        pts += e; parts.append(f"demo engagement {dm['child_engagement_score_1_to_5']}/5 {e:+d}")
    sigs = {}
    if lid in llm_calls:
        sigs = {k: v.get("value") for k, v in llm_calls[lid]["crm"]["intent_signals"].items()}
    elif lid in demo_only:
        sigs = {k: v.get("value") for k, v in demo_only[lid]["intent_signals"].items()}
    for k, w in IC["signals"].items():
        if sigs.get(k):
            pts += w; parts.append(f"{k} {w:+d}")
    if o and o["payment_link_status"] in IC["payment_action_statuses"]:
        pts += IC["payment_action_points"]; parts.append(f"payment action ({o['payment_link_status']}) {IC['payment_action_points']:+d}")
    if o and o["payment_link_status"] == "Paid":
        return 10, "Converted", parts + ["override: Paid → 10"]
    if sigs.get("dnc_or_hostile"):
        return 1, "Cold", parts + ["override: DNC/hostile → 1"]
    pts = max(1, min(IC["unpaid_cap"], pts))
    return pts, label_for(pts), parts

rows = []
for l in leads:
    lid, num = l["lead_code"], l["id"]
    o, dm = orders.get(num), demos.get(num)
    a = audits.get(lid)
    call_flags = [f for f in (a["flags"] if a else []) if f["verified"]]
    all_flags = call_flags + lead_flags[lid]
    crit_call = any(f["severity"] == "CRITICAL" for f in call_flags)
    score, label, parts = intent_for(lid, num)
    if lid in dup_of:
        stage, score, label = "Merged_Duplicate", None, "n/a"
    elif crit_call:
        stage = "Compliance_Hold"
    elif o and o["payment_link_status"] == "Paid":
        stage = "Enrolled_Paid"
    elif o and o["payment_link_status"] == "Payment_Failed":
        stage = "Payment_Failed_Recovery"
    elif l["crm_lead_stage"] == "Demo_Completed_Uncalled":
        stage = "Demo_Completed_Uncalled"
    elif lid not in llm_calls:
        stage = "Contacted_Discovery_Pending"
    else:
        stage = f"Follow_Up_{label}"
    provisional = lid not in llm_calls and lid not in dup_of
    rep_label = l["crm_lead_stage"]
    if a:
        disp = llm_calls[lid]["crm"]["rep_disposition_accurate"]
        if rep_label == "Follow_Up_Hot" and score is not None and score <= 3:
            lead_flags[lid].append(flag("CRM_DISPOSITION_MISMATCH", "HIGH", f"Rep logged {rep_label} ('{l['manual_rep_notes']}'); AI intent {score}/10. {disp['reason']}"))
        elif not disp["value"]:
            lead_flags[lid].append(flag("CRM_DISPOSITION_MISMATCH", "MEDIUM", f"Rep logged {rep_label} ('{l['manual_rep_notes']}'). {disp['reason']}"))
        all_flags = call_flags + lead_flags[lid]
    sev = max([SEV_RANK[f["severity"]] for f in all_flags] or [0])
    if stage == "Compliance_Hold" or any(f["code"] in ("PAID_STAGE_NOT_UPDATED",) for f in all_flags) or (stage == "Payment_Failed_Recovery"):
        prio = "P0"
    elif any(f["code"] == "UNCALLED_SLA_BREACH" for f in all_flags) or label == "Hot":
        prio = "P1"
    elif label in ("Warm",) or stage == "Contacted_Discovery_Pending" or (sev >= 3 and stage != "Merged_Duplicate"):
        prio = "P2"
    else:
        prio = "P3"
    if a:
        c = llm_calls[lid]["crm"]
        po = c["primary_objection"]
        highlight, gap = c["child_demo_highlight"], c["child_learning_gap"]
        prim, pstat = po["code"], po["status"]
        sec = ";".join(f"{s['code']}({s['status']})" for s in c["secondary_objections"])
        blocker, nba, note = c["current_blocker"], c["next_best_action"], c["clean_note"]
        dmaker, sched = c["decision_maker"], c["schedule_agreed"] or ""
        root = c["objection_root_cause"]
    elif lid in demo_only:
        dd = demo_only[lid]
        highlight, gap, prim, pstat, sec = dd["child_demo_highlight"], dd["child_learning_gap"], "UNKNOWN", "not_discovered", ""
        blocker, nba, dmaker, sched, root = "Not yet discovered", dd["nba"], "Unknown", "", ""
        note = f"No call recording. {dd['nba']['action']}"
    else:
        highlight = gap = sec = sched = root = ""
        prim, pstat, blocker, dmaker = "n/a", "n/a", "Duplicate", "n/a"
        nba = {"nba_code": "MERGE_DUPLICATE", "owner": "ops_finance", "action": f"Merge into {dup_of.get(lid)}; suppress all messaging from this record."}
        note = f"Duplicate of {dup_of.get(lid)} (brochure re-download {l['created_at']}): intent signal added to original."
    rows.append({
        "lead_id": lid, "student_age": l["student_age"], "grade": l["student_grade"], "country": l["country"],
        "timezone": l["city_timezone"], "course_pitched": l["course_pitched"], "counsellor": l["assigned_counsellor_name"],
        "rep_stage_before": l["crm_lead_stage"], "rep_disposition_before": nul(l["manual_rep_disposition"]) or "",
        "rep_note_before": nul(l["manual_rep_notes"]) or "",
        "ai_crm_stage": stage, "priority": prio,
        "intent_label": (label + (" (provisional)" if provisional and label not in ("n/a",) else "")),
        "intent_score": score if score is not None else "", "intent_breakdown": " | ".join(parts) if score is not None else "",
        "call_audit_score": a["final_score"] if a else "", "call_grade": a["grade"] if a else "",
        "primary_objection": prim, "objection_status": pstat, "secondary_objections": sec,
        "objection_root_cause": root, "current_blocker": blocker, "decision_maker": dmaker, "schedule_agreed": sched,
        "child_demo_highlight": highlight, "child_learning_gap": gap,
        "payment_status": o["payment_link_status"] if o else "No order",
        "nba_code": nba["nba_code"], "nba_owner": nba["owner"], "next_best_action": nba["action"],
        "compliance_and_data_flags": "; ".join(f"{f['severity']}:{f['code']}" for f in sorted(all_flags, key=lambda f: -SEV_RANK[f['severity']])),
        "max_flag_severity": next((k for k, v in SEV_RANK.items() if v == sev), "INFO") if all_flags else "",
        "ai_clean_note": note,
        "needs_human_review": bool(a and a["needs_human_review"]) or sev >= 4 or provisional,
    })
row_by = {r["lead_id"]: r for r in rows}


# ---------------------------------------------------------------- 4. WhatsApp send gates
RANK = CFG["approval_rank"]
INV = {v: k for k, v in RANK.items()}
banned = re.compile(CFG["regex_banned"], re.I)
EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50\u2705\u2728\u203C\u2049\u20E3\uFE0F]")

def safety(msg, touch_n, mode):
    issues = []
    if banned.search(msg):
        issues.append(f"banned phrase '{banned.search(msg).group(0)}'")
    caps = [w for w in re.findall(r"\b[A-Z]{4,}\b", msg) if w not in CFG["caps_allowlist"]]
    if caps:
        issues.append(f"ALL-CAPS {caps}")
    em = len([c for c in EMOJI.findall(msg) if c not in "\uFE0F\u20E3"])
    if em > 2:
        issues.append(f"{em} emojis (>2)")
    words = len(re.sub(r"\{\{.*?\}\}|\[.*?\]", "X", msg).split())
    limit = 110 if touch_n == 1 else 70
    if mode != "COMPLIANCE_HOLD" and words > limit:
        issues.append(f"{words} words (> {limit})")
    return issues, words

def in_quiet_window(send_at, tags):
    m = re.search(r"(\d{2}):(\d{2})", send_at)
    if not m or send_at.startswith("["):
        return True
    hm = int(m.group(1)) * 60 + int(m.group(2))
    end = 21 * 60 + 30 if "payment_retry" in tags else 20 * 60 + 30
    return 9 * 60 <= hm <= end

gates = {}
for lid, seq in followups.items():
    r = row_by[lid]
    flags_here = r["compliance_and_data_flags"]
    out = []
    for t in seq["touches"]:
        lvl = RANK[t["proposed_approval"]]
        for tag in t["content_tags"]:
            lvl = max(lvl, RANK[CFG["tag_min_approval"][tag]])
        reasons = []
        status = "READY"
        if r["ai_crm_stage"] == "Compliance_Hold":
            lvl = max(lvl, RANK["T3_MANAGER"]); reasons.append("lead on Compliance_Hold")
        if t["touch"] == 1 and "HIGH:" in flags_here and r["ai_crm_stage"] not in ("Payment_Failed_Recovery",) and seq["mode"] == "SALES_SEQUENCE" and lid in llm_calls:
            if lvl < RANK["T2_TEAM_LEAD"]:
                reasons.append("first touch after HIGH-flag call")
            lvl = max(lvl, RANK["T2_TEAM_LEAD"])
        if r["payment_status"] == "Paid" and seq["mode"] == "SALES_SEQUENCE":
            status, lvl = "BLOCKED", RANK["BLOCKED"]; reasons.append("paid gate")
        if ("CURRENCY_NOT_IN_CATALOG" in flags_here or "CLASS_NOT_IN_CATALOG" in flags_here) and (set(t["content_tags"]) & {"price", "payment_retry", "installment", "discount"}):
            status = "HELD_PENDING_OPS"; reasons.append("price not in catalog: ops must confirm")
        if not in_quiet_window(t["send_at_local"], t["content_tags"]):
            status = "RESCHEDULE"; reasons.append("outside 09:00-20:30 local window")
        issues, words = safety(t["message"], t["touch"], seq["mode"])
        if issues:
            status = "FIX_REQUIRED"; reasons += issues
        out.append({**t, "final_approval": INV[lvl], "gate_status": status, "gate_reasons": reasons, "word_count": words})
    gates[lid] = {**seq, "touches": out}


# ---------------------------------------------------------------- 5. write outputs
OUT.mkdir(parents=True, exist_ok=True)
cols = list(rows[0].keys())
with open(OUT / "cleaned_crm_leads.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
(OUT / "cleaned_crm_leads.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False))
(OUT / "call_audits.json").write_text(json.dumps(audits, indent=2, ensure_ascii=False))
(OUT / "whatsapp_sequences.json").write_text(json.dumps(gates, indent=2, ensure_ascii=False))

def md_escape(s):
    return str(s).replace("|", "\\|").replace("\n", " ")

# --- call audit scorecards
L = ["# Call Audit Scorecards (6 recorded calls)\n",
     "Generated by `scripts/rules_engine.py` from LLM judgements in `outputs/llm_raw/`. Points = score/4 × weight; caps applied in code.\n",
     "| Lead | Counsellor | Rep talk % | Raw | Cap | **Final** | Grade | Gaming | Flags (C/H/M/L) |", "|---|---|---|---|---|---|---|---|---|"]
for lid, a in audits.items():
    cnt = {s: sum(1 for f in a["flags"] if f["severity"] == s and f["verified"]) for s in ("CRITICAL", "HIGH", "MEDIUM", "LOW")}
    L.append(f"| {lid} | {a['counsellor']} | {a['rep_talk_pct']}% | {a['raw_total']} | {a['cap_applied'] or '-'} | **{a['final_score']}** | {a['grade']} | {'YES' if a['rubric_gaming'] else 'no'} | {cnt['CRITICAL']}/{cnt['HIGH']}/{cnt['MEDIUM']}/{cnt['LOW']} |")
for lid, a in audits.items():
    L += [f"\n## {lid}: call {a['call_id']} ({a['counsellor']}, {a['language']})",
          f"**Final score: {a['final_score']}/100 · {a['grade']}**" + (f" (raw {a['raw_total']}, capped at {a['cap_applied']})" if a['cap_applied'] and a['raw_total'] > a['cap_applied'] else ""),
          "", "| Dim | Score (0-4) | Pts | Evidence | Rationale |", "|---|---|---|---|---|"]
    for d in a["dimensions"]:
        ev = "<br>".join(f"[{e['ts']}] \"{md_escape(e['quote'])}\"" for e in d["evidence"]) or "–"
        L.append(f"| {d['id']} {d['name']} ({d['weight']}) | {d['score_0_4']} | {d['points']} | {ev} | {md_escape(d['rationale'])}{' ⚠ ' + d['note'] if d['note'] else ''} |")
    if a["needs_human_review"]:
        L.append(f"\n> Human review required: {', '.join(a['review_reasons']) or 'critical flag'}")
(OUT / "call_audit_scorecards.md").write_text("\n".join(L) + "\n")

# --- compliance alerts
L = ["# Compliance & Data-Integrity Alerts\n", "## A. Call compliance flags (LLM-detected, quote-verified)\n",
     "| Severity | Lead | Rep | Code | When | Verbatim evidence | Policy | Verified |", "|---|---|---|---|---|---|---|---|"]
allf = []
for lid, a in audits.items():
    for f in a["flags"]:
        allf.append((SEV_RANK[f["severity"]], lid, a["counsellor"], f))
for _, lid, rep, f in sorted(allf, key=lambda x: (-x[0], x[1])):
    L.append(f"| **{f['severity']}** | {lid} | {rep} | `{f['code']}` | {f['ts']} | \"{md_escape(f['quote'])}\" | {md_escape(f['policy_ref'])} | {'✅' if f['verified'] else '❌'} |")
L += ["\n## B. Data guardrail flags (rules engine, deterministic)\n", "| Severity | Lead | Code | Detail |", "|---|---|---|---|"]
dl = [(SEV_RANK[f["severity"]], lid, f) for lid, fs in lead_flags.items() for f in fs]
for _, lid, f in sorted(dl, key=lambda x: (-x[0], x[1])):
    L.append(f"| **{f['severity']}** | {lid} | `{f['code']}` | {md_escape(f['why'])} |")
L += ["\n## C. System-level flags\n", "| Severity | Code | Detail |", "|---|---|---|"]
for f in system_flags:
    L.append(f"| **{f['severity']}** | `{f['code']}` | {md_escape(f['why'])} |")
(OUT / "compliance_alerts.md").write_text("\n".join(L) + "\n")

# --- coaching cards
L = ["# Rep Coaching Cards\n", "Delivered privately to each counsellor in the CRM/Slack within 15 minutes of the call: strengths first, max 2 fixes, one drill.\n"]
for lid, a in audits.items():
    c = a["coaching"]
    L += [f"## {a['counsellor']}: {lid} (score {a['final_score']}, {a['grade']})", "**What you did well**"]
    L += [f"- [{s['ts']}] {s['text']}" for s in c["strengths"]] or ["- (none recorded on this call)"]
    L.append("\n**Your top fixes**")
    for fx in c["fixes"]:
        L += [f"- **[{fx['moment_ts']}] {fx['what_happened']}** {fx['why_it_cost_us']}", f"  - 💬 *Try saying:* \"{fx['say_this_instead']}\""]
    L += [f"\n**10-minute drill:** {c['micro_drill']}\n"]
reps = {}
for lid, a in audits.items():
    reps.setdefault(a["counsellor"], []).append((lid, a["final_score"], a["grade"]))
L += ["## Team-lead roll-up", "| Counsellor | Calls | Avg score | Open pipeline issues | Action |", "|---|---|---|---|---|"]
for rep, lst in reps.items():
    issues = [f"{r['lead_id']}:{f.split(':')[1]}" for r in rows if r["counsellor"] == rep for f in r["compliance_and_data_flags"].split("; ") if f and f.split(":")[0] in ("CRITICAL", "HIGH")]
    avg = round(sum(s for _, s, _ in lst) / len(lst), 1)
    action = ("Suspend live calls pending compliance review; reassign open leads" if any(g.startswith("AUTO") for _, _, g in lst)
              else "Team-lead 1:1 in 48h + shadow a Grade-A rep" if avg < 50
              else "Feature as 'Call of the Week' (opt-in)" if avg >= 85 else "One coaching tip")
    L.append(f"| {rep} | {', '.join(l for l, _, _ in lst)} | {avg} | {'; '.join(issues) or '-'} | {action} |")
(OUT / "coaching_cards.md").write_text("\n".join(L) + "\n")

# --- whatsapp sequences
L = ["# WhatsApp Follow-Up Sequences (with send gates)\n",
     "Approval tiers: **T0** auto-send (pre-approved template) · **T1** counsellor 1-click · **T2** team lead · **T3** manager only. "
     "Gate status is computed by `rules_engine.py` (paid gate, compliance hold, catalog coverage, quiet hours, regex safety, length).\n"]
for lid, g in gates.items():
    r = row_by[lid]
    L += [f"## {lid}: {g['mode']} · {r['intent_label']} {r['intent_score']} · objection: {r['primary_objection']} · lang: {g['language']}"]
    if not g["touches"]:
        L.append("**No messages: suppressed.**")
    for t in g["touches"]:
        L += [f"\n**Touch {t['touch']}** · {t['send_at_local']} · _{t['condition']}_ · from {t['sender']}  ",
              f"Approval: **{t['final_approval']}** · Gate: **{t['gate_status']}**" + (f" ({'; '.join(t['gate_reasons'])})" if t['gate_reasons'] else "") + f" · {t['word_count']} words", ""]
        L += ["> " + line if line else ">" for line in t["message"].split("\n")]
    L.append(f"\n**Stop triggers:** {'; '.join(g['stop_triggers'])}  ")
    if g["internal_alerts"]:
        L.append("**Internal alerts:** " + " · ".join(g["internal_alerts"]))
    L.append("")
(OUT / "whatsapp_sequences.md").write_text("\n".join(L) + "\n")

# --- pipeline leak report
L = ["# Pipeline Leak Audit: 12-lead CRM table\n", f"Snapshot: {CFG['snapshot_time_ist']} IST.\n",
     "| Priority | Lead | Rep stage → **AI stage** | Rep note | AI intent | Payment | Top flags | Next best action (owner) |", "|---|---|---|---|---|---|---|---|"]
for r in sorted(rows, key=lambda r: (r["priority"], r["lead_id"])):
    top = "; ".join(r["compliance_and_data_flags"].split("; ")[:3])
    L.append(f"| **{r['priority']}** | {r['lead_id']} | {r['rep_stage_before']} → **{r['ai_crm_stage']}** | \"{md_escape(r['rep_note_before'])}\" | {r['intent_label']} {r['intent_score']} | {r['payment_status']} | {top} | {md_escape(r['next_best_action'])} ({r['nba_owner']}) |")
L += ["\n## Intent score breakdown (deterministic)\n", "| Lead | Score | Breakdown |", "|---|---|---|"]
for r in rows:
    if r["intent_breakdown"]:
        L.append(f"| {r['lead_id']} | {r['intent_score']} ({r['intent_label']}) | {r['intent_breakdown']} |")
(OUT / "pipeline_leak_report.md").write_text("\n".join(L) + "\n")

# --- evidence verification log
ok = sum(v["verified"] for v in verification_log)
L = ["# Evidence Verification Log\n", f"{ok}/{len(verification_log)} quotes verified as verbatim (or ≥0.9 fuzzy) substrings of the source transcript / demo notes.\n",
     "| Lead | Field | ts | Match | Verified |", "|---|---|---|---|---|"]
L += [f"| {v['lead_id']} | {v['where']} | {v['ts']} | {v['match']} | {'✅' if v['verified'] else '❌'} |" for v in verification_log]
(OUT / "evidence_verification_log.md").write_text("\n".join(L) + "\n")

summary = {"evidence_verified": f"{ok}/{len(verification_log)}",
           "audits": {k: {"score": v["final_score"], "grade": v["grade"], "rep": v["counsellor"]} for k, v in audits.items()},
           "leads": {r["lead_id"]: {k: r[k] for k in ("ai_crm_stage", "priority", "intent_label", "intent_score", "primary_objection", "payment_status", "nba_code", "max_flag_severity")} for r in rows},
           "gate_status": {lid: [(t["touch"], t["final_approval"], t["gate_status"]) for t in g["touches"]] for lid, g in gates.items()},
           "system_flags": system_flags}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))

print(f"Evidence verified: {ok}/{len(verification_log)}")
for v in verification_log:
    if not v["verified"]:
        print("  UNVERIFIED:", v["lead_id"], v["where"], v["match"], v["quote"][:70])
for lid, a in audits.items():
    print(f"{lid} audit {a['final_score']:>5} {a['grade']}")
for r in rows:
    print(f"{r['lead_id']} {r['priority']} {r['ai_crm_stage']:<28} {str(r['intent_score']):>2} {r['intent_label']:<18} {r['max_flag_severity']}")
for lid, g in gates.items():
    for t in g["touches"]:
        if t["gate_status"] != "READY":
            print(f"  GATE {lid} T{t['touch']} {t['final_approval']} {t['gate_status']} {t['gate_reasons']}")
