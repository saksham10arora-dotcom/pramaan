import json

from pramaan.llm import read, verify
from pramaan.validate import FAIL, PASS, REVIEW, validate
from samples.make_samples import bundle, write

LETTER = [
    "Delhi Fire Service, Government of NCT of Delhi",
    "Fire Safety No Objection Certificate",
    "This is to certify that the premises of Shree Ram Institute of Technology,",
    "Plot 14, Sector 9, Rohini, have been inspected and found compliant.",
    "This certificate shall remain in force till 31st March, 2027.",
]


def fake(answer):
    return lambda prompt: json.dumps(answer)


def test_verify_accepts_a_date_written_in_words():
    assert verify("remain in force till 31st March, 2027.", "31/03/2027", "remain in force till 31st March, 2027")


def test_verify_rejects_a_quote_that_is_not_in_the_text():
    assert not verify("remain in force till 31st March, 2026.", "31/03/2027", "remain in force till 31st March, 2027")


def test_verify_rejects_a_value_the_quote_does_not_contain():
    assert not verify("in force till 31st March, 2026.", "31/03/2027", "in force till 31st March, 2026")


def test_free_form_noc_is_read_and_checked(tmp_path):
    bundle(tmp_path)
    write(tmp_path / "fire_noc.pdf", "Certificate", LETTER)
    reader = lambda text: read(text, fake({"doc_type": "fire_noc", "fields": {
        "institution": {"value": "Shree Ram Institute of Technology",
                        "quote": "the premises of Shree Ram Institute of Technology"},
        "valid_until": {"value": "31/03/2027", "quote": "shall remain in force till 31st March, 2027"}}}))
    found = validate({p.name: p for p in tmp_path.glob("*.pdf")}, reader=reader)
    noc = [x for x in found if x.rule == "fire NOC validity"][0]
    assert noc.status == PASS and "31st March, 2027" in noc.evidence[0][1]


def test_hallucinated_value_goes_to_a_human(tmp_path):
    bundle(tmp_path)
    write(tmp_path / "fire_noc.pdf", "Certificate", [l.replace("2027", "2026") for l in LETTER])
    reader = lambda text: read(text, fake({"doc_type": "fire_noc", "fields": {
        "valid_until": {"value": "31/03/2027", "quote": "shall remain in force till 31st March, 2027"}}}))
    found = validate({p.name: p for p in tmp_path.glob("*.pdf")}, reader=reader)
    assert any(x.status == REVIEW and "not in the document" in x.reason for x in found)
    assert not any(x.rule == "fire NOC validity" and x.status == PASS for x in found)


def test_model_failure_never_passes_silently(tmp_path):
    def broken(prompt):
        raise ConnectionError
    kind, good, bad = read("anything", broken)
    assert kind is None and good == {} and "unavailable" in bad[0][2]
