import pymupdf
import pytest
from fastapi.testclient import TestClient

from pramaan.area import engineering_ug
from pramaan.registry import Registry
from pramaan.report import to_pdf
from pramaan.validate import FAIL, NORMS, PASS, REVIEW, analyse, summary, validate
from samples.make_samples import bundle, staff, write


def files(folder):
    return {p.name: p for p in sorted(folder.glob("*.pdf"))}


def rule(found, name):
    return [x for x in found if x.rule.startswith(name)]


def test_area_matches_a_hand_worked_example():
    # 2 courses, 120 a year, 4 years: instructional 2450, admin 1200, amenities 800, plus 25% circulation
    need = engineering_ug(2, 120, 4)
    assert need["intake"] == 480 and need["instructional"] == 2450 and need["total"] == 5562.5


def test_small_building_fails(tmp_path):
    bundle(tmp_path, built="4,000")
    f = rule(validate(files(tmp_path)), "built-up area")[0]
    assert f.status == FAIL and "5,562" in f.reason


def test_no_norm_means_a_human_decides(tmp_path):
    bundle(tmp_path)
    write(tmp_path / "application_form.pdf", "AICTE Application", [
        "Name of Institution: Shree Ram Institute of Technology", "Programme: Pharmacy", "Intake per Year: 120",
        "Duration (years): 4", "Date of Application: 15/09/2026"])
    assert rule(validate(files(tmp_path)), "student to faculty")[0].status == REVIEW


def test_unreadable_key_field_never_reaches_compliant(tmp_path):
    bundle(tmp_path)
    write(tmp_path / "fire_noc.pdf", "Fire Safety Certificate", ["Name of Premises: Shree Ram Institute of Technology"])
    report = analyse(files(tmp_path))
    assert report.verdict == "SEND TO A HUMAN REVIEWER"
    assert "valid until" in rule(report.findings, "unreadable fields")[0].reason


def test_old_building_needs_structural_certificate(tmp_path):
    bundle(tmp_path)
    write(tmp_path / "building_completion.pdf", "Building Completion Certificate", [
        "Issued to: Shree Ram Institute of Technology", "Built-up Area (sq m): 6,000", "Date of Issue: 12/06/1990"])
    assert rule(validate(files(tmp_path)), "structural stability")[0].status == FAIL
    write(tmp_path / "structural.pdf", "Structural Stability Certificate", ["Date of Issue: 01/02/2024"])
    assert rule(validate(files(tmp_path)), "structural stability")[0].status == PASS


def test_stated_total_must_match_the_names(tmp_path):
    bundle(tmp_path)
    write(tmp_path / "faculty_list.pdf", "Faculty List 2026-27", [
        "Name of Institution: Shree Ram Institute of Technology", "Total Faculty: 30", *staff(25)])
    assert rule(validate(files(tmp_path)), "faculty count")[0].status == FAIL


def test_same_id_twice_fails(tmp_path):
    bundle(tmp_path, faculty=staff(25) + staff(1))
    assert rule(validate(files(tmp_path)), "faculty listed twice")[0].status == FAIL


def test_second_document_of_a_type_is_not_silently_ignored(tmp_path):
    bundle(tmp_path)
    (tmp_path / "another_noc.pdf").write_bytes((tmp_path / "fire_noc.pdf").read_bytes())
    assert rule(validate(files(tmp_path)), "duplicate document")[0].status == REVIEW


def ghost(folder):
    bundle(folder, inst="Ganga College of Engineering", trust="Ganga Vidya Trust", addr="Sonipat Road, Haryana")


def test_ghost_faculty_and_reused_certificate_are_caught(tmp_path):
    reg = Registry()
    bundle(tmp_path / "a")
    reg.record(analyse(files(tmp_path / "a"), registry=reg))
    ghost(tmp_path / "b")
    found = analyse(files(tmp_path / "b"), registry=reg).findings
    assert "25 faculty" in rule(found, "faculty at another")[0].reason
    assert "certificate number DFS/NOC/2026/0417" in rule(found, "reused document: fire_noc")[0].reason


def test_each_ghost_is_counted_once_across_resubmissions(tmp_path):
    reg = Registry()
    for i, valid in enumerate(("31/03/2027", "31/03/2028", "31/03/2029")):
        bundle(tmp_path / str(i), fire_valid=valid)
        reg.record(analyse(files(tmp_path / str(i)), registry=reg))
    ghost(tmp_path / "b")
    assert "25 faculty" in rule(analyse(files(tmp_path / "b"), registry=reg).findings, "faculty at another")[0].reason


def test_rechecking_the_original_does_not_blame_it_for_a_later_copy(tmp_path):
    reg = Registry()
    bundle(tmp_path / "a")
    reg.record(analyse(files(tmp_path / "a"), registry=reg))
    ghost(tmp_path / "b")
    reg.record(analyse(files(tmp_path / "b"), registry=reg))
    assert analyse(files(tmp_path / "a"), registry=reg).verdict == "COMPLIANT"
    assert analyse(files(tmp_path / "b"), registry=reg).verdict.startswith("REJECT")


def test_resubmission_by_the_same_institution_is_not_a_clash(tmp_path):
    reg = Registry()
    bundle(tmp_path)
    reg.record(analyse(files(tmp_path), registry=reg))
    report = analyse(files(tmp_path), registry=reg)
    assert report.verdict == "COMPLIANT"
    reg.record(report)
    assert len(reg.queue()) == 1


def test_queue_puts_the_riskiest_first(tmp_path):
    reg = Registry()
    bundle(tmp_path / "a")
    reg.record(analyse(files(tmp_path / "a"), registry=reg))
    ghost(tmp_path / "b")
    reg.record(analyse(files(tmp_path / "b"), registry=reg))
    assert reg.queue()[0]["institution"] == "Ganga College of Engineering"


def sign(src, dst, tmp):
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from datetime import datetime, timedelta, timezone
    from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
    from pyhanko.sign import signers

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, "Test Fire Officer")])
    now = datetime.now(timezone.utc)
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
            .serial_number(7).not_valid_before(now - timedelta(days=1)).not_valid_after(now + timedelta(days=30))
            .sign(key, hashes.SHA256()))
    (tmp / "k.pem").write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                                  serialization.NoEncryption()))
    (tmp / "c.pem").write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    signer = signers.SimpleSigner.load(str(tmp / "k.pem"), str(tmp / "c.pem"))
    with open(src, "rb") as f:
        out = signers.sign_pdf(IncrementalPdfFileWriter(f), signers.PdfSignatureMetadata(field_name="Sig"), signer=signer)
    dst.write_bytes(out.getvalue())


def test_signature_intact_then_broken(tmp_path):
    bundle(tmp_path / "b")
    noc = tmp_path / "b" / "fire_noc.pdf"
    sign(noc, tmp_path / "signed.pdf", tmp_path)
    noc.write_bytes((tmp_path / "signed.pdf").read_bytes())
    f = rule(validate(files(tmp_path / "b")), "digital signature")[0]
    assert f.status == PASS and "Test Fire Officer" in f.reason
    pdf = pymupdf.open(noc)
    pdf[0].insert_text((60, 300), "Valid Until: 31/03/2030")
    pdf.saveIncr()
    assert rule(validate(files(tmp_path / "b")), "digital signature")[0].status == FAIL


def test_api_round_trip(tmp_path, monkeypatch):
    bundle(tmp_path)
    import pramaan.api as api
    monkeypatch.setattr(api, "registry", Registry())
    client = TestClient(api.app)
    upload = [("files", (p.name, p.read_bytes(), "application/pdf")) for p in sorted(tmp_path.glob("*.pdf"))]
    r = client.post("/applications", files=upload).json()
    assert r["verdict"] == "COMPLIANT"
    assert client.get("/applications").json()[0]["id"] == r["id"]
    pdf = client.get(f"/applications/{r['id']}/report.pdf")
    assert pdf.content[:4] == b"%PDF"
    assert client.get("/applications/999").status_code == 404
