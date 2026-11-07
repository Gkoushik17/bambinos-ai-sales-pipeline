# Structured CRM Taxonomy

Every field is either **enum-constrained** (the LLM must pick one value from a fixed list) or **evidence-backed** (it must cite a transcript or evaluation quote). Free text is allowed only in `clean_note`, which is limited to 280 characters.

## 1. Lead Intent Score: Hot / Warm / Cold + 1–10

The LLM does **not** guess the number. It extracts boolean **buying signals**, each with evidence. The rules engine then computes the score with a fixed formula (`config/scoring_config.json`), so the same call always gets the same score.

| Signal | Source | Points |
|---|---|---|
| Base | – | +2 |
| Demo engagement 5 / 4 / 3 / ≤2 | `2_demo_class_evaluations.csv` | +2 / +1 / 0 / −1 |
| Parent states the learning pain in their own words | transcript | +1 |
| Fee accepted (explicitly OK with price or plan) | transcript | +1 |
| Price objection still unresolved | transcript | −1 |
| Schedule confirmed | transcript | +1 |
| Next step agreed with a specific time | transcript | +1 |
| Explicit commitment to pay ("I'll pay after dinner") | transcript | +2 |
| Payment action (link opened twice, payment attempted) | `4_live_orders_and_invoices.csv` | +2 |
| Decision-maker absent | transcript | −1 |
| Competitor still being actively evaluated | transcript | −1 |
| Parent asked for information/material | transcript | +1 |
| Conditional yes with a fix available in the catalog ("only if a 5–6-year-old batch") | transcript + catalog | +2 |
| Explicit buying question ("when does the batch start?") | transcript / evaluation | +2 |
| Parent visibly enthusiastic | transcript / evaluation | +1 |
| **Overrides** | Paid → **10 (Converted)** · Do-not-call / hostile → **1** · Unpaid capped at **9** | |

**Labels:** Hot = 8–10 · Warm = 4–7 · Cold = 1–3. Leads with no call get `confidence: low` and the suffix *(provisional)*.

## 2. Objection Taxonomy

`primary_objection` takes exactly one value and `secondary_objections` takes zero or more. Each one needs a quote and a status (`open` or `resolved`).

| Code | Bucket | Typical parent words | Root causes to probe |
|---|---|---|---|
| `PRICE_VALUE` | **Price** | "Why pay double for online?" | Value not shown, or comparing with cheaper local tuition |
| `PRICE_CASHFLOW` | **Price** | "Rs. 12,000 at once is tight" | Timing (festival, school fee). Fix: 50/50 installment, not a discount |
| `SPOUSE_DECISION` | **Spouse Decision** | "My husband wasn't there, we decide together" | Absent decision-maker needs proof they can forward |
| `SCHEDULE_CONFLICT` | **Schedule Conflict** | "She has gymnastics Tue/Thu" | Batch time or timezone. Fix: alternative batch with the same teacher |
| `CHILD_NOT_INTERESTED` | **Child Not Interested** | "She said chess is too hard" | Usually **demo batch mismatch** (age/level), not lack of interest |
| `COMPETITOR_COMPARISON` | **Competitor Comparison** | "PlanetSpark does 1-on-1" / "local tutor AED 350" | 1-on-1 vs. peer group, price vs. method |
| `EXAM_TIMING` | Timing | "After half-yearly exams" | Fear of overload. Fix: exam pause/reschedule |
| `SCREEN_TIME` | Product fit | "He already watches the iPad" | Needs active-vs-passive screen framing |
| `TRUST_CREDIBILITY` | Trust | "This sounds like a scam" | Usually **rep-caused**; route to the manager |
| `NONE` | – | – | – |

`current_blocker` records what is stopping payment *right now*. It can differ from the objection (e.g., the objection was resolved but `PAYMENT_FAILURE_TECHNICAL` is blocking).

## 3. Child Demo Highlight
- `child_demo_highlight`: one sentence taken **only** from `demo_magic_moment_for_parent` or a parent quote. No embellishment.
- `child_learning_gap`: taken from `learning_gaps_observed`, in plain language a parent would use.

## 4. Next Best Action (NBA)
| Field | Allowed values |
|---|---|
| `nba_code` | `CALL_NOW_SLA` · `SEND_SPOUSE_SUMMARY` · `VALUE_REPITCH_METHOD` · `PAYMENT_RECOVERY` · `ONBOARDING_HANDOFF` · `ACADEMIC_BATCH_FIX` · `REDISCOVERY_CALL` · `COMPLIANCE_HOLD` · `MERGE_DUPLICATE` |
| `nba_owner` | `counsellor` · `team_lead` · `sales_head` · `academic_team` · `onboarding` · `ops_finance` |
| `nba_due_local` | timestamp in the **parent's** timezone |

## 5. Standardised CRM stages
`Demo_Completed_Uncalled` → `Contacted_Discovery_Pending` → `Follow_Up_Hot | Warm | Cold` → `Payment_Link_Sent` → `Payment_Failed_Recovery` → `Enrolled_Paid`
Side states: `Compliance_Hold`, `Merged_Duplicate`, `Lost_DNC`.

Stage is set by **rules**, not by the LLM. For example, if the order status is `Paid`, the stage is `Enrolled_Paid` whatever the rep logged.

## 6. Example of a cleaned record (LEAD-801)
```json
{
  "lead_id": "LEAD-801",
  "crm_stage": "Follow_Up_Hot",
  "intent_label": "Hot", "intent_score": 9,
  "primary_objection": "SPOUSE_DECISION", "objection_status": "open",
  "decision_maker": "Joint (mother + father; father pays by card)",
  "child_demo_highlight": "At minute 18, using the 3-step Superhero Hook, Aarav unmuted and told a 45-second space rescue story with hand gestures.",
  "child_learning_gap": "Freezes for the first ~10 seconds on open questions (stage fear), not a grammar gap.",
  "nba_code": "SEND_SPOUSE_SUMMARY", "nba_owner": "counsellor",
  "clean_note": "Mother sold on fee and Tue-Thu 6PM. Father (pays) missed demo; his question: 'grammar tuition or stage-fear fix?'. Spouse summary sent; seat held till 11AM; callback 11AM."
}
```
