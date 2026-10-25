from pramaan.validate import summary, validate
from samples.make_samples import bundle, scan


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
