"""Read fields from free-form documents with Gemini. The model proposes; the code verifies.

A proposed value is kept only if the sentence the model quotes is really in the document and
contains the value. Everything else is reported as unverified and goes to a human.
Set PRAMAAN_OFFLINE=1 to never call the model.
"""
import json
import os
import re
from pathlib import Path

import requests
from rapidfuzz import fuzz

from .extract import FIELDS, Field

MODELS = ("gemini-2.5-flash", "gemini-flash-lite-latest")  # first that answers wins
URL = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent"


def _key():
    if os.environ.get("PRAMAAN_OFFLINE") == "1":
        return None
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"]
    env = Path.home() / ".config" / "keys.env"
    if env.exists():
        m = re.search(r"^GEMINI_API_KEY=(.+)$", env.read_text(), re.M)
        return m.group(1).strip().strip('"') if m else None
    return None


def available() -> bool:
    return _key() is not None


def gemini(prompt: str) -> str:
    err = None
    for model in MODELS:
        try:
            r = requests.post(URL.format(model), params={"key": _key()}, timeout=30, json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0, "responseMimeType": "application/json"}})
            r.raise_for_status()
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            err = e
    raise err


def prompt_for(text: str) -> str:
    spec = {kind: list(fields) for kind, fields in FIELDS.items()}
    return (
        "You read documents submitted to AICTE for institution approval.\n"
        f"Document types and their fields: {json.dumps(spec)}\n"
        "Return JSON: {\"doc_type\": one of the types or null, \"fields\": {field: {\"value\": str, \"quote\": str}}}.\n"
        "quote is the whole line the value appears on, copied exactly from the document. "
        "Dates as DD/MM/YYYY. Numbers without units. Leave out any field the document does not state.\n\n"
        f"DOCUMENT:\n{text[:12000]}")


MONTHS = "january february march april may june july august september october november december".split()


def _numbers(s: str) -> list[float]:
    return [float(n) for n in re.findall(r"\d+(?:\.\d+)?", s.replace(",", ""))]


def verify(text: str, value: str, quote: str) -> bool:
    """True when quote is really in text and value is really in quote."""
    flat, quote = " ".join(text.split()).lower(), " ".join(quote.split()).lower()
    # words may differ by an OCR slip, numbers may not differ at all
    if not quote or fuzz.partial_ratio(quote, flat) < 95 or not set(_numbers(quote)) <= set(_numbers(flat)):
        return False
    v = value.strip()
    in_quote = set(_numbers(quote))
    date = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", v)
    if date:  # "31/03/2027" is in "31/03/2027" or in "31st March, 2027"
        d, mo, y = (float(x) for x in date.groups())
        month_named = MONTHS[int(mo) - 1][:3] in quote
        return {d, y} <= in_quote and (mo in in_quote or month_named)
    if _numbers(v):
        return set(_numbers(v)) <= in_quote
    return fuzz.partial_ratio(v.lower(), quote) >= 90


def read(text: str, ask=None):
    """Return (doc_type, verified fields, unverified [(field, value, quote)])."""
    ask = ask or gemini
    try:
        data = json.loads(ask(prompt_for(text)))
    except Exception as e:  # network, quota, bad JSON: fall back to a human, never guess
        return None, {}, [("*", "", f"AI reader unavailable: {type(e).__name__}")]
    kind = data.get("doc_type") if data.get("doc_type") in FIELDS else None
    good, bad = {}, []
    for key, item in (data.get("fields") or {}).items():
        if kind and key not in FIELDS[kind]:
            continue
        value, quote = str(item.get("value", "")), str(item.get("quote", ""))
        if verify(text, value, quote):
            good[key] = Field(value, quote, source="ai")
        else:
            bad.append((key, value, quote))
    return kind, good, bad
