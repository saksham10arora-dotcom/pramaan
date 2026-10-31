from pathlib import Path

import pytest

from pramaan.validate import FAIL, PASS, REVIEW, summary, validate
from samples.make_samples import bundle, forge_fire_noc, write


def run(folder: Path):
    return validate({p.name: p for p in sorted(folder.glob("*.pdf"))})


def by_rule(findings, rule):
    return [x for x in findings if x.rule.startswith(rule)]


def test_clean_bundle_is_compliant(tmp_path):
    bundle(tmp_path)
    found = run(tmp_path)
    assert summary(found) == "COMPLIANT"
    assert all(x.status == PASS for x in found)


def test_forged_noc_and_wrong_land_owner_are_caught(tmp_path):
    bundle(tmp_path, land_owner="Rajesh Kumar Gupta", fire_valid="31/03/2026")
    forge_fire_noc(tmp_path / "fire_noc.pdf")
    found = run(tmp_path)
    assert summary(found).startswith("REJECT")
    assert by_rule(found, "land owned")[0].status == FAIL
    assert by_rule(found, "fire NOC")[0].status == FAIL  # the covered date is still in the file
    checks = " ".join(x.reason for x in by_rule(found, "tampering"))
    for sign in ("incremental save", "white box", "odd font"):
        assert sign in checks


def test_too_few_faculty_fails_ratio(tmp_path):
    bundle(tmp_path)
    write(tmp_path / "faculty_list.pdf", "Faculty List 2026-27",
          ["Name of Institution: Shree Ram Institute of Technology", "Total Faculty: 10"])
    f = by_rule(run(tmp_path), "student to faculty")[0]
    assert f.status == FAIL and "at least 24" in f.reason


def test_missing_document_fails(tmp_path):
    bundle(tmp_path)
    (tmp_path / "fire_noc.pdf").unlink()
    f = by_rule(run(tmp_path), "required documents")[0]
    assert f.status == FAIL and "fire_noc" in f.reason


def test_unknown_document_goes_to_a_human(tmp_path):
    bundle(tmp_path)
    write(tmp_path / "misc.pdf", "Some Letter", ["Dear Sir"])
    found = run(tmp_path)
    assert by_rule(found, "document type")[0].status == REVIEW


def test_evidence_quotes_the_source_line(tmp_path):
    bundle(tmp_path)
    f = by_rule(run(tmp_path), "fire NOC")[0]
    assert ("fire_noc.pdf", "Valid Until: 31/03/2027") in f.evidence
