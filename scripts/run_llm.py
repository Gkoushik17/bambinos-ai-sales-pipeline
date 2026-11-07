#!/usr/bin/env python3
"""
Regenerate outputs/llm_raw/* by sending the system prompts to an LLM API.

Works with any OpenAI-compatible chat-completions endpoint (set LLM_API_URL, LLM_API_KEY, LLM_MODEL).
Standard library only.

    export LLM_API_URL=https://<provider>/v1/chat/completions
    export LLM_API_KEY=...
    export LLM_MODEL=<model-id>
    python3 scripts/run_llm.py            # prompt 01 for all 6 calls (+ demo-only mode)
    python3 scripts/run_llm.py --followups # prompt 02 for all 12 leads (needs rules_engine output first)
    python3 scripts/rules_engine.py       # deterministic scoring, gating and reports
"""
import csv, json, os, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW, LLM_OUT = ROOT / "data" / "raw", ROOT / "outputs" / "llm_raw"

def system_prompt(fname):
    md = (ROOT / "prompts" / fname).read_text()
    return re.search(r"## SYSTEM PROMPT\s+```\n(.*?)```", md, re.S).group(1)

def rows(name):
    with open(RAW / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def chat(system, user, temperature):
    body = json.dumps({"model": os.environ["LLM_MODEL"], "temperature": temperature,
                       "response_format": {"type": "json_object"},
                       "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}).encode()
    req = urllib.request.Request(os.environ["LLM_API_URL"], data=body, headers={
        "Authorization": f"Bearer {os.environ['LLM_API_KEY']}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(json.loads(r.read())["choices"][0]["message"]["content"])

def main():
    leads = {r["id"]: r for r in rows("1_crm_leads.csv")}
    demos = {r["lead_id"]: r for r in rows("2_demo_class_evaluations.csv")}
    catalog = {r["class_id"]: r for r in rows("reference_courses_pricing_and_compliance_policy.csv")}
    calls = rows("3_sales_call_logs.csv")
    if "--followups" in sys.argv:
        sp = system_prompt("02_whatsapp_followup_generator.md")
        crm = json.loads((ROOT / "outputs" / "final" / "cleaned_crm_leads.json").read_text())
        orders = {f"LEAD-{r['lead_id']}": r for r in rows("4_live_orders_and_invoices.csv")}
        seqs = []
        for r in crm:
            num = r["lead_id"].split("-")[1]
            user = (f"<CRM_CLEAN>{json.dumps(r)}</CRM_CLEAN><DEMO_EVALUATION>{json.dumps(demos.get(num, {}))}</DEMO_EVALUATION>"
                    f"<CATALOG_POLICY>{json.dumps(catalog.get(leads[num]['class_id'], {}))}</CATALOG_POLICY>"
                    f"<ORDER>{json.dumps(orders.get(r['lead_id']))}</ORDER><GATE_RESULT>{r['ai_crm_stage']}</GATE_RESULT>"
                    f"<TZ>{r['timezone']}</TZ>")
            seqs.append(chat(sp, user, 0.4))
            print("followups", r["lead_id"])
        (LLM_OUT / "followups.json").write_text(json.dumps({"sequences": seqs}, indent=2, ensure_ascii=False))
        return
    sp = system_prompt("01_call_audit_and_crm_extraction.md")
    for i, c in enumerate(calls, 1):
        lead = leads[c["lead_id"]]
        tr = (RAW / "call_transcripts" / c["transcript_filename"]).read_text(encoding="utf-8")
        user = (f"<CALL_LOG>{json.dumps(c)}</CALL_LOG><CRM_LEAD>{json.dumps(lead)}</CRM_LEAD>"
                f"<DEMO_EVALUATION>{json.dumps(demos.get(c['lead_id'], {}))}</DEMO_EVALUATION>"
                f"<CATALOG_POLICY>{json.dumps(catalog.get(lead['class_id'], {}))}</CATALOG_POLICY>"
                f"<TRANSCRIPT>\n{tr}\n</TRANSCRIPT>\nReturn the JSON object now.")
        out = chat(sp, user, 0)
        (LLM_OUT / f"call_{i:02d}_LEAD-{c['lead_id']}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
        print("audited", c["lead_id"])

if __name__ == "__main__":
    main()
