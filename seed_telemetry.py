#!/usr/bin/env python3
"""
Expand historical_avengers_data.csv from 1 resource per sector to 5,
then insert all rows into the telemetry_readings table.

Original CSV: each sector has only one resource type (10K rows).
Output: every sector gets all 5 resource types (50K rows).
Synthetic resources use the original's usage pattern with random deviation.
"""

import csv
import random
import sys
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

DEFAULT_URL = "postgresql://edith_user:edith_password@localhost:5433/edith_db"
CSV_PATH = Path(__file__).parent / "info" / "historical_avengers_data.csv"

ALL_RESOURCES = [
    "Arc Reactor Cores",
    "Clean Water (L)",
    "Medical Kits",
    "Pym Particles",
    "Vibranium (kg)",
]

INITIAL_STOCK = {
    "Arc Reactor Cores": 500.0,
    "Clean Water (L)":   2500.0,
    "Medical Kits":      400.0,
    "Pym Particles":     250.0,
    "Vibranium (kg)":    200.0,
}

INSERT_SQL = """
    INSERT INTO telemetry_readings
           (timestamp, sector_id, resource_type, stock_level, usage_rate_hourly, snap_event_detected)
    VALUES %s
"""


def _deviate(value: float, pct: float = 0.15) -> float:
    """Add random deviation to a value (default +-15%)."""
    return round(value * random.uniform(1 - pct, 1 + pct), 2)


def expand_rows(csv_path: Path) -> list[tuple]:
    """Read the CSV and produce 5x rows — original + 4 synthetic resource types."""
    rows: list[tuple] = []

    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = row["timestamp"]
            sector = row["sector_id"]
            orig_resource = row["resource_type"]
            stock = float(row["stock_level"])
            usage = float(row["usage_rate_hourly"])
            snap = row["snap_event_detected"] == "True"

            orig_initial = INITIAL_STOCK.get(orig_resource, stock)
            stock_ratio = stock / orig_initial if orig_initial else 1.0

            for resource in ALL_RESOURCES:
                if resource == orig_resource:
                    rows.append((ts, sector, resource, stock, usage, snap))
                else:
                    synth_stock = round(INITIAL_STOCK[resource] * stock_ratio * random.uniform(0.92, 1.08), 2)
                    synth_stock = max(0, synth_stock)
                    synth_usage = _deviate(usage)
                    rows.append((ts, sector, resource, synth_stock, synth_usage, snap))

    return rows


def seed(db_url: str) -> None:
    rows = expand_rows(CSV_PATH)
    print(f"Generated {len(rows)} telemetry rows from {CSV_PATH.name}")

    conn = psycopg2.connect(db_url)
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM telemetry_readings;")
            execute_values(cur, INSERT_SQL, rows, page_size=5000)
        conn.commit()

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM telemetry_readings;")
            count = cur.fetchone()[0]
            cur.execute("SELECT sector_id, COUNT(DISTINCT resource_type) FROM telemetry_readings GROUP BY sector_id ORDER BY sector_id;")
            breakdown = cur.fetchall()

        print(f"Done — {count} rows in telemetry_readings.")
        print("\nResources per sector:")
        for sector, n in breakdown:
            print(f"  {sector}: {n}")
    finally:
        conn.close()


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    seed(url)
