"""Run every check on an application bundle and return findings with evidence."""
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

import yaml
from rapidfuzz import fuzz

from . import forensics, llm
from .area import engineering_ug
from .docs import load
from .extract import FIELDS, classify, extract, faculty_rows, parse_date, parse_number

NORMS = yaml.safe_load((Path(__file__).parent / "norms.yaml").read_text())
PASS, FAIL, REVIEW = "PASS", "FAIL", "NEEDS REVIEW"


def same_name(a: str, b: str) -> float:
    """0-100. Takes the better of word overlap and a spaceless compare, so OCR-merged words still match."""
    a, b = a.lower(), b.lower()
    return max(fuzz.token_set_ratio(a, b), fuzz.ratio(a.replace(" ", ""), b.replace(" ", "")))


@dataclass
class Finding:
    rule: str
    status: str
    reason: str
    evidence: list  # (document name, quoted line)


@dataclass
class Report:
    findings: list
    institution: str = ""
    documents: list = field(default_factory=list)  # {name, kind, sha256, cert_no}
    faculty: list = field(default_factory=list)  # (faculty id, name)

    def count(self, status):
        return sum(x.status == status for x in self.findings)

    @property
    def verdict(self):
        return summary(self.findings)

    def to_dict(self):
        return {"institution": self.institution, "verdict": self.verdict, "documents": self.documents,
                "findings": [asdict(x) for x in self.findings]}


def summary(findings: list[Finding]) -> str:
    if any(x.status == FAIL for x in findings):
        return "REJECT: fix the failed items"
    if any(x.status == REVIEW for x in findings):
        return "SEND TO A HUMAN REVIEWER"
    return "COMPLIANT"


def validate(files: dict, norms: dict = NORMS, reader="auto", registry=None) -> list[Finding]:
    return analyse(files, norms, reader, registry).findings


def analyse(files: dict, norms: dict = NORMS, reader="auto", registry=None) -> Report:
    """files maps file name -> path or bytes. reader reads free-form text: llm.read by default when
    a key is set, None for label matching only, or any callable with the same signature."""
    if reader == "auto":
        reader = llm.read if llm.available() else None
    docs, fields, findings = {}, {}, []
    for name, src in files.items():
        doc = load(src, name)
        kind = classify(doc.text)
        found = extract(kind, doc.text) if kind else {}
        if reader and (kind is None or len(found) < len(FIELDS[kind])):
            ai_kind, ai_fields, unverified = reader(doc.text)
            kind = kind or ai_kind
            found = {**ai_fields, **found}  # a label match beats a model reading
            for key, value, quote in unverified:
                findings.append(Finding(f"unverified reading: {name}", REVIEW,
                                        f"AI read {key} = \"{value}\" but that is not in the document" if value else quote,
                                        [(name, quote)] if value else [(name, "")]))
        if kind is None:
            findings.append(Finding("document type", REVIEW, f"could not tell what {name} is", [(name, "")]))
            continue
        if kind in docs:
            findings.append(Finding("duplicate document", REVIEW, f"{name} and {docs[kind].name} are both {kind.replace('_', ' ')}: "
                                    f"only {docs[kind].name} was checked", [(name, ""), (docs[kind].name, "")]))
            continue
        docs[kind] = doc
        fields[kind] = found

    def f(kind, key):
        return fields.get(kind, {}).get(key)

    def ev(kind, key):
        x = f(kind, key)
        return (docs[kind].name, x.line) if x else (docs[kind].name if kind in docs else kind, "field not found")

    def num(kind, key):
        x = f(kind, key)
        return parse_number(x.value) if x else None

    missing = [k for k in norms["required_documents"] if k not in docs]
    findings.append(Finding("required documents", FAIL if missing else PASS,
                            "missing: " + ", ".join(missing) if missing else "all required documents present", []))

    inst = f("application_form", "institution")
    for kind in ("building_completion", "fire_noc", "faculty_list"):
        other = f(kind, "institution")
        if inst and other:
            score = same_name(inst.value, other.value)
            ok = score >= norms["name_match_threshold"]
            findings.append(Finding(f"institution name on {kind.replace('_', ' ')}", PASS if ok else FAIL,
                                    f"matches the application ({score:.0f}%)" if ok else
                                    f"\"{other.value}\" does not match \"{inst.value}\" ({score:.0f}%)",
                                    [ev("application_form", "institution"), ev(kind, "institution")]))

    trust = f("application_form", "trust")
    for kind, label in (("land_document", "land owned by applicant trust"), ("land_use_certificate", "land use issued to applicant trust")):
        owner = f(kind, "owner")
        if trust and owner:
            score = same_name(trust.value, owner.value)
            ok = score >= norms["name_match_threshold"]
            findings.append(Finding(label, PASS if ok else FAIL,
                                    f"in the trust's name ({score:.0f}%)" if ok else
                                    f"in the name of \"{owner.value}\", not the applicant \"{trust.value}\"",
                                    [ev("application_form", "trust"), ev(kind, "owner")]))

    x = f("application_form", "application_date")
    app_date = parse_date(x.value) if x else None
    valid = f("fire_noc", "valid_until")
    if valid:
        until = parse_date(valid.value)
        if until is None or app_date is None:
            findings.append(Finding("fire NOC validity", REVIEW, "could not read the dates", [ev("fire_noc", "valid_until")]))
        else:
            ok = until >= app_date
            findings.append(Finding("fire NOC validity", PASS if ok else FAIL,
                                    f"valid until {until:%d %b %Y}, application dated {app_date:%d %b %Y}"
                                    + ("" if ok else ": expired before the application"),
                                    [ev("fire_noc", "valid_until"), ev("application_form", "application_date")]))

    # clause 6.17(h): an old building needs a current Structural Stability Certificate
    x = f("building_completion", "issue_date")
    issued = parse_date(x.value) if x else None
    if issued and app_date and (app_date - issued).days > norms["structural_after_years"] * 365.25:
        y = f("structural_stability", "issue_date")
        stable = parse_date(y.value) if y else None
        ok = stable is not None and (app_date - stable).days <= norms["structural_valid_years"] * 365.25
        findings.append(Finding("structural stability", PASS if ok else FAIL,
                                f"building is over {norms['structural_after_years']} years old: certificate "
                                + ("is current" if ok else f"is missing or older than {norms['structural_valid_years']} years"),
                                [ev("building_completion", "issue_date")]))

    rows = faculty_rows(docs["faculty_list"].text) if "faculty_list" in docs else []
    ids = [i for i, _ in rows]
    repeated = sorted({i for i in ids if ids.count(i) > 1})
    if repeated:
        findings.append(Finding("faculty listed twice", FAIL, "same faculty ID appears twice: " + ", ".join(repeated),
                                [(docs["faculty_list"].name, r) for r in repeated]))
    stated = num("faculty_list", "faculty_count")
    if rows and stated is not None and stated != len(set(ids)):
        findings.append(Finding("faculty count", FAIL, f"the list says {stated:.0f} but names {len(set(ids))}",
                                [ev("faculty_list", "faculty_count")]))
    faculty = len(set(ids)) or stated

    programme = f("application_form", "programme")
    per_year, years = num("application_form", "intake_per_year"), num("application_form", "duration")
    limit = norms["faculty_ratio"].get(programme.value.strip().lower()) if programme else None
    intake = per_year * years if per_year and years else None
    if programme and limit is None:
        findings.append(Finding("student to faculty ratio", REVIEW, f"no norm loaded for programme \"{programme.value}\"",
                                [ev("application_form", "programme")]))
    elif intake and faculty:
        ratio = intake / faculty
        ok = ratio <= limit
        findings.append(Finding("student to faculty ratio", PASS if ok else FAIL,
                                f"{ratio:.1f} students per faculty member across {intake:.0f} students, limit {limit} (Annexure 5.2)"
                                + ("" if ok else f": needs at least {-(-intake // limit):.0f} faculty"),
                                [ev("application_form", "intake_per_year"), (docs["faculty_list"].name, f"{faculty:.0f} faculty")]))

    built, courses = num("building_completion", "built_up_sqm"), num("application_form", "courses")
    if built and per_year and years and courses:
        if programme and programme.value.strip().lower() == "engineering and technology":
            need = engineering_ug(int(courses), int(per_year), int(years))
            ok = built >= need["total"]
            findings.append(Finding("built-up area", PASS if ok else FAIL,
                                    f"{built:,.0f} sq m built, {need['total']:,.0f} sq m needed for {need['intake']} students (Annexure 3)",
                                    [ev("building_completion", "built_up_sqm"), ev("application_form", "intake_per_year")]))
        else:
            findings.append(Finding("built-up area", REVIEW, "area tables are loaded for Engineering and Technology only",
                                    [ev("building_completion", "built_up_sqm")]))

    # a QR code printed by the issuer carries the certificate's own values; compare them with the page
    for kind, doc in docs.items():
        for payload in forensics.qr_payloads(doc):
            for key, qv in extract(kind, payload).items():
                pv = fields[kind].get(key)
                if not pv:
                    continue
                qd, pd = parse_date(qv.value), parse_date(pv.value)
                same = (qd == pd) if qd and pd else same_name(qv.value, pv.value) >= norms["name_match_threshold"]
                findings.append(Finding(f"QR code on {doc.name}: {key.replace('_', ' ')}", PASS if same else FAIL,
                                        "QR code matches the printed text" if same else
                                        f"QR code says \"{qv.value}\", the page says \"{pv.value}\": the page was altered",
                                        [(doc.name, "QR: " + qv.line), (doc.name, pv.line)]))

    for kind, doc in docs.items():
        for sig in forensics.signatures(doc):
            findings.append(Finding(f"digital signature on {doc.name}", PASS if sig["ok"] else FAIL,
                                    f"signed by {sig['signer']}, unchanged since signing" if sig["ok"] else
                                    f"signature by {sig['signer']} is broken: the file changed after signing", [(doc.name, "")]))
        for hit in forensics.check(doc):
            findings.append(Finding(f"tampering: {doc.name}", REVIEW, f"{hit['check']}: {hit['detail']}", [(doc.name, "")]))

    institution = inst.value if inst else ""
    documents = [{"name": d.name, "kind": k, "sha256": d.sha256,
                  "cert_no": fields[k]["cert_no"].value if "cert_no" in fields[k] else ""} for k, d in docs.items()]
    if registry:
        elsewhere = lambda who: institution and same_name(who, institution) < norms["name_match_threshold"]
        for d in documents:
            hits = [r for r in registry.document_elsewhere(d["sha256"], d["cert_no"]) if elsewhere(r["institution"])]
            if hits:
                what = "the same file" if hits[0]["same_file"] else f"certificate number {d['cert_no']}"
                findings.append(Finding(f"reused document: {d['name']}", FAIL,
                                        f"{what} was already submitted by {hits[0]['institution']}", [(d["name"], d["cert_no"])]))
        shared = {}  # one row per person, however many times the other institution submitted
        for i, n in rows:
            for r in registry.faculty_elsewhere(i):
                if elsewhere(r["institution"]):
                    shared[i] = (i, n, r["institution"])
        shared = list(shared.values())
        if shared:
            shown = ", ".join(f"{n} ({i})" for i, n, _ in shared[:3])
            findings.append(Finding("faculty at another institution", FAIL,
                                    f"{len(shared)} faculty are also listed by {shared[0][2]}, for example {shown}",
                                    [(docs["faculty_list"].name, f"{i} {n}") for i, n, _ in shared[:5]]))
    return Report(findings, institution, documents, rows)
