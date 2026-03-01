#!/usr/bin/env python3
"""Apply SCHEMA.sql to a PostgreSQL database."""

import sys
import psycopg2
from pathlib import Path

DEFAULT_URL = "postgresql://edith_user:edith_password@localhost:5433/edith_db"
SCHEMA_PATH = Path(__file__).parent.parent.parent / "SCHEMA.sql"


def apply_schema(db_url: str) -> None:
    raw = SCHEMA_PATH.read_text()

    # Drop in reverse-dependency order so FK constraints don't block the drops.
    # CASCADE handles any remaining cross-references.
    drop_stmts = [
        "DROP TABLE IF EXISTS telemetry_readings CASCADE",
        "DROP TABLE IF EXISTS redaction_audit CASCADE",
        "DROP TABLE IF EXISTS intel_extracted CASCADE",
        "DROP TABLE IF EXISTS reports CASCADE",
    ]

    # Split CREATE statements on semicolons, skip blank / comment-only chunks.
    create_stmts = []
    for chunk in raw.split(";"):
        stmt = chunk.strip()
        code_lines = [ln for ln in stmt.splitlines()
                      if ln.strip() and not ln.strip().startswith("--")]
        if code_lines:
            create_stmts.append(stmt)

    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            for stmt in drop_stmts:
                cur.execute(stmt)
            for stmt in create_stmts:
                cur.execute(stmt)
        print(f"Schema applied successfully to {db_url.split('@')[-1]}")
        print(f"  ({len(drop_stmts)} drops + {len(create_stmts)} creates)")
    finally:
        conn.close()


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    apply_schema(url)
