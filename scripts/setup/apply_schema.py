#!/usr/bin/env python3
"""Apply SCHEMA.sql to a PostgreSQL database."""

import sys
import psycopg2
from pathlib import Path

DEFAULT_URL = "postgresql://edith_user:edith_password@localhost:5433/edith_db"
SCHEMA_PATH = Path(__file__).parent.parent.parent / "SCHEMA.sql"


def apply_schema(db_url: str) -> None:
    raw = SCHEMA_PATH.read_text()

    # Split on statement boundaries, skip blank lines and comment-only chunks
    statements = []
    for chunk in raw.split(";"):
        stmt = chunk.strip()
        # Drop lines that are only SQL comments, keep mixed content
        code_lines = [ln for ln in stmt.splitlines() if ln.strip() and not ln.strip().startswith("--")]
        if not code_lines:
            continue
        stmt = stmt.replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ")
        statements.append(stmt)

    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            for stmt in statements:
                cur.execute(stmt)
        print(f"Schema applied successfully to {db_url.split('@')[-1]}")
        print(f"  ({len(statements)} statements executed)")
    finally:
        conn.close()


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    apply_schema(url)
