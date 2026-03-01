"""
llm_extractor.py — LLM Entity Extraction + Modifier Generation (Module 2)

Takes a tokenized report text (PII already replaced by tokens), calls Claude
to extract structured intel, then deterministically computes a modifier.

Public API:
    extract(tokenized_text, report_id) -> (extraction_result, modifier)
    format_for_db(report_id, extraction_result, modifier, raw_llm_response) -> dict

The LLM extracts: sector, resource, severity, event_type, summary.
Python computes:  modifier_type, modifier_value, modifier_duration_hours.
"""

import json
import re
from pathlib import Path

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2"

# ── Constants ──────────────────────────────────────────────────────────────

VALID_SECTORS = {
    "Avengers Compound",
    "New Asgard",
    "Sanctum Sanctorum",
    "Sokovia",
    "Wakanda",
}

VALID_RESOURCES = {
    "Arc Reactor Cores",
    "Clean Water (L)",
    "Medical Kits",
    "Pym Particles",
    "Vibranium (kg)",
}

VALID_EVENT_TYPES = {"DEPLETION", "DISRUPTION", "THREAT", "RESUPPLY"}

# Fix 2: Lookup map from stripped (no-unit) lowercase name → canonical resource name.
# Handles cases where Llama adds a wrong unit suffix (e.g. "Pym Particles (kg)").
_RESOURCE_LOOKUP: dict[str, str] = {
    re.sub(r"\s*\(.*?\)", "", r).strip().lower(): r
    for r in VALID_RESOURCES
}

# Deterministic modifier table — keyed by event_type.
# modifier_value is the BASE value before severity scaling.
# Severity (1–10) scales it: scaled_value = base * (severity / 5.0)
#
# How these map to telemetry_readings.usage_rate_hourly:
#   usage_rate_multiplier > 1.0  → resource burning faster than normal
#   usage_rate_multiplier < 0.0  → effective usage reduced (cache found)
#   resupply_halt = 0.0          → supply chain stopped, no new stock incoming
MODIFIER_TABLE: dict[str, dict] = {
    "DEPLETION":  {"modifier_type": "usage_rate_multiplier", "modifier_value": 2.0,  "modifier_duration_hours": 48},
    "DISRUPTION": {"modifier_type": "resupply_halt",         "modifier_value": 0.0,  "modifier_duration_hours": 72},
    "THREAT":     {"modifier_type": "usage_rate_multiplier", "modifier_value": 1.5,  "modifier_duration_hours": 24},
    "RESUPPLY":   {"modifier_type": "usage_rate_multiplier", "modifier_value": -0.5, "modifier_duration_hours": 12},
}

SYSTEM_PROMPT = """You are an intelligence analyst processing field reports.
Extract structured data from the report and return ONLY a valid JSON object — no prose, no markdown fences.

Required keys:
  "sector"     — the location (string, must be one of the valid sectors)
  "resource"   — the resource affected (string, must be one of the valid resources)
  "severity"   — integer from 1 (minor) to 10 (catastrophic). NEVER null. NEVER 0. Always a number.
  "event_type" — one of: DEPLETION, DISRUPTION, THREAT, RESUPPLY. NEVER null. Always a string.
  "summary"    — one-sentence plain-English summary of the situation

Valid sectors: Avengers Compound, New Asgard, Sanctum Sanctorum, Sokovia, Wakanda
Valid resources: Arc Reactor Cores, Clean Water (L), Medical Kits, Pym Particles, Vibranium (kg)

Event type guide:
  DEPLETION  — stock is gone or critically low
  DISRUPTION — supply chain is compromised or blocked
  THREAT     — active threat putting stock at risk
  RESUPPLY   — new stock has been secured or is incoming
  For RESUPPLY events, severity represents the strategic value of the find:
    1–3 = minor cache, 4–6 = moderate stockpile, 7–10 = major strategic reserve.

Return nothing except the JSON object."""

# ── Core functions ─────────────────────────────────────────────────────────


def _call_llm(tokenized_text: str) -> tuple[dict, str]:
    """
    Call local Ollama (Llama 3.2) and parse the JSON response.

    Returns:
        (parsed_dict, raw_response_text)

    Raises:
        ValueError if Ollama is unreachable or the response is not valid JSON.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": tokenized_text},
        ],
        "stream": False,
        "format": "json",  # Ollama JSON mode — guarantees valid JSON output
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise ValueError("Ollama is not running. Start it with: ollama serve")

    raw = response.json()["message"]["content"]
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Ollama returned non-JSON: {raw!r}") from e

    return parsed, raw


def _validate(parsed: dict) -> dict:
    """
    Validate and normalise the LLM response dict.
    Raises ValueError with a descriptive message on any violation.

    Normalisation applied:
      - severity: None → 5, clamped to 1–10 (never crashes on nulls or 0)
      - resource: strips accidental unit suffixes before matching
        e.g. "Pym Particles (kg)" → matched to "Pym Particles"
      - event_type: uppercased and validated
    """
    required = {"sector", "resource", "severity", "event_type", "summary"}
    missing = required - parsed.keys()
    if missing:
        raise ValueError(f"LLM response missing keys: {missing}")

    if parsed["sector"] not in VALID_SECTORS:
        raise ValueError(f"Unknown sector: {parsed['sector']!r}")

    # Fix 2: try exact match first; fall back to stripped lookup
    resource_raw = parsed["resource"]
    if resource_raw not in VALID_RESOURCES:
        stripped = re.sub(r"\s*\(.*?\)", "", str(resource_raw)).strip().lower()
        canonical = _RESOURCE_LOOKUP.get(stripped)
        if canonical is None:
            raise ValueError(f"Unknown resource: {resource_raw!r}")
        parsed["resource"] = canonical

    event_type = str(parsed["event_type"]).upper()
    if event_type not in VALID_EVENT_TYPES:
        raise ValueError(f"Unknown event_type: {parsed['event_type']!r}")
    parsed["event_type"] = event_type

    # Fix 1: clamp severity — None → 5, out-of-range → clamped to 1–10
    raw_severity = parsed["severity"]
    severity = int(raw_severity) if raw_severity is not None else 5
    parsed["severity"] = max(1, min(10, severity))

    return parsed


def _compute_modifier(event_type: str, severity: int) -> dict:
    """
    Deterministically compute the modifier from event_type + severity.
    severity scales the modifier_value: scaled = base * (severity / 5.0)
    DISRUPTION (resupply_halt) is not scaled — it's binary.
    """
    base = MODIFIER_TABLE[event_type].copy()
    if base["modifier_type"] == "usage_rate_multiplier":
        base["modifier_value"] = round(base["modifier_value"] * (severity / 5.0), 4)
    return base


def extract(tokenized_text: str, report_id: str) -> tuple[dict, dict, str]:
    """
    Extract structured intel from a tokenized report and compute its modifier.

    Args:
        tokenized_text: Report text with PII replaced by tokens (Module 1 output).
        report_id: UUID of the source report.

    Returns:
        (extraction_result, modifier, raw_llm_response)
        - extraction_result: {sector, resource, severity, event_type, summary}
        - modifier: {modifier_type, modifier_value, modifier_duration_hours}
        - raw_llm_response: raw JSON string from the LLM (for DB storage)
    """
    parsed, raw_llm_response = _call_llm(tokenized_text)
    extraction_result = _validate(parsed)
    modifier = _compute_modifier(extraction_result["event_type"], extraction_result["severity"])
    return extraction_result, modifier, raw_llm_response


def format_for_db(
    report_id: str,
    extraction_result: dict,
    modifier: dict,
    raw_llm_response: str,
) -> dict:
    """
    Shape extract() output into a row matching the intel_extracted DB table.

    Args:
        report_id: UUID of the source report.
        extraction_result: dict returned by extract().
        modifier: dict returned by extract().
        raw_llm_response: raw JSON string from the LLM (stored in JSONB column).

    Returns:
        dict matching the intel_extracted table schema.
    """
    return {
        "report_id": report_id,
        "sector": extraction_result["sector"],
        "resource": extraction_result["resource"],
        "severity": extraction_result["severity"],
        "event_type": extraction_result["event_type"],
        "summary": extraction_result["summary"],
        "modifier_type": modifier["modifier_type"],
        "modifier_value": modifier["modifier_value"],
        "modifier_duration_hours": modifier["modifier_duration_hours"],
        "raw_llm_response": raw_llm_response,
    }


# ── Standalone test runner ─────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    from collections import Counter

    tokenizer_results_path = Path(__file__).resolve().parent / "tokenizer_results.json"
    if not tokenizer_results_path.exists():
        print(f"tokenizer_results.json not found at {tokenizer_results_path}")
        print("Run tokenizer.py first to generate it.")
        sys.exit(1)

    with open(tokenizer_results_path) as f:
        tokenizer_output = json.load(f)

    reports = tokenizer_output["reports_table"]
    print(f"Loaded {len(reports)} reports from tokenizer_results.json\n")

    intel_rows: list[dict] = []
    event_type_counts: Counter = Counter()
    severity_total = 0
    errors: list[dict] = []

    for i, report in enumerate(reports):
        report_id = report["report_id"]
        text = report.get("redacted_text") or report.get("raw_text", "")

        try:
            extraction_result, modifier, raw_response = extract(text, report_id)
            row = format_for_db(report_id, extraction_result, modifier, raw_response)
            intel_rows.append(row)
            event_type_counts[extraction_result["event_type"]] += 1
            severity_total += extraction_result["severity"]
        except (ValueError, Exception) as e:
            errors.append({"report_id": report_id, "error": str(e)})

        if (i + 1) % 20 == 0:
            print(f"  Processed {i + 1}/{len(reports)}...")

    print("\n" + "=" * 60)
    print(f"Processed:    {len(intel_rows)} / {len(reports)} reports")
    print(f"Errors:       {len(errors)}")
    if intel_rows:
        print(f"Avg severity: {severity_total / len(intel_rows):.1f}")
    print(f"Event types:  {dict(event_type_counts)}")
    print("=" * 60)

    if intel_rows:
        print("\n── Sample intel_extracted row ──")
        sample = intel_rows[0]
        for k, v in sample.items():
            if k != "raw_llm_response":
                print(f"  {k:30} = {v}")

    if errors:
        print(f"\n── First error ──")
        print(f"  {errors[0]}")

    out_path = Path(__file__).resolve().parent / "llm_extractor_results.json"
    output = {
        "intel_extracted_table": intel_rows,
        "errors": errors,
    }
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {out_path}")
