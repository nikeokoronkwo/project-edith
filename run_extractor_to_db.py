#!/usr/bin/env python3
"""
Run the LLM extractor against all REDACTED reports in the database,
then write results into the intel_extracted table.

Only processes reports that don't already have an intel_extracted row.
"""

import json
import sys
from pathlib import Path

import psycopg2
import psycopg2.extras

sys.path.insert(0, str(Path(__file__).parent / "ReportPipline"))
from llm_extractor import extract, format_for_db

DEFAULT_URL = "postgresql://edith_user:edith_password@localhost:5433/edith_db"

INSERT_INTEL = """
    INSERT INTO intel_extracted (
        report_id, sector, resource, severity, event_type, summary,
        modifier_type, modifier_value, modifier_duration_hours, raw_llm_response
    ) VALUES (
        %(report_id)s, %(sector)s, %(resource)s, %(severity)s, %(event_type)s, %(summary)s,
        %(modifier_type)s, %(modifier_value)s, %(modifier_duration_hours)s, %(raw_llm_response)s
    );
"""

UPDATE_STATUS = """
    UPDATE reports SET status = 'COMPLETE' WHERE report_id = %s;
"""


def run(db_url: str) -> None:
    conn = psycopg2.connect(db_url)

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT r.report_id::text, r.redacted_text
              FROM reports r
             WHERE r.status = 'REDACTED'
               AND NOT EXISTS (
                   SELECT 1 FROM intel_extracted ie WHERE ie.report_id = r.report_id
               );
        """)
        rows = cur.fetchall()

    if not rows:
        print("No REDACTED reports without intel — nothing to do.")
        conn.close()
        return

    print(f"Found {len(rows)} reports to process.\n")

    success = 0
    errors = []

    for i, r in enumerate(rows):
        rid = r["report_id"]
        text = r["redacted_text"] or ""

        try:
            extraction_result, modifier, raw_llm = extract(text, rid)
            row = format_for_db(rid, extraction_result, modifier, raw_llm)

            if isinstance(row["raw_llm_response"], dict):
                row["raw_llm_response"] = json.dumps(row["raw_llm_response"])

            with conn.cursor() as cur:
                cur.execute(INSERT_INTEL, row)
                cur.execute(UPDATE_STATUS, (rid,))
            conn.commit()

            success += 1
        except Exception as e:
            conn.rollback()
            errors.append({"report_id": rid, "error": str(e)})

        if (i + 1) % 10 == 0 or (i + 1) == len(rows):
            print(f"  Processed {i + 1}/{len(rows)} ({success} ok, {len(errors)} errors)")

    print("\n" + "=" * 55)
    print(f"Intel rows inserted: {success}")
    print(f"Reports updated to COMPLETE: {success}")
    print(f"Errors: {len(errors)}")
    if errors:
        print(f"First error: {errors[0]}")
    print("=" * 55)

    conn.close()


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    run(url)
