"""
api.py — FastAPI backend for the Avengers Intel Pipeline.

Single endpoint:
    POST /reports  — accepts a hero's structured report, runs M1 + M2, saves to DB.

Run with:
    export DATABASE_URL="postgresql://user:password@localhost:5432/yourdb"
    uvicorn api:app --reload
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from db import get_connection, insert_intel_extracted, insert_redaction_audit, insert_report
from llm_extractor import VALID_SECTORS
from pipeline import process_report

app = FastAPI(title="Avengers Intel API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Text synthesis ──────────────────────────────────────────────────────────

def _build_raw_text(hero_alias: str, secure_contact: Optional[str], sector: str, event_description: str) -> str:
    """
    Combine structured fields into a natural-language report body.
    The LLM (Module 2) will extract resource, event_type, and severity from this text.
    If secure_contact is provided it appears in the body so Module 1 can redact it.
    """
    if secure_contact:
        return (
            f"This is {hero_alias}, reporting from {sector}. {event_description} "
            f"Call me back at {secure_contact}."
        )
    return f"This is {hero_alias}, reporting from {sector}. {event_description}"


# ── Pydantic models ─────────────────────────────────────────────────────────

class ReportRequest(BaseModel):
    hero_alias:        str
    sector:            str
    event_description: str
    secure_contact:    Optional[str] = None
    priority:          str = "Routine"

    @field_validator("sector")
    @classmethod
    def validate_sector(cls, v):
        if v not in VALID_SECTORS:
            raise ValueError(f"sector must be one of: {sorted(VALID_SECTORS)}")
        return v


class ReportResponse(BaseModel):
    report_id:     str
    status:        str
    redacted_text: str
    intel:         dict
    modifier:      dict
    audit_count:   int


# ── Endpoint ────────────────────────────────────────────────────────────────

@app.post("/reports", response_model=ReportResponse)
def submit_report(body: ReportRequest):
    """
    Accept a hero's report, run the full pipeline, persist to DB, return results.

    Flow:
      1. Synthesize raw_text from structured fields
      2. pipeline.process_report() — M1 tokenization + M2 LLM extraction
      3. INSERT into reports, intel_extracted, redaction_audit
      4. Return processed result
    """
    report_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    raw_text = _build_raw_text(
        body.hero_alias, body.secure_contact,
        body.sector, body.event_description,
    )

    report_dict = {
        "report_id": report_id,
        "timestamp": timestamp,
        "raw_text":  raw_text,
        "priority":  body.priority,
        "metadata": {
            "hero_alias":     body.hero_alias,
            "secure_contact": body.secure_contact or "",
        },
    }

    try:
        result = process_report(report_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")

    try:
        conn = get_connection()
        insert_report(conn, result["report_row"])
        insert_intel_extracted(conn, result["intel_row"])
        insert_redaction_audit(conn, result["audit_rows"])
        conn.commit()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    return ReportResponse(
        report_id     = result["report_row"]["report_id"],
        status        = result["report_row"]["status"],
        redacted_text = result["report_row"]["redacted_text"],
        intel         = result["extraction_result"],
        modifier      = result["modifier"],
        audit_count   = len(result["audit_rows"]),
    )
