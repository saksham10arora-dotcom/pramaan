"""REST API so the AICTE portal can send an application and read the result."""
import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response

from .registry import Registry
from .report import to_pdf
from .validate import analyse

app = FastAPI(title="Pramaan")
registry = Registry(os.environ.get("PRAMAAN_DB", "data/pramaan.db"))


@app.post("/applications")
async def submit(files: list[UploadFile] = File(...)):
    report = analyse({f.filename: await f.read() for f in files}, registry=registry)
    return {"id": registry.record(report), **report.to_dict()}


@app.get("/applications")
def queue():
    return registry.queue()


@app.get("/applications/{app_id}")
def one(app_id: int):
    report = registry.report(app_id)
    if report is None:
        raise HTTPException(404, "no such application")
    return report


@app.get("/applications/{app_id}/report.pdf")
def pdf(app_id: int):
    return Response(to_pdf(one(app_id)), media_type="application/pdf")
