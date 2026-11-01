# Pramaan

**Smart India Hackathon 2026 · Problem Statement SIH26261 · AICTE**

Pramaan reads every document an institution submits for AICTE approval and returns one verdict, **COMPLIANT**, **REJECT** or **SEND TO A HUMAN REVIEWER**. Every finding quotes the exact line it came from, and it flags documents that were edited after they were issued.

---

**Live demo:** https://pramaan-teal.vercel.app

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

> **Teammates: action needed.** The SIH portal was under maintenance when this was written, so the full official description is not copied here yet. Paste it into this section from sih.gov.in, then check section 3 against it in case the statement asks for something we have not covered.

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
| **Reading** | Typed PDFs, scanned PDFs, photos. OCR runs offline. Tolerates OCR noise. | `pramaan/docs.py` |
| **Document types** | Application form, land deed, land use certificate, building completion, structural stability, fire safety certificate, faculty list. | `pramaan/extract.py` |
| **AI reading** | Gemini reads free-form letters. A value is kept only if its source line is in the document, numbers exact. Offline mode: `PRAMAAN_OFFLINE=1`. | `pramaan/llm.py` |
| **Real AICTE norms** | From the Approval Process Handbook 2024-27: faculty ratio by programme (Annexure 5.2), built-up area room by room for Engineering UG (Annexure 3), valid fire certificate, structural stability after 30 years (clause 6.17). | `norms.yaml`, `area.py` |
| **Cross-document checks** | Institution name on every certificate, land and land use in the trust's name, stated faculty total against the names listed. | `pramaan/validate.py` |
| **Forgery checks** | Saved after issue, white box over text, odd font, editing software, QR code vs printed text, digital signature broken by a later change. | `pramaan/forensics.py` |
| **Registry** | Same file, certificate number or faculty ID at a second institution. Only earlier applications count, so the original is never blamed for a later copy. | `pramaan/registry.py` |
| **Never approves a doubt** | Unreadable key fields, unknown documents, missing norms and AI failures all go to a human. | `pramaan/validate.py` |
| **Reviewer screen** | Upload or demo, verdict, quoted evidence, covered region outlined, PDF report, queue sorted by risk. | `app.py` |
| **REST API** | `POST /applications`, `GET /applications`, `GET /applications/{id}`, `GET /applications/{id}/report.pdf`. | `pramaan/api.py` |
| **Tests** | 29 tests. | `tests/` |

## 4. Submission material 🎬

| File | What |
|---|---|
| [`docs/slides/Pramaan_SIH_deck.pptx`](docs/slides/Pramaan_SIH_deck.pptx) | 6-slide deck in the SIH template, with speaker notes |
| [`docs/slides/Pramaan_SIH_deck.pdf`](docs/slides/Pramaan_SIH_deck.pdf) | PDF of the deck, drawn by our own script; re-export from PowerPoint or Keynote if you edit the pptx |
| [`docs/demo/pramaan_demo.mp4`](docs/demo/pramaan_demo.mp4) | 2 min 35 s narrated demo of the real app |
| [`docs/demo/script.md`](docs/demo/script.md) | Video script, scene by scene |

To rebuild: start the app on port 8517, then run `docs/demo/narrate.py`, `docs/demo/record.py`, `docs/slides/make_deck.py` and `docs/slides/to_pdf.py`.

## 5. What remains ⏳

Only people can do these:

| # | Task | Owner |
|---|---|---|
| 1 | Fill **Team Name** on all slides and **Team ID** on slide 1 | _unassigned_ |
| 2 | Paste the **official problem statement** into section 1 and check it against section 3 | _unassigned_ |
| 3 | Try Pramaan on **real scanned documents** from your own college and fix what breaks | _unassigned_ |

**Dropped because it can't be done in this project:**
- **Live issuer verification (DigiLocker, fire department portals):** needs government API access.
- **Checking who signed against India's CCA root list:** signatures are checked for tampering only, so a pass means "unchanged since signing", not "signed by the right office".
- **Hindi and regional-language documents:** the offline OCR model reads English. The handbook requires notarized English translations of vernacular land documents anyway.
- **Error level analysis on photos:** tried, and it could not tell a pasted date from an innocent re-save.

**Known limits (say these upfront to judges):**
- All test documents are synthetic. Nothing has run on real AICTE submissions.
- Built-up area is calculated for Engineering and Technology UG only, assuming divisions of 60 and no X-category workshops. Other programmes go to a human.
- Administrative and amenities area above an intake of 300 is scaled pro rata. That is our reading; the handbook gives only the figure up to 300.
- There is no fixed land-area check, because the handbook sets land by local FSI/FAR.
- A careful paste on a photo with no QR code or signature is not caught.
- The AI reader needs internet. Offline mode handles standard forms but sends free-form letters to a human.
- The name match threshold (85%) is our setting and needs tuning on real documents.

---

## 6. Run it

Needs Python 3.11.

```bash
git clone https://github.com/saksham10arora-dotcom/pramaan && cd pramaan
python3.11 -m venv .venv
.venv/bin/pip install -r requirements-full.txt
.venv/bin/python samples/make_samples.py     # demo applications in samples/out/
.venv/bin/streamlit run app.py               # reviewer screen
.venv/bin/uvicorn pramaan.api:app            # REST API, docs at /docs
.venv/bin/python -m pytest -q                # 29 tests
```

**AI reader (optional):** set `GEMINI_API_KEY` in your environment or in `~/.config/keys.env`.

**Web demo vs full version:** the Vercel site runs the same engine, with `requirements.txt`. The OCR models do not fit in Vercel's size limit, so uploaded scans go to human review there; only the `forged_scan` demo works, from saved OCR text in `pramaan/ocr_cache.json`. The AI reader is off on the site because no key is set. The site's record lives in `/tmp` and resets when Vercel restarts the function. The full local version (`requirements-full.txt`) has OCR and a permanent database. Redeploy with `vercel deploy --prod`.

**Demo order:** `clean`, `forged`, `forged_scan`, `ghost`, then the Reviewer queue tab.

**Layout:** `pramaan/` is the engine, `app.py` the reviewer screen, `samples/` the fictional applications, `tests/` the test suite, `docs/` the deck and video, `CHANGES.md` the log of every change.

## 7. Working on it

- Branch from `main`, open a pull request; don't push to `main` directly.
- Add a line to `CHANGES.md` for every change.
- A new check needs a test that fails without it.
- All sample data must stay fictional. Never commit a real institution's documents.
