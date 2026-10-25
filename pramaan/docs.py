"""Load a PDF into text, spans and metadata that the other modules read."""
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf


@dataclass
class Span:
    page: int
    text: str
    font: str
    bbox: tuple


@dataclass
class Document:
    name: str
    raw: bytes
    text: str
    spans: list = field(default_factory=list)
    whiteouts: list = field(default_factory=list)  # (page, bbox) of filled white boxes
    metadata: dict = field(default_factory=dict)


def load(path_or_bytes, name=None) -> Document:
    if isinstance(path_or_bytes, (str, Path)):
        raw = Path(path_or_bytes).read_bytes()
        name = name or Path(path_or_bytes).name
    else:
        raw = bytes(path_or_bytes)
    pdf = pymupdf.open(stream=raw, filetype="pdf")
    spans, whiteouts, pages = [], [], []
    for pno, page in enumerate(pdf):
        pages.append(page.get_text())
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for s in line["spans"]:
                    if s["text"].strip():
                        spans.append(Span(pno, s["text"], s["font"], tuple(s["bbox"])))
        for d in page.get_drawings():
            if d.get("fill") == (1.0, 1.0, 1.0) and d["rect"].width < page.rect.width * 0.9:
                whiteouts.append((pno, tuple(d["rect"])))
    return Document(name, raw, "\n".join(pages), spans, whiteouts, dict(pdf.metadata or {}))
