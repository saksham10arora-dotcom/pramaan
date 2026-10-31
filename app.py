"""Pramaan reviewer screen: upload an application bundle, get a verdict with evidence."""
from pathlib import Path

import pymupdf
import streamlit as st

from pramaan.docs import load
from pramaan.registry import Registry
from pramaan.report import to_pdf
from pramaan.validate import FAIL, PASS, REVIEW, analyse

ROOT = Path(__file__).parent
SAMPLES = ROOT / "samples" / "out"
ICON = {PASS: "✅", FAIL: "❌", REVIEW: "🟡"}
ORDER = [FAIL, REVIEW, PASS]


@st.cache_resource
def registry():
    return Registry(ROOT / "data" / "pramaan.db")


def demo_files(name):
    return {p.name: p.read_bytes() for p in sorted((SAMPLES / name).iterdir()) if p.is_file()}


st.set_page_config(page_title="Pramaan", layout="wide")
st.title("Pramaan")
st.caption("AICTE application validation: every document checked against the handbook norms, against each other, "
           "and against every other application.")
check, queue = st.tabs(["Check an application", "Reviewer queue"])

with check:
    left, right = st.columns([1, 2])
    with left:
        uploads = st.file_uploader("Application documents (PDF or photo)",
                                   type=["pdf", "jpg", "jpeg", "png", "webp", "tif", "tiff"], accept_multiple_files=True)
        demo = st.radio("or load a demo application", ["none", "clean", "forged", "forged_scan", "ghost"], horizontal=True)

    files = {u.name: u.getvalue() for u in uploads or []}
    if not files and demo != "none":
        if demo == "ghost":  # the ghost college copies the clean one, so that one must be on record first
            registry().record(analyse(demo_files("clean"), registry=registry()))
        files = demo_files(demo)
    if not files:
        st.info("Upload the documents of one application, or pick a demo.")
    else:
        report = analyse(files, registry=registry())
        registry().record(report)
        findings, verdict = report.findings, report.verdict
        with left:
            color = "red" if verdict.startswith("REJECT") else "orange" if "HUMAN" in verdict else "green"
            st.markdown(f"## :{color}[{verdict}]")
            if report.institution:
                st.write(report.institution)
            a, b, c = st.columns(3)
            a.metric("Passed", report.count(PASS)); b.metric("Failed", report.count(FAIL)); c.metric("Review", report.count(REVIEW))
            st.download_button("Download report (PDF)", to_pdf(report.to_dict()), "pramaan_report.pdf", "application/pdf")
            st.write("**Documents read**")
            for d in report.documents:
                st.write(f"- {d['kind'].replace('_', ' ')}: {d['name']}")
        with right:
            for x in sorted(findings, key=lambda x: ORDER.index(x.status)):
                with st.expander(f"{ICON[x.status]} {x.rule}: {x.reason}", expanded=x.status != PASS):
                    for doc, line in x.evidence:
                        st.markdown(f"`{doc}`  \n> {line}" if line else f"`{doc}`")
                    if x.rule.startswith("tampering") and "white box" in x.reason:
                        name = x.rule.split(": ", 1)[1]
                        doc = load(files[name], name)
                        pdf = pymupdf.open(stream=doc.raw, filetype="pdf")
                        for pno, box in doc.whiteouts:
                            page = pdf[pno]
                            page.draw_rect(pymupdf.Rect(box) + (-4, -4, 4, 4), color=(0.9, 0.1, 0.1), width=2)
                            clip = pymupdf.Rect(0, max(0, box[1] - 120), page.rect.width, box[3] + 80)
                            st.image(page.get_pixmap(dpi=110, clip=clip).tobytes("png"),
                                     caption="the page as submitted, with the covered region outlined")

with queue:
    rows = registry().queue()
    st.subheader(f"{len(rows)} applications, riskiest first")
    if rows:
        st.dataframe([{"Institution": r["institution"], "Verdict": r["verdict"], "Failed": r["failed"],
                       "Review": r["review"], "Passed": r["passed"], "Checked": r["created"]} for r in rows],
                     use_container_width=True, hide_index=True)
