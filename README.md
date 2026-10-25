# Pramaan

**Smart India Hackathon 2026 · Problem Statement SIH26261 · AICTE**

Pramaan reads every document an institution submits for AICTE approval and returns one verdict, **COMPLIANT**, **REJECT** or **SEND TO A HUMAN REVIEWER**. Every finding quotes the exact line it came from, and it flags documents that were edited after they were issued.

---

## 1. Problem statement

| | |
|---|---|
| **ID** | SIH26261 |
| **Title** | AI-Powered Application Validation, Document Authentication and Regulatory Compliance Verification |
| **Organisation** | All India Council for Technical Education (AICTE) |
| **Category** | Software |
| **Theme** | Smart Automation |
| **Idea submission deadline** | 28 October 2026 |

> **Teammates: action needed.** The SIH portal was under maintenance when this was written, so the full official description is not copied here yet. Paste it into this section from sih.gov.in, then check section 6 against it in case the statement asks for something we have not covered.

**Our reading of the problem.** Every year thousands of institutions apply to AICTE for approval or extension of approval. Each application is a bundle of documents: the application form, land ownership deed, building completion certificate, fire safety NOC, faculty list and more. Today officials check these by hand. That is slow, inconsistent, and easy to fool with an edited certificate, such as an expired fire NOC with a new date typed over it. The problem asks for an AI system that:
1. **validates the application:** all required documents are present and their details agree with each other,
2. **authenticates the documents:** detects forged or altered documents,
3. **verifies regulatory compliance:** checks the application against AICTE norms (land, built-up area, faculty ratio, valid safety certificates and so on).

---

## 2. How it works

```
documents (PDF, scanned PDF, phone photo)
        │
        ▼
 1. Read      typed PDF → text layer;  scan/photo → OCR (RapidOCR, offline)
        │
        ▼
 2. Classify  which document is this? (fire NOC, land deed, ...)
        │
        ▼
 3. Extract   label matching first;  free-form layouts → Gemini proposes a value
              plus the line it came from → code checks that line is really in the
              document (numbers must match exactly) → otherwise NEEDS REVIEW
        │
        ▼
 4. Check     completeness · cross-document consistency · AICTE norms
              · forgery signs · QR code vs printed text
        │
        ▼
 5. Verdict   COMPLIANT / REJECT / SEND TO A HUMAN REVIEWER, each finding with evidence
```

**Design rule:** the system never approves anything it is unsure of. Unreadable text, unverified AI readings, model failures and edit marks all go to a human, with the reason.

---

## 3. What is done ✅

| Area | What works | Where |
|---|---|---|
| **Reading** | Typed PDFs, scanned PDFs, photos (jpg/png/webp/tif). OCR runs offline, so documents never leave the machine. Tolerates OCR noise (merged words, l/I mix-ups). | `pramaan/docs.py` |
| **Classifying** | Application form, land deed, building completion certificate, fire NOC, faculty list. Unknown documents go to a human. | `pramaan/extract.py` |
| **AI extraction** | Gemini reads free-form letters (for example "shall remain in force till 31st March, 2027"). Each value is verified against the document text; a made-up value is rejected. Works offline with label matching only (`PRAMAAN_OFFLINE=1`). | `pramaan/llm.py` |
| **Completeness** | Every required document is present. | `pramaan/validate.py` |
| **Cross-document checks** | Institution name matches on every certificate (fuzzy match). Land is owned by the applicant trust. | `pramaan/validate.py` |
| **Norms** | Fire NOC valid on the application date, student-to-faculty ratio, built-up area for the intake, minimum land area. Values in a config file. | `pramaan/norms.yaml` |
| **Forgery: PDF** | Saved again after issue (incremental save), white box over text (the covered text is still read), a value in a font used nowhere else, last written by an editing tool (iLovePDF, Photoshop, Canva, ...). | `pramaan/forensics.py` |
| **Forgery: QR code** | Decodes QR codes on the page and compares them with the printed text. Catches a forgery that was printed and scanned again, where no edit marks survive. | `pramaan/forensics.py`, `validate.py` |
| **Reviewer screen** | Upload documents or load a demo, see the verdict, each finding with the quoted evidence, and the covered region outlined. | `app.py` |
| **Demo data** | Three fictional applications: `clean`, `forged` (edited PDF + land in the wrong name), `forged_scan` (edited, printed, scanned). | `samples/make_samples.py` |
| **Tests** | 13 tests: clean application, forgeries, OCR scan, AI reading, made-up AI value, model failure. | `tests/` |

Full history of every change: [`CHANGES.md`](CHANGES.md).

---

## 4. What remains ⏳

Ordered by priority for the 28 October submission.

| # | Task | Why it matters | Owner |
|---|---|---|---|
| 1 | **6-slide SIH idea deck** (title, idea, technical approach, feasibility, impact, research/references) | This is the actual submission | _unassigned_ |
| 2 | **Paste the official problem statement** into section 1 and re-check this list against it | We built from the title alone | _unassigned_ |
| 3 | **Real AICTE norms** from the Approval Process Handbook (by programme, intake, urban/rural) into `norms.yaml`, with page references | Current values are demo placeholders | _unassigned_ |
| 4 | **Registry across applications** (SQLite): the same document file or certificate number used by two institutions; the same faculty member (PAN / AICTE faculty ID) listed by two institutions | Catches ghost faculty, a known AICTE fraud pattern | _unassigned_ |
| 5 | **Faculty list as a table:** read each row (name, ID, qualification), not just the total | Needed for #4 and qualification checks | _unassigned_ |
| 6 | **Digital signature validation** (e.g. pyHanko): signed by whom, and was the file changed after signing | The strongest authenticity proof when issuers sign | _unassigned_ |
| 7 | **Issuer verification:** check certificate numbers against DigiLocker / issuing-authority portals where an API exists | Moves from "looks real" to "confirmed by issuer" | _unassigned_ |
| 8 | **REST API** (FastAPI) so the AICTE portal can call Pramaan, plus a downloadable PDF/JSON report | Integration story for judges | _unassigned_ |
| 9 | **Reviewer queue** across many applications, sorted by risk | Shows scale | _unassigned_ |
| 10 | **More document types:** affiliation letter, NAAC/NBA, AISHE, building plan approval, lab equipment lists | Coverage | _unassigned_ |
| 11 | **Hindi and regional-language documents** (OCR models + prompts) | Many certificates are bilingual | _unassigned_ |

### Known drawbacks (be honest about these with judges)
- **All test documents are synthetic.** We have not yet run Pramaan on real AICTE submissions. Real scans are messier.
- **Photo forensics is limited.** Error level analysis (spotting a pasted region by its compression) was tried and **dropped**: on rendered documents it scored a pasted date the same as an innocent re-save. A carefully pasted edit on a photo with no QR code is not caught yet.
- **Norm values are placeholders** until #3 is done.
- **The AI reader needs internet** (Gemini). Offline mode falls back to label matching, which handles standard forms but not free-form letters. A self-hosted model would fix this for government deployment.
- **The QR check only works when the issuer prints a QR code** that holds the certificate's fields.
- **One document per type per application.** A second fire NOC would overwrite the first.

---

## 5. Run it

Needs Python 3.11.

```bash
git clone https://github.com/saksham10arora-dotcom/pramaan && cd pramaan
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python samples/make_samples.py     # writes demo applications to samples/out/
.venv/bin/streamlit run app.py               # opens the reviewer screen
.venv/bin/python -m pytest -q                # 13 tests
```

**AI reader (optional):** put `GEMINI_API_KEY=...` in your environment or in `~/.config/keys.env`. Without a key, Pramaan runs offline with label matching only.

**Demo for judges:** in the app, pick `forged`, then `forged_scan`. The first is caught by edit marks and by reading the real date under the white box. The second has no edit marks at all and is caught only because its QR code disagrees with the page.

---

## 6. Project layout

```
pramaan/
  docs.py         load PDF/image → text, spans, page images; OCR for scans
  extract.py      classify document type; label-based field extraction; date/number parsing
  llm.py          Gemini reader with quote verification (propose, then verify)
  forensics.py    edit marks, editing-software trace, QR decoding
  validate.py     runs every check, returns findings + verdict
  norms.yaml      compliance thresholds (placeholders, see task #3)
app.py            Streamlit reviewer screen
samples/          fictional demo applications (clean, forged, forged_scan)
tests/            pytest suite
CHANGES.md        log of every change
```

## 7. Working on it

- Branch from `main`, open a pull request; don't push to `main` directly.
- Add a line to `CHANGES.md` for every change.
- A new check needs a test that fails without it.
- All sample data must stay fictional. Never commit a real institution's documents.
