# Call Quality Scorecard (7 dimensions, 100 points)

## Why parents buy kids' courses, and what that means for a counselling call

A parent never buys "48 sessions". They buy relief from a specific worry about their child, and they buy it only once they trust that this teacher and this format will fix it. The demo class creates the proof. The counselling call has to turn that proof into the parent's own story.

| Driver | India | GCC (UAE/Qatar, mostly expat Indian/Arab families) | US/UK (diaspora and local) |
|---|---|---|---|
| **Core anxiety** | Competition, school marks, "falling behind", stage fear in front of relatives | Board/curriculum exams (British, CBSE, IB), value for money compared with local tuition | Confidence, character, staying connected to culture; parents resist "lectures" |
| **Decision unit** | Joint decision (spouse, sometimes grandparents). One parent often handles payment | Joint; often the father pays | Often one parent decides fast, but schedules are packed (sports, activities) |
| **Price lens** | Price per session and EMI/installments; very discount-aware | Compares with cheap offline building tuition (AED 300–400) | Low price sensitivity, high time sensitivity. Timezone and batch fit decide it |
| **What builds trust** | The teacher's specific feedback about *my* child; small batch size; refund policy | Proof of *method*, not brand ("how is this different from worksheets?") | Peer fit (kids of the same age and region), non-dogmatic framing, convenience |
| **What kills the deal** | Pressure, fake guarantees, "call centre" tone | Price dumped before value; brand bragging | Schedule friction; being treated as a generic lead |

Five principles follow from this, and the scorecard enforces them:
1. **Child first, product second.** Open with the child's *specific* demo moment, taken from the educator's note.
2. **The parent names the pain.** A gap the parent says out loud is worth ten that the rep asserts.
3. **Bridge before price.** Go from pain to demo proof to curriculum, and only then to price. Price before value is the most common conversion killer (see call 02).
4. **Treat every objection as a question to answer.** Isolate it, find the real concern behind it, and give the parent what they need to resolve it (e.g., a spouse-ready summary).
5. **Close with a commitment, not pressure.** Agree a specific, time-bound next step. Fake urgency, threats and side deals are compliance failures, not "closing".

---

## The scorecard

Each dimension is scored **0–4** by the AI. Every score above 0 must be backed by at least one verbatim, timestamped quote from the transcript. The rules engine (not the LLM) converts scores to points, checks that each quote really exists in the transcript, and applies caps.

| # | Dimension | Weight | 4 = Excellent | 2 = Partial | 0 = Missing / harmful |
|---|---|---|---|---|---|
| D1 | **Rapport & Child-Specific Praise** | 10 | Opens with a concrete demo moment that matches the educator's evaluation (e.g., "45-second space rescue story") | Generic praise ("she did great") | No praise, or praise that contradicts the evaluation ("natural Grandmaster" for an overwhelmed 6-year-old) |
| D2 | **Diagnosing the Learning Pain** | 20 | Open questions; the parent states the gap in their own words; the rep links it to the educator's observed gap | Asks, but doesn't dig into or use the answer | No discovery, or checklist questions read out with the answers never used (rubric gaming) |
| D3 | **Demo-Linked Value Pitch Before Price** | 20 | Pain → demo proof → curriculum/format → *then* price, framed per session and with the refund policy | Value pitch exists but is generic (brand, Shark Tank) | Price quoted before any value framing ("price dumping") |
| D4 | **Objection Handling** | 20 | Isolates the real objection, asks a follow-up question, and gives a concrete fix (spouse summary, weekend batch, installment, age-matched batch) | Acknowledges the objection, then answers generically | Ignores or argues with it, or reaches straight for a discount or pressure |
| D5 | **Commitment & Clear Next Step** | 15 | Specific, time-bound next step agreed by the parent (e.g., "call at 11 AM, seat held till then") | Vague ("I'll send details") | High-pressure close or no next step |
| D6 | **Listening & Talk Balance** | 10 | Rep talk-time 40–55%; responds to what the parent actually said | 56–65% | >65% monologue, or talks over the parent's concern |
| D7 | **Compliance & Trust** | 5 | Only verified claims; policy-accurate pricing, discounts and refunds | Minor unverified claim (scarcity, competitor price) | Any red flag (see the guardrails document) |

**Score = Σ (dimension score ÷ 4 × weight).**

### Hard caps (applied in code, not by the LLM)
| Condition | Effect |
|---|---|
| Any **CRITICAL** compliance flag (fake guarantee, off-policy refund, discount above the cap, threat, false 1-on-1 claim) | Total capped at **30**, grade = **AUTO-FAIL**, immediate manager alert |
| Any **HIGH** flag (price dump against policy, required remedy not offered, dismissive of child wellbeing) | Total capped at **60** |
| **Rubric gaming detected** (discovery questions read out without using the answers, self-narrated "praise", "urgency close") | D1 and D2 forced to 0; flag `RUBRIC_GAMING` |
| A score above 0 with **no verified quote** | That dimension falls to 0 and the call goes to human review |

### Grade bands
| Score | Grade | What happens |
|---|---|---|
| 85–100 | **A: Model call** | Added to the "Call of the Week" library (rep opt-in) |
| 70–84 | **B: Solid** | One coaching tip |
| 50–69 | **C: Needs coaching** | Coaching card plus a 10-minute micro-drill |
| <50 | **D: At risk** | Team-lead 1:1 within 48h |
| AUTO-FAIL | **Compliance** | Lead frozen, manager review within 2h |

### Anti-gaming design
Reps will learn the rubric. That is fine as long as gaming it means doing the job well. So:
- Scores reward **outcomes visible in the parent's words** (the parent names the pain, the parent agrees a time), not keywords the rep says.
- A discovery question counts only if the **answer is used later** in the call.
- Praise has to **match the educator's evaluation** (we cross-check `2_demo_class_evaluations.csv`).
- Every 50th call, plus every call where the AI score and the outcome disagree, gets a **blind human audit** to calibrate the AI.
