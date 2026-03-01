#!/usr/bin/env python3
"""
Merge all MCU event data into combined datasets
"""

import csv
import json
import os
from pathlib import Path
from datetime import datetime

EVENTS = [
    ("chitauri_invasion", "Chitauri Invasion", "2012"),
    ("sokovia_attack", "Sokovia Attack (Ultron)", "2015"),
    ("thanos_snap", "Thanos Snap (Infinity War)", "2018"),
    ("hulk_blip", "Hulk Blip (Endgame)", "2023"),
    ("emergence", "The Emergence (Eternals)", "2024"),
    ("wakanda_forever", "Wakanda Forever", "2024"),
    ("quantumania", "Quantumania (Kang)", "2025"),
]


def merge_csv_files():
    """Merge all CSV files into one combined dataset"""
    combined_rows = []
    total_rows = 0

    for event_dir, event_name, year in EVENTS:
        filepath = f"data/{event_dir}/resource_timeseries.csv"
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row["event_name"] = event_name
                    row["event_year"] = year
                    combined_rows.append(row)
                    total_rows += 1

    output_path = "data/combined/resource_timeseries_all_events.csv"
    os.makedirs("data/combined", exist_ok=True)

    fieldnames = [
        "timestamp",
        "location",
        "resource_type",
        "inventory_level",
        "consumption_rate",
        "supply_rate",
        "days_remaining",
        "threat_level",
        "event_name",
        "event_year",
    ]

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combined_rows)

    print(f"Combined CSV: {total_rows} rows -> {output_path}")
    return total_rows


def merge_jsonl_files():
    """Merge all JSONL files into one combined dataset"""
    combined_reports = []
    total_reports = 0

    for event_dir, event_name, year in EVENTS:
        filepath = f"data/{event_dir}/field_intel_reports.jsonl"
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                for line in f:
                    report = json.loads(line.strip())
                    report["event_name"] = event_name
                    report["event_year"] = year
                    combined_reports.append(report)
                    total_reports += 1

    output_path = "data/combined/field_intel_reports_all_events.jsonl"

    with open(output_path, "w") as f:
        for report in combined_reports:
            f.write(json.dumps(report) + "\n")

    print(f"Combined JSONL: {total_reports} reports -> {output_path}")
    return total_reports


def create_event_summary():
    """Create a summary file for all events"""
    summary = []

    csv_rows = 0
    jsonl_reports = 0

    for event_dir, event_name, year in EVENTS:
        csv_path = f"data/{event_dir}/resource_timeseries.csv"
        jsonl_path = f"data/{event_dir}/field_intel_reports.jsonl"

        if os.path.exists(csv_path):
            with open(csv_path, "r") as f:
                csv_rows = sum(1 for _ in f) - 1  # subtract header

        if os.path.exists(jsonl_path):
            with open(jsonl_path, "r") as f:
                jsonl_reports = sum(1 for _ in f)

        summary.append(
            {
                "event_directory": event_dir,
                "event_name": event_name,
                "year": year,
                "csv_rows": csv_rows,
                "jsonl_reports": jsonl_reports,
            }
        )

    output_path = "data/combined/event_summary.json"
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Event summary: {output_path}")
    return summary


def main():
    print("=" * 60)
    print("MERGING MCU EVENT DATASETS")
    print("=" * 60)

    csv_rows = merge_csv_files()
    jsonl_reports = merge_jsonl_files()
    summary = create_event_summary()

    print("\n" + "=" * 60)
    print("MERGE SUMMARY")
    print("=" * 60)
    print(f"Total CSV rows: {csv_rows}")
    print(f"Total JSONL reports: {jsonl_reports}")
    print(f"\nEvents included:")
    for s in summary:
        print(
            f"  - {s['event_name']} ({s['year']}): {s['csv_rows']} CSV rows, {s['jsonl_reports']} reports"
        )


if __name__ == "__main__":
    main()
