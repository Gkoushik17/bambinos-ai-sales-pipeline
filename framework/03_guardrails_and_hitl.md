# Guardrails, Compliance Flags & Human-in-the-Loop

## 1. Compliance red flags the AI must catch on calls

Severity drives automation: **CRITICAL** freezes the lead and pages the manager; **HIGH** caps the score and needs team-lead approval before any message goes out; **MEDIUM/LOW** feeds coaching.

| Code | Severity | What it looks like | Policy source |
|---|---|---|---|
| `FAKE_OUTCOME_GUARANTEE` | CRITICAL | "Rank 1 in 30 days", "reads Harry Potter in a month", "Olympiad gold guaranteed" | Catalog `forbidden_compliance_red_flags` |
| `UNAUTHORIZED_REFUND_PROMISE` | CRITICAL | "100% refund anytime in 6 months", "off the record I'll refund" | Official refund policy: 100% within 14 days (≤4 classes), pro-rata after |
| `DISCOUNT_ABOVE_CAP` | CRITICAL | Any discount above 10% without a Team Lead approval code. **Also checked in code against the order table** | `max_rep_discount_allowed_pct` |
| `FALSE_PRODUCT_CLAIM` | CRITICAL | Promising 1-on-1 for a 6-kid group plan | Course 104/101 rules |
| `THREAT_OR_COERCION` | CRITICAL | "Child's ID will be blacklisted if you don't pay in 5 minutes" | Course 104 rule |
| `OFF_RECORD_SIDE_DEAL` | CRITICAL | "Between you and me", "I hacked my manager's quota" | Code of conduct |
| `DNC_REQUEST` | CRITICAL (routing) | "Do not call me again". Lead moves to `Lost_DNC` for calls | Consumer protection / TRAI DND norms |
| `PRICE_DUMP_BEFORE_VALUE` | HIGH | Fee quoted in the first 2 minutes before explaining the method | Course 205 rule |
| `REQUIRED_REMEDY_NOT_OFFERED` | HIGH | Overwhelmed 5–6-year-old pushed into a standard batch instead of a micro-batch or 1-on-1 bridge | Course 401 rule |
| `DISMISSIVE_OF_CHILD_WELLBEING` | HIGH | "Kids always make excuses", "force her to sit" | Code of conduct |
| `FALSE_URGENCY` | HIGH | "Link expires in 30 minutes, seats fill fast" (when not true) | Code of conduct |
| `RUBRIC_GAMING` | HIGH | Reads checklist items in 30 seconds and narrates "I am praising the child now" | Audit integrity |
| `CRM_DISPOSITION_MISMATCH` | HIGH | Rep logs "Interested, will pay today" on a call where the parent hung up angry | CRM integrity (rules engine) |
| `UNVERIFIED_PRICING` | MEDIUM | Quotes a package not in the catalog (e.g., "12-month AED 2,100") | Catalog |
| `UNSUBSTANTIATED_CLAIM` | MEDIUM | "Improves maths scores by 40%", "top 1% teachers" | Marketing claims policy |
| `FALSE_EXCLUSIVITY` | MEDIUM | "Shortlisted for an Elite batch" when no such batch exists | Code of conduct |
| `SCARCITY_CLAIM_UNVERIFIED` | LOW | "1 seat left": verified against the live batch roster | Roster API |
| `COMPETITOR_CLAIM_UNVERIFIED` | LOW | "Half the price of 1-on-1" | Marketing claims policy |
| `DISCOUNT_STACKING` | LOW | Discount offered when an installment alone would have closed (margin leak) | Commercial coaching |

## 2. Deterministic data guardrails (rules engine, no LLM)

| Check | Rule |
|---|---|
| **Paid gate** | If the order status is `Paid`, stop **all** sales messages, set the stage to `Enrolled_Paid` and start onboarding. (Prevents asking a parent who already paid to "kindly confirm payment" – LEAD-804.) |
| **Discount gate** | `discount_applied / catalog_fee > cap` means the link is voided and the lead frozen. The gateway's own anomaly threshold is **15%**, but policy is **10%**. Discounts of 10–15% would slip through today, so the gateway rule must be fixed. |
| **Amount sanity** | `standard_amount` must equal the catalog fee for that currency (LEAD-802 shows AED 12,000 instead of 1,200). |
| **Catalog coverage** | The class and currency must exist in the catalog before a price can be messaged (class 108 and GBP are missing). |
| **Duplicate merge** | Same `student_id` or mobile number: merge into the oldest active lead, keep its owner and suppress messages from the duplicate (LEAD-811 → 801). |
| **Speed-to-lead SLA** | Demo attended and not called within **2 hours**: P1 alert to the rep and the team lead (LEAD-807, 812). |
| **Follow-up hygiene** | `next_followup_at` that is null, or earlier than `last_call_at`, gets flagged (LEAD-802, 808, 810). |
| **Disposition quality** | Notes under 15 characters, or from a vague list ("cb", "ok", "thinking"), are replaced by the AI `clean_note`. |
| **Text integrity** | Non-ASCII homoglyphs in names break dedup and matching (LEAD-812 contains Cyrillic "Ме"). |

## 3. When does the AI send automatically vs. when must a human click "Approve"?

**Principle:** the AI writes 100% of drafts. Whether a draft is sent automatically depends on **what the message commits the company to**, not on how good the AI is.

| Tier | Who sends | Message types | Example |
|---|---|---|---|
| **T0: Auto-send** | System, via a pre-approved WhatsApp template with variable slots | Factual demo recap with no price, payment-retry link for the **same** amount (no new offer), onboarding/batch confirmation, class reminders | LEAD-804 welcome, LEAD-805 failed-UPI retry, LEAD-810 demo recap |
| **T1: Counsellor 1-click approve** | The rep reviews it in the CRM or Slack and taps Approve or Edit | Anything mentioning **price, installment, discount (≤10%), batch change, seat hold**, or an objection-specific argument | LEAD-801 spouse summary, LEAD-805 exam-pause message |
| **T2: Team-lead approve** | Team lead | The first message after a **HIGH**-flag call, any re-pitch after a botched call, any new concession (free bridge session, extended seat hold) | LEAD-802 value re-pitch, LEAD-806 micro-batch offer |
| **T3: Manager / Sales Head only** | The human writes or approves it. The AI never auto-sends | **CRITICAL** flags, refunds, DNC requests, complaints, discounts above 10%, child-safety concerns | LEAD-803 apology and correction |
| **Blocked** | Nobody | Lead paid (for sales content), merged duplicate, DNC on that channel, quiet hours, a 4th touch | LEAD-811, LEAD-804 sales cadence |

### Cadence rules
- **At most 3 touches** per objection cycle. Touch 3 always offers an easy opt-out ("reply *later* and I'll pause").
- **Quiet hours:** only send between 09:00 and 20:30 in the **parent's** local timezone. Event-driven utility messages (payment failure) may go out within 15 minutes of the event, until 21:30.
- **Stop triggers:** a payment webhook = Paid, a parent reply (hand off to a human), a STOP/"not interested" keyword, a compliance hold, a duplicate merge, or a flagged link.
- **Language:** reply in the call's language (Hinglish call → Hinglish WhatsApp).
- **WhatsApp Business policy:** outside the 24-hour customer-service window, messages go out as Meta-approved **Utility** or **Marketing** templates. The LLM only fills **variables** (child moment, objection answer), and a validator checks each variable's length and that it contains no banned words.

## 4. Anti-hallucination controls
1. **Grounded inputs only:** the prompt receives the transcript, the demo evaluation, the order row and the catalog row. Nothing else.
2. **Quote-or-zero:** every score, flag and objection must cite `{ts, quote}`. The code checks that each quote is a real substring of the transcript (fuzzy match ≥ 0.9). If it isn't, the dimension score drops to 0 and the call goes to `needs_human_review`.
3. **Enum-only fields:** the JSON schema rejects any value outside the enums.
4. **Numbers come from code:** prices, discounts, intent scores and totals are computed by the rules engine from the catalog and order tables, never written freely by the LLM.
5. **Outgoing message check:** each WhatsApp draft passes a second LLM call (`prompts/03_outgoing_message_safety_check.md`) and a regex filter for guarantees, refund terms, discounts above the cap, "last chance", and ALL-CAPS urgency.
6. **Calibration:** 5% of calls are double-scored by managers. If agreement between AI and human (± 1 point per dimension) drops below 85%, the prompt goes back for review.
