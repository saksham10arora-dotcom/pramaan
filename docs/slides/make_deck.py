"""SIH idea deck in the same template as the SIGMA deck: one thesis per slide, real app screenshots."""
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

D = Path(__file__).parent
I = D / "img"
C = lambda h: RGBColor.from_string(h)
NAVY, BLUE, INK, MUT, WHITE, DARK = C("17335C"), C("1E5AA8"), C("1B2430"), C("5B6877"), C("FFFFFF"), C("0B121A")
GRN, AMB, RED, PUR = C("2E9E78"), C("C47F16"), C("C94F42"), C("6B4FA0")
prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)


def crop(name, box, out):
    """box is in the 1440x810 layout the screenshots were taken at."""
    Image.open(I / f"{name}.png").crop(tuple(v * 2 for v in box)).save(I / f"{out}.png")
    return f"{out}.png"


def tx(s, x, y, w, h, lines, size=14, color=INK, bold=False, font="Arial", align=None, anchor=None):
    tf = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)).text_frame; tf.word_wrap = True
    if anchor: tf.vertical_anchor = anchor
    for i, ln in enumerate(lines if isinstance(lines, list) else [lines]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        b, sz, col = bold, size, color
        if isinstance(ln, tuple): ln, b, sz, col = (list(ln) + [bold, size, color][len(ln) - 1:])[:4]
        p.text = ln; p.font.size = Pt(sz); p.font.color.rgb = col; p.font.bold = b; p.font.name = font; p.space_after = Pt(3)
        if align is not None: p.alignment = align


def rect(s, x, y, w, h, fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    r = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h)); r.fill.solid(); r.fill.fore_color.rgb = fill
    r.line.fill.background()
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE: r.adjustments[0] = .08
    return r


def img(s, name, x, y, w=None, h=None, border=True):
    p = s.shapes.add_picture(str(I / name), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)
    if border: p.line.color.rgb = C("D5DBE3")
    return p


def card(s, x, y, w, h, head, body, col, num=None):
    rect(s, x, y, w, h, C("F3F5F8")); rect(s, x, y, .09, h, col, MSO_SHAPE.RECTANGLE)
    if num: tx(s, x + .2, y + .08, .8, .6, num, 26, col, True)
    tx(s, x + (.85 if num else .25), y + .1, w - (1.0 if num else .4), h - .2, [(head, True, 15, INK)] + [(b, False, 12, MUT) for b in body])


def slide(n, title, thesis, notes):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    e = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(.35), Inches(.28), Inches(1.5), Inches(.9)); e.fill.background()
    e.line.color.rgb = C("7A4E9A"); e.text_frame.text = "Team Name"
    e.text_frame.paragraphs[0].font.size = Pt(13); e.text_frame.paragraphs[0].font.color.rgb = INK
    tx(s, 2.1, .25, 8.8, .8, title, 32, INK, True, "Times New Roman", PP_ALIGN.CENTER)
    tx(s, 2.1, .9, 8.8, .5, thesis, 16, BLUE, False, "Georgia", PP_ALIGN.CENTER)
    tx(s, 10.7, .35, 2.4, .9, ["SMART INDIA", "HACKATHON 2026"], 14, NAVY, True, align=PP_ALIGN.RIGHT)
    rect(s, 0, 6.95, 13.333, .55, BLUE, MSO_SHAPE.RECTANGLE)
    tx(s, 4.2, 7.0, 5, .4, "@SIH Idea submission- Template", 12, WHITE, align=PP_ALIGN.CENTER)
    tx(s, 12.2, 7.0, .8, .4, str(n), 12, WHITE, True)
    s.notes_slide.notes_text_frame.text = notes
    return s


whitebox = crop("app_whitebox", (500, 200, 1370, 600), "c_whitebox")
qr = crop("app_qr", (60, 270, 1370, 620), "c_qr")
ghost = crop("app_ghost", (500, 280, 1370, 640), "c_ghost")
queue = crop("app_queue", (60, 290, 1390, 530), "c_queue")
evidence = crop("app_clean", (60, 130, 1420, 620), "c_clean")

# 1 Title
s = prs.slides.add_slide(prs.slide_layouts[6])
tx(s, .5, .3, 12.3, .8, "SMART INDIA HACKATHON 2026", 34, NAVY, True, "Times New Roman", PP_ALIGN.CENTER)
tx(s, .5, 1.05, 12.3, .5, "TITLE PAGE", 22, INK, True, "Times New Roman", PP_ALIGN.CENTER)
facts = [("Problem Statement ID", "SIH26261"),
         ("Problem Statement Title", "AI-Powered Application Validation, Document Authentication and Regulatory Compliance Verification"),
         ("Theme", "Smart Automation"), ("PS Category", "Software"), ("Team ID", ""), ("Team Name (Registered on portal)", "")]
y = 1.8
for k, v in facts:
    h = .95 if len(v) > 40 else .55
    tx(s, .6, y, 5.4, h, [(k, True, 12, MUT), (v or " ", True, 14 if len(v) > 40 else 17, INK)]); y += h + .2
rect(s, 6.4, 1.8, 6.5, 4.9, DARK)
tx(s, 6.75, 2.0, 6, .9, "Pramaan", 54, WHITE, True)
tx(s, 6.75, 2.95, 6, .5, "Every AICTE application verdict, with proof", 15, C("9FB0C4"))
img(s, whitebox, 6.75, 3.65, w=5.8, border=False)
s.notes_slide.notes_text_frame.text = "Pramaan means proof. It checks an AICTE application end to end and every result comes with its evidence."

# 2 Idea
s = slide(2, "IDEA TITLE", "From manual scrutiny to one verdict, with proof",
          "Officials read every document by hand. Pramaan reads the whole application and gives one of three verdicts, and it never approves something it is unsure of.")
tx(s, .45, 1.55, 6.4, .4, "Today", 16, RED, True)
tx(s, .45, 1.9, 6.4, 1.2, ["• Officials read every land, building, fire and faculty document by hand",
                           "• An edited certificate looks genuine to the eye",
                           "• Nobody can compare one faculty list with every other institution's"], 13)
tx(s, .45, 3.2, 6.4, .4, "Proposed Solution", 16, NAVY, True)
tx(s, .45, 3.55, 6.4, 1.2, "Pramaan reads an institution's whole application, checks it against the AICTE Approval Process Handbook, "
   "against itself and against every earlier application, and returns one verdict with quoted evidence.", 13)
for i, (t, c) in enumerate([("COMPLIANT", GRN), ("REJECT", RED), ("HUMAN REVIEW", AMB)]):
    r = rect(s, .45 + i * 2.17, 5.1, 2.05, .6, c); r.text_frame.text = t; r.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = r.text_frame.paragraphs[0]; p.font.size = Pt(13); p.font.bold = True; p.font.color.rgb = WHITE; p.alignment = PP_ALIGN.CENTER
tx(s, .45, 5.85, 6.4, .9, "Rule: never approves what it is unsure of. Unreadable text, unverified AI readings and edit marks all go to an officer, with the reason.", 12, MUT)
for i, (h, b, c) in enumerate([("Read", ["typed PDFs, scans and phone photos", "OCR runs offline on the server"], BLUE),
                                ("Check norms", ["faculty ratio, built-up area, fire validity", "from the AICTE handbook, with annexure cited"], AMB),
                                ("Authenticate", ["edit marks, QR vs page, digital signatures"], GRN),
                                ("Remember", ["same faculty or certificate at two", "institutions is caught across applications"], RED)]):
    card(s, 7.2, 1.6 + i * 1.3, 5.7, 1.15, h, b, c, f"0{i + 1}")

# 3 Technical approach
s = slide(3, "TECHNICAL APPROACH", "AI proposes. Code verifies.",
          "Label matching reads standard forms. Gemini reads free-form letters, but a value is kept only if its source line is in the document and numbers match exactly. Then the rule engine, forensics and registry run.")
steps = [("Read", "PyMuPDF\nRapidOCR", BLUE), ("Classify", "document\ntype", BLUE), ("Extract", "labels, then\nGemini", PUR), ("Verify", "quote must be\nin the text", PUR),
         ("Check", "norms and\ncross-document", AMB), ("Authenticate", "edits, QR,\nsignature", GRN), ("Registry", "against earlier\napplications", RED), ("Verdict", "with quoted\nevidence", NAVY)]
for i, (h, b, c) in enumerate(steps):
    x = .4 + i * 1.57
    r = rect(s, x, 1.55, 1.42, 1.3, c)
    tx(s, x, 1.6, 1.42, 1.2, [(h, True, 14, WHITE)] + [(l, False, 11, WHITE) for l in b.split("\n")], align=PP_ALIGN.CENTER)
    if i < 7: rect(s, x + 1.42, 2.13, .15, .14, MUT, MSO_SHAPE.RIGHT_ARROW)
img(s, qr, .4, 3.05, w=8.2)
tx(s, .4, 5.35, 8.2, .9, ["Example: a forger prints and scans the page, so no edit marks survive. The issuer's QR code still holds the true date, so Pramaan rejects it."], 12, MUT)
chips = [("Python", BLUE), ("FastAPI", BLUE), ("Streamlit", BLUE), ("SQLite", BLUE), ("PyMuPDF", NAVY), ("RapidOCR", NAVY), ("OpenCV", NAVY), ("pyHanko", NAVY),
         ("Gemini", PUR), ("RapidFuzz", PUR), ("ReportLab", GRN), ("pytest", GRN)]
for i, (t, c) in enumerate(chips):
    r = rect(s, 8.95 + (i % 2) * 2.0, 3.1 + (i // 2) * .56, 1.88, .46, c)
    r.text_frame.text = t; r.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE; p = r.text_frame.paragraphs[0]; p.font.size = Pt(12); p.font.bold = True
    p.font.color.rgb = WHITE; p.alignment = PP_ALIGN.CENTER

# 4 Feasibility
s = slide(4, "FEASIBILITY AND VIABILITY", "Working prototype, real norms, honest limits",
          "This is built and running. The norms come from the actual handbook. Be upfront that all test documents so far are synthetic, and that signatures are checked for integrity, not yet against the CCA root list.")
for i, (big, small, c) in enumerate([("28", "automated tests\nall passing", BLUE), ("7", "document types\nread", AMB),
                                      ("<1 s", "per demo application\non a laptop", GRN), ("REST", "API ready for\nportal integration", NAVY)]):
    rect(s, .45 + i * 1.62, 1.6, 1.5, 1.9, c)
    tx(s, .45 + i * 1.62, 1.7, 1.5, .9, big, 34, WHITE, True, align=PP_ALIGN.CENTER)
    tx(s, .5 + i * 1.62, 2.55, 1.4, .9, small.split("\n"), 11, WHITE, align=PP_ALIGN.CENTER)
img(s, queue, .45, 3.7, w=6.4)
tx(s, .45, 5.65, 6.4, 1.2, [("Viability", True, 14, NAVY), "• Open-source stack; OCR and every rule run on the server",
                            "• Norms live in one config file, updated each handbook cycle"], 12)
tx(s, 7.1, 1.55, 5.8, .4, "Risks and how we handle them", 16, NAVY, True)
for i, (h, b, c) in enumerate([("Real scans are messier than our samples", ["Tested on synthetic documents so far; unreadable fields go to a human"], RED),
                               ("AI can invent a value", ["Kept only if its source line is in the document, numbers exact"], AMB),
                               ("A careful paste on a photo with no QR", ["Not caught yet; issuer QR and signatures are the defence"], RED),
                               ("Sensitive documents", ["AI reader is optional; offline mode sends nothing out"], GRN)]):
    card(s, 7.1, 2.0 + i * 1.2, 5.8, 1.08, h, b, c)

# 5 Impact
s = slide(5, "IMPACT AND BENEFITS", "Faster scrutiny, harder fraud, decisions you can audit",
          "The impact is less time on clean applications and more officer attention on risky ones. Ghost faculty is the strongest example, because no check on one file can find it.")
for i, (h, c, pts) in enumerate([("AICTE officers", BLUE, ["Clean files verified at once", "Riskiest applications first", "Every finding quotes its source"]),
                                  ("Honest institutions", GRN, ["Know exactly what to fix", "Consistent rules for everyone", "No first-glance bias"]),
                                  ("Students", AMB, ["Real faculty, not names on paper", "Safer, fire-certified buildings", "Trustworthy approvals"]),
                                  ("Government", NAVY, ["Audit trail for every decision", "Ghost faculty detected at scale", "Portal plugs in over REST"])]):
    x = .45 + i * 3.15
    rect(s, x, 1.6, 3.0, .6, c); tx(s, x, 1.62, 3.0, .55, h, 17, WHITE, True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    rect(s, x, 2.2, 3.0, 1.55, C("F3F5F8"))
    tx(s, x + .15, 2.3, 2.8, 1.4, ["• " + p for p in pts], 13, INK)
img(s, ghost, .45, 3.95, h=2.85)
tx(s, 7.55, 4.2, 5.35, 2.4, [("Caught across applications", True, 17, RED),
                           ("A second college lists 25 faculty already on another institution's record, and reuses its fire certificate number.", False, 14, INK),
                           ("Every document looks fine alone. Only memory across applications finds it.", False, 13, MUT)])

# 6 References
s = slide(6, "RESEARCH AND REFERENCES", "Built on the AICTE handbook and published standards",
          "Every norm in the system cites the handbook annexure it comes from.")
tx(s, .5, 1.55, 6, .4, "Regulation", 18, NAVY, True)
for i, (a, b) in enumerate([("AICTE Approval Process Handbook 2024-27", "Annexure 3 (land, area), Annexure 5 (faculty), clause 6.17"),
                            ("AICTE Act, 1987", "Statutory basis for approval of technical institutions"),
                            ("Information Technology Act, 2000", "Legal recognition of digital signatures"),
                            ("Digital Personal Data Protection Act, 2023", "Handling of faculty and applicant data")]):
    card(s, .5, 2.05 + i * 1.15, 5.9, 1.02, a, [b], BLUE)
tx(s, 6.9, 1.55, 6, .4, "Standards and research", 18, NAVY, True)
for i, (a, b) in enumerate([("ISO 32000-2", "PDF structure, incremental updates, signatures"),
                            ("ISO/IEC 18004", "QR code symbology"),
                            ("Du et al., 2020, PP-OCR", "Lightweight OCR, arXiv:2009.09941; basis of RapidOCR"),
                            ("Levenshtein, 1966", "Edit distance, used for name matching")]):
    card(s, 6.9, 2.05 + i * 1.15, 6.0, 1.02, a, [b], GRN)

prs.save(D / "Pramaan_SIH_deck.pptx"); print("saved")
