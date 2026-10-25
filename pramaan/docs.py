"""Load a PDF or an image into text, spans and metadata that the other modules read.

Pages without a text layer (scans, photos) go through offline OCR, so nothing leaves the machine.
"""
import hashlib
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
import pymupdf

IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff")
OCR_DPI = 200


@dataclass
class Span:
    page: int
    text: str
    font: str  # "ocr" when the text came from OCR
    bbox: tuple
    conf: float = 1.0


@dataclass
class Document:
    name: str
    raw: bytes
    text: str
    spans: list = field(default_factory=list)
    whiteouts: list = field(default_factory=list)  # (page, bbox) of filled white boxes
    metadata: dict = field(default_factory=dict)
    images: list = field(default_factory=list)  # one BGR array per page, for OCR, QR and image forensics
    is_image: bool = False
    ocr_pages: list = field(default_factory=list)
    signed: bool = False

    @property
    def sha256(self):
        return hashlib.sha256(self.raw).hexdigest()


@lru_cache(maxsize=1)
def _ocr():
    from rapidocr_onnxruntime import RapidOCR
    return RapidOCR()


def ocr(img, page: int) -> list[Span]:
    result, _ = _ocr()(img)
    spans = []
    for box, text, conf in result or []:
        xs, ys = [p[0] for p in box], [p[1] for p in box]
        spans.append(Span(page, text, "ocr", (min(xs), min(ys), max(xs), max(ys)), float(conf)))
    return spans


def _lines(spans: list[Span]) -> str:
    """Group OCR boxes into reading-order lines."""
    out, row, last_y = [], [], None
    for s in sorted(spans, key=lambda s: ((s.bbox[1] + s.bbox[3]) / 2, s.bbox[0])):
        mid, h = (s.bbox[1] + s.bbox[3]) / 2, s.bbox[3] - s.bbox[1]
        if last_y is not None and abs(mid - last_y) > h * 0.6:
            out.append(" ".join(x.text for x in sorted(row, key=lambda x: x.bbox[0])))
            row = []
        row.append(s)
        last_y = mid
    if row:
        out.append(" ".join(x.text for x in sorted(row, key=lambda x: x.bbox[0])))
    return "\n".join(out)


def load(path_or_bytes, name=None) -> Document:
    if isinstance(path_or_bytes, (str, Path)):
        raw = Path(path_or_bytes).read_bytes()
        name = name or Path(path_or_bytes).name
    else:
        raw = bytes(path_or_bytes)
    name = name or "document"
    if name.lower().endswith(IMAGE_EXT):
        img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return Document(name, raw, "", is_image=True)
        spans = ocr(img, 0)
        return Document(name, raw, _lines(spans), spans, images=[img], is_image=True, ocr_pages=[0])

    pdf = pymupdf.open(stream=raw, filetype="pdf")
    spans, whiteouts, pages, images, ocr_pages = [], [], [], [], []
    for pno, page in enumerate(pdf):
        pix = page.get_pixmap(dpi=OCR_DPI)
        img = cv2.cvtColor(np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)[..., :3], cv2.COLOR_RGB2BGR)
        images.append(img)
        page_spans = []
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for s in line["spans"]:
                    if s["text"].strip():
                        page_spans.append(Span(pno, s["text"], s["font"], tuple(s["bbox"])))
        if page_spans:
            pages.append(page.get_text())
        else:  # scanned page: OCR it, boxes scaled back to PDF points
            scale = 72 / OCR_DPI
            page_spans = [Span(s.page, s.text, s.font, tuple(v * scale for v in s.bbox), s.conf) for s in ocr(img, pno)]
            pages.append(_lines(page_spans))
            ocr_pages.append(pno)
        spans += page_spans
        for d in page.get_drawings():
            if d.get("fill") == (1.0, 1.0, 1.0) and d["rect"].width < page.rect.width * 0.9:
                whiteouts.append((pno, tuple(d["rect"])))
    signed = pdf.get_sigflags() > 0
    return Document(name, raw, "\n".join(pages), spans, whiteouts, dict(pdf.metadata or {}),
                    images, False, ocr_pages, signed)
