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
        "programme": ["Programme"],
        "courses": ["Number of Courses"],
        "intake_per_year": ["Intake per Year", "Annual Intake"],
        "duration": ["Duration (years)", "Course Duration"],
        "application_date": ["Date of Application", "Application Date"],
    },
    "land_document": {
        "owner": ["Name of Owner", "Owner", "In the name of"],
        "address": ["Property Address", "Address"],
        "cert_no": ["Registration No"],
    },
    "land_use_certificate": {
        "owner": ["Issued to", "Name of Applicant"],
        "land_use": ["Permitted Use", "Land Use"],
        "cert_no": ["Certificate No"],
    },
    "building_completion": {
        "institution": ["Name of Institution", "Issued to"],
        "built_up_sqm": ["Built-up Area (sq m)", "Total Built-up Area"],
        "issue_date": ["Date of Issue", "Issue Date"],
        "cert_no": ["Certificate No"],
    },
    "structural_stability": {
        "issue_date": ["Date of Issue", "Issue Date"],
        "cert_no": ["Certificate No"],
    },
    "fire_noc": {
        "institution": ["Name of Premises", "Name of Institution"],
        "valid_until": ["Valid Until", "Validity", "Valid upto"],
        "address": ["Address of Premises", "Address"],
        "cert_no": ["Certificate No"],
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
    source: str = "rule"  # "rule" for label matching, "ai" for a verified model reading


def _squash(text: str) -> str:
    """Lowercase, no spaces, and the letter confusions OCR makes most (l/I, 0/O in words)."""
    return re.sub(r"\s+", "", text.lower()).replace("l", "i")


def classify(text: str) -> str | None:
    t = _squash(text)

    def has(*words):
        return all(_squash(w) in t for w in words)

    if has("structural stability"):
        return "structural_stability"
    if has("land use") or has("land conversion"):
        return "land_use_certificate"
    if has("fire") and (has("no objection") or has("noc") or has("safety certificate")):
        return "fire_noc"
    if has("building completion") or has("occupancy certificate"):
        return "building_completion"
    if has("faculty", "list"):
        return "faculty_list"
    if has("land") and (has("deed") or has("registry") or has("ownership")):
        return "land_document"
    if has("application", "aicte"):
        return "application_form"
    return None


def extract(doc_type: str, text: str) -> dict:
    out = {}
    for key, labels in FIELDS.get(doc_type, {}).items():
        for label in labels:
            # OCR drops spaces, so every gap in the label is optional
            pattern = r"\s*".join(re.escape(c) for c in label.replace(" ", ""))
            m = re.search(rf"^\s*{pattern}\s*[:\-]\s*(.+?)\s*$", text, re.I | re.M)
            if m:
                out[key] = Field(m.group(1), m.group(0).strip())
                break
    return out


def faculty_rows(text: str) -> list[tuple]:
    """(faculty id, name) for every row of a faculty list. AICTE faculty IDs look like 1-1000000123."""
    rows = []
    for line in text.splitlines():
        m = re.search(r"\b(1-\d{6,10})\b", line)
        if m:
            name = re.sub(r"^\s*\d+[.)]?\s*", "", line[:m.start()]).strip(" |,-")
            rows.append((m.group(1), name))
    return rows


def parse_date(s: str) -> date | None:
    s = re.sub(r"(\d)(st|nd|rd|th)\b", r"\1", s.replace(",", ""))
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            pass
    return None


def parse_number(s: str) -> float | None:
    m = re.search(r"\d[\d,]*(?:\.\d+)?", s)
    return float(m.group(0).replace(",", "")) if m else None
