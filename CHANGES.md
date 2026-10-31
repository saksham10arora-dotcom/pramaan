# Changes

Every change from the prototype on, newest last.

## 2026-10-25
- Prototype: bundle validation (completeness, cross-document names, land owner, fire NOC validity, faculty ratio, built-up area, land area), PDF tamper checks (incremental save, white box over text, odd font), Streamlit reviewer screen, 6 tests.
- **Scans and photos.** Pages with no text layer and image uploads (jpg/png/webp/tif) go through RapidOCR, offline. OCR spacing and l/I confusions are tolerated in document classification, field labels and name matching. Test: a fully scanned bundle with a phone-photo NOC gives the same verdict as the typed one.
- **AI reading, propose then verify.** When label matching cannot read a document (free-form letters, unusual layouts), Gemini (`gemini-2.5-flash`, falls back to `gemini-flash-lite-latest`) proposes each field with the line it came from. A value is kept only if that line is in the document (numbers must match exactly) and contains the value; anything else becomes a NEEDS REVIEW finding. A model failure (network, quota, bad JSON) also goes to a human, never passes. Label matches always beat model readings. `PRAMAAN_OFFLINE=1` turns the model off. Dates like "31st March, 2027" now parse.
- **QR cross-check.** QR codes on any page or photo are decoded (OpenCV) and their fields compared with the printed text; a mismatch FAILS ("the page was altered"). Catches a forgery that was printed and re-scanned, where no PDF edit marks survive. New demo bundle `samples/out/forged_scan`.
- **Editing-software trace.** PDF producer/creator and image EXIF Software naming a known editor (iLovePDF, Photoshop, Canva, ...) goes to review.
- **Tried and dropped: error level analysis on photos.** On rendered documents it scored a pasted date the same as an innocent re-save, so it is not shipped. Listed as an open drawback.
- Structured README for teammates (problem statement, done, remaining, drawbacks, run steps); requirements.txt; app accepts photos and has the forged_scan demo.

## 2026-10-31
- **Real norms.** Replaced the placeholders with the AICTE Approval Process Handbook 2024-27: faculty ratio by programme and built-up area room by room. Removed the 2.5-acre land rule: the handbook has no fixed minimum and sets land by FSI/FAR. Sample applications updated.
- **Registry.** SQLite record across applications: reused files, certificate numbers, ghost faculty. Only earlier applications count against an application.
- **Faculty rows** read from the list; repeated IDs and a total that disagrees with the names fail.
- **Digital signature check** with pyHanko (integrity only). Structural stability rule. Land use certificate added. Second document of one type goes to review.
- **Unreadable key fields go to a human.** Previously the rule skipped silently and a bad scan could reach COMPLIANT.
- **REST API, PDF report, reviewer queue.**
- **Deck and demo video** with script, in `docs/`.
- **Dropped:** issuer verification, CCA root check, Hindi OCR, error level analysis. Reasons in the README.
