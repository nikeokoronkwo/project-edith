#!/usr/bin/env python3
"""Apply SCHEMA.sql to a PostgreSQL database."""

import sys
import psycopg2
from pathlib import Path

DEFAULT_URL = "postgresql://edith_user:edith_password@localhost:5433/edith_db"
SCHEMA_PATH = Path(__file__).parent / "SCHEMA.sql"


def apply_schema(db_url: str) -> None:
    sql = SCHEMA_PATH.read_text()
    sql = sql.replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ")
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        print(f"Schema applied successfully to {db_url.split('@')[-1]}")
    finally:
        conn.close()


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    apply_schema(url)
