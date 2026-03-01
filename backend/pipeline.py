"""
pipeline.py — The Full Chain (Module 3)

Orchestrates Module 1 (tokenizer) and Module 2 (llm_extractor) in sequence.
Takes a raw report dict, returns a complete processed result ready for DB insertion.

Public API:
    process_report(report_dict) -> dict
"""

from tokenizer import tokenize_pii
from tokenizer import format_for_db as tokenizer_format_for_db
from llm_extractor import extract
from llm_extractor import format_for_db as intel_format_for_db


def process_report(report_dict: dict) -> dict:
    """
    Run a raw report through the full pipeline: PII tokenization → LLM extraction.

    Args:
        report_dict: Must contain:
            - report_id (str UUID)
            - raw_text (str)
            - metadata.hero_alias (str)
            - metadata.secure_contact (str, optional)
            - timestamp (str ISO)
            - priority (str)

    Returns:
        {
          "report_row":        dict — matches `reports` table schema
          "audit_rows":        list[dict] — matches `redaction_audit` table schema
          "intel_row":         dict — matches `intel_extracted` table schema
          "extraction_result": dict — {sector, resource, severity, event_type, summary}
          "modifier":          dict — {modifier_type, modifier_value, modifier_duration_hours}
        }
    """
    report_id = report_dict["report_id"]
    raw_text = report_dict["raw_text"]
    hero_alias = report_dict.get("metadata", {}).get("hero_alias", "")

    # ── Module 1: PII Tokenization ─────────────────────────────────────────
    tokenized_text, _, audit_log = tokenize_pii(
        text=raw_text,
        report_id=report_id,
        known_names={hero_alias} if hero_alias else None,
    )
    report_row, audit_rows = tokenizer_format_for_db(report_dict, tokenized_text, audit_log)

    # ── Module 2: LLM Extraction ───────────────────────────────────────────
    extraction_result, modifier, raw_llm = extract(tokenized_text, report_id)
    intel_row = intel_format_for_db(report_id, extraction_result, modifier, raw_llm)

    report_row["status"] = "COMPLETE"

    return {
        "report_row":        report_row,
        "audit_rows":        audit_rows,
        "intel_row":         intel_row,
        "extraction_result": extraction_result,
        "modifier":          modifier,
    }
