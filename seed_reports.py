#!/usr/bin/env python3
"""Load field_intel_reports.json into the reports table."""

import json
import sys
import psycopg2
from pathlib import Path

DEFAULT_URL = "postgresql://edith_user:edith_password@localhost:5433/edith_db"
JSON_PATH = Path(__file__).parent / "project-edith" / "info" / "field_intel_reports.json"

INSERT_SQL = """
    INSERT INTO reports (report_id, timestamp, operative_name, operative_contact, raw_text, priority)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (report_id) DO NOTHING;
"""


def seed(db_url: str) -> None:
    reports = json.loads(JSON_PATH.read_text())

    conn = psycopg2.connect(db_url)
    try:
        with conn.cursor() as cur:
            for r in reports:
                cur.execute(INSERT_SQL, (
                    r["report_id"],
                    r["timestamp"],
                    r["metadata"]["hero_alias"],
                    r["metadata"]["secure_contact"],
                    r["raw_text"],
                    r["priority"],
                ))
        conn.commit()

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM reports;")
            count = cur.fetchone()[0]

        print(f"Done — {count} reports now in the database ({len(reports)} from JSON).")
    finally:
        conn.close()


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    seed(url)
