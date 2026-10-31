"""Draw the deck to PDF directly from the pptx, for machines without Keynote or LibreOffice."""
from io import BytesIO
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfgen import canvas

D = Path(__file__).parent
FONT = {"Times New Roman": ("Times-Roman", "Times-Bold"), "Georgia": ("Times-Italic", "Times-BoldItalic")}
prs = Presentation(D / "Pramaan_SIH_deck.pptx")
W, H = prs.slide_width / 12700, prs.slide_height / 12700
c = canvas.Canvas(str(D / "Pramaan_SIH_deck.pdf"), pagesize=(W, H))
c.setTitle("Pramaan SIH 2026 idea deck")


def pt(v):
    return v / 12700


def text(shape):
    tf = shape.text_frame
    lines = []
    box = pt(shape.width) - 14.4
    for p in tf.paragraphs:
        if not p.text:
            continue
        pair = FONT.get(p.font.name, ("Helvetica", "Helvetica-Bold"))
        font, size = pair[1 if p.font.bold else 0], p.font.size.pt if p.font.size else 12
        try:
            colour = "#" + str(p.font.color.rgb)
        except AttributeError:
            colour = "#1B2430"
        for ln in simpleSplit(p.text, font, size, box):
            lines.append((ln, font, size, colour, p.alignment))
        lines.append(None)
    height = sum(l[2] * 1.2 for l in lines if l) + 3 * lines.count(None)
    x, top, w, h = pt(shape.left), pt(shape.top), pt(shape.width), pt(shape.height)
    y = H - top - 3.6
    if tf.vertical_anchor == MSO_ANCHOR.MIDDLE or (shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE):
        y = H - top - (h - height) / 2
    for l in lines:
        if l is None:
            y -= 3
            continue
        ln, font, size, colour, align = l
        y -= size * 1.2
        c.setFont(font, size); c.setFillColor(HexColor(colour))
        if align == PP_ALIGN.CENTER:
            c.drawCentredString(x + w / 2, y + size * .2, ln)
        elif align == PP_ALIGN.RIGHT:
            c.drawRightString(x + w - 7.2, y + size * .2, ln)
        else:
            c.drawString(x + 7.2, y + size * .2, ln)


for slide in prs.slides:
    c.setFillColor(HexColor("#FFFFFF")); c.rect(0, 0, W, H, stroke=0, fill=1)
    for s in slide.shapes:
        x, y, w, h = pt(s.left), H - pt(s.top) - pt(s.height), pt(s.width), pt(s.height)
        if s.shape_type == MSO_SHAPE_TYPE.PICTURE:
            c.drawImage(ImageReader(BytesIO(s.image.blob)), x, y, w, h)
            c.setStrokeColor(HexColor("#D5DBE3")); c.rect(x, y, w, h, stroke=1, fill=0)
            continue
        if s.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
            kind = s.auto_shape_type
            if kind == MSO_SHAPE.OVAL:
                c.setStrokeColor(HexColor("#7A4E9A")); c.ellipse(x, y, x + w, y + h, stroke=1, fill=0)
            else:
                c.setFillColor(HexColor("#" + str(s.fill.fore_color.rgb)))
                if kind == MSO_SHAPE.ROUNDED_RECTANGLE:
                    c.roundRect(x, y, w, h, min(w, h) * .08, stroke=0, fill=1)
                elif kind == MSO_SHAPE.RIGHT_ARROW:
                    p = c.beginPath(); p.moveTo(x, y); p.lineTo(x + w, y + h / 2); p.lineTo(x, y + h); p.close()
                    c.drawPath(p, stroke=0, fill=1)
                else:
                    c.rect(x, y, w, h, stroke=0, fill=1)
        if s.has_text_frame and s.text_frame.text:
            text(s)
    c.showPage()
c.save()
