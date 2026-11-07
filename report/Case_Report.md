<div class="cover">
<div class="kicker">BAMBINOS.LIVE · AI PROGRAM MANAGER (SALES) · STAGE 2 CASE</div>
<h1 class="title">Post-Demo Conversion &amp; Call Intelligence Engine</h1>
<p class="subtitle">An AI pipeline that audits every counselling call, cleans the CRM, scores intent and writes follow-ups parents actually read.</p>
<p class="meta">Submitted by Koushik Goteti · Repository: <code>bambinos-ai-sales-pipeline</code></p>
</div>

## Executive summary

**The problem.** Managers hear about 2% of calls. The CRM says "cb" and "ok". Follow-ups read like spam. The six sample calls show what that hides: one parent had **already paid** and was still sitting in "Payment_Link_Sent". One rep made **six critical compliance violations** but logged the lead as "Hot – will pay today". A mother ready to pay for an age-matched batch was logged as "child not interested". Two high-intent demos were **never called**.

**The solution.** An n8n pipeline: *call ends → multilingual transcript → LLM audit and extraction (quote-or-zero) → deterministic rules engine → auto-CRM update, private coaching card, and a gated 3-touch WhatsApp sequence*. Payment webhooks and a 30-minute hygiene sweep close the leaks the calls never reveal.

**What I built and ran on the dataset (all in the repo):**

| Output | Result on the provided data |
|---|---|
| Call audit scores (6 calls) | 98.8 · 15.0 · **0.0 AUTO-FAIL** · 96.2 · 91.2 · 3.8 (**rubric gaming detected**) |
| Evidence verification | **100/100** quotes verified verbatim against the transcripts by code |
| Compliance flags | 7 CRITICAL, 7 HIGH, 4 MEDIUM, 4 LOW on calls, plus 26 data-guardrail and system flags |
| Cleaned CRM | 12 rows re-staged. **9 of 12 rep stages corrected** (paid, compliance hold, recovery, merged duplicate…) |
| WhatsApp | 9 three-touch sales sequences, 1 onboarding flow, 1 compliance-hold apology, 1 suppressed duplicate. Every touch gated |

**The business case.** At 1,000 demos a week, a **+2 to +3 pp** lift in conversion is **20–30 extra enrollments a week**, or **₹1.55–2.33 Cr a year** in new revenue (₹1.14–1.70 Cr on India-only pricing). The system runs for about ₹26k a week and **breaks even at 1.7 extra enrollments a week**. It gives 100% audit coverage and saves about **563 manager-hours a week** compared with doing the same coverage manually.

---

## A. Sales discovery and call evaluation framework

### A1. Why parents buy, and how that differs by market

Parents don't buy "48 sessions". They buy relief from a specific worry about their child, once they trust this teacher and this format. The demo creates the proof. The counselling call's job is to turn that proof into the parent's own story.

| | India | GCC | US/UK |
|---|---|---|---|
| Core anxiety | Marks, competition, stage fear in front of relatives | Curriculum exams (British/CBSE/IB), value for money | Confidence, character, staying connected to culture |
| Decision unit | Joint (spouse; one parent often pays) | Joint; father often pays | Often one parent, fast, but time-poor |
| Price lens | Per-session cost, EMIs, discount-aware | Compared with AED 300–400 local tuition | Low price sensitivity, high schedule sensitivity |
| Trust builders | Teacher feedback on *my* child, small batch, refund | Proof of **method**, not brand | Peer fit (same age and region), non-dogmatic framing |
| Deal killers | Pressure, fake guarantees | Price before value, brand bragging | Schedule friction, generic treatment |

The sample calls bear this out. Rohan's spouse-objection call (01) and the Gita schedule call (04) score 96–99 because they lead with the child's moment. Sneha's Dubai call (02) loses a parent who *wanted* the product, because the price came at 0:30 and "Shark Tank" was offered where the bar-model method should have been.

### A2. The call quality scorecard (7 dimensions, 100 points)

| # | Dimension | Wt | What a 4/4 looks like |
|---|---|---|---|
| D1 | Rapport & child-specific praise | 10 | Opens with a concrete demo moment that **matches the educator's evaluation** |
| D2 | Diagnosing the learning pain | 20 | The parent names the gap in their own words; the rep links it to the evaluation |
| D3 | Demo-linked value pitch **before** price | 20 | Pain → demo proof → format/curriculum → *then* price (per session + refund) |
| D4 | Objection handling | 20 | Isolates the real objection and gives a concrete fix that exists in the catalog |
| D5 | Commitment & clear next step | 15 | Time-bound next step **agreed by the parent** |
| D6 | Listening & talk balance | 10 | Rep talk-time 40–55% and responds to what the parent actually said |
| D7 | Compliance & trust | 5 | Only verified claims; policy-accurate price, discount and refund terms |

**Caps applied in code:** any CRITICAL flag caps the score at 30 (**AUTO-FAIL**). Any HIGH flag caps it at 60. **Rubric gaming** sets D1 and D2 to 0. A score with no verified quote falls to 0.
**Anti-gaming:** a discovery question counts only if the *answer is used later*, and praise must match the educator's note. That is why Karan's call 06 (checklist read out in 27 seconds, "I am praising the child now") scores **3.8**, not the 60+ a keyword-matching rubric would give it.

### A3. Structured CRM taxonomy

| Field | Values / rule |
|---|---|
| **Lead intent** | Hot 8–10 · Warm 4–7 · Cold 1–3. The LLM extracts 13 evidence-backed boolean signals, and **code computes the number** (base 2; demo engagement −1 to +2; commitment to pay +2; payment action +2; spouse absent −1; …). Overrides: Paid = 10, DNC = 1, unpaid capped at 9 |
| **Primary objection** | `PRICE_VALUE` · `PRICE_CASHFLOW` · `SPOUSE_DECISION` · `SCHEDULE_CONFLICT` · `CHILD_NOT_INTERESTED` (with a mandatory *root cause*, e.g. batch mismatch) · `COMPETITOR_COMPARISON` · `EXAM_TIMING` · `SCREEN_TIME` · `TRUST_CREDIBILITY`. Each has a quote and a status (open/resolved) |
| **Current blocker** | What stops payment *now* (e.g., "UPI mandate OTP timeout"), separate from the objection |
| **Child's demo highlight** | One sentence taken **only** from the educator's "magic moment" field, with no embellishment |
| **Next best action** | Enum code + owner + due time in the **parent's** timezone: `CALL_NOW_SLA`, `SEND_SPOUSE_SUMMARY`, `VALUE_REPITCH_METHOD`, `PAYMENT_RECOVERY`, `ONBOARDING_HANDOFF`, `ACADEMIC_BATCH_FIX`, `REDISCOVERY_CALL`, `COMPLIANCE_HOLD`, `MERGE_DUPLICATE` |
| **CRM stage** | Set by **rules**, never by the LLM: Paid → `Enrolled_Paid`; CRITICAL → `Compliance_Hold`; failed → `Payment_Failed_Recovery`; duplicate → `Merged_Duplicate` |

---

## B. End-to-end workflow and CRM automation

### B1. Pipeline map

<div class="diagram">
<svg viewBox="0 0 1000 300" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica, Arial" font-size="12">
<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#475569"/></marker></defs>
<g fill="#eef2ff" stroke="#4f46e5" stroke-width="1.4">
<rect x="10" y="40" width="120" height="56" rx="8"/><rect x="155" y="40" width="120" height="56" rx="8"/><rect x="300" y="40" width="130" height="56" rx="8"/><rect x="455" y="40" width="140" height="56" rx="8"/>
</g>
<g fill="#fef3c7" stroke="#d97706" stroke-width="1.4"><rect x="620" y="40" width="150" height="56" rx="8"/></g>
<g fill="#ecfdf5" stroke="#059669" stroke-width="1.4"><rect x="800" y="10" width="190" height="40" rx="8"/><rect x="800" y="62" width="190" height="40" rx="8"/><rect x="800" y="114" width="190" height="40" rx="8"/></g>
<g fill="#fee2e2" stroke="#dc2626" stroke-width="1.4"><rect x="620" y="140" width="150" height="44" rx="8"/></g>
<g fill="#f1f5f9" stroke="#475569" stroke-width="1.4"><rect x="800" y="180" width="190" height="44" rx="8"/><rect x="800" y="240" width="190" height="44" rx="8"/><rect x="10" y="200" width="250" height="44" rx="8"/><rect x="300" y="200" width="270" height="44" rx="8"/></g>
<g fill="#0f172a" text-anchor="middle">
<text x="70" y="64">Call ends</text><text x="70" y="80" font-size="10">Zoom / telephony</text>
<text x="215" y="64">Transcription</text><text x="215" y="80" font-size="10">EN · Hinglish · AR-EN</text>
<text x="365" y="64">Context join</text><text x="365" y="80" font-size="10">CRM · demo eval · catalog</text>
<text x="525" y="64">LLM Prompt 01</text><text x="525" y="80" font-size="10">audit · flags · signals</text>
<text x="695" y="62">Rules engine</text><text x="695" y="78" font-size="10">verify quotes · score · caps</text><text x="695" y="90" font-size="10">intent · stage · guardrails</text>
<text x="895" y="35">Auto-CRM update</text>
<text x="895" y="87">Private coaching card (rep)</text>
<text x="895" y="132">Prompt 02 → WhatsApp 3-touch</text><text x="895" y="146" font-size="10">gated: T0 auto · T1–T3 approve</text>
<text x="695" y="160">CRITICAL flag</text><text x="695" y="175" font-size="10">freeze · page Sales Head</text>
<text x="895" y="200">Send gate + Prompt 03</text><text x="895" y="214" font-size="10">paid · quiet hours · regex · stop</text>
<text x="895" y="260">WhatsApp Cloud API</text><text x="895" y="274" font-size="10">approved templates</text>
<text x="135" y="220">Payment webhooks (Razorpay/Stripe)</text><text x="135" y="235" font-size="10">Paid → onboarding · Failed → recovery</text>
<text x="435" y="220">Cron every 30 min: hygiene sweep</text><text x="435" y="235" font-size="10">uncalled SLA · duplicates · stale follow-ups</text>
</g>
<g stroke="#475569" stroke-width="1.4" fill="none" marker-end="url(#a)">
<path d="M130 68 H153"/><path d="M275 68 H298"/><path d="M430 68 H453"/><path d="M595 68 H618"/>
<path d="M770 60 L798 30"/><path d="M770 70 H798"/><path d="M770 82 L798 130"/><path d="M695 96 V138"/>
<path d="M895 154 V178"/><path d="M895 224 V238"/><path d="M570 222 C 700 222, 700 120, 770 100"/>
</g>
</svg>
</div>

**Stack:** Zoom/Exotel recording webhooks → Deepgram Nova-3 multilingual (diarized, handles code-switching) → **n8n** (self-hosted; the rules engine runs inline in a Code node) → any JSON-mode LLM at temperature 0 → **Google Sheets CRM** for the pilot (then LeadSquared/Zoho over HTTP) → WhatsApp Cloud API templates → Slack for approvals and alerts. Two workflow exports are in `/workflow` (26 + 11 nodes). **About 2 minutes from hang-up to an updated CRM and the rep's coaching card.**

**Why the LLM is not trusted alone.** The LLM gives *judgments* (0–4 scores, booleans, enums), each with a timestamped verbatim quote. Code turns them into numbers, stages and send decisions, and checks every quote against the transcript. On this dataset **100/100 quotes verified**. Any score without verified evidence is set to zero and the call goes to a human.

### B2. Guardrails and human-in-the-loop

The AI drafts 100% of messages. **Whether a message is sent automatically depends on what it commits the company to**, not on how good the AI is.

| Tier | Sender | Used for | Examples from the dataset |
|---|---|---|---|
| **T0: Auto** | System (pre-approved template) | Factual recap with no price, same-amount payment retry, onboarding, reminders | 804 welcome, 805 failed-UPI retry, 810 recap |
| **T1: Counsellor 1-click** | Rep | Anything with price, installment, discount ≤10%, batch change, seat hold, objection argument | 801 spouse summary, 805 seat/installment |
| **T2: Team lead** | Team lead | First message after a HIGH-flag call, re-pitch after a botched call, any new concession | 802 bar-model re-pitch, 806 micro-batch offer |
| **T3: Manager only** | Sales Head | CRITICAL flags, refunds, DNC, complaints, >10% discount | 803 apology and correction |
| **Blocked** | Nobody | Paid (sales content), duplicate, DNC, quiet hours, 4th touch | 811; 804 sales cadence |

**Compliance red flags caught on calls:** CRITICAL = fake outcome guarantee · unauthorized refund promise · discount above cap · false 1-on-1 claim · threat/coercion · off-record side deal · DNC request. HIGH = price dump before value · required remedy not offered · dismissive of child wellbeing · false urgency · rubric gaming. MEDIUM/LOW = unverified package pricing · unsubstantiated statistics · fake exclusivity · unverified scarcity, competitor or feature claims · discount stacking.

**Data guardrails (deterministic, no LLM):** the paid gate · discount-vs-catalog check on every order · order amount sanity · catalog coverage (no price message if the class or currency is missing) · duplicate merge on student_id/mobile · 2-hour speed-to-lead SLA · follow-up date hygiene · vague-disposition replacement · non-ASCII homoglyph detection.

**Cadence rules:** at most 3 touches. Sends only between 09:00 and 20:30 *parent-local* time (payment-failure help allowed until 21:30). Same language as the call. Touch 3 always includes a soft opt-out. Stop on payment, reply, STOP, merge or hold. The LLM fills **template variables only**, and a regex filter plus an LLM safety pass (Prompt 03) block guarantees, refund-term changes, off-catalog prices, ALL-CAPS and countdowns.

---

## C. Prototype results across the dataset

### C1. Call audits (6 recorded calls)

| Lead | Rep | Talk % | Score | Grade | Key finding |
|---|---|---|---|---|---|
| 801 Aarav | Rohan | 46% | **98.8** | A | Turned the spouse objection into a forwardable summary; held the seat; agreed an 11 AM callback |
| 802 Zoya | Sneha | 68% | **15.0** | D | Price at 0:30 (breaks the class 205 rule), 30-min fake deadline, couldn't explain the bar-model method |
| 803 Vihaan | Amitabh | 84% | **0.0** | AUTO-FAIL | Rank-1 guarantee, 6-month refund, **42% discount**, fake 1-on-1, blacklist threat, DNC. Rep logged "Hot" |
| 804 Meera | Rohan | 44% | **96.2** | A | Fixed the schedule live (Sat-Sun 9:30 PST, same teacher). **Paid 2h later but stage never updated** |
| 805 Kabir | Pooja | 48% | **91.2** | A | Hinglish; competitor, exam and cash-flow objections all resolved. Gave a discount *and* an installment (₹1,200 margin leak) |
| 806 Ananya | Karan | 74% | **3.8** | D | **Rubric gaming**. Refused the class 401 remedy (micro-batch / 1-on-1 bridge) to a mother ready to pay |

### C2. Cleaned CRM and pipeline leaks (all 12 leads)

| P | Lead | Rep stage → **AI stage** | Intent | Objection / blocker | Next best action |
|---|---|---|---|---|---|
| P0 | 803 | Follow_Up_Hot → **Compliance_Hold** | Cold 1 | Trust (rep-caused); screen time | Void ₹5,500 link, DNC, Sales Head review within 2h |
| P0 | 804 | Payment_Link_Sent → **Enrolled_Paid** | Converted | Schedule (resolved) | Stop sales cadence; **check batch is weekend, not portal default Tue/Thu** |
| P0 | 805 | Follow_Up_Warm → **Payment_Failed_Recovery** | Hot 9 | UPI mandate OTP timeout | Auto retry link (one-time UPI/card), Hinglish |
| P0 | 809 | Payment_Link_Sent → **Payment_Failed_Recovery** | Hot 8* | 3DS declined | **Held** until ops confirms GBP price (not in catalog) |
| P1 | 801 | Follow_Up_Warm → **Follow_Up_Hot** | Hot 9 | Spouse decision | Spouse summary; offer father a 10-min call with the teacher |
| P1 | 807 | Uncalled → Uncalled (**SLA breach 29.5h**) | Warm 6* | Not yet discovered | Call now: 5/5 Olympiad, asked when the batch starts |
| P1 | 812 | Uncalled → Uncalled (**SLA breach 14.5h**) | Warm 5* | Not yet discovered | Call in CST hours. Name has Cyrillic homoglyphs |
| P2 | 802 | Follow_Up_Cold → Follow_Up_Cold | Cold 3 | Price-value vs local tutor | Team-lead re-pitch of the method. No discount, no deadline |
| P2 | 806 | Follow_Up_Cold → **Follow_Up_Warm** | Warm 4 | Child not interested → **batch mismatch** | Academic team offers a free 1-on-1 bridge or a 5–6 micro-batch |
| P2 | 808 | Follow_Up_Warm → Discovery_Pending | Cold 3* | "Busy / ok" | Re-discover. **Class 108 missing from catalog.** Reassign from Amitabh |
| P2 | 810 | Follow_Up_Warm → Discovery_Pending | Cold 3* | "cb" | Re-discover. Follow-up date is *before* the last call |
| P3 | 811 | New_Duplicate → **Merged_Duplicate** | n/a | Duplicate of 801 | Merge; brochure download counts as an intent signal for 801 |

\* provisional: demo-only signals, no call yet. **System-level findings:** the gateway's discount anomaly rule fires at >15% while policy caps discounts at 10%, so discounts of 10–15% pass silently. Order 99402 stores AED 12,000 instead of 1,200. Timestamps mix IST and PST with no offsets.

### C3. Follow-ups: three examples

**801: spouse decision (T1, rep approves).** *"Hi Divya, Rohan here 😊 As promised, a note you can forward to Aarav's dad: 🎤 Today, at minute 18, Ms. Rhea gave Aarav a 3-step 'Superhero Hook'. He unmuted and told a 45-second space rescue story… So it's not grammar tuition. His gap is freezing when put on the spot, and that's what we fix…"* This answers the father's exact question ("Is this just grammar tuition?") with his son's own moment.

**802: price-value (T2, team lead approves).** *"You asked a fair question I didn't answer well: what exactly Mr. Vikram did with Zoya today… he taught her the Bar-Model method… She then solved two Grade-6 British-curriculum fraction word puzzles on her own… That's the difference from worksheets."* No discount and no deadline. The message repairs the value gap the rep created.

**805: payment recovery (T0 auto, Hinglish, sent within 5 minutes of the failure).** *"Rajesh ji… bank ke OTP timeout ki wajah se UPI payment complete nahi hua. Yeh fresh link hai Installment 1 (Rs. 5,400) ke liye… Is baar autopay mandate ki jagah normal UPI, card ya netbanking choose kar sakte hain…"*

Stop-trigger cases: **804** goes to onboarding only, never "kindly confirm payment". **803** gets one manager-voice correction (true refund policy, link cancelled, "we won't call you"). **811** is suppressed. All 31 touches, with approval tier and gate status, are in `outputs/final/whatsapp_sequences.md`.

---

## D. Revenue impact, adoption and the 30-60-90 day rollout

### D1. Funnel math

| | Baseline | +2 pp | +3 pp |
|---|---|---|---|
| Demo → paid conversion | 15% | 17% | 18% |
| Enrollments per week (1,000 demos) | 150 | 170 (+20) | 180 (+30) |
| Extra enrollments per year | – | +1,040 | +1,560 |
| **Extra revenue/yr (blended ₹14,928 per enrollment)** | – | **₹1.55 Cr** | **₹2.33 Cr** |
| Extra revenue/yr (conservative, India-only ₹10,917) | – | ₹1.14 Cr | ₹1.70 Cr |

*Blended revenue per enrollment = catalog averages across 6 courses, weighted 70% India / 15% GCC / 15% US-UK at ₹22.9/AED and ₹88/USD.*

**Where the +2–3 pp comes from:** (1) speed-to-lead. 2 of the 12 sample leads were high-intent and never called, and the SLA sweep catches this within 30 minutes. (2) payment recovery. 2 of 6 orders failed, and an automatic retry within 5 minutes recovers many of them. (3) objection-specific follow-ups instead of "kindly confirm payment". (4) coaching the bottom-quartile reps up to the level of Rohan's calls.

**Manager and rep hours**

| | Hours/week |
|---|---|
| Today: 2% manual audit (20 calls × 35 min) | 11.7 |
| Manual effort needed for 100% coverage | 583 (≈14.6 FTE) |
| With AI: 100% audited; managers review only the flagged 20% at 6 min | 20 |
| **Manager hours saved vs. equivalent coverage** | **≈563 hrs/week (≈14 FTE)** |
| Counsellor admin saved (notes + follow-up drafting, 6 min/call) | 100 hrs/week ≈ **2.5 hrs per rep**, reinvested in calls |

**Run cost:** STT ₹13.2k + LLM ₹8.8k + WhatsApp ₹2.4k + hosting ₹1.2k ≈ **₹25.6k/week (₹13.3 L/yr)**. That is a **12× ROI at +2 pp**, with break-even at **1.7 extra enrollments a week (0.2 pp)**. Not counted: renewals, refunds and chargebacks avoided through compliance, and referrals.

### D2. Rep pushback: making counsellors *want* the tool

Reps hate being policed. They love tools that save time and help them earn. So the positioning is **"your AI co-pilot that does your admin and finds your money"**, not "AI audit".

1. **Give value before asking for anything.** Week 1, reps get auto-filled CRM notes and ready-to-send follow-ups (about 2.5 hrs a week back) **before** any score is visible to a manager.
2. **Private by default.** For the first 60 days, coaching cards go *only* to the rep. Managers see team trends and CRITICAL compliance only.
3. **Strengths first, at most two fixes, and a sentence to say next time.** Every card opens with what went well, and every fix includes an exact line to try.
4. **Show reps the money.** A daily "Hot lead radar" plus "₹ you recovered from failed payments and uncalled demos". Commission goes up, so adoption follows.
5. **Reps can dispute.** A one-tap "dispute" sends the call to human review. AI mistakes are fixed visibly and fed back into the prompt.
6. **Co-designed and transparent.** Five champion reps (Rohan and Pooja are natural choices) co-write the rubric. The rubric is public, and because it rewards what the parent actually says, "gaming" it means doing the job well.
7. **Compliance as protection.** The AI catches a risky promise *before* it becomes a refund, a chargeback or a complaint with the rep's name on it.
8. **Recognition over punishment.** An opt-in "Call of the Week" and a "most improved" board. No firing decision is ever made on an AI score alone; CRITICAL flags are always reviewed by a human.

### D3. 30-60-90 day rollout

| Phase | Scope | Milestones | Exit criteria |
|---|---|---|---|
| **Days 0–30: Shadow and no-regret fixes** | All calls processed silently; Sheets CRM | Guardrails go live right away: paid gate, payment-retry T0, SLA sweep, duplicate merge, gateway 10% rule. Managers double-score 200 calls to calibrate. Co-design the rubric with 5 champion reps | AI–human agreement ≥85% (±1 per dimension); 0 messages to paid leads; SLA alerts under 30 min |
| **Days 31–60: Pilot vs. control** | 2 teams (~15 reps) vs. 2 control teams | Private coaching cards, auto-CRM, T1/T2 approval flow, Hinglish templates approved by Meta. Weekly prompt retro. Track draft edit rate | Conversion lift ≥1.5 pp vs. control; approval rate ≥80%; rep satisfaction ≥7/10 |
| **Days 61–90: Scale** | All 40 reps; LeadSquared/Zoho integration | Manager dashboard, Call-of-the-Week library, T0 recaps auto-sent, compliance trend review with HR/legal, monthly calibration | +2 pp company-wide; critical flags down 50%; 100% of called leads have a valid NBA and follow-up date |

**KPIs on the dashboard:** demo→paid conversion · median speed-to-lead · payment-failure recovery rate · CRM completeness (% of leads with a valid NBA and follow-up date) · WhatsApp reply rate and opt-out rate · CRITICAL flags per 100 calls · AI–human agreement · draft approval and edit rate · rep tool NPS.

**Risks and mitigations:** Hinglish/Arabic STT errors → multilingual model plus a low-confidence route to human review. Hallucination → quote-or-zero with code verification and enum-only fields. WhatsApp policy → templates plus an opt-in check. Privacy (DPDP Act; children's data) → consent disclosure, PII minimisation, zero-retention API, 90-day transcript retention. Rep distrust → private-first, dispute button, co-design.

---

<div class="appendix">

### Repository map
`framework/` scorecard, taxonomy, guardrails · `prompts/` the 3 system prompts (audit/extract, follow-up writer, safety check) · `config/scoring_config.json` weights, caps, intent formula, approval tiers · `scripts/rules_engine.py` deterministic engine (standard library only) · `scripts/run_llm.py` regenerates the LLM outputs via any OpenAI-compatible API · `scripts/funnel_math.py` · `workflow/` two n8n exports + architecture · `outputs/llm_raw/` raw LLM JSON · `outputs/final/` scorecards, compliance alerts, coaching cards, **cleaned_crm_leads.csv** (import into Google Sheets), WhatsApp sequences, pipeline-leak report, evidence log.

</div>
