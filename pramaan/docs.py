"""Load a PDF or an image into text, spans and metadata that the other modules read.

Pages without a text layer (scans, photos) go through offline OCR, so nothing leaves the machine.
"""
import hashlib
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import io
import json

import pymupdf
from PIL import Image

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
    images: list = field(default_factory=list)  # one PIL image per page, for OCR and QR
    is_image: bool = False
    ocr_pages: list = field(default_factory=list)
    signed: bool = False
    unread_scan: bool = False  # a scan arrived but OCR is not installed here

    @property
    def sha256(self):
        return hashlib.sha256(self.raw).hexdigest()


CACHE = Path(__file__).parent / "ocr_cache.json"  # OCR results for the demo scans, used where OCR cannot be installed


@lru_cache(maxsize=1)
def _ocr():
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:  # the web deployment is too small to carry the OCR models
        return None
    return RapidOCR()


@lru_cache(maxsize=1)
def _cache():
    return json.loads(CACHE.read_text()) if CACHE.exists() else {}


def available() -> bool:
    return _ocr() is not None


def ocr(img, page: int, key: str = "") -> list[Span] | None:
    """None means OCR is not available for this page."""
    engine = _ocr()
    if engine is None:
        rows = _cache().get(key)
        return None if rows is None else [Span(page, t, "ocr", tuple(b), c) for t, b, c in rows]
    import numpy as np
    result, _ = engine(np.array(img.convert("RGB"))[:, :, ::-1])
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
    key = hashlib.sha256(raw).hexdigest()
    if name.lower().endswith(IMAGE_EXT):
        try:
            img = Image.open(io.BytesIO(raw)).convert("RGB")
        except Exception:
            return Document(name, raw, "", is_image=True)
        spans = ocr(img, 0, f"{key}:0")
        return Document(name, raw, _lines(spans or []), spans or [], images=[img], is_image=True, ocr_pages=[0],
                        unread_scan=spans is None)

    pdf = pymupdf.open(stream=raw, filetype="pdf")
    spans, whiteouts, pages, images, ocr_pages = [], [], [], [], []
    unread = False
    for pno, page in enumerate(pdf):
        pix = page.get_pixmap(dpi=OCR_DPI)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples) if pix.n == 3 else Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
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
            read = ocr(img, pno, f"{key}:{pno}")
            unread = unread or read is None
            page_spans = [Span(s.page, s.text, s.font, tuple(v * scale for v in s.bbox), s.conf) for s in read or []]
            pages.append(_lines(page_spans))
            ocr_pages.append(pno)
        spans += page_spans
        for d in page.get_drawings():
            if d.get("fill") == (1.0, 1.0, 1.0) and d["rect"].width < page.rect.width * 0.9:
                whiteouts.append((pno, tuple(d["rect"])))
    signed = pdf.get_sigflags() > 0
    return Document(name, raw, "\n".join(pages), spans, whiteouts, dict(pdf.metadata or {}),
                    images, False, ocr_pages, signed, unread)
