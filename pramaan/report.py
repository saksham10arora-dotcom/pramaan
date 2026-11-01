"""Downloadable review report for one application."""
import base64
import io
from xml.sax.saxutils import escape

import pymupdf
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

COLOUR = {"FAIL": "#C0392B", "NEEDS REVIEW": "#B9770E", "PASS": "#1E8449"}


def to_pdf(report: dict) -> bytes:
    style = getSampleStyleSheet()
    out = io.BytesIO()
    body = [Paragraph("Pramaan review report", style["Title"]),
            Paragraph(f"<b>Institution:</b> {escape(report['institution'] or 'not read')}", style["Normal"]),
            Paragraph(f"<b>Verdict:</b> {escape(report['verdict'])}", style["Normal"]), Spacer(1, 12)]
    order = {"FAIL": 0, "NEEDS REVIEW": 1, "PASS": 2}
    for x in sorted(report["findings"], key=lambda x: order[x["status"]]):
        body.append(Paragraph(f'<font color="{COLOUR[x["status"]]}"><b>{x["status"]}</b></font> '
                              f'<b>{escape(x["rule"])}</b>: {escape(x["reason"])}', style["Normal"]))
        for doc, line in x["evidence"]:
            if line:
                body.append(Paragraph(f'<font size="8" color="grey">{escape(doc)}: "{escape(line)}"</font>', style["Normal"]))
        body.append(Spacer(1, 6))
    SimpleDocTemplate(out, pagesize=A4, title="Pramaan review report").build(body)
    return out.getvalue()


def highlights(files: dict, findings: list) -> list[dict]:
    """The page around every white box, outlined, as a PNG data URL for the reviewer."""
    from .docs import load
    out = []
    for x in findings:
        if x.rule.startswith("tampering") and "white box" in x.reason:
            name = x.rule.split(": ", 1)[1]
            doc = load(files[name], name)
            pdf = pymupdf.open(stream=doc.raw, filetype="pdf")
            for pno, box in doc.whiteouts:
                page = pdf[pno]
                page.draw_rect(pymupdf.Rect(box) + (-4, -4, 4, 4), color=(0.9, 0.1, 0.1), width=2)
                clip = pymupdf.Rect(0, max(0, box[1] - 120), page.rect.width, box[3] + 80)
                png = page.get_pixmap(dpi=110, clip=clip).tobytes("png")
                out.append({"rule": x.rule, "image": "data:image/png;base64," + base64.b64encode(png).decode()})
    return out
