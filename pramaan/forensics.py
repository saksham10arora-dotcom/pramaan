"""Signs that a PDF was edited after it was issued. Each check returns findings, never a verdict on its own."""
import re

from .docs import Document


def _overlaps(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def check(doc: Document) -> list[dict]:
    found = []
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
