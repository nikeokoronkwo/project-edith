"""
db.py — PostgreSQL connection and INSERT helpers.

Reads DATABASE_URL from the environment:
    export DATABASE_URL="postgresql://user:password@localhost:5432/yourdb"

Public API:
    get_connection() -> psycopg2 connection
    insert_report(conn, row)
    insert_intel_extracted(conn, row)
    insert_redaction_audit(conn, rows)
"""

import json
import os

import psycopg2


def get_connection():
    """Open and return a psycopg2 connection from DATABASE_URL env var."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    return psycopg2.connect(url)


def insert_report(conn, row: dict) -> None:
    """
    INSERT a row into the `reports` table.
    ON CONFLICT DO NOTHING — safe to call multiple times for the same report_id.
    """
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
    """
    INSERT a row into the `intel_extracted` table.
    raw_llm_response is stored as JSONB — serialised to string if needed.
    """
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
    """
    INSERT all redaction audit entries for a report.
    No-ops cleanly if rows is empty (clean report with no PII).
    """
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
