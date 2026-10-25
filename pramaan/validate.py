"""Run every check on an application bundle and return findings with evidence."""
from dataclasses import dataclass
from pathlib import Path

import yaml
from rapidfuzz import fuzz

from . import forensics
from .docs import load
from .extract import classify, extract, parse_date, parse_number

NORMS = yaml.safe_load((Path(__file__).parent / "norms.yaml").read_text())
PASS, FAIL, REVIEW = "PASS", "FAIL", "NEEDS REVIEW"


@dataclass
class Finding:
    rule: str
    status: str
    reason: str
    evidence: list  # (document name, quoted line)


def validate(files: dict, norms: dict = NORMS) -> list[Finding]:
    """files maps file name -> path or bytes."""
    docs, fields, findings = {}, {}, []
    for name, src in files.items():
        doc = load(src, name)
        kind = classify(doc.text)
        if kind is None:
            findings.append(Finding("document type", REVIEW, f"could not tell what {name} is", [(name, "")]))
            continue
        docs[kind] = doc
        fields[kind] = extract(kind, doc.text)

    def f(kind, key):
        return fields.get(kind, {}).get(key)

    def ev(kind, key):
        x = f(kind, key)
        return (docs[kind].name, x.line) if x else (docs[kind].name if kind in docs else kind, "field not found")

    missing = [k for k in norms["required_documents"] if k not in docs]
    findings.append(Finding("required documents", FAIL if missing else PASS,
                            "missing: " + ", ".join(missing) if missing else "all required documents present", []))

    # every document must name the same institution as the application
    inst = f("application_form", "institution")
    for kind in ("building_completion", "fire_noc", "faculty_list"):
        other = f(kind, "institution")
        if inst and other:
            score = fuzz.token_set_ratio(inst.value.lower(), other.value.lower())
            ok = score >= norms["name_match_threshold"]
            findings.append(Finding(f"institution name on {kind.replace('_', ' ')}", PASS if ok else FAIL,
                                    f"matches the application ({score:.0f}%)" if ok else
                                    f"\"{other.value}\" does not match \"{inst.value}\" ({score:.0f}%)",
                                    [ev("application_form", "institution"), ev(kind, "institution")]))

    trust, owner = f("application_form", "trust"), f("land_document", "owner")
    if trust and owner:
        score = fuzz.token_set_ratio(trust.value.lower(), owner.value.lower())
        ok = score >= norms["name_match_threshold"]
        findings.append(Finding("land owned by applicant trust", PASS if ok else FAIL,
                                f"land is in the trust's name ({score:.0f}%)" if ok else
                                f"land is in the name of \"{owner.value}\", not the applicant \"{trust.value}\"",
                                [ev("application_form", "trust"), ev("land_document", "owner")]))

    acres = f("land_document", "area_acres")
    if acres:
        a = parse_number(acres.value)
        findings.append(Finding("minimum land area", PASS if a and a >= norms["min_land_acres"] else FAIL,
                                f"{a} acres against a minimum of {norms['min_land_acres']}",
                                [ev("land_document", "area_acres")]))

    app_date = parse_date(f("application_form", "application_date").value) if f("application_form", "application_date") else None
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

    intake, faculty = f("application_form", "intake"), f("faculty_list", "faculty_count")
    if intake and faculty:
        n, m = parse_number(intake.value), parse_number(faculty.value)
        ratio = n / m if m else float("inf")
        ok = ratio <= norms["max_student_faculty_ratio"]
        findings.append(Finding("student to faculty ratio", PASS if ok else FAIL,
                                f"{ratio:.1f} students per faculty member, limit {norms['max_student_faculty_ratio']}"
                                + ("" if ok else f": needs at least {-(-n // norms['max_student_faculty_ratio']):.0f} faculty"),
                                [ev("application_form", "intake"), ev("faculty_list", "faculty_count")]))

    built = f("building_completion", "built_up_sqm")
    if intake and built:
        need = parse_number(intake.value) * norms["built_up_sqm_per_student"]
        have = parse_number(built.value)
        findings.append(Finding("built-up area", PASS if have >= need else FAIL,
                                f"{have:,.0f} sq m built, {need:,.0f} sq m needed for this intake",
                                [ev("building_completion", "built_up_sqm"), ev("application_form", "intake")]))

    for kind, doc in docs.items():
        for hit in forensics.check(doc):
            findings.append(Finding(f"tampering: {doc.name}", REVIEW, f"{hit['check']}: {hit['detail']}", [(doc.name, "")]))
    return findings


def summary(findings: list[Finding]) -> str:
    if any(x.status == FAIL for x in findings):
        return "REJECT: fix the failed items"
    if any(x.status == REVIEW for x in findings):
        return "SEND TO A HUMAN REVIEWER"
    return "COMPLIANT"
