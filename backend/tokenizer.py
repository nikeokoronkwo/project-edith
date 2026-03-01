"""
tokenizer.py — PII Tokenization Pipeline (Module 1)

Three-layer reversible tokenization:
  Layer 1: Regex — phone/callsign patterns
  Layer 2: Dictionary — known operative names (loaded from report metadata)
  Layer 3: Heuristic NER — capitalized multi-word PERSON patterns

Public API:
    build_known_names(reports) -> set[str]
    tokenize_pii(text, report_id, known_names) -> (tokenized_text, token_map, audit_log)
    get_token_vault() -> dict
    clear_token_vault() -> None
"""

import json
import re
import secrets
from pathlib import Path
from typing import Optional

# Matches "FirstName LastName" (and optionally more words) — all title-cased
_PERSON_PATTERN = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b')

_token_vault: dict[str, dict] = {}


def _generate_token_id(prefix: str) -> str:
    return f"{prefix}-{secrets.token_hex(2).upper()}"


def _ensure_unique_token(prefix: str) -> str:
    token_id = _generate_token_id(prefix)
    while token_id in _token_vault:
        token_id = _generate_token_id(prefix)
    return token_id


def build_known_names(reports: list[dict]) -> set[str]:
    """Extract all unique operative names from report metadata."""
    names = set()
    for report in reports:
        alias = report.get("metadata", {}).get("hero_alias")
        if alias:
            names.add(alias)
    return names


def build_known_non_persons(reports: list[dict]) -> set[str]:
    """
    Build a blocklist of multi-word title-cased strings that are clearly not
    person names (e.g. "Avengers Compound", "Stark Industries").  We use a
    simple heuristic: any title-cased match that appears in the metadata
    location/facility fields is treated as a non-person.
    """
    non_persons: set[str] = set()
    location_keys = ("location", "facility", "sector", "region", "site")
    for report in reports:
        meta = report.get("metadata", {})
        for key in location_keys:
            val = meta.get(key)
            if isinstance(val, str) and re.match(r'^[A-Z]', val):
                non_persons.add(val)
    return non_persons


def tokenize_pii(
    text: str,
    report_id: str,
    known_names: Optional[set[str]] = None,
    known_non_persons: Optional[set[str]] = None,
) -> tuple[str, dict, list[dict]]:
    """
    Run three-layer PII detection on a text string.

    Args:
        text: Raw report text.
        report_id: UUID of the source report (for vault linkage).
        known_names: Set of operative names to match via dictionary layer.
        known_non_persons: Set of strings to exclude from NER PERSON matching
            (e.g. location names that spaCy may misclassify).

    Returns:
        (tokenized_text, token_map, audit_log)
        - tokenized_text: text with PII replaced by tokens like [OPERATIVE-A7F3]
        - token_map: {token_id: {real_value, type}} for this report
        - audit_log: list of dicts recording each detection
    """
    if known_names is None:
        known_names = set()
    if known_non_persons is None:
        known_non_persons = set()

    token_map: dict[str, dict] = {}
    audit_log: list[dict] = []
    tokenized = text

    # ── Layer 1: Regex — phone / callsign patterns ──
    # Catches: 555-0147, 555-GOD-OF-THUNDER, 555-0199 (Black Widow Comms)
    phone_pattern = r"\d{3}[-.][\w]+(?:[-.][\w]+)*(?:\s*\([^)]+\))?"

    def _phone_replacer(match: re.Match) -> str:
        original = match.group()
        token_id = _ensure_unique_token("CONTACT")
        tag = f"[{token_id}]"
        _token_vault[token_id] = {
            "real_value": original,
            "type": "PHONE",
            "report_id": report_id,
        }
        token_map[token_id] = {"real_value": original, "type": "PHONE"}
        audit_log.append(
            {
                "original_fragment": original,
                "token_replacement": token_id,
                "entity_type": "PHONE",
                "detection_layer": "REGEX",
            }
        )
        return tag

    tokenized = re.sub(phone_pattern, _phone_replacer, tokenized)

    # ── Layer 2: Dictionary — known operative names ──
    # Sort longest-first so "Natasha Romanoff" is matched before a hypothetical "Natasha"
    for name in sorted(known_names, key=len, reverse=True):
        if name not in tokenized:
            continue
        token_id = _ensure_unique_token("OPERATIVE")
        tag = f"[{token_id}]"
        _token_vault[token_id] = {
            "real_value": name,
            "type": "PERSON",
            "report_id": report_id,
        }
        token_map[token_id] = {"real_value": name, "type": "PERSON"}
        audit_log.append(
            {
                "original_fragment": name,
                "token_replacement": token_id,
                "entity_type": "PERSON",
                "detection_layer": "DICTIONARY",
            }
        )
        tokenized = tokenized.replace(name, tag)

    # ── Layer 3: Heuristic NER — catch unknown PERSON entities ──
    # Match title-cased multi-word patterns on the ORIGINAL text for context,
    # then apply replacements only for matches still present in tokenized text.
    already_replaced = {entry["original_fragment"] for entry in audit_log}

    for match in _PERSON_PATTERN.finditer(text):
        fragment = match.group()
        if fragment in already_replaced:
            continue
        if fragment not in tokenized:
            continue
        if fragment in known_non_persons:
            continue
        token_id = _ensure_unique_token("OPERATIVE")
        tag = f"[{token_id}]"
        _token_vault[token_id] = {
            "real_value": fragment,
            "type": "PERSON",
            "report_id": report_id,
        }
        token_map[token_id] = {"real_value": fragment, "type": "PERSON"}
        audit_log.append(
            {
                "original_fragment": fragment,
                "token_replacement": token_id,
                "entity_type": "PERSON",
                "detection_layer": "NER",
            }
        )
        tokenized = tokenized.replace(fragment, tag)
        already_replaced.add(fragment)

    return tokenized, token_map, audit_log


def format_for_db(
    report: dict,
    tokenized_text: str,
    audit_log: list[dict],
) -> tuple[dict, list[dict]]:
    """
    Shape tokenizer output into rows matching the DB schema (SCHEMA.MD).

    Args:
        report: The original report dict from field_intel_reports.json.
        tokenized_text: The redacted text returned by tokenize_pii.
        audit_log: The audit log returned by tokenize_pii.

    Returns:
        (report_row, audit_rows)
        - report_row: dict matching the `reports` table schema
        - audit_rows: list of dicts matching the `redaction_audit` table schema
    """
    metadata = report.get("metadata", {})

    report_row = {
        "report_id": report["report_id"],
        "timestamp": report["timestamp"],
        "operative_name": metadata.get("hero_alias"),
        "operative_contact": metadata.get("secure_contact"),
        "raw_text": report["raw_text"],
        "redacted_text": tokenized_text,
        "priority": report.get("priority"),
        "status": "REDACTED",
    }

    audit_rows = [
        {
            "report_id": report["report_id"],
            "original_fragment": entry["original_fragment"],
            "replacement": f"[{entry['token_replacement']}]",
            "entity_type": entry["entity_type"],
            "detection_layer": entry["detection_layer"],
        }
        for entry in audit_log
    ]

    return report_row, audit_rows


def get_token_vault() -> dict:
    """Return a copy of the in-memory token vault."""
    return _token_vault.copy()


def clear_token_vault() -> None:
    """Reset the in-memory token vault."""
    _token_vault.clear()


# ── Standalone test runner ──
if __name__ == "__main__":
    data_path = (
        Path(__file__).resolve().parent.parent
        / "info"
        / "field_intel_reports.json"
    )
    if not data_path.exists():
        print(f"Data file not found: {data_path}")
        raise SystemExit(1)

    with open(data_path) as f:
        reports = json.load(f)
    print(f"Loaded {len(reports)} reports from {data_path.name}\n")

    known_names = build_known_names(reports)
    print(f"Known operatives: {sorted(known_names)}")

    print("Building non-person blocklist from metadata locations...")
    known_non_persons = build_known_non_persons(reports)
    print(f"Non-person blocklist ({len(known_non_persons)} entries): {sorted(known_non_persons)}\n")

    clear_token_vault()

    pii_body_count = 0
    total_detections = 0
    layer_counts = {"REGEX": 0, "DICTIONARY": 0, "NER": 0}

    all_report_rows: list[dict] = []
    all_audit_rows: list[dict] = []

    for report in reports:
        rid = report["report_id"]
        raw = report["raw_text"]
        tokenized, tmap, audit = tokenize_pii(raw, rid, known_names, known_non_persons)

        if audit:
            pii_body_count += 1
            total_detections += len(audit)
            for entry in audit:
                layer_counts[entry["detection_layer"]] += 1

        report_row, audit_rows = format_for_db(report, tokenized, audit)
        all_report_rows.append(report_row)
        all_audit_rows.extend(audit_rows)

    print("=" * 60)
    print(f"Reports with PII in body text:  {pii_body_count} / {len(reports)}")
    print(f"Total PII detections:           {total_detections}")
    print(f"Detections by layer:            {layer_counts}")
    print(f"Token vault size:               {len(_token_vault)}")
    print(f"DB rows:  {len(all_report_rows)} reports, {len(all_audit_rows)} audit entries")
    print("=" * 60)

    pii_report_rows = [r for r in all_report_rows if r["redacted_text"] != r["raw_text"]]
    print("\n── Example: reports table row (PII report) ──")
    if pii_report_rows:
        r = pii_report_rows[0]
        for k, v in r.items():
            print(f"  {k:20} = {v}")

    print("\n── Example: reports table row (clean report) ──")
    clean_rows = [r for r in all_report_rows if r["redacted_text"] == r["raw_text"]]
    if clean_rows:
        c = clean_rows[0]
        for k, v in c.items():
            print(f"  {k:20} = {v}")

    matching_audits = [a for a in all_audit_rows if a["report_id"] == pii_report_rows[0]["report_id"]]
    if matching_audits:
        print(f"\n── Example: redaction_audit rows for report {matching_audits[0]['report_id'][:8]}... ──")
        for a in matching_audits:
            print(f"  '{a['original_fragment']}' → {a['replacement']}  [{a['entity_type']}, {a['detection_layer']}]")

    db_output = {
        "reports_table": all_report_rows,
        "redaction_audit_table": all_audit_rows,
    }
    out_path = Path(__file__).resolve().parent / "tokenizer_results.json"
    with open(out_path, "w") as f:
        json.dump(db_output, f, indent=2)
    print(f"\nDB-shaped results saved to {out_path}")
