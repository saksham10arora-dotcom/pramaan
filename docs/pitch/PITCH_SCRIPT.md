# Pramaan: pitch and demo script

**Say** is what to speak. *Italics* are what to do on screen.

Total: about 6 minutes, with the demo inside it. Every number here is true and checked. Do not add numbers of your own.

---

## Before you start (15 minutes early)

*Plug in the charger and turn on Do Not Disturb. Open two tabs in Chrome:*

1. Slides: `docs/slides/Pramaan_SIH_deck.pptx`
2. Live demo: https://pramaan-teal.vercel.app

*Click Clean and Ghost faculty once to wake the server.*

**Backup:** if the internet fails, play `docs/demo/pramaan_demo.mp4`, or run the local version:

```bash
.venv/bin/streamlit run app.py
```

---

## Part 1: Problem (45 sec) · Slide 1

> Good morning. Our problem statement is SIH26261 from AICTE: AI-powered application validation, document authentication and regulatory compliance verification.
>
> To get AICTE approval, every institution submits a full set of documents: land deed, building certificate, fire safety certificate, faculty list. Today, officers read all of it by hand.
>
> That creates three problems. It is slow. An edited certificate looks genuine to the eye. And no officer can compare one college's faculty list against every other college.

## Part 2: Our idea (40 sec) · Slide 2

> We built Pramaan, which means proof.
>
> Give it a full application and it returns one of three verdicts: compliant, reject, or human review. Every finding shows the exact line of the document it came from.
>
> One rule is fixed: where it is unsure, it does not approve on its own. It sends the case to an officer, with the reason.

## Part 3: Live demo (2 min 15 sec)

*Switch to the demo tab.*

**Clean** · *Click Clean. Open the student to faculty ratio and built-up area lines.*

> This is a valid application. The verdict is compliant. Here we have 480 students and 25 faculty, which is 19.2, and the handbook limit is 20. The building area comes from the room-wise tables in Annexure 3: 5,562 square metres are needed and 6,000 are built.

**Forged PDF** · *Click Forged PDF and scroll down to the white box image.*

> Now a forgery. This fire certificate expired in March 2026. Someone covered the date with a white box and typed 2027. By eye it looks fine. But Pramaan reads the real date hidden underneath, and outlines in red where it was changed. It also caught that the land belongs to a private person, not the trust.

**Forged, then scanned** · *Click the button.*

> What does a smart forger do? They print and scan the page so no edit marks survive. The page now says 2027. But the certificate's QR code still says 2026. Pramaan compares the two and rejects it.

**Ghost faculty** · *Click the button.*

> This is the most important case. This is a different college, and every document looks fine on its own. But Pramaan remembers earlier applications. These 25 faculty are already on another institution's list, and the fire certificate number is the same. You can never catch this by looking at one file.

**Reviewer queue** · *Open the tab.*

> The officer gets one queue with the riskiest first, and a PDF report for each application. There is also a REST API, so the AICTE portal can connect directly.

## Part 4: Technology (30 sec) · Slide 3

> Our core idea is: AI proposes, code verifies. Gemini reads free-form letters, but a value is kept only if its source line is really in the document and the numbers match exactly. If the AI invents something, it goes to an officer, not into the verdict.
>
> For scanned documents, OCR runs offline on our server. QR codes, PDF edits and digital signatures are each checked separately.

## Part 5: Feasibility and limits (30 sec) · Slide 4

> This is not just an idea, it is running. There is a live link, 29 automated tests pass, and the norms come from the AICTE Approval Process Handbook 2024-27.
>
> We are also clear about our limits. So far we have tested only on synthetic documents, and real scans will be harder. For signatures, we check that the file was not changed, not that the right office signed it. And a very careful edit on a photo, with no QR code or signature, is not caught yet.

## Part 6: Impact and close (30 sec) · Slide 5

> Officers save time on clean applications and spend it on risky ones. Honest colleges learn what to fix. Students get real faculty and safe buildings.
>
> Pramaan: every verdict, with proof. Thank you.

---

## Likely questions

**What is your accuracy?**
> We have not measured it on real documents yet, so we will not quote a number. Every case in our synthetic demo is caught, and testing on real scans is our next step.

**What if the AI reads something wrong?**
> A value is kept only if its line is in the document and the numbers match exactly. Otherwise it goes to an officer.

**What if there is no QR code?**
> The other checks still run: PDF edits, fonts, signatures and cross-document checks. A careful edit on a scan with no QR code is not caught yet. That is a known limit.

**Why is there no minimum land check?**
> The 2024-27 handbook has no fixed acreage. Land is decided by local FSI/FAR, so we check built-up area instead.

**What about data security?**
> In the local version, OCR and all rules run on the server. The AI reader is optional, and in offline mode nothing leaves the machine.

**What about other programmes?**
> Faculty ratios are loaded for all UG programmes. Room-wise area is done for Engineering UG so far; the rest go to human review.

**What if ghost faculty is flagged wrongly?**
> It is based on matching faculty IDs, and the final decision is the officer's, with the evidence in front of them.

**How strong is the signature check?**
> We catch a file changed after signing. Confirming the signer is the right office needs the CCA root list, which is not loaded yet.
