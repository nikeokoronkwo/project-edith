"""
api.py — FastAPI backend for the Avengers Intel Pipeline.

Endpoints under /api:
    POST /api/reports          — submit a new report (accepts frontend & direct shapes)
    GET  /api/reports          — list processed reports
    GET  /api/reports/{id}     — single report
    GET  /api/events           — list events (derived from intel_extracted)
    GET  /api/events/{id}      — single event
    GET  /api/analytics        — telemetry time-series data
    GET  /api/analytics/sector/{sector}     — sector breakdown
    GET  /api/analytics/resource/{resource} — resource breakdown
    GET  /api/analytics/forecast            — simple linear forecast

Run with:
    export DATABASE_URL="postgresql://edith_user:edith_password@localhost:5433/edith_db"
    uvicorn api:app --host 0.0.0.0 --port 8080
"""

import base64
import json
import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

import pika
from fastapi import FastAPI, HTTPException, Query, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

log = logging.getLogger(__name__)

from db import (
    get_connection,
    insert_report,
    insert_intel_extracted,
    insert_redaction_audit,
    get_reports,
    get_report_by_id,
    get_events,
    get_event_by_id,
    get_analytics,
    get_sector_analytics,
    get_resource_analytics,
    get_telemetry_for_forecast,
)
from llm_extractor import VALID_SECTORS
from pipeline import process_report
from publisher import start_publisher


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop, threads = start_publisher()
    log.info("[lifespan] Background publisher started (%d threads)", len(threads))
    yield
    stop.set()
    for t in threads:
        t.join(timeout=5)
    log.info("[lifespan] Background publisher stopped")


app = FastAPI(title="Avengers Intel API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api")

RABBITMQ_EXCHANGE = "shield_events"


def _publish_to_rabbitmq(message: dict) -> None:
    """Publish a JSON message to the shield_events fanout exchange (fire-and-forget)."""
    rabbitmq_url = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672")
    try:
        params = pika.URLParameters(rabbitmq_url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type="fanout", durable=True)
        channel.basic_publish(
            exchange=RABBITMQ_EXCHANGE,
            routing_key="",
            body=json.dumps(message),
            properties=pika.BasicProperties(expiration="300000"),
        )
        connection.close()
    except Exception as exc:
        log.warning("RabbitMQ publish failed (non-fatal): %s", exc)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _decode_jwt_payload(token: str) -> dict:
    """Base64-decode a JWT payload without verification (we trust the Nuxt server)."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return {}
        payload = parts[1]
        payload += "=" * (4 - len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))
    except Exception:
        return {}


def _severity_to_label(severity: int | None) -> str:
    if severity is None:
        return "normal"
    if severity >= 9:
        return "critical"
    if severity >= 7:
        return "warning"
    if severity >= 4:
        return "elevated"
    return "normal"


def _format_report_for_frontend(row: dict) -> dict:
    """Shape a joined reports+intel_extracted DB row into the frontend Report type."""
    ts = row.get("timestamp")
    return {
        "heroAlias": row.get("operative_name", "Unknown"),
        "description": row.get("redacted_text") or row.get("raw_text", ""),
        "affectedResources": [row["resource"]] if row.get("resource") else [],
        "affectedLocations": [row["sector"]] if row.get("sector") else [],
        "relatedReportIds": [],
        "timeStarted": ts.isoformat() if ts else "",
        "metadata": row.get("report_id", ""),
        "severity": _severity_to_label(row.get("severity")),
        "reportId": str(row.get("report_id", "")),
        "status": row.get("status", ""),
        "sector": row.get("sector", ""),
        "resource": row.get("resource", ""),
        "eventType": row.get("event_type", ""),
        "summary": row.get("summary", ""),
    }


def _build_raw_text(
    hero_alias: str, secure_contact: str | None, sector: str, description: str
) -> str:
    if secure_contact:
        return (
            f"This is {hero_alias}, reporting from {sector}. {description} "
            f"Call me back at {secure_contact}."
        )
    return f"This is {hero_alias}, reporting from {sector}. {description}"


# ── POST /api/reports ────────────────────────────────────────────────────────


class FrontendReportRequest(BaseModel):
    """Shape sent by the Nuxt server proxy (new.post.ts)."""
    description: str
    affectedResources: list[str] = []
    affectedLocations: list[str] = []
    relatedReportIds: list[str] = []
    timeStarted: Optional[str] = None
    metadata: str = ""
    hero_alias: Optional[str] = None
    sector: Optional[str] = None
    event_description: Optional[str] = None
    secure_contact: Optional[str] = None
    priority: str = "Routine"


@router.post("/reports")
def submit_report(body: FrontendReportRequest):
    is_direct = body.hero_alias is not None and body.sector is not None

    if is_direct:
        hero_alias = body.hero_alias
        sector = body.sector
        description = body.event_description or body.description
        secure_contact = body.secure_contact
    else:
        jwt_data = _decode_jwt_payload(body.metadata) if body.metadata else {}
        hero_alias = jwt_data.get("heroAlias", "Unknown Operative")
        sector = body.affectedLocations[0] if body.affectedLocations else "Avengers Compound"
        description = body.description
        secure_contact = None

    if sector not in VALID_SECTORS:
        closest = min(VALID_SECTORS, key=lambda s: _fuzzy_score(s, sector))
        sector = closest

    report_id = str(uuid.uuid4())
    timestamp = body.timeStarted or datetime.now(timezone.utc).isoformat()

    raw_text = _build_raw_text(hero_alias, secure_contact, sector, description)

    report_dict = {
        "report_id": report_id,
        "timestamp": timestamp,
        "raw_text": raw_text,
        "priority": body.priority,
        "metadata": {
            "hero_alias": hero_alias,
            "secure_contact": secure_contact or "",
        },
    }

    try:
        result = process_report(report_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")

    try:
        conn = get_connection()
        insert_report(conn, result["report_row"])
        insert_redaction_audit(conn, result["audit_rows"])
        insert_intel_extracted(conn, result["intel_row"])
        conn.commit()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    ext = result.get("extraction_result", {})
    mod = result.get("modifier", {})

    _publish_to_rabbitmq({
        "id": report_id,
        "heroAlias": hero_alias,
        "description": description,
        "timeStarted": timestamp,
        "affectedLocations": [ext.get("sector", sector)],
        "severity": _severity_to_label(ext.get("severity")),
    })

    _publish_to_rabbitmq({
        "id": str(uuid.uuid4()),
        "event": ext.get("summary", description),
        "priority": 2,
        "started": timestamp,
        "timestamp": int(datetime.fromisoformat(timestamp).timestamp() * 1000)
        if timestamp else int(datetime.now(timezone.utc).timestamp() * 1000),
    })

    return {
        "success": True,
        "reportId": report_id,
        "message": "Report processed successfully",
    }


def _fuzzy_score(a: str, b: str) -> int:
    """Simple char-overlap distance for sector name matching."""
    a_lower, b_lower = a.lower(), b.lower()
    if a_lower == b_lower:
        return 0
    if a_lower in b_lower or b_lower in a_lower:
        return 1
    return sum(1 for c in b_lower if c not in a_lower)


# ── GET /api/reports ─────────────────────────────────────────────────────────


@router.get("/reports")
def list_reports(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)):
    conn = get_connection()
    try:
        rows, total = get_reports(conn, limit, offset)
    finally:
        conn.close()
    return {
        "reports": [_format_report_for_frontend(r) for r in rows],
        "total": total,
    }


@router.get("/reports/{report_id}")
def read_report(report_id: str):
    conn = get_connection()
    try:
        row = get_report_by_id(conn, report_id)
    finally:
        conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Report not found")
    return _format_report_for_frontend(row)


# ── GET /api/events ──────────────────────────────────────────────────────────


@router.get("/events")
def list_events(
    priority: Optional[int] = Query(None, ge=1, le=4),
    limit: int = Query(50, ge=1, le=500),
):
    conn = get_connection()
    try:
        events = get_events(conn, priority, limit)
    finally:
        conn.close()
    return {"events": events}


@router.get("/events/{event_id}")
def read_event(event_id: str):
    conn = get_connection()
    try:
        event = get_event_by_id(conn, event_id)
    finally:
        conn.close()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


# ── GET /api/analytics ───────────────────────────────────────────────────────


@router.get("/analytics")
def read_analytics(
    resource: Optional[str] = None,
    sector: Optional[str] = None,
    limit: int = Query(200, ge=1, le=5000),
):
    conn = get_connection()
    try:
        data = get_analytics(conn, resource, sector, limit)
    finally:
        conn.close()
    return {"data": data}


@router.get("/analytics/sector/{sector}")
def read_sector_analytics(sector: str):
    conn = get_connection()
    try:
        result = get_sector_analytics(conn, sector)
    finally:
        conn.close()
    return result


@router.get("/analytics/resource/{resource}")
def read_resource_analytics(resource: str):
    conn = get_connection()
    try:
        result = get_resource_analytics(conn, resource)
    finally:
        conn.close()
    return result


@router.get("/analytics/forecast")
def read_forecast(
    resource: str = Query(...),
    sector: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
):
    conn = get_connection()
    try:
        readings = get_telemetry_for_forecast(conn, resource, sector, limit=100)
    finally:
        conn.close()

    if not readings:
        raise HTTPException(status_code=404, detail="No data for forecast")

    values = [r["stock_level"] for r in readings]
    timestamps = [r["timestamp"].timestamp() for r in readings]

    current = values[-1]
    n = len(values)

    if n >= 2:
        x_mean = sum(range(n)) / n
        y_mean = sum(values) / n
        num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        den = sum((i - x_mean) ** 2 for i in range(n))
        slope = num / den if den else 0
    else:
        slope = 0

    if slope < -0.5:
        trend = "decreasing"
        impact = "high" if abs(slope) > 2 else "medium"
    elif slope > 0.5:
        trend = "increasing"
        impact = "low"
    else:
        trend = "stable"
        impact = "low"

    last_ts = timestamps[-1]
    hours_per_step = 1
    if n >= 2:
        hours_per_step = max(1, (timestamps[-1] - timestamps[0]) / (n - 1) / 3600)

    forecast_points = []
    for step in range(1, days * 24 + 1, max(1, int(hours_per_step))):
        predicted = current + slope * step
        predicted = max(0, predicted)
        forecast_points.append({
            "timestamp": int((last_ts + step * 3600) * 1000),
            "predicted": round(predicted, 2),
            "lower": round(max(0, predicted * 0.85), 2),
            "upper": round(predicted * 1.15, 2),
        })
        if len(forecast_points) >= 200:
            break

    return {
        "resource": resource,
        "sector": sector,
        "currentValue": round(current, 2),
        "forecast": forecast_points,
        "description": f"{resource} stock is {trend} at {round(current, 1)} units",
        "trend": trend,
        "impact": impact,
    }


# ── Mount router & run ───────────────────────────────────────────────────────

app.include_router(router)
