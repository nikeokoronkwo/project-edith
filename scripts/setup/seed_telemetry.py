#!/usr/bin/env python3
"""
Insert historical_avengers_data.csv into the telemetry_readings table.

The CSV already contains all 25 series (5 sectors × 5 resources × 2160 ticks).
Run scripts/dev/generate_telemetry.py first if the file is missing or outdated.
"""

import csv
import sys
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

DEFAULT_URL = "postgresql://edith_user:edith_password@localhost:5433/edith_db"
CSV_PATH = Path(__file__).parent.parent.parent / "plan" / "info" / "historical_avengers_data.csv"

INSERT_SQL = """
    INSERT INTO telemetry_readings
           (timestamp, sector_id, resource_type, stock_level, usage_rate_hourly, snap_event_detected)
    VALUES %s
"""


def seed(db_url: str) -> None:
    if not CSV_PATH.exists():
        print(f"CSV not found: {CSV_PATH}")
        print("Run:  python scripts/dev/generate_telemetry.py")
        raise SystemExit(1)

    rows: list[tuple] = []
    with open(CSV_PATH, newline="") as f:
        for row in csv.DictReader(f):
            rows.append((
                row["timestamp"],
                row["sector_id"],
                row["resource_type"],
                float(row["stock_level"]),
                float(row["usage_rate_hourly"]),
                row["snap_event_detected"] == "True",
            ))

    print(f"Loaded {len(rows):,} rows from {CSV_PATH.name}")

    conn = psycopg2.connect(db_url)
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM telemetry_readings;")
            execute_values(cur, INSERT_SQL, rows, page_size=5000)
        conn.commit()

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM telemetry_readings;")
            count = cur.fetchone()[0]
            cur.execute("""
                SELECT sector_id, COUNT(DISTINCT resource_type)
                  FROM telemetry_readings
                 GROUP BY sector_id
                 ORDER BY sector_id;
            """)
            breakdown = cur.fetchall()

        print(f"Done — {count:,} rows in telemetry_readings.")
        print("\nResources per sector:")
        for sector, n in breakdown:
            print(f"  {sector}: {n}")
    finally:
        conn.close()


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    seed(url)
