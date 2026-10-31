"""Write fictional application bundles for the demo. No institution, person or number here is real."""
import shutil
import sys
from pathlib import Path

import pymupdf
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

INST = "Shree Ram Institute of Technology"
TRUST = "Shree Ram Educational Trust"
ADDR = "Plot 14, Sector 9, Rohini, New Delhi 110085"


def write(path, title, lines, qr=None):
    c = canvas.Canvas(str(path), pagesize=A4)
    if qr:
        import io
        import qrcode
        from reportlab.lib.utils import ImageReader
        buf = io.BytesIO()
        qrcode.make(qr, box_size=6, border=2).save(buf, format="PNG")
        c.drawImage(ImageReader(io.BytesIO(buf.getvalue())), 430, 600, 110, 110)
    c.setTitle(title)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(60, 780, title)
    c.setFont("Helvetica", 11)
    y, step = 740, 24 if len(lines) < 15 else 22
    for line in lines:
        c.drawString(60, y, line)
        y -= step
    c.save()


FIRST = "Asha Vikram Neha Rohan Priya Arjun Kavita Manish Sunita Deepak Anjali Rahul Meena Sanjay Pooja".split()
LAST = "Sharma Verma Iyer Nair Das Khan Joshi Reddy Bose Malhotra".split()


def staff(n=25):
    """Fictional faculty rows; the names and IDs do not belong to anyone."""
    return [f"{i + 1}. Dr. {FIRST[i % 15]} {LAST[i % 10]} | 1-10000{i + 101:05d}" for i in range(n)]


def bundle(out: Path, land_owner=TRUST, fire_valid="31/03/2027", inst=INST, trust=TRUST, addr=ADDR,
           faculty=None, built="6,000", noc_no="DFS/NOC/2026/0417"):
    out.mkdir(parents=True, exist_ok=True)
    faculty = staff() if faculty is None else faculty
    land_owner = trust if land_owner == TRUST else land_owner
    write(out / "application_form.pdf", "AICTE Application for Extension of Approval 2026-27", [
        f"Name of Institution: {inst}", f"Name of Society/Trust: {trust}", f"Address: {addr}",
        "Programme: Engineering and Technology", "Number of Courses: 2", "Intake per Year: 120",
        "Duration (years): 4", "Date of Application: 15/09/2026"])
    write(out / "land_document.pdf", "Land Ownership Deed (Registry Copy)", [
        f"Name of Owner: {land_owner}", f"Property Address: {addr}", "Land Area (acres): 3.0",
        f"Registration No: DL-RH-2009-{len(inst) * 977}" if inst != INST else "Registration No: DL-RH-2009-44812"])
    write(out / "land_use_certificate.pdf", "Land Use Certificate", [
        f"Issued to: {land_owner}", "Permitted Use: Educational Institution",
        f"Certificate No: LUC/{'2011' if inst == INST else '2014'}/{len(inst)}8821", "Issued by: Delhi Development Authority"])
    write(out / "building_completion.pdf", "Building Completion Certificate", [
        f"Issued to: {inst}", f"Built-up Area (sq m): {built}", "Date of Issue: 12/06/2012",
        f"Certificate No: MCD/BCC/2012/{len(inst)}733", "Issuing Authority: Municipal Corporation of Delhi"])
    write(out / "fire_noc.pdf", "Fire Safety No Objection Certificate (NOC)", [
        f"Name of Premises: {inst}", f"Address of Premises: {addr}", f"Valid Until: {fire_valid}",
        "Issued by: Delhi Fire Service", f"Certificate No: {noc_no}"],
        qr=f"Certificate No: {noc_no}\nName of Premises: {inst}\nValid Until: {fire_valid}")
    write(out / "faculty_list.pdf", "Faculty List 2026-27", [
        f"Name of Institution: {inst}", f"Total Faculty: {len(faculty)}", *faculty])


def forge_fire_noc(path: Path, new_date="31/03/2027"):
    """What a forger does: cover the expired date with a white box, type a new one, save over the file."""
    pdf = pymupdf.open(path)
    page = pdf[0]
    hit = page.search_for("31/03/2026")[0]
    page.draw_rect(hit, color=(1, 1, 1), fill=(1, 1, 1))
    page.insert_text((hit.x0, hit.y1 - 2), new_date, fontname="tiro", fontsize=11)
    pdf.saveIncr()


def scan(pdf_path: Path, out_path: Path, dpi=150):
    """Turn a PDF into what a scanner produces: a page image with no text layer."""
    src = pymupdf.open(pdf_path)
    pix = src[0].get_pixmap(dpi=dpi)
    if out_path.suffix.lower() in (".jpg", ".jpeg", ".png"):
        pix.save(out_path)
        return
    dst = pymupdf.open()
    page = dst.new_page(width=src[0].rect.width, height=src[0].rect.height)
    page.insert_image(page.rect, pixmap=pix)
    dst.save(out_path)


if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "out")
    shutil.rmtree(root, ignore_errors=True)
    bundle(root / "clean")
    bundle(root / "forged", land_owner="Rajesh Kumar Gupta", fire_valid="31/03/2026")
    forge_fire_noc(root / "forged" / "fire_noc.pdf")
    # the careful forger: edits the PDF, then prints and scans it so no edit marks survive
    bundle(root / "forged_scan", fire_valid="31/03/2026")
    forge_fire_noc(root / "forged_scan" / "fire_noc.pdf")
    scan(root / "forged_scan" / "fire_noc.pdf", root / "forged_scan" / "fire_noc.jpg")
    (root / "forged_scan" / "fire_noc.pdf").unlink()
    # a second college borrowing the first one's faculty and fire certificate number
    bundle(root / "ghost", inst="Ganga College of Engineering", trust="Ganga Vidya Trust",
           addr="Khasra 212, Sonipat Road, Haryana 131001")
    print(f"wrote clean, forged, forged_scan and ghost to {root}")
