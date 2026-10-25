"""Pramaan reviewer screen: upload an application bundle, get a verdict with evidence."""
from pathlib import Path

import pymupdf
import streamlit as st

from pramaan.docs import load
from pramaan.validate import FAIL, PASS, REVIEW, summary, validate

SAMPLES = Path(__file__).parent / "samples" / "out"
ICON = {PASS: "✅", FAIL: "❌", REVIEW: "🟡"}

st.set_page_config(page_title="Pramaan", layout="wide")
st.title("Pramaan")
st.caption("AICTE application validation: checks every document against the norms and against each other, "
           "and flags files that were edited after issue.")

left, right = st.columns([1, 2])
with left:
    uploads = st.file_uploader("Application documents (PDF)", type="pdf", accept_multiple_files=True)
    demo = st.radio("or load a demo bundle", ["none", "clean", "forged"], horizontal=True)

files = {u.name: u.getvalue() for u in uploads or []}
if not files and demo != "none":
    files = {p.name: p.read_bytes() for p in sorted((SAMPLES / demo).glob("*.pdf"))}
if not files:
    st.info("Upload the documents of one application, or pick a demo bundle.")
    st.stop()

findings = validate(files)
verdict = summary(findings)
with left:
    color = "red" if verdict.startswith("REJECT") else "orange" if "HUMAN" in verdict else "green"
    st.markdown(f"## :{color}[{verdict}]")
    counts = {s: sum(x.status == s for x in findings) for s in (PASS, FAIL, REVIEW)}
    a, b, c = st.columns(3)
    a.metric("Passed", counts[PASS]); b.metric("Failed", counts[FAIL]); c.metric("Review", counts[REVIEW])
    st.write("**Documents read**")
    for name in files:
        st.write(f"- {name}")

with right:
    for x in sorted(findings, key=lambda x: [FAIL, REVIEW, PASS].index(x.status)):
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
                             caption="what the reviewer sees, with the covered region outlined")
