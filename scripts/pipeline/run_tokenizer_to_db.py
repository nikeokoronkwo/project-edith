#!/usr/bin/env python3
"""
Run the tokenizer against all PENDING reports in the database,
then write redacted_text and audit rows back to the DB.

Updates:
  - reports.redacted_text  (NULL → tokenized text)
  - reports.status         (PENDING → REDACTED)
Inserts:
  - redaction_audit rows   (one per PII detection)
"""

import sys
from pathlib import Path

import psycopg2
import psycopg2.extras

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))
from tokenizer import build_known_names, build_known_non_persons, tokenize_pii, clear_token_vault

DEFAULT_URL = "postgresql://edith_user:edith_password@localhost:5433/edith_db"

UPDATE_REPORT = """
    UPDATE reports
       SET redacted_text = %s,
           status = 'REDACTED'
     WHERE report_id = %s;
"""

INSERT_AUDIT = """
    INSERT INTO redaction_audit
           (report_id, original_fragment, replacement, entity_type, detection_layer)
    VALUES %s;
"""


def run(db_url: str) -> None:
    conn = psycopg2.connect(db_url)

    # Pull all PENDING reports from the DB
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT report_id::text, operative_name, operative_contact, raw_text
              FROM reports
             WHERE status = 'PENDING';
        """)
        rows = cur.fetchall()

    if not rows:
        print("No PENDING reports found — nothing to do.")
        conn.close()
        return

    print(f"Found {len(rows)} PENDING reports.\n")

    # Build the known-names set from the DB data itself
    fake_reports = [
        {"metadata": {"hero_alias": r["operative_name"]}, "raw_text": r["raw_text"]}
        for r in rows
    ]
    known_names = build_known_names(fake_reports)
    print(f"Known operatives: {sorted(known_names)}")

    print("Building NER blocklist...")
    known_non_persons = build_known_non_persons(fake_reports)
    print(f"Non-person blocklist: {len(known_non_persons)} entries\n")

    clear_token_vault()

    report_updates = []
    audit_values = []
    pii_count = 0

    for r in rows:
        rid = r["report_id"]
        tokenized, _, audit = tokenize_pii(
            r["raw_text"], rid, known_names, known_non_persons
        )
        report_updates.append((tokenized, rid))

        if audit:
            pii_count += 1
            for entry in audit:
                audit_values.append((
                    rid,
                    entry["original_fragment"],
                    f"[{entry['token_replacement']}]",
                    entry["entity_type"],
                    entry["detection_layer"],
                ))

    # Write everything in one transaction
    with conn.cursor() as cur:
        cur.executemany(UPDATE_REPORT, report_updates)

        if audit_values:
            psycopg2.extras.execute_values(cur, INSERT_AUDIT, audit_values)

    conn.commit()
    conn.close()

    print("=" * 55)
    print(f"Updated {len(report_updates)} reports → status = REDACTED")
    print(f"Reports with PII in body text: {pii_count}")
    print(f"Audit rows inserted: {len(audit_values)}")
    print("=" * 55)


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    run(url)
