# Pipeline Leak Audit: 12-lead CRM table

Snapshot: 2026-11-03 21:00 IST.

| Priority | Lead | Rep stage → **AI stage** | Rep note | AI intent | Payment | Top flags | Next best action (owner) |
|---|---|---|---|---|---|---|---|
| **P0** | LEAD-803 | Follow_Up_Hot → **Compliance_Hold** | "good call sent payment link will pay today" | Cold 1 | Unpaid_Flagged_Discount_Anomaly | CRITICAL:FAKE_OUTCOME_GUARANTEE; CRITICAL:UNAUTHORIZED_REFUND_PROMISE; CRITICAL:OFF_RECORD_SIDE_DEAL | Freeze lead, void link 99403, no calls (DNC). Sales Head reviews within 2h; optional one-time written apology and correction, no sales ask. (sales_head) |
| **P0** | LEAD-804 | Payment_Link_Sent → **Enrolled_Paid** | "wants weekend batch sent link" | Converted 10 | Paid | CRITICAL:PAID_STAGE_NOT_UPDATED; MEDIUM:CRM_DISPOSITION_MISMATCH | Stop sales cadence; move to Enrolled_Paid; confirm order is mapped to Sat-Sun 9:30 AM PST batch (not portal default Tue/Thu); send welcome. (onboarding) |
| **P0** | LEAD-805 | Follow_Up_Warm → **Payment_Failed_Recovery** | "comparing with planetspark and school exam going on" | Hot 9 | Payment_Failed | HIGH:PAYMENT_FAILED; MEDIUM:CRM_DISPOSITION_MISMATCH; LOW:COMPETITOR_CLAIM_UNVERIFIED | Auto-send fresh INR 5,400 link with one-time UPI/card/netbanking (no mandate); Pooja offers 2-min assisted call next day; Day-30 installment 2 via separate link. (counsellor) |
| **P0** | LEAD-809 | Payment_Link_Sent → **Payment_Failed_Recovery** | "mother tried paying on stripe link failed need to send new link" | Hot (provisional) 8 | Payment_Failed | HIGH:PAYMENT_FAILED; MEDIUM:CURRENCY_NOT_IN_CATALOG | Ops confirms GBP 210 price (GBP not in catalog), then fresh Stripe link + 3DS tip within London business hours. (counsellor) |
| **P1** | LEAD-801 | Follow_Up_Warm → **Follow_Up_Hot** | "will ask husband and tell tomorrow" | Hot 9 | Unpaid_Link_Opened_Twice | MEDIUM:CRM_DISPOSITION_MISMATCH; LOW:SCARCITY_CLAIM_UNVERIFIED; INFO:PAYMENT_LINK_OPENED | Send forwardable 60-sec summary before 8:30 PM IST; 11 AM callback; offer father a 10-min call with Ms. Rhea. (counsellor) |
| **P1** | LEAD-807 | Demo_Completed_Uncalled → **Demo_Completed_Uncalled** | "" | Warm (provisional) 6 | No order | HIGH:UNCALLED_SLA_BREACH | Call within 1 hour; demo was 29.5h ago and uncalled. (counsellor) |
| **P1** | LEAD-812 | Demo_Completed_Uncalled → **Demo_Completed_Uncalled** | "" | Warm (provisional) 5 | No order | HIGH:UNCALLED_SLA_BREACH; LOW:NON_ASCII_HOMOGLYPH | Call in Texas (CST) daytime; recommend Teen Leadership Track, US weekend batch. (counsellor) |
| **P2** | LEAD-802 | Follow_Up_Cold → **Follow_Up_Cold** | "price high thinking" | Cold 3 | Unpaid_Link_Not_Clicked | HIGH:PRICE_DUMP_BEFORE_VALUE; HIGH:FALSE_URGENCY; MEDIUM:UNVERIFIED_PRICING | Team-lead-approved re-pitch: send the bar-model explanation of Zoya's demo, then offer a 15-min screen-share with Mr. Vikram. No discount, no deadline. (team_lead) |
| **P2** | LEAD-806 | Follow_Up_Cold → **Follow_Up_Warm** | "kid did not like demo" | Warm 4 | No order | HIGH:RUBRIC_GAMING; HIGH:REQUIRED_REMEDY_NOT_OFFERED; HIGH:DISMISSIVE_OF_CHILD_WELLBEING | Coach Arvind/academic counsellor offers a free 1-on-1 bridge or Little Starters micro-batch (max 3, age 5-6); reassign lead away from Karan. (academic_team) |
| **P2** | LEAD-808 | Follow_Up_Warm → **Contacted_Discovery_Pending** | "ok" | Cold (provisional) 3 | No order | MEDIUM:CLASS_NOT_IN_CATALOG; MEDIUM:MISSING_FOLLOWUP_DATE; MEDIUM:VAGUE_DISPOSITION | Re-discovery call (Doha time). Disposition 'Busy / ok' has no information. Confirm GCC Track pricing first (class 108 missing from catalog). (counsellor) |
| **P2** | LEAD-810 | Follow_Up_Warm → **Contacted_Discovery_Pending** | "cb" | Cold (provisional) 3 | No order | MEDIUM:STALE_FOLLOWUP_DATE; MEDIUM:VAGUE_DISPOSITION | Re-discovery call; fix invalid follow-up date (2026-11-01 is before last call). (counsellor) |
| **P3** | LEAD-811 | New_Duplicate_Lead → **Merged_Duplicate** | "parent clicked brochure download on website" | n/a  | No order | HIGH:DUPLICATE_LEAD | Merge into LEAD-801; suppress all messaging from this record. (ops_finance) |

## Intent score breakdown (deterministic)

| Lead | Score | Breakdown |
|---|---|---|
| LEAD-801 | 9 (Hot) | base +2 | demo engagement 5/5 +2 | parent_stated_pain +1 | fee_accepted +1 | schedule_confirmed +1 | next_step_agreed_with_time +1 | decision_maker_absent -1 | payment action (Unpaid_Link_Opened_Twice) +2 |
| LEAD-802 | 3 (Cold) | base +2 | demo engagement 4/5 +1 | parent_stated_pain +1 | price_objection_unresolved -1 | competitor_active -1 | info_requested +1 |
| LEAD-803 | 1 (Cold) | base +2 | demo engagement 4/5 +1 | parent_stated_pain +1 | parent_visible_enthusiasm +1 | override: DNC/hostile → 1 |
| LEAD-804 | 10 (Converted) | base +2 | demo engagement 5/5 +2 | parent_stated_pain +1 | fee_accepted +1 | schedule_confirmed +1 | next_step_agreed_with_time +1 | explicit_commitment_to_pay +2 | parent_visible_enthusiasm +1 | override: Paid → 10 |
| LEAD-805 | 9 (Hot) | base +2 | demo engagement 4/5 +1 | parent_stated_pain +1 | fee_accepted +1 | schedule_confirmed +1 | next_step_agreed_with_time +1 | explicit_commitment_to_pay +2 | info_requested +1 | payment action (Payment_Failed) +2 |
| LEAD-806 | 4 (Warm) | base +2 | demo engagement 2/5 -1 | parent_stated_pain +1 | conditional_yes_with_available_fix +2 |
| LEAD-807 | 6 (Warm (provisional)) | base +2 | demo engagement 5/5 +2 | explicit_buying_question +2 |
| LEAD-808 | 3 (Cold (provisional)) | base +2 | demo engagement 4/5 +1 |
| LEAD-809 | 8 (Hot (provisional)) | base +2 | demo engagement 5/5 +2 | explicit_commitment_to_pay +2 | payment action (Payment_Failed) +2 |
| LEAD-810 | 3 (Cold (provisional)) | base +2 | demo engagement 4/5 +1 |
| LEAD-812 | 5 (Warm (provisional)) | base +2 | demo engagement 5/5 +2 | parent_visible_enthusiasm +1 |
