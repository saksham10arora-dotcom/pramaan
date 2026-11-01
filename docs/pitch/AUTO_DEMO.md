# Auto-demo: 5 speakers, 5 minutes

The page plays by itself. Each speaker reads their own lines.

**The scene number shows at the bottom right of the screen (like 7/22), and it matches the number here.** When the thin line above the caption fills up, move to the next line. If someone gets stuck, press **Space** to pause, and Space again to continue.

| Speaker | Name | Scenes | Time |
|---|---|---|---|
| 1 | _____ | 1 to 3 | 0.9 min |
| 2 | _____ | 4 to 7 | 1.0 min |
| 3 | _____ | 8 to 12 | 1.2 min |
| 4 | _____ | 13 to 17 | 1.2 min |
| 5 | _____ | 18 to 22 | 1.0 min |

## How to record

1. Do one practice run first, to check your speed.
2. Open in Chrome: https://pramaan-teal.vercel.app/?tour=1
3. Make Chrome full screen (Ctrl + Cmd + F).
4. Press **Cmd + Shift + 5**, choose Record Entire Screen, select your mic under Options, and press Record.
5. Press **Start demo** on the page. Speaker 1 begins.
6. On the last card, wait 2 seconds, then press Stop in the menu bar.

Sit around one laptop and move close to the mic to speak. If you are in different places, join a Google Meet, have one person share the screen, and record the Meet.

## Speaker 1: Problem and idea

| Scene | Sec | Say |
|---|---|---|
| 1 | 12 | Good morning. Our problem statement is SIH26261 from AICTE: AI-powered application validation, document authentication and regulatory compliance verification. Our solution is Pramaan, which means proof. |
| 2 | 25 | To get AICTE approval, every institution submits a land deed, a building certificate, a fire safety certificate and a faculty list, and officers read all of it by hand. That creates three problems. It is slow. An edited certificate looks genuine to the eye. And no officer can compare one college's faculty list against every other college. |
| 3 | 18 | Pramaan reads the whole application and gives one of three verdicts: compliant, reject, or human review. Every finding shows the exact line of the document it came from. And wherever it is unsure, it does not approve on its own. |

## Speaker 2: Clean application, start of the forgery

| Scene | Sec | Say |
|---|---|---|
| 4 | 14 | Let's see it live. This is a complete application from a fictional college, Shree Ram Institute of Technology. With one click, Pramaan reads every document and gives its verdict: compliant. |
| 5 | 19 | Look at this check. There are 480 students and 25 faculty, which is 19.2 students per faculty member. The limit in Annexure 5 of the AICTE handbook is 20, so it passes. Below it is the exact line that number came from. |
| 6 | 17 | The building area is not a guess either. It is calculated room by room from the tables in Annexure 3: classrooms, labs, library, all of it. The college needs 5,562 square metres, and its certificate shows 6,000. |
| 7 | 11 | Now a forgery. This college's fire certificate expired in March 2026, and the application is dated September 2026. So this should be rejected. |

## Speaker 3: Catching the forgery

| Scene | Sec | Say |
|---|---|---|
| 8 | 17 | Someone placed a white box over the date and typed 2027. Look at the page. By eye it looks perfectly fine, and an officer could pass it. But Pramaan outlines in red exactly where it was changed. |
| 9 | 18 | Pramaan caught the white box, the different font, and the fact that the file was saved again after it was issued. The real date is still in the file under the white box, and that is the date Pramaan reads. |
| 10 | 12 | It also found that the land is in a private person's name, not the trust's. Pramaan matched two separate documents on its own to catch that. |
| 11 | 14 | Now a smarter forger. They print the page and scan it, so no edit marks survive. There is no white box and no odd font. The page simply says 2027. |
| 12 | 10 | But the QR code still says 2026. Pramaan reads the QR code, compares it with the page, and rejects the application. |

## Speaker 4: Ghost faculty, queue, how it works

| Scene | Sec | Say |
|---|---|---|
| 13 | 12 | Now the most important case. This is a different college, Ganga College of Engineering. Every document looks fine on its own. No edits, no expired dates. |
| 14 | 14 | But Pramaan remembers earlier applications. These 25 faculty members are already listed by Shree Ram Institute. The same people are being shown at two colleges. This is called ghost faculty. |
| 15 | 11 | The fire certificate number is also the same one the first college submitted. You can never catch this by looking at one file. |
| 16 | 17 | This is the officer's screen. All applications sit in one queue with the riskiest on top, and each has a PDF report with its evidence. There is also a REST API, so the AICTE portal can connect directly. |
| 17 | 16 | How does it work inside? Each document is read, using offline OCR if it is a scan. Then the norms are checked, the forgery checks run, and the registry compares it with earlier applications. |

## Speaker 5: AI, feasibility, limits, close

| Scene | Sec | Say |
|---|---|---|
| 18 | 17 | Free-form letters are read by Gemini, but we do not simply trust it. A value is kept only if its source line is really in the document and the numbers match exactly. Otherwise it goes to an officer. |
| 19 | 13 | This is not just an idea. The live link is running, 29 automated tests pass, and the norms come directly from the AICTE Approval Process Handbook 2024 to 27. |
| 20 | 18 | We are also clear about our limits. So far we have tested only on synthetic documents, and real scans will be harder. And a very careful edit on a photo, with no QR code or signature, is not caught yet. |
| 21 | 10 | Officers spend their time on risky applications, honest colleges learn exactly what to fix, and students get real faculty and safe buildings. |
| 22 | 4 | Pramaan: every verdict, with proof. Thank you. |
