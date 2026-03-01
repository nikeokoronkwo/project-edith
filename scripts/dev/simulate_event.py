#!/usr/bin/env python3
"""
simulate_event.py — Real-time event simulator for the EDITH dashboard.

Generates a stream of field reports (JSON) and telemetry ticks (CSV-compatible)
that model a named MCU scenario, then either:

  • dumps them to files for offline review / seeding, and / or
  • plays them back live — posting reports to the FastAPI and publishing
    telemetry updates directly to RabbitMQ so the dashboard updates in
    real time.

Usage
─────
  # List available scenarios
  python simulate_event.py --list

  # Dump files without running anything live
  python simulate_event.py --scenario chitauri_invasion --mode dump

  # Live playback at 60× speed (1 scenario-minute = 1 real second)
  python simulate_event.py --scenario chitauri_invasion --mode live --speed 60

  # Both dump and live at 30× speed
  python simulate_event.py --scenario the_snap --mode both --speed 30

  # Override endpoints
  python simulate_event.py --scenario sokovia_incident --mode live \\
      --speed 120 \\
      --api-url http://localhost:8080 \\
      --rabbitmq amqp://guest:guest@localhost:5672

Options
───────
  --scenario SCENARIO   Scenario key to run (see --list)
  --mode MODE           dump | live | both  (default: both)
  --speed FLOAT         Scenario-minutes per real second (default: 60)
  --output DIR          Output directory for dump mode  (default: ./sim_output/<scenario>)
  --api-url URL         FastAPI base URL for report posting
  --rabbitmq URL        RabbitMQ AMQP URL for telemetry publishing
  --list                Print available scenarios and exit

Environment variables (override CLI defaults):
  DATABASE_URL    PostgreSQL URL  (unused at runtime, present for parity)
  RABBITMQ_URL    RabbitMQ AMQP URL
  EXTERNAL_BACKEND_URL  FastAPI base URL
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import logging
import os
import random
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pika
import requests

log = logging.getLogger("sim")

# ─────────────────────────────────────────────────────────────────────────────
# Domain constants (must match SCHEMA + llm_extractor.py)
# ─────────────────────────────────────────────────────────────────────────────

SECTORS = [
    "Avengers Compound",
    "New Asgard",
    "Sanctum Sanctorum",
    "Sokovia",
    "Wakanda",
]

RESOURCES = [
    "Arc Reactor Cores",
    "Clean Water (L)",
    "Medical Kits",
    "Pym Particles",
    "Vibranium (kg)",
]

# Default initial stock per resource (matches seed_telemetry.py)
DEFAULT_INITIAL_STOCK: dict[str, float] = {
    "Arc Reactor Cores":  500.0,
    "Clean Water (L)":   2500.0,
    "Medical Kits":       400.0,
    "Pym Particles":      250.0,
    "Vibranium (kg)":     200.0,
}

DEFAULT_USAGE_RATE: dict[str, float] = {
    "Arc Reactor Cores":  5.0,
    "Clean Water (L)":    6.0,
    "Medical Kits":       4.5,
    "Pym Particles":      3.0,
    "Vibranium (kg)":     2.0,
}

RABBITMQ_EXCHANGE = "shield_events"
TICK_INTERVAL_MINUTES = 5   # simulated minutes between telemetry ticks


# ─────────────────────────────────────────────────────────────────────────────
# Scenario data model
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Shock:
    """A stock / usage-rate shock applied at a specific scenario minute."""
    at_minute: float
    sector: str
    resource: str
    # Applied simultaneously at the tick:
    usage_multiplier: float = 1.0   # multiplies current usage_rate_hourly
    stock_delta: float = 0.0        # immediate absolute change to stock_level
    stock_multiplier: float = 1.0   # multiplies current stock (applied before delta)
    snap_event: bool = False        # marks the tick as snap_event_detected=True


@dataclass
class ReportTemplate:
    """A scripted field report dispatched at a specific scenario minute."""
    at_minute: float
    hero_alias: str
    sector: str
    text: str                        # the raw_text body (no PII required for sim)
    priority: str = "Routine"
    secure_contact: str | None = None


@dataclass
class Scenario:
    key: str
    name: str
    description: str
    duration_minutes: float
    reports: list[ReportTemplate] = field(default_factory=list)
    shocks: list[Shock] = field(default_factory=list)
    # Per-sector overrides for initial stock.  Missing keys use DEFAULT_INITIAL_STOCK.
    initial_stock: dict[str, dict[str, float]] = field(default_factory=dict)
    initial_usage: dict[str, dict[str, float]] = field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Scenario definitions
# ─────────────────────────────────────────────────────────────────────────────

def _s(sector: str, resource: str, at: float, **kw) -> Shock:
    return Shock(at_minute=at, sector=sector, resource=resource, **kw)


def _r(at: float, hero: str, sector: str, text: str, **kw) -> ReportTemplate:
    return ReportTemplate(at_minute=at, hero_alias=hero, sector=sector, text=text, **kw)


# ── Chitauri Invasion ────────────────────────────────────────────────────────

CHITAURI_INVASION = Scenario(
    key="chitauri_invasion",
    name="Chitauri Invasion",
    description=(
        "Loki opens a tesseract portal above Stark Tower. "
        "A Chitauri armada pours through, striking Avengers Compound hardest "
        "before rippling outward to Sokovia.  Wakanda and New Asgard deploy "
        "emergency aid.  The portal closes after 90 minutes."
    ),
    duration_minutes=110,

    # ── Telemetry shocks ──────────────────────────────────────────────────────
    shocks=[
        # T+0 — portal opens, initial surge
        _s("Avengers Compound", "Medical Kits",      0,  usage_multiplier=4.0),
        _s("Avengers Compound", "Arc Reactor Cores", 0,  usage_multiplier=3.0),

        # T+10 — full assault wave
        _s("Avengers Compound", "Medical Kits",      10, usage_multiplier=8.0,  stock_delta=-80.0),
        _s("Avengers Compound", "Arc Reactor Cores", 10, usage_multiplier=6.0,  stock_delta=-60.0),
        _s("Avengers Compound", "Clean Water (L)",   10, stock_delta=-200.0),
        _s("Avengers Compound", "Vibranium (kg)",    10, usage_multiplier=2.5),

        # T+20 — Sokovia secondary strike
        _s("Sokovia", "Medical Kits",      20, usage_multiplier=5.0, stock_delta=-50.0),
        _s("Sokovia", "Clean Water (L)",   20, stock_multiplier=0.75),
        _s("Sokovia", "Pym Particles",     20, usage_multiplier=2.0),

        # T+30 — supply chain disrupted globally
        _s("Avengers Compound", "Arc Reactor Cores", 30, stock_delta=-120.0),
        _s("Sanctum Sanctorum", "Pym Particles",     30, stock_multiplier=0.8),
        _s("New Asgard",        "Medical Kits",      30, usage_multiplier=2.0),

        # T+40 — Wakanda mobilises, Vibranium incoming
        _s("Avengers Compound", "Vibranium (kg)",    40, stock_delta=+50.0, usage_multiplier=0.5),
        _s("Wakanda",           "Vibranium (kg)",    40, stock_delta=-40.0),

        # T+50 — arc reactor grid collapses at compound
        _s("Avengers Compound", "Arc Reactor Cores", 50, usage_multiplier=12.0, stock_delta=-80.0),
        _s("Avengers Compound", "Clean Water (L)",   50, stock_multiplier=0.5),

        # T+60 — New Asgard sends Medical Kits resupply convoy
        _s("Avengers Compound", "Medical Kits",      60, stock_delta=+120.0, usage_multiplier=0.6),
        _s("New Asgard",        "Medical Kits",      60, stock_delta=-100.0),

        # T+70 — Iron Man closes portal; combat intensity drops
        _s("Avengers Compound", "Medical Kits",      70, usage_multiplier=0.3),
        _s("Avengers Compound", "Arc Reactor Cores", 70, usage_multiplier=0.4),
        _s("Sokovia",           "Medical Kits",      70, usage_multiplier=0.5),

        # T+80 — Sanctum Sanctorum mystic shields engage, stabilise compound
        _s("Avengers Compound", "Clean Water (L)",   80, stock_delta=+300.0),
        _s("Sanctum Sanctorum", "Pym Particles",     80, stock_delta=+50.0),

        # T+90 — portal sealed, Chitauri remnants mopped up
        _s("Avengers Compound", "Medical Kits",      90, usage_multiplier=0.15),
        _s("Avengers Compound", "Arc Reactor Cores", 90, usage_multiplier=0.2),
        _s("Sokovia",           "Clean Water (L)",   90, stock_delta=+150.0),

        # T+100 — recovery aid arrives from all sectors
        _s("Avengers Compound", "Arc Reactor Cores", 100, stock_delta=+80.0),
        _s("Avengers Compound", "Pym Particles",     100, stock_delta=+40.0),
    ],

    # ── Field reports ─────────────────────────────────────────────────────────
    reports=[
        _r(0, "Tony Stark", "Avengers Compound",
           "Tesseract portal confirmed above Stark Tower. Multiple bogies inbound. "
           "Activating Iron Legion. Arc reactor grid at full draw. Requesting all hands.",
           priority="Urgent"),

        _r(3, "Natasha Romanoff", "Avengers Compound",
           "Chitauri ground units breaching the perimeter. Medical bay overwhelmed—"
           "requesting 200 additional medical kits from Wakanda reserves immediately.",
           priority="Urgent"),

        _r(6, "Steve Rogers", "Avengers Compound",
           "We have Chitauri units in sector seven. Three civilians down. "
           "Clean water distribution points compromised. Air support needed over the compound.",
           priority="Urgent"),

        _r(10, "Clint Barton", "Avengers Compound",
           "Chitauri leviathan has cleared the outer wall. "
           "Arc reactor power cells depleting at triple the normal rate. "
           "Vibranium reinforcements holding the south corridor.",
           priority="Urgent"),

        _r(15, "Thor Odinson", "New Asgard",
           "Portal energy readings detected from New Asgard. Dispatching Einherjar to the compound. "
           "Medical kit stockpiles packaged for emergency airlift.",
           priority="Routine"),

        _r(18, "Wanda Maximoff", "Sokovia",
           "Secondary Chitauri wave has entered Sokovia airspace. "
           "Civilians evacuating. Water treatment plant is offline. Requesting SHIELD support.",
           priority="Urgent"),

        _r(22, "Vision", "Avengers Compound",
           "Energy output from the tesseract sceptre spike detected. "
           "Pym Particle containment units at Sanctum Sanctorum showing anomalous readings. "
           "Recommend isolation protocol.",
           priority="Routine"),

        _r(28, "Sam Wilson", "Avengers Compound",
           "EXO-7 wing damaged. Arc reactor cores at 18% capacity in the east block. "
           "Requesting emergency cores from the Stark warehouse. "
           "We will not hold without them.",
           priority="Urgent"),

        _r(35, "T\'Challa", "Wakanda",
           "Wakanda is dispatching 50 kg of vibranium plating to reinforce the compound perimeter. "
           "Border Tribe mobilised. Expect convoy arrival within the hour.",
           priority="Routine"),

        _r(45, "Bruce Banner", "Avengers Compound",
           "The Hulk is contained. Lab is intact but power is down to 8%. "
           "Arc reactor cores fully depleted in Block C. "
           "Other hulk out imminent if we lose containment.",
           priority="Urgent"),

        _r(52, "Tony Stark", "Avengers Compound",
           "Nuke disposal complete. Warhead was Chitauri. "
           "Arc reactor cells blown across the north quad—stock critical. "
           "Portal structure is weakening. Preparing to close it.",
           priority="Urgent"),

        _r(60, "Thor Odinson", "Avengers Compound",
           "Asgardian medical convoy has arrived. 120 kits distributed to field stations. "
           "Bifrost stable. New Asgard reserves stretched but holding.",
           priority="Routine"),

        _r(68, "Tony Stark", "Avengers Compound",
           "Portal closed. Iron Man mark XLVII offline—taking it in for repairs. "
           "Arc reactor cores still critical but the rate has dropped. Good job everyone.",
           priority="Routine"),

        _r(75, "Stephen Strange", "Sanctum Sanctorum",
           "Mystic barrier projected over the compound. Pym Particle readings normalising. "
           "Sorcerers on standby for clean-up. "
           "Recommend a full resource audit within 24 hours.",
           priority="Routine"),

        _r(85, "Natasha Romanoff", "Avengers Compound",
           "Perimeter secured. Medical stations processing final casualties. "
           "Clean water supply restored to the east wing. "
           "Compound functional but resources stretched thin.",
           priority="Routine"),

        _r(95, "Steve Rogers", "Sokovia",
           "Sokovia stabilised. Chitauri remnants neutralised. "
           "Water treatment back online—expect full restoration in 6 hours. "
           "Population returning to shelters.",
           priority="Routine"),

        _r(105, "Tony Stark", "Avengers Compound",
           "Arc reactor emergency stock arrived from Stark Industries facility. "
           "80 cores delivered. "
           "Full post-incident resource audit underway. Situation resolved.",
           priority="Routine"),
    ],
)


# ── Sokovia Incident ─────────────────────────────────────────────────────────

SOKOVIA_INCIDENT = Scenario(
    key="sokovia_incident",
    name="Sokovia Incident",
    description=(
        "Ultron lifts Sokovia.  Vibranium reserves in the city are commandeered. "
        "Supply lines to Sokovia are severed. "
        "Avengers scramble to evacuate and hold out."
    ),
    duration_minutes=80,

    shocks=[
        _s("Sokovia", "Vibranium (kg)",    0,  usage_multiplier=10.0, stock_delta=-80.0),
        _s("Sokovia", "Medical Kits",      0,  usage_multiplier=6.0),
        _s("Sokovia", "Clean Water (L)",   0,  stock_multiplier=0.6),
        _s("Sokovia", "Arc Reactor Cores", 5,  usage_multiplier=4.0),
        _s("Wakanda", "Vibranium (kg)",    10, stock_delta=-30.0),
        _s("Sokovia", "Vibranium (kg)",    15, stock_delta=-60.0, stock_multiplier=0.4),
        _s("Sokovia", "Pym Particles",     20, usage_multiplier=3.0),
        _s("Avengers Compound", "Medical Kits", 25, usage_multiplier=3.5),
        _s("Avengers Compound", "Arc Reactor Cores", 25, usage_multiplier=2.5),
        _s("Sokovia", "Clean Water (L)",   30, stock_delta=-500.0),
        _s("Wakanda", "Vibranium (kg)",    35, stock_delta=+40.0),
        _s("Sokovia", "Medical Kits",      40, usage_multiplier=0.5, stock_delta=+60.0),
        _s("Sokovia", "Vibranium (kg)",    50, usage_multiplier=0.2),
        _s("Sokovia", "Clean Water (L)",   60, stock_delta=+400.0),
        _s("Avengers Compound", "Medical Kits", 70, usage_multiplier=0.3),
    ],

    reports=[
        _r(0,  "Pietro Maximoff", "Sokovia",
           "Ultron is here. The city is moving. Vibranium reserves gone. "
           "We need evacuation NOW.", priority="Urgent"),
        _r(5,  "Wanda Maximoff", "Sokovia",
           "Civilians trapped on the north plateau. "
           "Medical supplies almost zero. Water cut off.", priority="Urgent"),
        _r(12, "Steve Rogers", "Sokovia",
           "Helicarrier inbound. Evacuating civilians. "
           "Vibranium completely stripped from city stockpiles.", priority="Urgent"),
        _r(20, "Tony Stark", "Avengers Compound",
           "Pulling arc reactor resources to power the evacuation platform. "
           "Expect drain on compound reserves.", priority="Routine"),
        _r(28, "T\'Challa", "Wakanda",
           "Wakanda releasing vibranium emergency cache to support Sokovia recovery.",
           priority="Routine"),
        _r(40, "Steve Rogers", "Sokovia",
           "City fragment neutralised. Survivors accounted for. "
           "Medical resupply convoy en route from New Asgard.", priority="Routine"),
        _r(55, "Bruce Banner", "Avengers Compound",
           "Hulk contained. Lab damaged. Resources at compound under strain "
           "but manageable.", priority="Routine"),
        _r(70, "Wanda Maximoff", "Sokovia",
           "Sokovia stabilised. Clean water being restored. "
           "Reconstruction aid from Wakanda and New Asgard arriving.", priority="Routine"),
    ],
)


# ── The Snap ─────────────────────────────────────────────────────────────────

THE_SNAP = Scenario(
    key="the_snap",
    name="The Snap",
    description=(
        "Thanos completes the Infinity Gauntlet and snaps his fingers. "
        "Half of all resources — and operatives — vanish instantly. "
        "All sectors record a catastrophic simultaneous shock."
    ),
    duration_minutes=60,

    shocks=[
        # T+0 — the snap: all resources halved simultaneously
        *[
            _s(sector, resource, 0, stock_multiplier=0.5, snap_event=True)
            for sector in SECTORS
            for resource in RESOURCES
        ],
        # T+10 — chaos: usage rates spike as survivors scramble
        *[
            _s(sector, resource, 10, usage_multiplier=3.0)
            for sector in SECTORS
            for resource in RESOURCES
        ],
        # T+20 — some sectors stabilise faster than others
        _s("Wakanda",    "Medical Kits",   20, usage_multiplier=0.6),
        _s("New Asgard", "Medical Kits",   20, usage_multiplier=0.6),
        _s("Wakanda",    "Vibranium (kg)", 20, usage_multiplier=0.4),
        # T+35 — Avengers Compound triage teams deployed
        _s("Avengers Compound", "Medical Kits",      35, usage_multiplier=0.3, stock_delta=+50.0),
        _s("Avengers Compound", "Clean Water (L)",   35, usage_multiplier=0.4),
        # T+50 — global aid begins
        *[
            _s(sector, resource, 50, usage_multiplier=0.25)
            for sector in SECTORS
            for resource in ["Medical Kits", "Clean Water (L)"]
        ],
    ],

    reports=[
        _r(0, "Tony Stark", "Avengers Compound",
           "Something happened. Half the team just disappeared. "
           "I don't — Peter. Spider-Man is gone. "
           "Compound sensors showing ALL resource levels halved. "
           "This is Thanos.", priority="Urgent"),
        _r(1, "Steve Rogers", "Avengers Compound",
           "Thanos has done it. Half of everything. Half of everyone. "
           "Medical bay is overwhelmed — we need every kit we have left.",
           priority="Urgent"),
        _r(2, "Thor Odinson", "New Asgard",
           "Half of New Asgard is gone. The people… the supplies. "
           "I should have gone for the head.",
           priority="Urgent"),
        _r(3, "Okoye", "Wakanda",
           "Wakanda is affected. Half our warriors gone. "
           "Vibranium stockpiles halved. Mobilising remaining forces. "
           "T\'Challa... T\'Challa is gone.",
           priority="Urgent"),
        _r(5, "Natasha Romanoff", "Avengers Compound",
           "Casualty reports coming in from every sector. "
           "Supply chains collapsed. We need a global audit immediately.",
           priority="Urgent"),
        _r(15, "Bruce Banner", "Avengers Compound",
           "Hulk is all that is left. Starting triage on compound. "
           "Arc reactor cores stable for now. Medical situation critical.",
           priority="Routine"),
        _r(25, "Rocket Raccoon", "Avengers Compound",
           "Groot is gone. Running diagnostics. "
           "Compound resources at 50% across the board. "
           "We need a plan.",
           priority="Routine"),
        _r(35, "Steve Rogers", "Avengers Compound",
           "Triage teams deployed. Compound operational at reduced capacity. "
           "Requesting emergency medical resupply from all remaining facilities.",
           priority="Routine"),
        _r(50, "Natasha Romanoff", "Avengers Compound",
           "Global aid networks activating. "
           "All remaining sectors beginning coordinated recovery operations. "
           "We do not stop.",
           priority="Routine"),
    ],
)


# ─────────────────────────────────────────────────────────────────────────────
# Registry
# ─────────────────────────────────────────────────────────────────────────────

SCENARIOS: dict[str, Scenario] = {
    s.key: s for s in [CHITAURI_INVASION, SOKOVIA_INCIDENT, THE_SNAP]
}


# ─────────────────────────────────────────────────────────────────────────────
# Simulation engine
# ─────────────────────────────────────────────────────────────────────────────

def _initial_state(scenario: Scenario) -> dict[tuple[str, str], list[float]]:
    """
    Build the starting stock state as {(sector, resource): [stock, usage_rate]}.
    Scenario overrides take priority; defaults fill the rest.
    """
    state: dict[tuple[str, str], list[float]] = {}
    for sector in SECTORS:
        for resource in RESOURCES:
            stock = (
                scenario.initial_stock.get(sector, {}).get(resource)
                or DEFAULT_INITIAL_STOCK[resource]
            )
            usage = (
                scenario.initial_usage.get(sector, {}).get(resource)
                or DEFAULT_USAGE_RATE[resource]
            )
            # Small per-sector noise so curves look distinct
            noise = random.uniform(0.85, 1.15)
            state[(sector, resource)] = [round(stock * noise, 2), round(usage * noise, 2)]
    return state


def build_telemetry_timeline(
    scenario: Scenario,
    base_time: datetime,
) -> list[dict[str, Any]]:
    """
    Step through the scenario minute-by-minute at TICK_INTERVAL_MINUTES cadence.
    Apply shocks at their scheduled minutes.

    Returns a list of dicts matching the telemetry_readings CSV schema.
    """
    state = _initial_state(scenario)
    rows: list[dict[str, Any]] = []

    # Group shocks by tick boundary for efficient lookup
    shock_index: dict[int, list[Shock]] = {}
    for shock in scenario.shocks:
        bucket = int(shock.at_minute // TICK_INTERVAL_MINUTES) * TICK_INTERVAL_MINUTES
        shock_index.setdefault(bucket, []).append(shock)

    minute = 0.0
    while minute <= scenario.duration_minutes:
        ts = base_time + timedelta(minutes=minute)
        snap_detected = False

        # Apply any shocks at this tick
        for shock in shock_index.get(int(minute), []):
            key = (shock.sector, shock.resource)
            if key not in state:
                continue
            stock, usage = state[key]
            stock = max(0.0, stock * shock.stock_multiplier + shock.stock_delta)
            usage = round(usage * shock.usage_multiplier, 4)
            state[key] = [round(stock, 2), usage]
            if shock.snap_event:
                snap_detected = True

        # Decay all stocks by usage and emit a row
        for (sector, resource), (stock, usage) in state.items():
            elapsed_h = TICK_INTERVAL_MINUTES / 60.0
            new_stock = max(0.0, stock - usage * elapsed_h + random.uniform(-1.0, 1.0))
            state[(sector, resource)] = [round(new_stock, 2), usage]

            rows.append({
                "timestamp": ts.isoformat(),
                "sector_id": sector,
                "resource_type": resource,
                "stock_level": round(new_stock, 2),
                "usage_rate_hourly": usage,
                "snap_event_detected": "True" if snap_detected else "False",
            })

        minute += TICK_INTERVAL_MINUTES

    return rows


def build_report_timeline(
    scenario: Scenario,
    base_time: datetime,
) -> list[dict[str, Any]]:
    """
    Convert ReportTemplate list to field_intel_reports.json-compatible dicts
    with ISO timestamps relative to base_time.
    """
    reports = []
    for tmpl in sorted(scenario.reports, key=lambda r: r.at_minute):
        ts = base_time + timedelta(minutes=tmpl.at_minute)
        reports.append({
            "report_id": str(uuid.uuid4()),
            "timestamp": ts.isoformat(),
            "metadata": {
                "hero_alias": tmpl.hero_alias,
                "secure_contact": tmpl.secure_contact or "",
            },
            "raw_text": tmpl.text,
            "priority": tmpl.priority,
            # extra fields used by the direct-post path
            "_sector": tmpl.sector,
            "_at_minute": tmpl.at_minute,
        })
    return reports


# ─────────────────────────────────────────────────────────────────────────────
# Output handlers
# ─────────────────────────────────────────────────────────────────────────────

def dump_to_files(
    scenario: Scenario,
    telemetry_rows: list[dict],
    report_rows: list[dict],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    # CSV telemetry
    csv_path = output_dir / f"{scenario.key}_telemetry.csv"
    fieldnames = ["timestamp", "sector_id", "resource_type",
                  "stock_level", "usage_rate_hourly", "snap_event_detected"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(telemetry_rows)
    log.info("Wrote %d telemetry rows → %s", len(telemetry_rows), csv_path)

    # JSON reports (strip internal _-prefixed keys)
    clean_reports = [
        {k: v for k, v in r.items() if not k.startswith("_")}
        for r in report_rows
    ]
    json_path = output_dir / f"{scenario.key}_reports.json"
    json_path.write_text(json.dumps(clean_reports, indent=2))
    log.info("Wrote %d reports → %s", len(clean_reports), json_path)


def _rabbitmq_channel(rabbitmq_url: str):
    params = pika.URLParameters(rabbitmq_url)
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type="fanout", durable=True)
    return conn, ch


def publish_telemetry_tick(ch, rows: list[dict]) -> None:
    """Publish one tick's worth of telemetry rows as individual RabbitMQ messages."""
    for row in rows:
        msg = {
            "timestamp": int(
                datetime.fromisoformat(row["timestamp"]).timestamp() * 1000
            ),
            "resource": row["resource_type"],
            "sector": row["sector_id"],
            "value": row["stock_level"],
            "metric": "",
            "forecast": {
                "slope": -row["usage_rate_hourly"],
                "confidence_band": 0.08,
                "critical_threshold": 10,
                "horizon_hours": 24,
            },
        }
        ch.basic_publish(
            exchange=RABBITMQ_EXCHANGE,
            routing_key="",
            body=json.dumps(msg),
            properties=pika.BasicProperties(expiration="300000"),
        )


def post_report(api_url: str, report: dict) -> bool:
    """POST a report to the FastAPI backend using the direct (hero_alias) path."""
    try:
        resp = requests.post(
            f"{api_url}/api/reports",
            json={
                "hero_alias": report["metadata"]["hero_alias"],
                "sector": report.get("_sector", "Avengers Compound"),
                "event_description": report["raw_text"],
                "secure_contact": report["metadata"].get("secure_contact") or None,
                "priority": report["priority"],
                # required by FrontendReportRequest schema
                "description": report["raw_text"],
            },
            timeout=30,
        )
        resp.raise_for_status()
        return True
    except Exception as exc:
        log.warning("Report POST failed: %s", exc)
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Live playback engine
# ─────────────────────────────────────────────────────────────────────────────

def run_live(
    scenario: Scenario,
    telemetry_rows: list[dict],
    report_rows: list[dict],
    speed: float,
    api_url: str | None,
    rabbitmq_url: str | None,
) -> None:
    """
    Replay the generated timeline in real time.

    speed = scenario-minutes per real second.
    e.g. speed=60 → 1 real second = 1 scenario minute.
    """
    real_tick_interval = (TICK_INTERVAL_MINUTES / speed)  # seconds

    # Group telemetry rows by their ISO timestamp (one group = one tick)
    tick_groups: dict[str, list[dict]] = {}
    for row in telemetry_rows:
        tick_groups.setdefault(row["timestamp"], []).append(row)
    sorted_ticks = sorted(tick_groups.items())

    # Index reports by at_minute for quick lookup
    report_queue = sorted(report_rows, key=lambda r: r["_at_minute"])
    report_ptr = 0

    # Establish RabbitMQ channel once if needed
    rmq_conn = rmq_ch = None
    if rabbitmq_url:
        try:
            rmq_conn, rmq_ch = _rabbitmq_channel(rabbitmq_url)
            log.info("Connected to RabbitMQ at %s", rabbitmq_url)
        except Exception as exc:
            log.warning("RabbitMQ connection failed (%s) — telemetry will be skipped", exc)

    total_ticks = len(sorted_ticks)
    total_reports = len(report_queue)
    log.info(
        "Playback start: %s | speed=%.0fx | %d ticks | %d reports | tick_interval=%.1fs",
        scenario.name, speed, total_ticks, total_reports, real_tick_interval,
    )

    start_real = time.monotonic()
    scenario_minute = 0.0

    for tick_idx, (tick_ts, tick_rows) in enumerate(sorted_ticks):
        tick_scenario_minute = tick_idx * TICK_INTERVAL_MINUTES

        # Emit any reports that fall before this tick
        while report_ptr < len(report_queue):
            rpt = report_queue[report_ptr]
            if rpt["_at_minute"] <= tick_scenario_minute:
                hero = rpt["metadata"]["hero_alias"]
                if api_url:
                    ok = post_report(api_url, rpt)
                    status = "✓" if ok else "✗"
                    log.info(
                        "[T+%05.1fm] REPORT %s  %-22s  %s — %s",
                        rpt["_at_minute"], status, f"({hero})", rpt["_sector"],
                        rpt["raw_text"][:60] + "…",
                    )
                else:
                    log.info(
                        "[T+%05.1fm] REPORT (no-api)  %-22s  %s — %s",
                        rpt["_at_minute"], f"({hero})", rpt["_sector"],
                        rpt["raw_text"][:60] + "…",
                    )
                report_ptr += 1
            else:
                break

        # Publish telemetry tick to RabbitMQ
        if rmq_ch:
            try:
                publish_telemetry_tick(rmq_ch, tick_rows)
            except Exception as exc:
                log.warning("RabbitMQ publish failed, reconnecting: %s", exc)
                try:
                    rmq_conn, rmq_ch = _rabbitmq_channel(rabbitmq_url)
                    publish_telemetry_tick(rmq_ch, tick_rows)
                except Exception:
                    rmq_ch = None

        resources_in_tick = len(set(r["sector_id"] for r in tick_rows))
        log.info(
            "[T+%05.1fm] TICK  %s  (%d sector×resource values)",
            tick_scenario_minute, tick_ts, len(tick_rows),
        )

        # Sleep until the next tick is due
        next_tick_real = start_real + (tick_idx + 1) * real_tick_interval
        sleep_s = next_tick_real - time.monotonic()
        if sleep_s > 0:
            time.sleep(sleep_s)

    # Flush any trailing reports
    while report_ptr < len(report_queue):
        rpt = report_queue[report_ptr]
        if api_url:
            post_report(api_url, rpt)
        log.info(
            "[T+%05.1fm] REPORT (tail)  %s  %s",
            rpt["_at_minute"], rpt["metadata"]["hero_alias"], rpt["raw_text"][:60] + "…",
        )
        report_ptr += 1

    if rmq_conn:
        try:
            rmq_conn.close()
        except Exception:
            pass

    elapsed = time.monotonic() - start_real
    log.info(
        "Playback complete.  Scenario: %.0f min | Real time: %.1f s (%.0f×)",
        scenario.duration_minutes, elapsed, scenario.duration_minutes * 60 / max(elapsed, 0.001),
    )


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def _list_scenarios() -> None:
    print("\nAvailable scenarios:\n")
    for key, sc in SCENARIOS.items():
        print(f"  {key:<24}  {sc.name}")
        print(f"  {'':24}  {sc.description[:80]}")
        print(f"  {'':24}  duration={sc.duration_minutes:.0f} min  "
              f"reports={len(sc.reports)}  shocks={len(sc.shocks)}")
        print()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Simulate a MCU scenario and push live data to EDITH.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--scenario", default="chitauri_invasion",
                        choices=list(SCENARIOS),
                        help="Scenario to simulate (default: chitauri_invasion)")
    parser.add_argument("--mode", default="both",
                        choices=["dump", "live", "both"],
                        help="Output mode (default: both)")
    parser.add_argument("--speed", type=float, default=60.0,
                        help="Scenario-minutes per real second (default: 60)")
    parser.add_argument("--output", default=None,
                        help="Directory for dump output (default: ./sim_output/<scenario>)")
    parser.add_argument("--api-url",
                        default=os.environ.get("EXTERNAL_BACKEND_URL", "http://localhost:8080"),
                        help="FastAPI base URL for report posting")
    parser.add_argument("--rabbitmq",
                        default=os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672"),
                        help="RabbitMQ AMQP URL")
    parser.add_argument("--list", action="store_true",
                        help="List available scenarios and exit")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducible runs")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%H:%M:%S",
    )

    if args.list:
        _list_scenarios()
        return

    if args.seed is not None:
        random.seed(args.seed)

    scenario = SCENARIOS[args.scenario]
    base_time = datetime.now(timezone.utc)

    log.info("═" * 60)
    log.info("Scenario : %s", scenario.name)
    log.info("Mode     : %s", args.mode)
    log.info("Speed    : %.0f×  (1 real sec = %.1f scenario min)",
             args.speed, args.speed)
    log.info("Reports  : %d  |  Shocks: %d  |  Duration: %.0f min",
             len(scenario.reports), len(scenario.shocks), scenario.duration_minutes)
    log.info("═" * 60)

    log.info("Building timeline…")
    telemetry_rows = build_telemetry_timeline(scenario, base_time)
    report_rows    = build_report_timeline(scenario, base_time)
    log.info("Timeline ready: %d telemetry rows, %d reports", len(telemetry_rows), len(report_rows))

    output_dir = Path(args.output or f"sim_output/{scenario.key}")

    if args.mode in ("dump", "both"):
        dump_to_files(scenario, telemetry_rows, report_rows, output_dir)

    if args.mode in ("live", "both"):
        # Determine whether to skip API / RabbitMQ if clearly unavailable
        api_url     = args.api_url if args.mode in ("live", "both") else None
        rabbitmq_url = args.rabbitmq

        run_live(
            scenario=scenario,
            telemetry_rows=telemetry_rows,
            report_rows=report_rows,
            speed=args.speed,
            api_url=api_url,
            rabbitmq_url=rabbitmq_url,
        )


if __name__ == "__main__":
    main()
