"""Pull labelled fields out of document text. Each field keeps the line it came from as evidence."""
import re
from dataclasses import dataclass
from datetime import date, datetime

# document type -> field -> label aliases seen on real forms
FIELDS = {
    "application_form": {
        "institution": ["Name of Institution", "Institution Name"],
        "trust": ["Name of Society/Trust", "Applicant Trust", "Society/Trust"],
        "address": ["Address", "Institution Address"],
        "intake": ["Total Approved Intake", "Total Intake", "Proposed Intake"],
        "application_date": ["Date of Application", "Application Date"],
    },
    "land_document": {
        "owner": ["Name of Owner", "Owner", "In the name of"],
        "address": ["Property Address", "Address"],
        "area_acres": ["Land Area (acres)", "Area in Acres"],
    },
    "building_completion": {
        "institution": ["Name of Institution", "Issued to"],
        "built_up_sqm": ["Built-up Area (sq m)", "Total Built-up Area"],
    },
    "fire_noc": {
        "institution": ["Name of Premises", "Name of Institution"],
        "valid_until": ["Valid Until", "Validity", "Valid upto"],
        "address": ["Address of Premises", "Address"],
    },
    "faculty_list": {
        "institution": ["Name of Institution"],
        "faculty_count": ["Total Faculty", "Number of Faculty"],
    },
}

DATE_FORMATS = ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y-%m-%d", "%d %B %Y", "%d %b %Y")


@dataclass
class Field:
    value: str
    line: str


def classify(text: str) -> str | None:
    t = text.lower()
    if "fire" in t and ("no objection" in t or "noc" in t):
        return "fire_noc"
    if "building completion" in t or "occupancy certificate" in t:
        return "building_completion"
    if "faculty" in t and "list" in t:
        return "faculty_list"
    if "land" in t and ("deed" in t or "registry" in t or "ownership" in t):
        return "land_document"
    if "application" in t and "aicte" in t:
        return "application_form"
    return None


def extract(doc_type: str, text: str) -> dict:
    out = {}
    for key, labels in FIELDS.get(doc_type, {}).items():
        for label in labels:
            m = re.search(rf"^\s*{re.escape(label)}\s*[:\-]\s*(.+?)\s*$", text, re.I | re.M)
            if m:
                out[key] = Field(m.group(1), m.group(0).strip())
                break
    return out


def parse_date(s: str) -> date | None:
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            pass
    return None


def parse_number(s: str) -> float | None:
    m = re.search(r"\d[\d,]*(?:\.\d+)?", s)
    return float(m.group(0).replace(",", "")) if m else None
