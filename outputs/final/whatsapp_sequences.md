# WhatsApp Follow-Up Sequences (with send gates)

Approval tiers: **T0** auto-send (pre-approved template) · **T1** counsellor 1-click · **T2** team lead · **T3** manager only. Gate status is computed by `rules_engine.py` (paid gate, compliance hold, catalog coverage, quiet hours, regex safety, length).

## LEAD-801: SALES_SEQUENCE · Hot 9 · objection: SPOUSE_DECISION · lang: English

**Touch 1** · 2026-11-02 18:05 IST · _Immediately after call (rep promised summary before father returns 8:30 PM)_ · from Rohan  
Approval: **T1_COUNSELLOR** · Gate: **READY** · 106 words

> Hi Divya, Rohan here 😊 As promised, a note you can forward to Aarav's dad:
>
> 🎤 Today, at minute 18, Ms. Rhea gave Aarav a 3-step 'Superhero Hook'. He unmuted and told a 45-second space rescue story, with hand gestures and words like 'asteroid' and 'gravity'.
>
> So it's not grammar tuition. His gap is freezing when put on the spot, and that's what we fix: max 6 kids, he speaks 4-5 times a class, and every 4th week is a Stage Showcase you can both watch live.
>
> Rs. 12,000 for 48 classes (≈ Rs. 250/class), 100% refund within 14 days. Seat held till 11 AM tomorrow.

**Touch 2** · 2026-11-03 13:00 IST · _11 AM callback not connected AND unpaid_ · from Rohan  
Approval: **T2_TEAM_LEAD** · Gate: **READY** · 49 words

> Hi Divya, tried you at 11, no rush at all. Did Aarav's dad get a chance to see the note? If he has questions, Ms. Rhea can do a 10-minute call with him this week, so he hears it straight from the teacher. Want me to set that up?

**Touch 3** · 2026-11-05 18:30 IST · _No reply AND unpaid_ · from Rohan  
Approval: **T0_AUTO** · Gate: **READY** · 43 words

> Hi Divya, one last note so I don't crowd your inbox. Aarav's 45-second space story is exactly where Ms. Rhea's batch starts from. Whenever you and his dad are ready, just reply here. If the timing isn't right, reply 'later' and I'll pause.

**Stop triggers:** Payment webhook = Paid; Parent replies (hand to Rohan); 'later'/'stop' keyword; Duplicate LEAD-811 must not message  
**Internal alerts:** Merge LEAD-811 (brochure re-download 2026-11-03 08:10) into LEAD-801. Treat as buying signal; Pooja must not contact.

## LEAD-802: SALES_SEQUENCE · Cold 3 · objection: PRICE_VALUE · lang: English

**Touch 1** · 2026-11-02 19:30 GST · _After team-lead review of the call_ · from Sneha  
Approval: **T2_TEAM_LEAD** · Gate: **READY** · 101 words

> Hi Amina, Sneha here. You asked a fair question I didn't answer well: what exactly Mr. Vikram did with Zoya today.
>
> He saw what you see: she's quick with straight sums, but on 4-line word problems she guesses + or × without breaking the sentence down. So he taught her the Bar-Model method: draw the story as bars first, then pick the operation. She then solved two Grade-6 British-curriculum fraction word puzzles on her own and said "Oh, that was so easy!"
>
> That's the difference from worksheets. The curriculum outline you asked for is attached. Take all the time you need.

**Touch 2** · 2026-11-04 17:30 GST · _No reply AND unpaid_ · from Sneha  
Approval: **T2_TEAM_LEAD** · Gate: **READY** · 45 words

> Hi Amina, would it help to see it for yourself? Mr. Vikram can do a 15-minute screen-share with you and Zoya on one word problem from her own school paper, using bar models. Her tutor is welcome to watch too. Shall I find a slot?

**Touch 3** · 2026-11-07 17:30 GST · _No reply AND unpaid_ · from Sneha  
Approval: **T1_COUNSELLOR** · Gate: **READY** · 49 words

> Hi Amina, last note from me. Brainiac is AED 1,200 for 48 live classes (2 a week), payable 50% now and 50% at Day 30, with a 100% refund in the first 14 days, so you can judge it on Zoya's own word problems. Reply 'later' and I'll pause.

**Stop triggers:** Payment webhook = Paid; Parent replies; 'later'/'stop' keyword  
**Internal alerts:** Do NOT resend the AED 100 / 30-minute link; void it. · Order 99402 standard_amount = 12000 AED (catalog AED 1,200), so fix the invoice record. · Set next_followup_at (currently NULL).

## LEAD-803: COMPLIANCE_HOLD · Cold 1 · objection: TRUST_CREDIBILITY · lang: English

**Touch 1** · 2026-11-04 11:00 IST · _ONLY if Sales Head approves after review; one-time; no sales ask_ · from Sales Team Lead (manager voice)  
Approval: **T3_MANAGER** · Gate: **READY** (lead on Compliance_Hold) · 103 words

> Mr. Desai, this is [Team Lead name], Sales Team Lead at Bambinos.live. I'm sorry about yesterday's call. It's not how we work, and it is being reviewed.
>
> To set the record straight: no one can promise ranks or a reading level in 30 days. Phonics blending takes steady practice. Our refund policy is 100% within the first 14 days (up to 4 classes), pro-rata after that. Our batches are small groups, not 1-on-1. Vihaan's ID is not blocked in any way, and the Rs. 5,500 link has been cancelled.
>
> We won't call you. If you'd ever like to continue with Ms. Simran, just reply here.

**Stop triggers:** DNC on calls: permanent; Any automated sales message: blocked  
**Internal alerts:** PAGE Sales Head: 6 CRITICAL flags on call 7003 (Amitabh R***). · Void Razorpay link 99403 (INR 5,500, 42% discount). · Correct CRM: rep logged 'Interested / will pay today' (falsified). · Pull Amitabh's other open leads (LEAD-808) for reassignment pending review.

## LEAD-804: ONBOARDING · Converted 10 · objection: SCHEDULE_CONFLICT · lang: English

**Touch 1** · 2026-11-03 11:45 PST · _Payment webhook = Paid (order 99404)_ · from Bambinos Onboarding  
Approval: **T0_AUTO** · Gate: **READY** · 41 words

> Hi Neha, payment received, thank you! 🎉 Meera is confirmed in Acharya Aditi's Little Yogi batch, Saturdays & Sundays 9:30-10:20 AM PST. Her first class is on [first class date]. The Zoom link and digital storybooks arrive 24 hours before. Your invoice: BMB-NEW-2026-99404.

**Touch 2** · [day before first class] 18:00 PST · _Day before first class_ · from Bambinos Onboarding  
Approval: **T0_AUTO** · Gate: **READY** · 40 words

> Hi Neha, Meera's first Little Yogi class with Acharya Aditi is tomorrow at 9:30 AM PST. Here's the Zoom link: [link]. A notebook for her reflections is all she needs, just like the one she wrote the Samatvam verse in!

**Touch 3** · [after week 2] 10:30 PST Sunday · _After 4 classes attended_ · from Rohan  
Approval: **T0_AUTO** · Gate: **READY** · 31 words

> Hi Neha, two weeks in! How is Meera finding the weekend sessions? If friends in your Parent Club are curious, I'm happy to set their kids up with a demo too.

**Stop triggers:** Sales cadence permanently blocked (Paid)  
**Internal alerts:** Set CRM stage Payment_Link_Sent → Enrolled_Paid. · Ops: confirm enrollment is mapped to Sat-Sun 9:30 AM PST batch, NOT the portal default Tue/Thu 5 PM (clashes with gymnastics).

## LEAD-805: SALES_SEQUENCE · Hot 9 · objection: COMPETITOR_COMPARISON · lang: Hinglish

**Touch 1** · 2026-11-03 20:50 IST · _Event: Razorpay Payment_Failed (Bank_OTP_Timeout_On_UPI_Mandate)_ · from Pooja  
Approval: **T0_AUTO** · Gate: **READY** · 64 words

> Rajesh ji, Pooja here 🙏 Lagta hai bank ke OTP timeout ki wajah se UPI payment complete nahi hua. Yeh fresh link hai Installment 1 (Rs. 5,400) ke liye: [payment link]. Is baar autopay mandate ki jagah normal UPI, card ya netbanking choose kar sakte hain, toh OTP wala step nahi aayega. Agar account se amount deduct dikhe toh mujhe bata dijiye, turant check karenge.

**Touch 2** · 2026-11-04 12:30 IST · _Still unpaid_ · from Pooja  
Approval: **T1_COUNSELLOR** · Gate: **READY** · 49 words

> Rajesh ji, payment mein koi dikkat ho toh 2 minute call kar loon? Saath mein PEEL roadmap bhej rahi hoon jo aapne maanga tha. Kabir ne demo mein PEEL se 60 seconds bina ek bhi 'umm' ke bola tha, wahi structure Ms. Rhea weekend batch mein aage le jayengi.

**Touch 3** · 2026-11-06 18:00 IST · _Still unpaid_ · from Pooja  
Approval: **T1_COUNSELLOR** · Gate: **READY** · 49 words

> Rajesh ji, Kabir ki Sat-Sun 11 AM seat Ms. Rhea ke batch mein abhi bhi available hai. Aaj sirf Rs. 5,400, baaki Day 30 par. Exams ke time ka plan bhi call par samjha dungi. Abhi sahi time na ho toh 'later' reply kar dijiye, main pause kar dungi.

**Stop triggers:** Payment webhook = Paid; Parent replies; 'later'/'stop'  
**Internal alerts:** Ops: issue installment 2 (INR 5,400) as a separate Day-30 link since the mandate failed. · Verify the 'Exam Pause / Reschedule' feature exists before it's repeated in writing (FEATURE_CLAIM_UNVERIFIED).

## LEAD-806: SALES_SEQUENCE · Warm 4 · objection: CHILD_NOT_INTERESTED · lang: English

**Touch 1** · 2026-11-03 18:30 IST · _After academic team confirms bridge/micro-batch availability_ · from Academic Counsellor with Coach Arvind  
Approval: **T2_TEAM_LEAD** · Gate: **READY** · 82 words

> Hi Swathi, I'm [Academic Counsellor name], writing with Coach Arvind. First, sorry. Ananya should never have been in a room with 8-9 year olds, and you were right to push back.
>
> Coach Arvind remembers her giggling when her Knight captured the dragon's treasure. That's the Ananya we want to build on. Two calm options:
> 1️⃣ A free 1-on-1 bridge session with Coach Arvind, at her pace
> 2️⃣ Our Little Starters micro-batch: max 3 kids, all aged 5-6
>
> Which would she be more comfortable with?

**Touch 2** · 2026-11-05 17:00 IST · _No reply_ · from Academic Counsellor  
Approval: **T1_COUNSELLOR** · Gate: **READY** · 30 words

> Hi Swathi, Coach Arvind has a bridge slot on [slot 1] or [slot 2]: 30 minutes, just Ananya and him, no other kids. Reply with whichever suits and we'll lock it in.

**Touch 3** · 2026-11-08 11:00 IST · _No reply_ · from Academic Counsellor  
Approval: **T0_AUTO** · Gate: **READY** · 29 words

> Last note from us, Swathi. Whenever Ananya feels ready, the bridge session is open, with no commitment. If you'd rather we didn't message, reply 'stop' and we'll respect that.

**Stop triggers:** Parent replies (academic team takes over); 'stop' keyword; Payment = Paid  
**Internal alerts:** Reassign LEAD-806 from Karan K*** to an academic counsellor. · Ops: fix demo batching rule; no 5-6 year olds in mixed 8-9 groups. · Karan: team-lead 1:1 within 48h (rubric gaming).

## LEAD-807: SALES_SEQUENCE · Warm (provisional) 6 · objection: UNKNOWN · lang: English

**Touch 1** · 2026-11-04 09:30 IST · _Paired with P1 call task at 10:00 IST (SLA breached; snapshot past quiet hours)_ · from Sneha  
Approval: **T1_COUNSELLOR** · Gate: **READY** · 48 words

> Hi {{parent_first_name}}, Sneha from Bambinos. {{child_first_name}} scored 5/5 on Ms. Rhea's live Olympiad inference challenge, and asked when the regular batch starts! 📚 Could I call you this morning? I'd love to share where he's strong and the one area Ms. Rhea wants to build: structuring persuasive essays.

**Touch 2** · 2026-11-04 17:30 IST · _Call not connected_ · from Sneha  
Approval: **T0_AUTO** · Gate: **READY** · 21 words

> Hi {{parent_first_name}}, missed you earlier. Would [slot 1] or [slot 2] work for a 10-minute chat about {{child_first_name}}'s Olympiad & Creative Writing plan?

**Touch 3** · 2026-11-06 18:00 IST · _No reply_ · from Sneha  
Approval: **T0_AUTO** · Gate: **READY** · 32 words

> Hi {{parent_first_name}}, last note from me. Ms. Rhea's feedback on {{child_first_name}}'s inference skills is ready whenever you'd like it. Just reply here. If now isn't the time, reply 'later' and I'll pause.

**Stop triggers:** Call connected (regenerate from call audit); Parent replies; 'later'/'stop'  
**Internal alerts:** P1 SLA BREACH: high-intent demo uncalled for 29.5h (Sneha V***).

## LEAD-808: SALES_SEQUENCE · Cold (provisional) 3 · objection: UNKNOWN · lang: English

**Touch 1** · 2026-11-04 10:00 AST · _After reassignment from Amitabh (compliance review)_ · from [Reassigned counsellor]  
Approval: **T0_AUTO** · Gate: **READY** · 42 words

> Hi {{parent_first_name}}, {{child_first_name}} loved the 'Mystery Box' speaking game in Ms. Simran's demo and asked for two extra rounds! 🎁 I'd love 5 minutes to hear what you'd like {{child_first_name}} to work on. When is a good time this week (Doha time)?

**Touch 2** · 2026-11-05 17:00 AST · _No reply_ · from [Reassigned counsellor]  
Approval: **T0_AUTO** · Gate: **READY** · 19 words

> Hi {{parent_first_name}}, would [slot 1] or [slot 2] (Doha time) suit for a quick chat about {{child_first_name}}'s storytelling and vocabulary plan?

**Touch 3** · 2026-11-08 11:00 AST · _No reply_ · from [Reassigned counsellor]  
Approval: **T0_AUTO** · Gate: **READY** · 23 words

> Hi {{parent_first_name}}, last note from me. Whenever you'd like to chat about {{child_first_name}}'s speaking journey, just reply here. Reply 'later' and I'll pause.

**Stop triggers:** Parent replies; 'later'/'stop'  
**Internal alerts:** Class 108 (Young Communicators GCC Track) missing from pricing catalog; no price may be messaged until added. · Lazy disposition 'Busy / ok' with no follow-up date.

## LEAD-809: SALES_SEQUENCE · Hot (provisional) 8 · objection: UNKNOWN · lang: English

**Touch 1** · 2026-11-03 16:00 GMT · _After ops confirms GBP 210 price (GBP not in catalog)_ · from Rohan  
Approval: **T0_AUTO** · Gate: **HELD_PENDING_OPS** (price not in catalog: ops must confirm) · 45 words

> Hi {{parent_first_name}}, Rohan from Bambinos. Your bank declined the card security check (3-D Secure) on the Brainiac Maths payment, so it didn't go through. Here's a fresh link: [payment link]. Tip: approve the prompt in your banking app when it pops up, or try another card.

**Touch 2** · 2026-11-04 12:30 GMT · _Still unpaid_ · from Rohan  
Approval: **T0_AUTO** · Gate: **READY** · 36 words

> Hi {{parent_first_name}}, still having trouble with the payment? Happy to stay on a 2-minute call while you try. {{child_first_name}} cracked the 4-disc Tower of Hanoi on his first go, so we'd love to get him started!

**Touch 3** · 2026-11-06 18:00 GMT · _Still unpaid_ · from Rohan  
Approval: **T0_AUTO** · Gate: **READY** · 28 words

> Hi {{parent_first_name}}, last note from me. If a card payment is tricky, we can also share a bank-transfer option. Just reply here, or reply 'later' and I'll pause.

**Stop triggers:** Payment webhook = Paid; Parent replies; 'later'/'stop'  
**Internal alerts:** Catalog has no GBP price for class 205 (USD 250 listed); confirm GBP 210 before re-issuing link. · Bank-transfer option must be confirmed by finance before T3 is sent.

## LEAD-810: SALES_SEQUENCE · Cold (provisional) 3 · objection: UNKNOWN · lang: English

**Touch 1** · 2026-11-04 10:00 IST · _Auto (no flags on lead)_ · from Karan  
Approval: **T0_AUTO** · Gate: **READY** · 44 words

> Hi {{parent_first_name}}, {{child_first_name}} mastered Ms. Simran's 'thumbs-up b & d bed' trick in just 5 minutes and read 4 sentences aloud! 📖 Could we do a quick 5-minute call about the long-vowel sounds Ms. Simran wants to work on next? What time suits you?

**Touch 2** · 2026-11-05 17:30 IST · _No reply_ · from Karan  
Approval: **T0_AUTO** · Gate: **READY** · 15 words

> Hi {{parent_first_name}}, would [slot 1] or [slot 2] work for a quick chat about {{child_first_name}}'s reading plan?

**Touch 3** · 2026-11-08 11:00 IST · _No reply_ · from Karan  
Approval: **T0_AUTO** · Gate: **READY** · 21 words

> Hi {{parent_first_name}}, last note from me. Whenever you'd like to talk about {{child_first_name}}'s phonics, just reply. Reply 'later' and I'll pause.

**Stop triggers:** Parent replies; 'later'/'stop'  
**Internal alerts:** next_followup_at 2026-11-01 is before last call (2026-11-02); reset. · Disposition note 'cb' carries no information; Karan under coaching review, team lead to spot-check this call.

## LEAD-811: SUPPRESSED · n/a  · objection: n/a · lang: English
**No messages: suppressed.**

**Stop triggers:** Duplicate of LEAD-801  
**Internal alerts:** Merge into LEAD-801 (same student_id 78001, same mobile). Keep owner Rohan; remove from Pooja's queue.

## LEAD-812: SALES_SEQUENCE · Warm (provisional) 5 · objection: UNKNOWN · lang: English

**Touch 1** · 2026-11-03 10:30 CST · _Paired with P1 call task (SLA breached)_ · from Sneha  
Approval: **T1_COUNSELLOR** · Gate: **READY** · 46 words

> Hi {{parent_first_name}}, Sneha from Bambinos. Acharya Aditi loved {{child_first_name}}'s question about how Karma Yoga applies to school grades and sports competitions. I hear you were clapping too! 😊 Could I call you today to share how the Teen Leadership track helps with pre-meet and test nerves?

**Touch 2** · 2026-11-03 17:30 CST · _Call not connected_ · from Sneha  
Approval: **T0_AUTO** · Gate: **READY** · 18 words

> Hi {{parent_first_name}}, would [slot 1] or [slot 2] (Central time) work for a 10-minute chat about {{child_first_name}}'s weekend batch options?

**Touch 3** · 2026-11-05 18:00 CST · _No reply_ · from Sneha  
Approval: **T0_AUTO** · Gate: **READY** · 25 words

> Hi {{parent_first_name}}, last note from me. Acharya Aditi's notes on {{child_first_name}} are ready whenever you'd like them. Reply here, or reply 'later' and I'll pause.

**Stop triggers:** Call connected; Parent replies; 'later'/'stop'  
**Internal alerts:** P1 SLA BREACH: high-intent demo uncalled (Sneha V***). · Student name contains Cyrillic homoglyphs ('Ме'). Normalise for dedup/WhatsApp matching.

