# Changes

Every change from the prototype on, newest last.

## 2026-10-25
- Prototype: bundle validation (completeness, cross-document names, land owner, fire NOC validity, faculty ratio, built-up area, land area), PDF tamper checks (incremental save, white box over text, odd font), Streamlit reviewer screen, 6 tests.
- **Scans and photos.** Pages with no text layer and image uploads (jpg/png/webp/tif) go through RapidOCR, offline. OCR spacing and l/I confusions are tolerated in document classification, field labels and name matching. Test: a fully scanned bundle with a phone-photo NOC gives the same verdict as the typed one.
- **AI reading, propose then verify.** When label matching cannot read a document (free-form letters, unusual layouts), Gemini (`gemini-2.5-flash`, falls back to `gemini-flash-lite-latest`) proposes each field with the line it came from. A value is kept only if that line is in the document (numbers must match exactly) and contains the value; anything else becomes a NEEDS REVIEW finding. A model failure (network, quota, bad JSON) also goes to a human, never passes. Label matches always beat model readings. `PRAMAAN_OFFLINE=1` turns the model off. Dates like "31st March, 2027" now parse.
