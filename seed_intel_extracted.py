#!/usr/bin/env python3
"""Load llm_extractor_results.json into the intel_extracted table."""

import json
import sys
from pathlib import Path

import psycopg2

DEFAULT_URL = "postgresql://edith_user:edith_password@localhost:5433/edith_db"
RESULTS_PATH = Path(__file__).parent / "ReportPipline" / "llm_extractor_results.json"

INSERT_SQL = """
    INSERT INTO intel_extracted (
        report_id, sector, resource, severity, event_type, summary,
        modifier_type, modifier_value, modifier_duration_hours, raw_llm_response
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    );
"""

UPDATE_STATUS = "UPDATE reports SET status = 'COMPLETE' WHERE report_id = %s;"


def seed(db_url: str) -> None:
    data = json.loads(RESULTS_PATH.read_text())
    rows = data["intel_extracted_table"]

    conn = psycopg2.connect(db_url)
    try:
        with conn.cursor() as cur:
            for r in rows:
                cur.execute(INSERT_SQL, (
                    r["report_id"],
                    r["sector"],
                    r["resource"],
                    r["severity"],
                    r["event_type"],
                    r["summary"],
                    r["modifier_type"],
                    r["modifier_value"],
                    r["modifier_duration_hours"],
                    r["raw_llm_response"],
                ))
                cur.execute(UPDATE_STATUS, (r["report_id"],))
        conn.commit()

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM intel_extracted;")
            count = cur.fetchone()[0]

        print(f"Done — {count} rows now in intel_extracted ({len(rows)} inserted).")
        print(f"All {len(rows)} reports updated to status = COMPLETE.")
    finally:
        conn.close()


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    seed(url)
