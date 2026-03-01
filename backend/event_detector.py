"""
event_detector.py — Continuous anomaly detection for the EDITH backend.

Runs as a daemon thread alongside publisher.py. On every scan it:

  1. Fetches the last READING_WINDOW telemetry readings per (sector, resource) pair.
  2. Splits them into a *recent* window (newest RECENT_N rows) and a *baseline*
     window (the older BASELINE_N rows immediately before that).
  3. Computes a least-squares slope (units/hour) for each window.
  4. Flags a pair as anomalous when:
       • recent slope is at least SLOPE_RATIO× more negative than the baseline, AND
       • current stock has fallen below STOCK_WARN_PCT of the local maximum seen
         in the full window (i.e. from the peak in that data slice).
  5. For every flagged sector, looks back REPORT_WINDOW_H hours in intel_extracted
     for high-severity (≥ SEVERITY_FLOOR) corroborating reports.
  6. Publishes a "major_event_alert" message to the shield_events fanout exchange.
  7. Applies a per-pair cooldown (COOLDOWN_MINUTES) to prevent alert storms.

RabbitMQ message shape
──────────────────────
{
  "type": "major_event_alert",
  "detected_at": "<ISO-8601 UTC>",
  "confidence": 0.0–1.0,
  "affected_pairs": [
    {
      "sector": str,
      "resource": str,
      "current_stock": float,
      "stock_pct": float,               # fraction of local max
      "recent_slope_per_hr": float,     # negative = depleting
      "baseline_slope_per_hr": float,
      "slope_ratio": float,             # recent / baseline (> 1 = worsening)
      "depletion_hours": float | null,  # estimated hours to zero
      "alert_level": "ELEVATED" | "WARNING" | "CRITICAL"
    }
  ],
  "corroborating_reports": [
    { "id": str, "summary": str, "severity": int,
      "event_type": str, "sector": str, "resource": str }
  ],
  "event_summary": str,
  "recommended_action": str
}
"""

import json
import logging
import os
import threading
import time
from datetime import datetime, timedelta, timezone

import pika
import psycopg2
import psycopg2.extras

log = logging.getLogger(__name__)

# ── Tuning constants ───────────────────────────────────────────────────────────

READING_WINDOW   = 96    # total readings fetched per pair for slope analysis
RECENT_N         = 12    # newest N readings  → "current trend"
BASELINE_N       = 48    # older  N readings  → "historical normal"
SLOPE_RATIO      = 2.5   # recent slope must be ≥ this × baseline to flag
STOCK_WARN_PCT   = 0.45  # WARNING  when stock < 45 % of local window max
STOCK_CRIT_PCT   = 0.15  # CRITICAL when stock < 15 % of local window max
SEVERITY_FLOOR   = 6     # minimum intel_extracted severity for corroboration
REPORT_WINDOW_H  = 12    # hours back to search for corroborating reports
COOLDOWN_MINUTES = 45    # minimum minutes between alerts for the same pair
SCAN_INTERVAL    = 60    # seconds between full scans

RABBITMQ_EXCHANGE = "shield_events"


# ── DB / RMQ helpers ───────────────────────────────────────────────────────────

def _get_db():
    url = os.environ.get(
        "DATABASE_URL",
        "postgresql://edith_user:edith_password@localhost:5433/edith_db",
    )
    return psycopg2.connect(url)


def _get_rmq_channel():
    url = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672")
    conn = pika.BlockingConnection(pika.URLParameters(url))
    ch = conn.channel()
    ch.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type="fanout", durable=True)
    return conn, ch


# ── Regression ─────────────────────────────────────────────────────────────────

def _slope_per_hour(timestamps: list[datetime], values: list[float]) -> float:
    """Ordinary least-squares slope in units/hour.  Returns 0.0 on degenerate input."""
    n = len(timestamps)
    if n < 2:
        return 0.0
    t0 = timestamps[0]
    xs = [(t - t0).total_seconds() / 3600.0 for t in timestamps]
    x_bar = sum(xs) / n
    y_bar = sum(values) / n
    num   = sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, values))
    denom = sum((x - x_bar) ** 2 for x in xs)
    return num / denom if denom else 0.0


# ── DB queries ─────────────────────────────────────────────────────────────────

def _fetch_all_pairs(conn) -> list[tuple[str, str]]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT DISTINCT sector_id, resource_type "
            "FROM telemetry_readings ORDER BY sector_id, resource_type;"
        )
        return [(r[0], r[1]) for r in cur.fetchall()]


def _fetch_recent_readings(conn, sector: str, resource: str, n: int) -> list[dict]:
    """Return the last `n` readings for this (sector, resource) pair, oldest first."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            SELECT timestamp, stock_level, usage_rate_hourly
              FROM telemetry_readings
             WHERE sector_id = %s AND resource_type = %s
             ORDER BY timestamp DESC
             LIMIT %s;
            """,
            (sector, resource, n),
        )
        rows = cur.fetchall()
    rows = list(rows)
    rows.reverse()  # oldest first
    return [dict(r) for r in rows]


def _fetch_corroborating_reports(
    conn, sector: str, hours: int
) -> list[dict]:
    """intel_extracted rows with severity ≥ SEVERITY_FLOOR for this sector, last `hours` hours."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            SELECT ie.id, ie.summary, ie.severity, ie.event_type,
                   ie.sector, ie.resource
              FROM intel_extracted ie
              JOIN reports r ON ie.report_id = r.report_id
             WHERE ie.sector = %s
               AND ie.severity >= %s
               AND r.timestamp >= %s
             ORDER BY ie.severity DESC
             LIMIT 5;
            """,
            (sector, SEVERITY_FLOOR, cutoff),
        )
        return [dict(r) for r in cur.fetchall()]


# ── Alert construction helpers ─────────────────────────────────────────────────

def _alert_level(stock_pct: float) -> str:
    if stock_pct < STOCK_CRIT_PCT:
        return "CRITICAL"
    if stock_pct < STOCK_WARN_PCT:
        return "WARNING"
    return "ELEVATED"


def _depletion_hours(stock: float, slope: float) -> float | None:
    """Hours until stock reaches zero at current rate.  None if not depleting."""
    if slope >= 0:
        return None
    return round(stock / abs(slope), 1)


def _compute_slope_ratio(recent: float, baseline: float) -> float:
    """
    A ratio > 1 means the situation is worsening relative to baseline.
    Handles the case where baseline is flat or recovering.
    """
    if baseline < -1e-4:
        return recent / baseline           # both negative → positive ratio
    if recent < -0.01:
        return SLOPE_RATIO + 1.0          # was stable/growing, now depleting → auto-flag
    return 1.0


def _confidence(slope_ratio: float, stock_pct: float, has_reports: bool) -> float:
    ratio_score  = min(0.5, (slope_ratio - SLOPE_RATIO) / (SLOPE_RATIO * 3))
    stock_score  = max(0.0, (STOCK_WARN_PCT - stock_pct) / STOCK_WARN_PCT) * 0.3
    report_score = 0.2 if has_reports else 0.0
    return round(min(1.0, ratio_score + stock_score + report_score), 2)


def _event_summary(affected: list[dict], reports: list[dict]) -> str:
    pairs = ", ".join(f"{p['resource']} @ {p['sector']}" for p in affected[:3])
    extra = f" and {len(affected) - 3} more pair(s)" if len(affected) > 3 else ""
    rpt_note = (
        f" Corroborated by {len(reports)} high-severity field report(s)."
        if reports
        else " No corroborating field reports — telemetry signal only."
    )
    return (
        f"Supply anomaly detected: {pairs}{extra}. "
        f"Depletion rate significantly exceeds historical baseline.{rpt_note}"
    )


def _recommended_action(affected: list[dict]) -> str:
    most_urgent = min(
        affected,
        key=lambda p: (p.get("depletion_hours") or 9_999),
    )
    eta = most_urgent.get("depletion_hours")
    window = f"within {eta} hours" if eta else "immediately"
    return (
        f"Emergency resupply required for {most_urgent['resource']} "
        f"at {most_urgent['sector']} {window}. "
        f"Review all {len(affected)} flagged pair(s) for coordinated response."
    )


# ── Main scan loop ─────────────────────────────────────────────────────────────

def run_event_detector(
    interval: int = SCAN_INTERVAL,
    stop_event: threading.Event | None = None,
) -> None:
    """
    Daemon loop: scan telemetry, detect anomalies, publish alerts.
    Call from a daemon thread via start_publisher() or standalone.
    """
    if stop_event is None:
        stop_event = threading.Event()

    log.info("[event-detector] Starting (interval=%ds, recent=%d, baseline=%d readings)",
             interval, RECENT_N, BASELINE_N)

    # (sector, resource) → datetime of last alert for that pair
    cooldowns: dict[tuple[str, str], datetime] = {}

    while not stop_event.is_set():
        try:
            db  = _get_db()
            now = datetime.now(timezone.utc)
            pairs = _fetch_all_pairs(db)

            affected: list[dict] = []
            seen_report_ids: set[int] = set()
            all_corroborating: list[dict] = []

            for sector, resource in pairs:
                key = (sector, resource)

                # Skip pairs still within their cooldown window
                if key in cooldowns:
                    elapsed_min = (now - cooldowns[key]).total_seconds() / 60.0
                    if elapsed_min < COOLDOWN_MINUTES:
                        continue

                rows = _fetch_recent_readings(db, sector, resource, READING_WINDOW)
                if len(rows) < RECENT_N + BASELINE_N:
                    continue  # not enough history yet

                recent_rows   = rows[-RECENT_N:]
                baseline_rows = rows[-(RECENT_N + BASELINE_N): -RECENT_N]

                recent_ts  = [r["timestamp"] for r in recent_rows]
                recent_val = [float(r["stock_level"]) for r in recent_rows]
                base_ts    = [r["timestamp"] for r in baseline_rows]
                base_val   = [float(r["stock_level"]) for r in baseline_rows]

                recent_slope   = _slope_per_hour(recent_ts, recent_val)
                baseline_slope = _slope_per_hour(base_ts, base_val)

                current_stock = recent_val[-1]
                local_max     = max(float(r["stock_level"]) for r in rows)
                stock_pct     = current_stock / local_max if local_max > 0 else 1.0

                slope_ratio = _compute_slope_ratio(recent_slope, baseline_slope)

                # ── Anomaly gate ──────────────────────────────────────────────
                if (
                    recent_slope < -0.01                # actually depleting
                    and slope_ratio >= SLOPE_RATIO      # meaningfully faster than baseline
                    and stock_pct < STOCK_WARN_PCT      # stock already significantly depleted
                ):
                    affected.append({
                        "sector":                 sector,
                        "resource":               resource,
                        "current_stock":          round(current_stock, 2),
                        "stock_pct":              round(stock_pct, 4),
                        "recent_slope_per_hr":    round(recent_slope, 4),
                        "baseline_slope_per_hr":  round(baseline_slope, 4),
                        "slope_ratio":            round(slope_ratio, 2),
                        "depletion_hours":        _depletion_hours(current_stock, recent_slope),
                        "alert_level":            _alert_level(stock_pct),
                    })

                    # Corroborating reports for this sector
                    rpts = _fetch_corroborating_reports(db, sector, REPORT_WINDOW_H)
                    for rpt in rpts:
                        if rpt["id"] not in seen_report_ids:
                            all_corroborating.append(rpt)
                            seen_report_ids.add(rpt["id"])

            # ── Publish if any pair is flagged ────────────────────────────────
            if affected:
                worst_ratio = max(p["slope_ratio"] for p in affected)
                worst_pct   = min(p["stock_pct"]   for p in affected)
                confidence  = _confidence(worst_ratio, worst_pct, bool(all_corroborating))

                alert = {
                    "type": "major_event_alert",
                    "detected_at": now.isoformat(),
                    "confidence": confidence,
                    "affected_pairs": affected,
                    "corroborating_reports": [
                        {
                            "id":         str(r["id"]),
                            "summary":    r["summary"],
                            "severity":   r["severity"],
                            "event_type": r["event_type"],
                            "sector":     r["sector"],
                            "resource":   r["resource"],
                        }
                        for r in all_corroborating
                    ],
                    "event_summary":      _event_summary(affected, all_corroborating),
                    "recommended_action": _recommended_action(affected),
                }

                rmq_conn, ch = _get_rmq_channel()
                ch.basic_publish(
                    exchange=RABBITMQ_EXCHANGE,
                    routing_key="",
                    body=json.dumps(alert, default=str),
                    properties=pika.BasicProperties(
                        expiration="600000",  # 10-minute TTL
                        delivery_mode=2,
                    ),
                )
                rmq_conn.close()

                # Set cooldowns for flagged pairs
                for entry in affected:
                    cooldowns[(entry["sector"], entry["resource"])] = now

                log.info(
                    "[event-detector] ALERT  confidence=%.2f  pairs=%d  reports=%d",
                    confidence, len(affected), len(all_corroborating),
                )
                for p in affected:
                    log.info(
                        "  [%-8s] %-26s / %-22s  stock=%.1f (%.0f%%)  "
                        "slope %.3f→%.3f u/hr  ETA=%s h",
                        p["alert_level"], p["sector"], p["resource"],
                        p["current_stock"], p["stock_pct"] * 100,
                        p["baseline_slope_per_hr"], p["recent_slope_per_hr"],
                        p["depletion_hours"] if p["depletion_hours"] else "∞",
                    )
            else:
                log.debug("[event-detector] Scan complete — no anomalies detected")

            db.close()

        except Exception as exc:
            log.warning("[event-detector] Scan error (will retry): %s", exc)

        stop_event.wait(interval)

    log.info("[event-detector] Stopped")


# ── Standalone entry point ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import signal

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
    )

    stop = threading.Event()

    def _shutdown(sig, frame):
        log.info("Shutdown received — stopping event detector…")
        stop.set()

    signal.signal(signal.SIGINT,  _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    log.info("Event detector running standalone. Press Ctrl+C to stop.")
    run_event_detector(stop_event=stop)
    log.info("Done.")
