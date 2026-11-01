"""REST API so the AICTE portal can send an application and read the result."""
import os
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response

from . import docs, llm
from .registry import Registry
from .report import highlights, to_pdf
from .validate import analyse

DEMOS = Path(__file__).parent.parent / "demo_bundles"
DEFAULT_DB = "/tmp/pramaan.db" if os.environ.get("VERCEL") else "data/pramaan.db"

app = FastAPI(title="Pramaan")
registry = Registry(os.environ.get("PRAMAAN_DB", DEFAULT_DB))


def check(files: dict) -> dict:
    report = analyse(files, registry=registry)
    return {"id": registry.record(report), **report.to_dict(), "highlights": highlights(files, report.findings)}


def demo_files(name: str) -> dict:
    return {p.name: p.read_bytes() for p in sorted((DEMOS / name).iterdir()) if p.is_file()}


@app.get("/api/status")
def status():
    return {"ocr": docs.available(), "ai_reader": llm.available()}


@app.post("/api/applications")
async def submit(files: list[UploadFile] = File(...)):
    return check({f.filename: await f.read() for f in files})


@app.post("/api/demo/{name}")
def demo(name: str):
    if name not in ("clean", "forged", "forged_scan", "ghost"):
        raise HTTPException(404, "no such demo")
    if name == "ghost":  # the ghost college copies the clean one, so that one must be on record first
        check(demo_files("clean"))
    return check(demo_files(name))


@app.get("/api/applications")
def queue():
    return registry.queue()


@app.get("/api/applications/{app_id}")
def one(app_id: int):
    report = registry.report(app_id)
    if report is None:
        raise HTTPException(404, "no such application")
    return report


@app.get("/api/applications/{app_id}/report.pdf")
def pdf(app_id: int):
    return Response(to_pdf(one(app_id)), media_type="application/pdf")
