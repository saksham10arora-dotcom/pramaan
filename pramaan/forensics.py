"""Signs that a PDF was edited after it was issued. Each check returns findings, never a verdict on its own."""
import re

import cv2
import numpy as np

from .docs import Document

# tools people use to edit an issued certificate; an issuing authority does not produce PDFs with these
EDITORS = ("ilovepdf", "smallpdf", "pdfescape", "sejda", "photoshop", "gimp", "canva", "picsart", "snapseed",
           "pdf-xchange", "foxit phantom", "pdffiller", "inkscape", "paint.net", "pixlr", "lightroom")


def _overlaps(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def editor_trace(doc: Document) -> str | None:
    tags = [doc.metadata.get("producer", ""), doc.metadata.get("creator", "")]
    if doc.is_image:
        try:
            from PIL import Image
            import io
            exif = Image.open(io.BytesIO(doc.raw)).getexif()
            tags += [str(exif.get(0x0131, "")), str(exif.get(0x000B, ""))]  # Software, ProcessingSoftware
        except Exception:
            pass
    for tag in tags:
        for tool in EDITORS:
            if tool in tag.lower():
                return tag
    return None


def qr_payloads(doc: Document) -> list[str]:
    out = []
    det = cv2.QRCodeDetector()
    for img in doc.images:
        ok, texts, _, _ = det.detectAndDecodeMulti(img)
        if ok:
            out += [t for t in texts if t]
    return out


def check(doc: Document) -> list[dict]:
    found = []
    tool = editor_trace(doc)
    if tool:
        found.append({"check": "editing software", "detail": f"file was last written by \"{tool}\""})
    eofs = doc.raw.count(b"%%EOF")
    if eofs > 1:
        found.append({"check": "incremental save",
                      "detail": f"file was saved {eofs - 1} more time(s) after it was first written"})

    created, modified = doc.metadata.get("creationDate", ""), doc.metadata.get("modDate", "")
    if created and modified and modified[:16] != created[:16]:
        found.append({"check": "modified after creation",
                      "detail": f"created {created[2:10]}, modified {modified[2:10]}"})

    for page, box in doc.whiteouts:
        covered = [s.text for s in doc.spans if s.page == page and _overlaps(s.bbox, box)]
        if covered:
            found.append({"check": "white box over text",
                          "detail": f"page {page + 1}: a white rectangle sits under \"{covered[0]}\""})

    fonts = {}
    for s in doc.spans:
        fonts.setdefault(re.sub(r"[-,].*", "", s.font), []).append(s)
    if len(fonts) > 1:
        rare = min(fonts.values(), key=len)
        if len(rare) <= 2:
            found.append({"check": "odd font",
                          "detail": f"\"{rare[0].text}\" is set in {rare[0].font}, used nowhere else in the document"})
    return found
