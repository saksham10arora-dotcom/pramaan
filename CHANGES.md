# Changes

Every change from the prototype on, newest last.

## 2026-10-25
- Prototype: bundle validation (completeness, cross-document names, land owner, fire NOC validity, faculty ratio, built-up area, land area), PDF tamper checks (incremental save, white box over text, odd font), Streamlit reviewer screen, 6 tests.
- **Scans and photos.** Pages with no text layer and image uploads (jpg/png/webp/tif) go through RapidOCR, offline. OCR spacing and l/I confusions are tolerated in document classification, field labels and name matching. Test: a fully scanned bundle with a phone-photo NOC gives the same verdict as the typed one.
