import pytest

from pramaan import docs
from pramaan.validate import summary, validate
from samples.make_samples import bundle, scan


def test_scan_without_ocr_goes_to_a_human(tmp_path, monkeypatch):
    bundle(tmp_path)
    scan(tmp_path / "fire_noc.pdf", tmp_path / "fire_noc.jpg")
    (tmp_path / "fire_noc.pdf").unlink()
    monkeypatch.setattr(docs, "_ocr", lambda: None)
    found = validate({p.name: p for p in tmp_path.iterdir()})
    assert summary(found) == "SEND TO A HUMAN REVIEWER"


@pytest.mark.skipif(not docs.available(), reason="OCR is not installed")
def test_scanned_bundle_gives_the_same_verdict(tmp_path):
    typed, scanned = tmp_path / "typed", tmp_path / "scanned"
    bundle(typed)
    scanned.mkdir()
    for p in typed.glob("*.pdf"):
        if p.stem == "fire_noc":
            scan(p, scanned / "fire_noc.jpg")  # a phone photo
        else:
            scan(p, scanned / p.name)  # a scanned PDF
    found = validate({p.name: p for p in scanned.iterdir()})
    assert summary(found) == "COMPLIANT", [(x.rule, x.reason) for x in found if x.status != "PASS"]
