"""
publisher.py — Long-running background publisher for EDITH backend.

Three daemon threads run concurrently:

  1. telemetry-ticker (every 30 s)
     Reads the latest stock level for every (sector, resource) pair, applies
     hourly usage-rate decay, inserts a new telemetry_readings row, and
     publishes an analytics message to the RabbitMQ exchange.

  2. report-watcher (every 5 s)
     Polls for reports inserted after the last watermark timestamp and
     publishes a report-shaped message for each new one.

  3. event-watcher (every 5 s)
     Polls for intel_extracted rows after the last watermark id and
     publishes an event-shaped message for each new one.

All messages are sent to the same fanout exchange ('shield_events') that
the Nuxt SSE streams consume from.

Run standalone:
    export DATABASE_URL="postgresql://edith_user:edith_password@localhost:5433/edith_db"
    export RABBITMQ_URL="amqp://guest:guest@localhost:5672"
    python publisher.py

Or call start_publisher() from a FastAPI lifespan handler.
"""

import json
import logging
import os
import threading
import time
from datetime import datetime, timezone

import pika
import psycopg2
import psycopg2.extras

log = logging.getLogger(__name__)

RABBITMQ_EXCHANGE = "shield_events"
TELEMETRY_INTERVAL = 30  # seconds between telemetry ticks
WATCHER_INTERVAL = 5     # seconds between report / event polls


# ── Connection helpers ────────────────────────────────────────────────────────

def _get_db():
    url = os.environ.get(
        "DATABASE_URL",
        "postgresql://edith_user:edith_password@localhost:5433/edith_db",
    )
    return psycopg2.connect(url)


def _get_rmq_channel():
    """Open a fresh pika connection + channel and declare the exchange."""
    url = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672")
    params = pika.URLParameters(url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type="fanout", durable=True)
    return conn, ch


def _publish(ch, message: dict) -> None:
    ch.basic_publish(
        exchange=RABBITMQ_EXCHANGE,
        routing_key="",
        body=json.dumps(message, default=str),
        properties=pika.BasicProperties(expiration="300000"),
    )


def _severity_label(severity: int | None) -> str:
    if severity is None:
        return "normal"
    if severity >= 9:
        return "critical"
    if severity >= 7:
        return "warning"
    if severity >= 4:
        return "elevated"
    return "normal"


def _severity_priority(severity: int | None) -> int:
    if severity is None:
        return 4
    if severity >= 9:
        return 1
    if severity >= 7:
        return 2
    if severity >= 4:
        return 3
    return 4


# ── Telemetry ticker ──────────────────────────────────────────────────────────

def run_telemetry_ticker(
    interval: int = TELEMETRY_INTERVAL,
    stop_event: threading.Event | None = None,
) -> None:
    """
    Every `interval` seconds:
      - Fetch the latest reading per (sector, resource) pair.
      - Decay stock_level by usage_rate_hourly * elapsed_hours.
      - Insert a new telemetry_readings row.
      - Publish an analytics message to RabbitMQ.
    """
    if stop_event is None:
        stop_event = threading.Event()

    log.info("[telemetry-ticker] Starting (interval=%ds)", interval)

    while not stop_event.is_set():
        try:
            db = _get_db()
            rmq_conn, ch = _get_rmq_channel()
            hours_elapsed = interval / 3600.0
            now = datetime.now(timezone.utc)

            with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT DISTINCT ON (sector_id, resource_type)
                        sector_id, resource_type, stock_level, usage_rate_hourly
                    FROM telemetry_readings
                    ORDER BY sector_id, resource_type, timestamp DESC;
                """)
                latest_rows = cur.fetchall()

            published = 0
            for row in latest_rows:
                new_level = max(
                    0.0,
                    float(row["stock_level"]) - float(row["usage_rate_hourly"]) * hours_elapsed,
                )
                with db.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO telemetry_readings
                            (timestamp, sector_id, resource_type,
                             stock_level, usage_rate_hourly, snap_event_detected)
                        VALUES (%s, %s, %s, %s, %s, FALSE);
                        """,
                        (now, row["sector_id"], row["resource_type"],
                         new_level, row["usage_rate_hourly"]),
                    )
                db.commit()

                _publish(ch, {
                    "timestamp": int(now.timestamp() * 1000),
                    "resource": row["resource_type"],
                    "sector": row["sector_id"],
                    "value": round(new_level, 2),
                    "metric": "",
                    "forecast": {
                        "slope": -float(row["usage_rate_hourly"]),
                        "confidence_band": 0.08,
                        "critical_threshold": 10,
                        "horizon_hours": 24,
                    },
                })
                published += 1

            db.close()
            rmq_conn.close()

            if published:
                log.info("[telemetry-ticker] Published %d analytics updates", published)

        except Exception as exc:
            log.warning("[telemetry-ticker] Error (will retry): %s", exc)

        stop_event.wait(interval)

    log.info("[telemetry-ticker] Stopped")


# ── Report watcher ────────────────────────────────────────────────────────────

def run_report_watcher(
    interval: int = WATCHER_INTERVAL,
    stop_event: threading.Event | None = None,
) -> None:
    """
    Every `interval` seconds, poll for reports newer than the last watermark
    and publish a report-shaped message to RabbitMQ for each one.
    """
    if stop_event is None:
        stop_event = threading.Event()

    log.info("[report-watcher] Starting (interval=%ds)", interval)
    last_seen: datetime | None = None

    while not stop_event.is_set():
        try:
            db = _get_db()
            rmq_conn, ch = _get_rmq_channel()

            with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                if last_seen is None:
                    # Initialise watermark to current max — don't re-publish history.
                    cur.execute("SELECT MAX(created_at) FROM reports;")
                    row = cur.fetchone()
                    last_seen = (
                        row["max"] if (row and row["max"]) else datetime.min.replace(tzinfo=timezone.utc)
                    )
                    db.close()
                    rmq_conn.close()
                    stop_event.wait(interval)
                    continue

                cur.execute(
                    """
                    SELECT r.report_id, r.timestamp, r.operative_name,
                           r.redacted_text, r.priority, r.status, r.created_at,
                           ie.sector, ie.resource, ie.severity, ie.event_type, ie.summary
                    FROM reports r
                    LEFT JOIN intel_extracted ie ON r.report_id = ie.report_id
                    WHERE r.created_at > %s
                    ORDER BY r.created_at ASC
                    LIMIT 50;
                    """,
                    (last_seen,),
                )
                new_rows = cur.fetchall()

            for row in new_rows:
                ts = row["timestamp"]
                _publish(ch, {
                    "id": str(row["report_id"]),
                    "heroAlias": row.get("operative_name") or "Unknown",
                    "description": row.get("redacted_text") or "",
                    "timeStarted": ts.isoformat() if ts else "",
                    "affectedLocations": [row["sector"]] if row.get("sector") else [],
                    "severity": _severity_label(row.get("severity")),
                })
                if row["created_at"] > last_seen:
                    last_seen = row["created_at"]

            db.close()
            rmq_conn.close()

            if new_rows:
                log.info("[report-watcher] Published %d new reports", len(new_rows))

        except Exception as exc:
            log.warning("[report-watcher] Error (will retry): %s", exc)

        stop_event.wait(interval)

    log.info("[report-watcher] Stopped")


# ── Event watcher ─────────────────────────────────────────────────────────────

def run_event_watcher(
    interval: int = WATCHER_INTERVAL,
    stop_event: threading.Event | None = None,
) -> None:
    """
    Every `interval` seconds, poll for new intel_extracted rows above the
    last watermark id and publish an event-shaped message for each one.
    """
    if stop_event is None:
        stop_event = threading.Event()

    log.info("[event-watcher] Starting (interval=%ds)", interval)
    last_id: int | None = None

    while not stop_event.is_set():
        try:
            db = _get_db()
            rmq_conn, ch = _get_rmq_channel()

            with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                if last_id is None:
                    cur.execute("SELECT MAX(id) FROM intel_extracted;")
                    row = cur.fetchone()
                    last_id = int(row["max"]) if (row and row["max"]) else 0
                    db.close()
                    rmq_conn.close()
                    stop_event.wait(interval)
                    continue

                cur.execute(
                    """
                    SELECT ie.id, ie.summary, ie.severity, ie.sector,
                           ie.resource, ie.event_type, r.timestamp
                    FROM intel_extracted ie
                    JOIN reports r ON ie.report_id = r.report_id
                    WHERE ie.id > %s
                    ORDER BY ie.id ASC
                    LIMIT 50;
                    """,
                    (last_id,),
                )
                new_rows = cur.fetchall()

            for row in new_rows:
                ts = row["timestamp"]
                ts_ms = int(ts.timestamp() * 1000) if ts else int(time.time() * 1000)
                _publish(ch, {
                    "id": str(row["id"]),
                    "event": row.get("summary") or row.get("event_type") or "Unknown event",
                    "priority": _severity_priority(row.get("severity")),
                    "started": ts.isoformat() if ts else "",
                    "timestamp": ts_ms,
                    "description": row.get("summary") or "",
                    "affectedResources": [row["resource"]] if row.get("resource") else [],
                    "affectedLocations": [row["sector"]] if row.get("sector") else [],
                })
                last_id = max(last_id, int(row["id"]))

            db.close()
            rmq_conn.close()

            if new_rows:
                log.info("[event-watcher] Published %d new events", len(new_rows))

        except Exception as exc:
            log.warning("[event-watcher] Error (will retry): %s", exc)

        stop_event.wait(interval)

    log.info("[event-watcher] Stopped")


# ── Public API ────────────────────────────────────────────────────────────────

def start_publisher(
    telemetry_interval: int = TELEMETRY_INTERVAL,
    watcher_interval: int = WATCHER_INTERVAL,
) -> tuple[threading.Event, list[threading.Thread]]:
    """
    Start the three background publisher threads as daemons.

    Returns (stop_event, threads).  Call stop_event.set() to request a clean
    shutdown; join the threads to wait for completion.
    """
    stop = threading.Event()

    threads = [
        threading.Thread(
            target=run_telemetry_ticker,
            kwargs={"interval": telemetry_interval, "stop_event": stop},
            name="telemetry-ticker",
            daemon=True,
        ),
        threading.Thread(
            target=run_report_watcher,
            kwargs={"interval": watcher_interval, "stop_event": stop},
            name="report-watcher",
            daemon=True,
        ),
        threading.Thread(
            target=run_event_watcher,
            kwargs={"interval": watcher_interval, "stop_event": stop},
            name="event-watcher",
            daemon=True,
        ),
    ]

    for t in threads:
        t.start()

    log.info(
        "[publisher] Started %d background threads: %s",
        len(threads),
        ", ".join(t.name for t in threads),
    )
    return stop, threads


# ── Standalone entry point ────────────────────────────────────────────────────

if __name__ == "__main__":
    import signal

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
    )

    stop, threads = start_publisher()

    def _shutdown(sig, frame):
        log.info("Shutdown signal received — stopping publisher…")
        stop.set()

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    log.info("Publisher running. Press Ctrl+C to stop.")
    for t in threads:
        t.join()
    log.info("Publisher stopped.")
