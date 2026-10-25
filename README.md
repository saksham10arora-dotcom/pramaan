# Pramaan

SIH 2026, **SIH26261**: AI-Powered Application Validation, Document Authentication and Regulatory Compliance Verification (AICTE).

An institution applying for AICTE approval uploads a bundle: application form, land deed, building completion certificate, fire NOC, faculty list. Today a person reads each one by hand. Pramaan reads the bundle and returns one verdict, **COMPLIANT**, **REJECT** or **SEND TO A HUMAN REVIEWER**, with every finding quoting the exact line it came from.

## What it checks (working now)
- **Completeness**: every required document is present; unknown documents go to a human.
- **Cross-document consistency**: the institution named on each certificate matches the application (fuzzy match), and the land is owned by the applicant trust.
- **Norms**: fire NOC valid on the application date, student-to-faculty ratio, built-up area for the intake, minimum land area. Norms live in `pramaan/norms.yaml` (demo values, to be replaced with the Approval Process Handbook figures).
- **Tampering**: the PDF was saved again after issue, a white box covers text, a value is set in a font used nowhere else. The covered text is still read, so a forged date is checked against the real one underneath.

The system never auto-approves something it is unsure of: anything it cannot read or that looks edited goes to a human, with the reason.

## Run
```
python3.11 -m venv .venv && .venv/bin/pip install pymupdf streamlit rapidfuzz pillow pytest reportlab pyyaml
.venv/bin/python samples/make_samples.py      # writes a clean and a forged demo bundle
.venv/bin/streamlit run app.py
.venv/bin/python -m pytest -q
```

## Next
1. Scanned documents: OCR, plus an LLM that extracts fields from free-form layouts, every value tied to a page and box.
2. Issuer verification: DigiLocker / issuing-authority lookup for NOCs and certificates, QR and digital-signature checks.
3. Image forensics for scans (error level analysis, copy-move).
4. Load the real APH norms per programme and intake; reviewer dashboard across all applications.
