#!/usr/bin/env python3
"""
skew_timestamps.py — Shift telemetry_readings timestamps so the latest
data point lands on today's date/time.

Computes:  offset = NOW() - MAX(timestamp)
Applies:   UPDATE telemetry_readings SET timestamp = timestamp + offset

Usage:
    python skew_timestamps.py                  # live run
    python skew_timestamps.py --dry-run        # print offset, touch nothing
    python skew_timestamps.py --db-url <url>   # override DATABASE_URL
"""

import argparse
import os
import sys

import psycopg2
import psycopg2.extras

DEFAULT_URL = "postgresql://edith_user:edith_password@localhost:5433/edith_db"


def main() -> None:
    parser = argparse.ArgumentParser(description="Shift telemetry timestamps to today.")
    parser.add_argument("--db-url", default=os.environ.get("DATABASE_URL", DEFAULT_URL))
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the computed offset without modifying anything.")
    args = parser.parse_args()

    conn = psycopg2.connect(args.db_url)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    MAX(timestamp)                        AS latest,
                    NOW()                                 AS now,
                    NOW() - MAX(timestamp)                AS offset,
                    COUNT(*)                              AS total_rows,
                    MIN(timestamp)                        AS earliest
                FROM telemetry_readings;
            """)
            info = cur.fetchone()

        if info["total_rows"] == 0:
            print("No rows in telemetry_readings — nothing to do.")
            return

        print(f"  Earliest : {info['earliest']}")
        print(f"  Latest   : {info['latest']}")
        print(f"  Now      : {info['now']}")
        print(f"  Offset   : {info['offset']}")
        print(f"  Rows     : {info['total_rows']}")

        if args.dry_run:
            print("\n[dry-run] No changes made.")
            return

        print("\nApplying shift…", end=" ", flush=True)
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE telemetry_readings
                SET    timestamp = timestamp + (NOW() - (SELECT MAX(timestamp) FROM telemetry_readings));
            """)
            updated = cur.rowcount
        conn.commit()
        print(f"done.  Updated {updated:,} rows.")

        # Verify
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT MIN(timestamp) AS earliest, MAX(timestamp) AS latest FROM telemetry_readings;")
            after = cur.fetchone()
        print(f"\nAfter shift:")
        print(f"  Earliest : {after['earliest']}")
        print(f"  Latest   : {after['latest']}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
