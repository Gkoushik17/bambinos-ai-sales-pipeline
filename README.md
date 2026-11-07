# Bambinos.live: Post-Demo Conversion & Call Intelligence Engine

**AI Program Manager (Sales) take-home case.** This pipeline takes raw counselling-call transcripts and CRM rows and automatically:
1. **Audits call quality**: a 7-dimension, evidence-backed scorecard, compliance red flags and private rep coaching
2. **Cleans the CRM and scores intent**: standardised objection taxonomy, a deterministic 1–10 intent score, rule-based stage, and next best action
3. **Generates personalised WhatsApp follow-ups**: 3-touch sequences tied to the child's demo moment and the parent's real objection, gated by human-in-the-loop approval tiers and stop triggers

📄 **Case report (Deliverables A, B, D): [`report/Case_Report.pdf`](report/Case_Report.pdf)**

---

## Results on the provided dataset (6 calls, 12 leads)

| Lead | Call score | AI stage (was) | Intent | What the system caught |
|---|---|---|---|---|
| 801 | **98.8 A** | Follow_Up_Hot (Warm) | Hot 9 | Spouse objection; a forwardable summary for the father; duplicate LEAD-811 merged in |
| 802 | **15.0 D** | Follow_Up_Cold | Cold 3 | Price dumped at 0:30 (breaks the class 205 rule), fake 30-min deadline, wrong AED amount on the invoice |
| 803 | **0.0 AUTO-FAIL** | **Compliance_Hold** (Hot) | Cold 1 | Rank-1 guarantee, 6-month refund, 42% discount, fake 1-on-1, blacklist threat, DNC; rep logged "will pay today" |
| 804 | **96.2 A** | **Enrolled_Paid** (Link_Sent) | Converted | Paid 2h after the call but the stage was never updated. Sales cadence blocked, onboarding sent, weekend batch mapping checked |
| 805 | **91.2 A** | **Payment_Failed_Recovery** (Warm) | Hot 9 | UPI mandate OTP timeout. Automatic Hinglish retry link; discount-stacking coaching |
| 806 | **3.8 D** | Follow_Up_Warm (Cold) | Warm 4 | **Rubric gaming**. "Child not interested" was really a demo batch mismatch; class 401 remedy offered |
| 807 | – | Uncalled (**SLA breach 29.5h**) | Warm 6* | High-intent demo never called |
| 808 | – | Discovery_Pending | Cold 3* | "ok" disposition; **class 108 missing from catalog**; owner under compliance review |
| 809 | – | **Payment_Failed_Recovery** | Hot 8* | 3DS decline; **GBP price not in catalog**, so the retry is held until ops confirm |
| 810 | – | Discovery_Pending | Cold 3* | "cb" disposition; follow-up date before the last call |
| 811 | – | **Merged_Duplicate** | – | Same student and mobile as 801; messaging suppressed |
| 812 | – | Uncalled (**SLA breach 14.5h**) | Warm 5* | High-intent demo uncalled; Cyrillic homoglyphs in the name |

\* provisional (demo-evaluation signals only). System-level: the gateway discount rule fires at >15% but policy says 10%. **100/100 evidence quotes verified** against the source transcripts by code.

---

## Repository map

```
├── report/
│   ├── Case_Report.pdf              ← compulsory PDF (A, B, D + results)
│   └── Case_Report.md               ← source
├── framework/                       ← Deliverable A + guardrails
│   ├── 01_call_quality_scorecard.md   parent psychology (India/GCC/US), 7-dim rubric, caps, anti-gaming
│   ├── 02_crm_taxonomy.md             intent formula, objection buckets, demo highlight, NBA, stages
│   └── 03_guardrails_and_hitl.md      compliance flags, data guardrails, T0–T3 approval tiers, cadence rules
├── prompts/                         ← exact system prompts
│   ├── 01_call_audit_and_crm_extraction.md   audit + flags + coaching + CRM signals (temp 0, quote-or-zero)
│   ├── 02_whatsapp_followup_generator.md     3-touch sequences by objection playbook
│   └── 03_outgoing_message_safety_check.md   LLM-as-judge + regex pre-filter before every send
├── config/scoring_config.json       ← weights, caps, intent signal points, approval tiers, banned phrases
├── scripts/
│   ├── rules_engine.py              ← deterministic engine: quote verification, scoring, intent, stages, gates, reports
│   ├── run_llm.py                   ← regenerates outputs/llm_raw via any OpenAI-compatible LLM API
│   ├── funnel_math.py               ← Deliverable D numbers (assumptions editable)
│   └── build_report.py              ← renders the PDF
├── workflow/                        ← Deliverable B
│   ├── architecture.md                pipeline map (mermaid), stack, latency, data protection
│   ├── n8n_post_call_pipeline.json    importable n8n workflow (26 nodes)
│   └── n8n_payment_and_hygiene.json   payment webhooks + 30-min SLA/duplicate sweep
├── data/raw/                        ← official assessment assets (unchanged)
└── outputs/
    ├── llm_raw/                     ← raw JSON from prompts 01 & 02 (6 calls, 5 demo-only leads, 12 follow-up plans)
    └── final/                       ← Deliverable C
        ├── call_audit_scorecards.md   per-dimension scores with timestamped evidence
        ├── compliance_alerts.md       call flags + data guardrail flags + system flags
        ├── coaching_cards.md          per-call rep cards + team-lead roll-up
        ├── cleaned_crm_leads.csv/json ← import into Google Sheets as the CRM tracker
        ├── whatsapp_sequences.md/json every touch with final approval tier + gate status
        ├── pipeline_leak_report.md    12-lead audit, priorities, intent breakdown
        ├── evidence_verification_log.md
        └── funnel_math.md
```

## How it works

```
Call ends → STT (multilingual, diarized) → context join (CRM + demo evaluation + catalog/policy)
  → LLM Prompt 01 (judgements + verbatim quotes, JSON, temp 0)
  → rules_engine (verify quotes · score · caps · intent · stage · data guardrails)
      ├─ CRITICAL → Compliance_Hold, page Sales Head, void link
      ├─ Auto-CRM update + private coaching card to rep
      └─ LLM Prompt 02 → send gate (tier, paid gate, catalog, quiet hours, regex) → Prompt 03 → approve/auto → WhatsApp
Payment webhook: Paid → Enrolled_Paid + onboarding · Failed → recovery touch
Cron 30 min: uncalled-demo SLA · duplicates · stale follow-ups
```

**Design principle: the LLM judges, code decides.** The LLM outputs 0–4 scores, booleans and enums, each with a timestamped verbatim quote. Python then verifies every quote against the transcript, computes totals and caps, derives the intent score from a fixed formula, sets the CRM stage by rule, and picks the approval tier for each message. The same input always gives the same CRM output, and invented evidence is caught automatically.

## Reproduce

```bash
# deterministic layer (no API key needed, standard library only)
python3 scripts/rules_engine.py
python3 scripts/funnel_math.py

# regenerate LLM outputs with your own model
export LLM_API_URL=https://<provider>/v1/chat/completions LLM_API_KEY=... LLM_MODEL=...
python3 scripts/run_llm.py && python3 scripts/rules_engine.py
python3 scripts/run_llm.py --followups && python3 scripts/rules_engine.py

# rebuild the PDF
pip install -r requirements.txt && python3 scripts/build_report.py
```

**Google Sheets CRM tracker:** import `outputs/final/cleaned_crm_leads.csv` as a tab named `ai_cleaned_crm`, next to the four raw tables. The n8n workflow reads and writes those same tab names.

**n8n:** Workflows → Import from file → `workflow/*.json`, then set the env variables listed in `workflow/architecture.md`.
