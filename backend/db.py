"""
db.py — PostgreSQL connection, INSERT helpers, and query functions.

Reads DATABASE_URL from the environment:
    export DATABASE_URL="postgresql://user:password@localhost:5432/yourdb"
"""

import json
import os

import psycopg2
import psycopg2.extras


_DEFAULT_URL = "postgresql://edith_user:edith_password@localhost:5433/edith_db"


def get_connection():
    """Open and return a psycopg2 connection from DATABASE_URL env var."""
    url = os.environ.get("DATABASE_URL", _DEFAULT_URL)
    return psycopg2.connect(url)


# ── INSERT helpers ────────────────────────────────────────────────────────────


def insert_report(conn, row: dict) -> None:
    sql = """
        INSERT INTO reports (
            report_id, timestamp, operative_name, operative_contact,
            raw_text, redacted_text, priority, status
        ) VALUES (
            %(report_id)s, %(timestamp)s, %(operative_name)s, %(operative_contact)s,
            %(raw_text)s, %(redacted_text)s, %(priority)s, %(status)s
        )
        ON CONFLICT (report_id) DO NOTHING;
    """
    with conn.cursor() as cur:
        cur.execute(sql, row)


def insert_intel_extracted(conn, row: dict) -> None:
    raw = row.get("raw_llm_response")
    if isinstance(raw, dict):
        raw = json.dumps(raw)

    sql = """
        INSERT INTO intel_extracted (
            report_id, sector, resource, severity, event_type, summary,
            modifier_type, modifier_value, modifier_duration_hours, raw_llm_response
        ) VALUES (
            %(report_id)s, %(sector)s, %(resource)s, %(severity)s, %(event_type)s, %(summary)s,
            %(modifier_type)s, %(modifier_value)s, %(modifier_duration_hours)s, %(raw_llm_response)s
        );
    """
    params = {**row, "raw_llm_response": raw}
    with conn.cursor() as cur:
        cur.execute(sql, params)


def insert_redaction_audit(conn, rows: list[dict]) -> None:
    if not rows:
        return
    sql = """
        INSERT INTO redaction_audit (
            report_id, original_fragment, replacement, entity_type, detection_layer
        ) VALUES (
            %(report_id)s, %(original_fragment)s, %(replacement)s,
            %(entity_type)s, %(detection_layer)s
        );
    """
    with conn.cursor() as cur:
        cur.executemany(sql, rows)


def insert_telemetry_reading(conn, row: dict) -> int:
    sql = """
        INSERT INTO telemetry_readings (
            timestamp, sector_id, resource_type,
            stock_level, usage_rate_hourly, snap_event_detected
        ) VALUES (
            %(timestamp)s, %(sector_id)s, %(resource_type)s,
            %(stock_level)s, %(usage_rate_hourly)s, %(snap_event_detected)s
        )
        RETURNING id;
    """
    params = {**row, "snap_event_detected": row.get("snap_event_detected", False)}
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()[0]


# ── READ helpers ──────────────────────────────────────────────────────────────


def _dict_rows(conn, sql: str, params: dict | tuple = ()) -> list[dict]:
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]


def _dict_row(conn, sql: str, params: dict | tuple = ()) -> dict | None:
    rows = _dict_rows(conn, sql, params)
    return rows[0] if rows else None


def get_reports(conn, limit: int = 50, offset: int = 0) -> tuple[list[dict], int]:
    """Return (reports_list, total_count) joining reports + intel_extracted."""
    count_sql = "SELECT COUNT(*) FROM reports;"
    with conn.cursor() as cur:
        cur.execute(count_sql)
        total = cur.fetchone()[0]

    sql = """
        SELECT r.report_id, r.timestamp, r.operative_name, r.redacted_text,
               r.priority, r.status,
               ie.sector, ie.resource, ie.severity, ie.event_type, ie.summary,
               ie.modifier_type, ie.modifier_value, ie.modifier_duration_hours
          FROM reports r
          LEFT JOIN intel_extracted ie ON r.report_id = ie.report_id
         ORDER BY r.timestamp DESC
         LIMIT %s OFFSET %s;
    """
    rows = _dict_rows(conn, sql, (limit, offset))
    return rows, total


def get_report_by_id(conn, report_id: str) -> dict | None:
    sql = """
        SELECT r.report_id, r.timestamp, r.operative_name, r.redacted_text,
               r.priority, r.status,
               ie.sector, ie.resource, ie.severity, ie.event_type, ie.summary,
               ie.modifier_type, ie.modifier_value, ie.modifier_duration_hours
          FROM reports r
          LEFT JOIN intel_extracted ie ON r.report_id = ie.report_id
         WHERE r.report_id = %s;
    """
    return _dict_row(conn, sql, (report_id,))


def _severity_to_priority(severity: int | None) -> int:
    """Map severity (1-10) to frontend priority (1=CRITICAL .. 4=LOW)."""
    if severity is None:
        return 4
    if severity >= 9:
        return 1
    if severity >= 7:
        return 2
    if severity >= 4:
        return 3
    return 4


def get_events(conn, priority: int | None = None, limit: int = 50) -> list[dict]:
    """Derive events from intel_extracted joined with reports."""
    sql = """
        SELECT ie.id, ie.summary, ie.severity, ie.sector, ie.resource,
               ie.event_type, r.timestamp
          FROM intel_extracted ie
          JOIN reports r ON ie.report_id = r.report_id
         ORDER BY r.timestamp DESC
         LIMIT %s;
    """
    rows = _dict_rows(conn, sql, (limit,))

    events = []
    for row in rows:
        p = _severity_to_priority(row["severity"])
        if priority is not None and p != priority:
            continue
        events.append({
            "id": str(row["id"]),
            "event": row["summary"] or row["event_type"],
            "priority": p,
            "started": row["timestamp"].isoformat() if row["timestamp"] else "",
            "timestamp": int(row["timestamp"].timestamp() * 1000) if row["timestamp"] else 0,
            "description": row["summary"],
            "affectedResources": [row["resource"]] if row["resource"] else [],
            "affectedLocations": [row["sector"]] if row["sector"] else [],
        })
    return events


def get_event_by_id(conn, event_id: str) -> dict | None:
    sql = """
        SELECT ie.id, ie.summary, ie.severity, ie.sector, ie.resource,
               ie.event_type, r.timestamp
          FROM intel_extracted ie
          JOIN reports r ON ie.report_id = r.report_id
         WHERE ie.id = %s;
    """
    row = _dict_row(conn, sql, (int(event_id),))
    if not row:
        return None
    p = _severity_to_priority(row["severity"])
    return {
        "id": str(row["id"]),
        "event": row["summary"] or row["event_type"],
        "priority": p,
        "started": row["timestamp"].isoformat() if row["timestamp"] else "",
        "timestamp": int(row["timestamp"].timestamp() * 1000) if row["timestamp"] else 0,
        "description": row["summary"],
        "affectedResources": [row["resource"]] if row["resource"] else [],
        "affectedLocations": [row["sector"]] if row["sector"] else [],
    }


def get_analytics(
    conn, resource: str | None = None, sector: str | None = None, limit: int = 200
) -> list[dict]:
    """Return telemetry readings as AnalyticsData-shaped dicts."""
    conditions = []
    params: list = []
    if resource:
        conditions.append("resource_type = %s")
        params.append(resource)
    if sector:
        conditions.append("sector_id = %s")
        params.append(sector)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    sql = f"""
        SELECT timestamp, resource_type, sector_id, stock_level
          FROM telemetry_readings
         {where}
         ORDER BY timestamp DESC
         LIMIT %s;
    """
    params.append(limit)
    rows = _dict_rows(conn, sql, tuple(params))
    return [
        {
            "timestamp": int(r["timestamp"].timestamp() * 1000),
            "resource": r["resource_type"],
            "sector": r["sector_id"],
            "value": r["stock_level"],
        }
        for r in rows
    ]


def get_sector_analytics(conn, sector: str) -> dict:
    """Aggregated analytics for one sector — all resources with recent trend."""
    sql = """
        SELECT resource_type, stock_level, timestamp
          FROM telemetry_readings
         WHERE sector_id = %s
         ORDER BY resource_type, timestamp DESC;
    """
    rows = _dict_rows(conn, sql, (sector,))

    resources_map: dict[str, dict] = {}
    for r in rows:
        name = r["resource_type"]
        if name not in resources_map:
            resources_map[name] = {"name": name, "totalValue": 0, "recentTrend": [], "_count": 0}
        entry = resources_map[name]
        entry["_count"] += 1
        entry["totalValue"] += r["stock_level"]
        if len(entry["recentTrend"]) < 50:
            entry["recentTrend"].append({
                "timestamp": int(r["timestamp"].timestamp() * 1000),
                "value": r["stock_level"],
            })

    resources = []
    for entry in resources_map.values():
        count = entry.pop("_count")
        entry["totalValue"] = round(entry["totalValue"] / count, 2) if count else 0
        entry["recentTrend"].reverse()
        resources.append(entry)

    return {"sector": sector, "resources": resources}


def get_resource_analytics(conn, resource: str) -> dict:
    """Aggregated analytics for one resource — broken down by sector."""
    sql = """
        SELECT sector_id, stock_level, timestamp
          FROM telemetry_readings
         WHERE resource_type = %s
         ORDER BY sector_id, timestamp DESC;
    """
    rows = _dict_rows(conn, sql, (resource,))

    by_sector: dict[str, dict] = {}
    all_trend: list[dict] = []
    total = 0.0
    count = 0

    for r in rows:
        sector = r["sector_id"]
        if sector not in by_sector:
            by_sector[sector] = {"country": sector, "value": 0, "_count": 0}
        by_sector[sector]["value"] += r["stock_level"]
        by_sector[sector]["_count"] += 1
        total += r["stock_level"]
        count += 1
        if len(all_trend) < 200:
            all_trend.append({
                "timestamp": int(r["timestamp"].timestamp() * 1000),
                "value": r["stock_level"],
            })

    by_country = []
    for entry in by_sector.values():
        c = entry.pop("_count")
        entry["value"] = round(entry["value"] / c, 2) if c else 0
        by_country.append(entry)

    all_trend.reverse()

    return {
        "resource": resource,
        "byCountry": by_country,
        "totalValue": round(total / count, 2) if count else 0,
        "trend": all_trend,
    }


def get_telemetry_for_forecast(
    conn, resource: str, sector: str | None = None, limit: int = 100
) -> list[dict]:
    """Recent telemetry readings for computing a forecast."""
    conditions = ["resource_type = %s"]
    params: list = [resource]
    if sector:
        conditions.append("sector_id = %s")
        params.append(sector)

    where = "WHERE " + " AND ".join(conditions)
    sql = f"""
        SELECT timestamp, stock_level
          FROM telemetry_readings
         {where}
         ORDER BY timestamp DESC
         LIMIT %s;
    """
    params.append(limit)
    rows = _dict_rows(conn, sql, tuple(params))
    rows.reverse()
    return rows
