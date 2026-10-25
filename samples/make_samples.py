"""Write two fictional application bundles: a clean one and one with a forged fire NOC and a land mismatch."""
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
    y = 740
    for line in lines:
        c.drawString(60, y, line)
        y -= 24
    c.save()


def bundle(out: Path, land_owner=TRUST, fire_valid="31/03/2027"):
    out.mkdir(parents=True, exist_ok=True)
    write(out / "application_form.pdf", "AICTE Application for Extension of Approval 2026-27", [
        f"Name of Institution: {INST}", f"Name of Society/Trust: {TRUST}", f"Address: {ADDR}",
        "Total Approved Intake: 300", "Date of Application: 15/09/2026"])
    write(out / "land_document.pdf", "Land Ownership Deed (Registry Copy)", [
        f"Name of Owner: {land_owner}", f"Property Address: {ADDR}", "Land Area (acres): 3.0",
        "Registration No: DL-RH-2009-44812"])
    write(out / "building_completion.pdf", "Building Completion Certificate", [
        f"Issued to: {INST}", "Built-up Area (sq m): 3,200", "Issuing Authority: Municipal Corporation of Delhi"])
    write(out / "fire_noc.pdf", "Fire Safety No Objection Certificate (NOC)", [
        f"Name of Premises: {INST}", f"Address of Premises: {ADDR}", f"Valid Until: {fire_valid}",
        "Issued by: Delhi Fire Service", "Certificate No: DFS/NOC/2026/0417"],
        qr=f"Certificate No: DFS/NOC/2026/0417\nName of Premises: {INST}\nValid Until: {fire_valid}")
    write(out / "faculty_list.pdf", "Faculty List 2026-27", [
        f"Name of Institution: {INST}", "Total Faculty: 16"])


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
    print(f"wrote {root}/clean and {root}/forged")
