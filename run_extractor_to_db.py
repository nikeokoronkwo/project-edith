#!/usr/bin/env python3
"""
Run the LLM extractor against all REDACTED reports in the database,
then write results into the intel_extracted table.

Only processes reports that don't already have an intel_extracted row.
"""

import json
import sys
from pathlib import Path

import psycopg2
import psycopg2.extras
import pika

sys.path.insert(0, str(Path(__file__).parent / "ReportPipline"))
from llm_extractor import extract, format_for_db

DEFAULT_URL = "postgresql://edith_user:edith_password@localhost:5433/edith_db"

INSERT_INTEL = """
    INSERT INTO intel_extracted (
        report_id, sector, resource, severity, event_type, summary,
        modifier_type, modifier_value, modifier_duration_hours, raw_llm_response
    ) VALUES (
        %(report_id)s, %(sector)s, %(resource)s, %(severity)s, %(event_type)s, %(summary)s,
        %(modifier_type)s, %(modifier_value)s, %(modifier_duration_hours)s, %(raw_llm_response)s
    );
"""

UPDATE_STATUS = """
    UPDATE reports SET status = 'COMPLETE' WHERE report_id = %s;
"""

db_conn = psycopg2.connect(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL)
rabbitmq_conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672, credentials=pika.PlainCredentials('guest', 'guest')))
channel = rabbitmq_conn.channel()
channel.basic_qos(prefetch_count=1)
channel.exchange_declare(exchange='shield_events', exchange_type='fanout', durable=True)
channel.queue_declare(queue='reports_stream', durable=True)
channel.queue_bind(queue='reports_stream', exchange='shield_events')

def run() -> None:
    conn = db_conn

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT r.report_id::text, r.redacted_text
              FROM reports r 
             WHERE r.status = 'REDACTED'
               AND NOT EXISTS (
                   SELECT 1 FROM intel_extracted ie WHERE ie.report_id = r.report_id
               );
        """)
        rows = cur.fetchall()

    if not rows:
        print("No REDACTED reports without intel — nothing to do.")
        conn.close()
        return

    print(f"Found {len(rows)} reports to process.\n")

    success = 0
    errors = []

    for i, r in enumerate(rows):
        rid = r["report_id"]
        text = r["redacted_text"] or ""

        try:
            extraction_result, modifier, raw_llm = extract(text, rid)
            # 'row' contains the dictionary with your extracted fields
            row = format_for_db(rid, extraction_result, modifier, raw_llm)

            if isinstance(row["raw_llm_response"], dict):
                row["raw_llm_response"] = json.dumps(row["raw_llm_response"])

            with conn.cursor() as cur:
                cur.execute(INSERT_INTEL, row)
                cur.execute(UPDATE_STATUS, (rid,))
            conn.commit()

            success += 1

            # --> MOVED INSIDE THE LOOP <--
            # Publish the specific report data to RabbitMQ
            channel.basic_publish(
                exchange='shield_events',
                routing_key='',
                body=json.dumps({
                    "report_id": rid,
                    "sector": row["sector"],
                    "resource": row["resource"],
                    "severity": row["severity"],
                    "event_type": row["event_type"]
                }),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                )
            )

        except Exception as e:
            conn.rollback()
            errors.append({"report_id": rid, "error": str(e)})

        if (i + 1) % 10 == 0 or (i + 1) == len(rows):
            print(f"  Processed {i + 1}/{len(rows)} ({success} ok, {len(errors)} errors)")

    # (Remove the basic_publish block from outside the loop here)

    print("\n" + "=" * 55)
    print(f"Intel rows inserted: {success}")
    print(f"Reports updated to COMPLETE: {success}")
    print(f"Errors: {len(errors)}")
    if errors:
        print(f"First error: {errors[0]}")
    print("=" * 55)

    conn.close()


def channel_callback(ch, method, properties, body):
    print(f"Received message: {body}")
    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

    # Work with DB 
    run()

if __name__ == "__main__":
    
    channel.basic_consume(queue='reports', on_message_callback=channel_callback)
    channel.start_consuming()