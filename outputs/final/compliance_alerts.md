# Compliance & Data-Integrity Alerts

## A. Call compliance flags (LLM-detected, quote-verified)

| Severity | Lead | Rep | Code | When | Verbatim evidence | Policy | Verified |
|---|---|---|---|---|---|---|---|
| **CRITICAL** | LEAD-803 | Amitabh R*** | `FAKE_OUTCOME_GUARANTEE` | 02:08 | "he will come Rank 1 in his school English exam! 100% guaranteed in writing by me!" | Class 101: NEVER promise specific school exam ranks (e.g., Rank 1 in 30 days) | ✅ |
| **CRITICAL** | LEAD-803 | Amitabh R*** | `UNAUTHORIZED_REFUND_PROMISE` | 02:54 | "I am giving you a 100% no-questions-asked full refund anytime in 6 months!" | Official: 100% refund within 14 days (up to 4 classes), pro-rata thereafter | ✅ |
| **CRITICAL** | LEAD-803 | Amitabh R*** | `OFF_RECORD_SIDE_DEAL` | 02:54 | "Sir, between you and me, off the record, don't look at the website policy" | Code of conduct | ✅ |
| **CRITICAL** | LEAD-803 | Amitabh R*** | `DISCOUNT_ABOVE_CAP` | 03:30 | "Because I hacked my manager's VIP scholarship quota just for you, sir—flat Rs. 4,000 off!" | Class 101: max 10% (Rs. 950) without Team Lead approval code | ✅ |
| **CRITICAL** | LEAD-803 | Amitabh R*** | `FALSE_PRODUCT_CLAIM` | 03:30 | "I will even make it a 1-on-1 private class for the price of a group batch!" | NEVER claim batches are 1-on-1 when selling a 6-kid group plan | ✅ |
| **CRITICAL** | LEAD-803 | Amitabh R*** | `THREAT_OR_COERCION` | 03:30 | "otherwise our system will permanently blacklist Vihaan's student ID forever!" | NEVER threaten that a child will be blacklisted if payment is not made in 5 minutes | ✅ |
| **CRITICAL** | LEAD-803 | Amitabh R*** | `DNC_REQUEST` | 03:54 | "I am cutting the call right now. Do not call me again!" | Consumer protection / DND | ✅ |
| **HIGH** | LEAD-802 | Sneha V*** | `PRICE_DUMP_BEFORE_VALUE` | 00:30 | "So let me quickly tell you our fee structure for Dubai students." | Class 205: Do NOT dump price in the first 2 minutes without explaining how visual Bar-Model problem solving differs from local rote worksheet tuition. | ✅ |
| **HIGH** | LEAD-802 | Sneha V*** | `FALSE_URGENCY` | 02:54 | "the discount link expires in 30 minutes because batch seats fill very fast in Dubai" | Code of conduct: no fabricated deadlines | ✅ |
| **HIGH** | LEAD-803 | Amitabh R*** | `DISMISSIVE_OF_CHILD_WELLBEING` | 02:08 | "Sir, forget about screen time and forget about "train" or "truck"! That is nothing!" | Code of conduct | ✅ |
| **HIGH** | LEAD-806 | Karan K*** | `RUBRIC_GAMING` | 00:05 | "Let me quickly complete my mandatory call checklist" | Audit integrity | ✅ |
| **HIGH** | LEAD-806 | Karan K*** | `REQUIRED_REMEDY_NOT_OFFERED` | 02:38 | "Ma'am all batches are standard 6 kids, just pay Rs. 9,900 on the link and Ops team will see later." | Class 401: if a 5-6 year old felt overwhelmed in a mixed-age demo, offer a complimentary 1-on-1 bridge session or Age 5-6 Micro-Batch (max 3 kids) | ✅ |
| **HIGH** | LEAD-806 | Karan K*** | `DISMISSIVE_OF_CHILD_WELLBEING` | 01:58 | "Ma'am kids always make excuses! Once you pay Rs. 11,000 and force her to sit in the 6-kid batch for 3 weeks" | Code of conduct | ✅ |
| **HIGH** | LEAD-806 | Karan K*** | `FALSE_URGENCY` | 01:58 | "Rs. 9,900 if you pay before 6 PM today" | Code of conduct | ✅ |
| **MEDIUM** | LEAD-802 | Sneha V*** | `UNVERIFIED_PRICING` | 00:30 | "for the 12-month package of 96 classes it is AED 2,100" | Catalog lists only the 48-session plan at AED 1,200 | ✅ |
| **MEDIUM** | LEAD-802 | Sneha V*** | `UNSUBSTANTIATED_CLAIM` | 01:12 | "we have top 1% certified teachers" | Marketing claims policy | ✅ |
| **MEDIUM** | LEAD-803 | Amitabh R*** | `FALSE_EXCLUSIVITY` | 00:06 | "Vihaan has been shortlisted for our super-exclusive Elite Phonics Accelerator batch!" | Catalog has no such batch | ✅ |
| **MEDIUM** | LEAD-806 | Karan K*** | `UNSUBSTANTIATED_CLAIM` | 01:20 | "Chess improves IQ, memory, concentration, and maths scores by 40%!" | Marketing claims policy | ✅ |
| **LOW** | LEAD-801 | Rohan S*** | `SCARCITY_CLAIM_UNVERIFIED` | 02:32 | "currently 5 kids are enrolled, so there is 1 seat left" | Roster verification | ✅ |
| **LOW** | LEAD-805 | Pooja M*** | `COMPETITOR_CLAIM_UNVERIFIED` | 01:40 | "aur price bhi 1-on-1 se almost half padta hai" | Marketing claims policy | ✅ |
| **LOW** | LEAD-805 | Pooja M*** | `FEATURE_CLAIM_UNVERIFIED` | 02:20 | "exam week mein hamare portal par 'Exam Pause / Reschedule' button hota hai" | Product feature list (not in catalog file) | ✅ |
| **LOW** | LEAD-805 | Pooja M*** | `DISCOUNT_STACKING` | 03:00 | "10% scholar discount de sakti hoon, jisse 48 classes ki fee Rs. 12,000 ki jagah Rs. 10,800 ho jayegi" | Commercial guideline | ✅ |

## B. Data guardrail flags (rules engine, deterministic)

| Severity | Lead | Code | Detail |
|---|---|---|---|
| **CRITICAL** | LEAD-803 | `DISCOUNT_ABOVE_CAP` | Order 99403 discount INR 4000 = 42.1% of catalog fee (cap 10%). Void link. |
| **CRITICAL** | LEAD-804 | `PAID_STAGE_NOT_UPDATED` | Order 99404 Paid at 2026-11-03 11:40:12 but CRM stage = Payment_Link_Sent. Block sales cadence; start onboarding. |
| **HIGH** | LEAD-803 | `CRM_DISPOSITION_MISMATCH` | Rep logged Follow_Up_Hot ('good call sent payment link will pay today'); AI intent 1/10. Rep logged 'Interested / will pay today' (Hot); parent hung up and asked not to be called. Falsified disposition. |
| **HIGH** | LEAD-805 | `PAYMENT_FAILED` | Order 99405 failed: Bank_OTP_Timeout_On_UPI_Mandate. Trigger payment-recovery touch. |
| **HIGH** | LEAD-807 | `UNCALLED_SLA_BREACH` | Demo attended 29.5h ago (engagement 5/5), never called. SLA = 2h. |
| **HIGH** | LEAD-809 | `PAYMENT_FAILED` | Order 99409 failed: 3DS_Authentication_Declined_By_Issuer. Trigger payment-recovery touch. |
| **HIGH** | LEAD-811 | `DUPLICATE_LEAD` | Same student_id/mobile as LEAD-801; merge, keep original owner, suppress messages. |
| **HIGH** | LEAD-812 | `UNCALLED_SLA_BREACH` | Demo attended 14.5h ago (engagement 5/5), never called. SLA = 2h. |
| **MEDIUM** | LEAD-801 | `CRM_DISPOSITION_MISMATCH` | Rep logged Follow_Up_Warm ('will ask husband and tell tomorrow'). 'Call back tomorrow' hides a Hot lead with a specific spouse objection and a held seat. |
| **MEDIUM** | LEAD-802 | `ORDER_AMOUNT_MISMATCH` | Order 99402 standard_amount 12000.0 AED vs catalog 1200. Invoice data error. |
| **MEDIUM** | LEAD-802 | `MISSING_FOLLOWUP_DATE` | Called lead with no next_followup_at: will silently go cold. |
| **MEDIUM** | LEAD-802 | `CRM_DISPOSITION_MISMATCH` | Rep logged Follow_Up_Cold ('price high thinking'). 'Price issue' masks a rep-caused value gap; parent is recoverable if shown the method. |
| **MEDIUM** | LEAD-804 | `CRM_DISPOSITION_MISMATCH` | Rep logged Payment_Link_Sent ('wants weekend batch sent link'). Stage left at 'Payment_Link_Sent' after payment cleared. |
| **MEDIUM** | LEAD-805 | `CRM_DISPOSITION_MISMATCH` | Rep logged Follow_Up_Warm ('comparing with planetspark and school exam going on'). 'Thinking' understates a committed parent who attempted payment. |
| **MEDIUM** | LEAD-806 | `MISSING_FOLLOWUP_DATE` | Called lead with no next_followup_at: will silently go cold. |
| **MEDIUM** | LEAD-806 | `CRM_DISPOSITION_MISMATCH` | Rep logged Follow_Up_Cold ('kid did not like demo'). Logged 'Child not interested / Cold'; parent stated explicit conditions under which she would pay. |
| **MEDIUM** | LEAD-808 | `CLASS_NOT_IN_CATALOG` | class_id 108 (Young Communicators GCC Track) missing from pricing/compliance catalog; no price may be messaged. |
| **MEDIUM** | LEAD-808 | `MISSING_FOLLOWUP_DATE` | Called lead with no next_followup_at: will silently go cold. |
| **MEDIUM** | LEAD-808 | `VAGUE_DISPOSITION` | Rep note 'ok' / disposition 'Busy' carries no buying-intent information. |
| **MEDIUM** | LEAD-809 | `CURRENCY_NOT_IN_CATALOG` | GBP price for class 205 not in catalog (order shows GBP 210.0); ops must confirm before re-issuing link. |
| **MEDIUM** | LEAD-810 | `STALE_FOLLOWUP_DATE` | next_followup_at 2026-11-01 10:00:00 is before last_call_at 2026-11-02 12:30:00. |
| **MEDIUM** | LEAD-810 | `VAGUE_DISPOSITION` | Rep note 'cb' / disposition 'Call back' carries no buying-intent information. |
| **LOW** | LEAD-812 | `NON_ASCII_HOMOGLYPH` | Name contains non-ASCII characters 'Ме' (e.g. Cyrillic); breaks dedup/matching. Normalise. |
| **INFO** | LEAD-801 | `PAYMENT_LINK_OPENED` | Order 99401 link opened twice: buying signal. |

## C. System-level flags

| Severity | Code | Detail |
|---|---|---|
| **HIGH** | `GATEWAY_THRESHOLD_MISMATCH` | Payment gateway anomaly rule fires at >15% but policy cap is 10%; discounts of 10-15% currently pass silently. Fix gateway rule. |
| **LOW** | `MIXED_TIMEZONES` | Timestamps are stored in local time without offsets (IST rows mixed with a PST paid_at). Store UTC + parent timezone. |
