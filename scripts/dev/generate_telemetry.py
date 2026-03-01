#!/usr/bin/env python3
"""
generate_telemetry.py — Generate historical_avengers_data.csv

90-day, hourly time series for 5 sectors × 5 resources = 25 series × 2160 ticks = 54,000 rows.

Timeline:
  END = current UTC hour (so the latest data point is always "now")
  START = END − 90 days
  Days  0–35  (40 %): Normal economic activity — stable stocks, regular resupply
  Days 36–89  (60 %): Event X "Operation Crimson Siege" — progressive multi-front
                       attack on SHIELD supply infrastructure

Economic model:
  • stock[t+1] = max(0, stock[t] − usage[t] + resupply[t])
  • usage[t]   = base_rate × day_night_factor × event_multiplier + gaussian_noise
  • resupply[t] = scheduled delivery (skipped with rising probability during event)
  • Emergency cache: 4 % chance per hour if stock < 8 % of initial and deep in event

The fields_intel_reports.json captures reports from day 88–89, when the crisis is
at its peak.  Harder-hit sector×resource pairs (more reports) are calibrated to
reach critically low levels (≈5–15 % of initial) by then.

Output columns:
  timestamp, sector_id, resource_type, stock_level, usage_rate_hourly, snap_event_detected
"""

import csv
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ── Reproducibility ───────────────────────────────────────────────────────────
RNG = random.Random(20250301)

# ── Time constants ────────────────────────────────────────────────────────────
# END is always the current UTC hour so the last data point is always "now".
END         = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0, tzinfo=None)
TOTAL_DAYS  = 90
START       = END - timedelta(days=TOTAL_DAYS)
NORMAL_DAYS = 36      # days 0–35 (40 %)
EVENT_START = NORMAL_DAYS * 24   # tick index where event begins (864)
TOTAL_TICKS = TOTAL_DAYS * 24    # 2160

# snap_event_detected becomes True once we are ≥18 days into the event period
SNAP_THRESHOLD_TICK = EVENT_START + 18 * 24  # tick 1296

# ── Domain constants ──────────────────────────────────────────────────────────
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

# Local UTC offset per sector — drives daily consumption cycle
TZ_OFFSET = {
    "Avengers Compound": -5,   # US Eastern
    "New Asgard":         1,   # Norway
    "Sanctum Sanctorum": -5,   # NYC
    "Sokovia":            1,   # Central Europe
    "Wakanda":            3,   # East Africa
}

# ── Economic parameters ───────────────────────────────────────────────────────

# Base hourly usage rate in normal period (units/hour).
# Sized so that initial stock lasts ~120 days without any resupply.
# Resupply is calibrated to match this rate → equilibrium in normal period.
BASE_USAGE = {
    ("Avengers Compound", "Arc Reactor Cores"): 0.60,
    ("Avengers Compound", "Clean Water (L)"):  80.0,
    ("Avengers Compound", "Medical Kits"):      4.5,
    ("Avengers Compound", "Pym Particles"):     0.45,
    ("Avengers Compound", "Vibranium (kg)"):    0.50,

    ("New Asgard",        "Arc Reactor Cores"): 0.35,
    ("New Asgard",        "Clean Water (L)"):  60.0,
    ("New Asgard",        "Medical Kits"):      3.5,
    ("New Asgard",        "Pym Particles"):     0.22,
    ("New Asgard",        "Vibranium (kg)"):    0.16,

    ("Sanctum Sanctorum", "Arc Reactor Cores"): 0.40,
    ("Sanctum Sanctorum", "Clean Water (L)"):  45.0,
    ("Sanctum Sanctorum", "Medical Kits"):      2.8,
    ("Sanctum Sanctorum", "Pym Particles"):     0.52,  # highest — R&D hub + tactical
    ("Sanctum Sanctorum", "Vibranium (kg)"):    0.25,

    ("Sokovia",           "Arc Reactor Cores"): 0.30,
    ("Sokovia",           "Clean Water (L)"):  40.0,
    ("Sokovia",           "Medical Kits"):      3.2,
    ("Sokovia",           "Pym Particles"):     0.17,
    ("Sokovia",           "Vibranium (kg)"):    0.14,

    ("Wakanda",           "Arc Reactor Cores"): 0.50,
    ("Wakanda",           "Clean Water (L)"):  90.0,
    ("Wakanda",           "Medical Kits"):      5.2,
    ("Wakanda",           "Pym Particles"):     0.37,
    ("Wakanda",           "Vibranium (kg)"):    1.50,  # large domestic mining throughput
}

# Initial stocks: base_usage × 24 h × 120 days (slightly rounded)
# Wakanda Vibranium gets a larger reserve as the source nation.
def _initial(sector: str, resource: str) -> float:
    u = BASE_USAGE[(sector, resource)]
    days = 200 if (sector == "Wakanda" and resource == "Vibranium (kg)") else 120
    return round(u * 24 * days, 1)

INITIAL_STOCK = {
    (s, r): _initial(s, r) for s in SECTORS for r in RESOURCES
}

# Resupply cadence (hours between deliveries) and amount per delivery.
# Amount ≈ usage_rate × period → keeps stock roughly level in normal period.
RESUPPLY_PERIOD = {
    "Arc Reactor Cores": 14 * 24,   # fortnightly
    "Clean Water (L)":   5  * 24,   # every 5 days (large tankers)
    "Medical Kits":      12 * 24,   # every 12 days
    "Pym Particles":     12 * 24,   # every 12 days
    "Vibranium (kg)":    14 * 24,   # fortnightly (except Wakanda mine)
}

def _resupply_amount(sector: str, resource: str) -> float:
    period = RESUPPLY_PERIOD[resource]
    if sector == "Wakanda" and resource == "Vibranium (kg)":
        period = 7 * 24  # mine ships weekly
    return round(BASE_USAGE[(sector, resource)] * period * 1.02, 1)  # 2% surplus keeps stock healthy

RESUPPLY_AMOUNT = {
    (s, r): _resupply_amount(s, r) for s in SECTORS for r in RESOURCES
}

# Event impact parameters per (sector, resource).
#   peak_mult   — usage multiplier at peak of event (reached via sigmoid ramp)
#   keep_prob   — fraction of scheduled resupplies that actually arrive during event
#   lag_hours   — hours after event start before this pair is first affected
#
# Calibration target (final stock as % of initial at day 89):
#   ~5–10 %  → Sanctum Pym (×6), Wakanda Water (×4), Sanctum Arc (×3.5)
#   ~10–20 % → New Asgard Water, Sokovia Med, Avengers Med/Water
#   ~20–35 % → remaining heavily-reported pairs
#   ~40–65 % → lightly affected pairs (few or no reports)
EVENT = {
    # ── Avengers Compound ────────────────────────────────────────────────────
    ("Avengers Compound", "Arc Reactor Cores"):
        {"peak_mult": 4.5,  "keep_prob": 0.20, "lag": 2  * 24},
    ("Avengers Compound", "Clean Water (L)"):
        # Sigmoid avg ≈ 35% of ramp → need peak_mult ≈ formula_result × 1.4
        {"peak_mult": 5.0,  "keep_prob": 0.12, "lag": 5  * 24},
    ("Avengers Compound", "Medical Kits"):
        {"peak_mult": 7.0,  "keep_prob": 0.12, "lag": 1  * 24},
    ("Avengers Compound", "Pym Particles"):
        {"peak_mult": 6.0,  "keep_prob": 0.15, "lag": 3  * 24},
    ("Avengers Compound", "Vibranium (kg)"):
        # Wakanda siege cuts imports; combat uses up stockpile
        {"peak_mult": 4.2,  "keep_prob": 0.09, "lag": 8  * 24},

    # ── New Asgard ───────────────────────────────────────────────────────────
    ("New Asgard",        "Arc Reactor Cores"):
        {"peak_mult": 4.2,  "keep_prob": 0.25, "lag": 7  * 24},
    ("New Asgard",        "Clean Water (L)"):
        {"peak_mult": 5.5,  "keep_prob": 0.10, "lag": 4  * 24},
    ("New Asgard",        "Medical Kits"):
        {"peak_mult": 6.5,  "keep_prob": 0.15, "lag": 3  * 24},
    ("New Asgard",        "Pym Particles"):
        {"peak_mult": 6.0,  "keep_prob": 0.14, "lag": 8  * 24},
    ("New Asgard",        "Vibranium (kg)"):
        {"peak_mult": 4.0,  "keep_prob": 0.08, "lag": 10 * 24},

    # ── Sanctum Sanctorum ────────────────────────────────────────────────────
    ("Sanctum Sanctorum", "Arc Reactor Cores"):
        {"peak_mult": 5.5,  "keep_prob": 0.14, "lag": 4  * 24},
    ("Sanctum Sanctorum", "Clean Water (L)"):
        {"peak_mult": 5.5,  "keep_prob": 0.08, "lag": 6  * 24},
    ("Sanctum Sanctorum", "Medical Kits"):
        {"peak_mult": 6.0,  "keep_prob": 0.16, "lag": 5  * 24},
    ("Sanctum Sanctorum", "Pym Particles"):
        # Most reported pair — very high peak, low resupply survival
        {"peak_mult": 9.0,  "keep_prob": 0.08, "lag": 2  * 24},
    ("Sanctum Sanctorum", "Vibranium (kg)"):
        {"peak_mult": 4.5,  "keep_prob": 0.10, "lag": 9  * 24},

    # ── Sokovia ─────────────────────────────────────────────────────────────
    # First to be hit (lag=0); most severe supply disruption
    ("Sokovia",           "Arc Reactor Cores"):
        {"peak_mult": 5.5,  "keep_prob": 0.10, "lag": 0},
    ("Sokovia",           "Clean Water (L)"):
        {"peak_mult": 7.0,  "keep_prob": 0.07, "lag": 0},
    ("Sokovia",           "Medical Kits"):
        # Complete depletion expected (10 reports, worst case) — emergency caches sustain
        {"peak_mult": 10.0, "keep_prob": 0.06, "lag": 0},
    ("Sokovia",           "Pym Particles"):
        {"peak_mult": 6.0,  "keep_prob": 0.18, "lag": 2  * 24},
    ("Sokovia",           "Vibranium (kg)"):
        {"peak_mult": 5.0,  "keep_prob": 0.09, "lag": 5  * 24},

    # ── Wakanda ──────────────────────────────────────────────────────────────
    ("Wakanda",           "Arc Reactor Cores"):
        {"peak_mult": 2.5,  "keep_prob": 0.42, "lag": 6  * 24},
    ("Wakanda",           "Clean Water (L)"):
        # Civil disruption and displacement — high demand, damaged infrastructure
        {"peak_mult": 6.0,  "keep_prob": 0.11, "lag": 4  * 24},
    ("Wakanda",           "Medical Kits"):
        {"peak_mult": 7.5,  "keep_prob": 0.13, "lag": 4  * 24},
    ("Wakanda",           "Pym Particles"):
        {"peak_mult": 2.0,  "keep_prob": 0.55, "lag": 10 * 24},
    ("Wakanda",           "Vibranium (kg)"):
        # Mine attacked — usage drops (halted production) but exports cease too
        # Non-Wakanda sectors' resupply collapsing is handled by their own keep_prob
        {"peak_mult": 0.65, "keep_prob": 0.18, "lag": 3  * 24},
}

# ── Helper functions ──────────────────────────────────────────────────────────

def day_night_factor(utc_tick: int, tz_offset: int, resource: str) -> float:
    """
    Smooth cosine daily cycle.  Peaks at 14:00 local (factor ≈ 1.0),
    minimum at 02:00 local (factor ≈ 0.62).
    Medical Kits are relatively flat (emergencies don't sleep) with an evening peak.
    """
    local_hour = (utc_tick % 24 + tz_offset) % 24
    if resource == "Medical Kits":
        return 0.82 + 0.18 * math.cos(math.pi * (local_hour - 20) / 12)
    return 0.81 + 0.19 * math.cos(2 * math.pi * (local_hour - 14) / 24)


def sigmoid_event_mult(event_tick: int, lag_hours: int,
                       peak_mult: float, total_event_ticks: int) -> float:
    """
    Sigmoid ramp from 1.0 → peak_mult over the event period.
    Inflection point at 45 % through the effective (post-lag) period → slow start,
    fast escalation in the middle, slight plateau toward the end.
    """
    if event_tick < lag_hours:
        return 1.0
    eff   = event_tick - lag_hours
    total = max(1, total_event_ticks - lag_hours)
    progress = eff / total
    x = (progress - 0.45) * 9.0   # stretch sigmoid to fill [0,1]
    s = 1.0 / (1.0 + math.exp(-x))
    mult = 1.0 + (peak_mult - 1.0) * s
    # For Wakanda Vibranium peak_mult < 1 → usage ramps *down*
    return mult


def add_noise(value: float, sigma_pct: float = 0.04) -> float:
    """Gaussian multiplicative noise (σ=4 % by default)."""
    return max(0.0, value * (1.0 + RNG.gauss(0, sigma_pct)))


def build_resupply_schedule(sector: str, resource: str) -> dict[int, float]:
    """
    Pre-generate all resupply delivery ticks for the 90-day window.

    During the event period each scheduled delivery is cancelled with
    probability (1 − keep_prob).  When stock is in emergency territory
    (< 8 % of initial), the keep_prob floor is raised to 0.40 for that
    delivery (representing emergency airlifts / cache discoveries) — this
    models the 'secured a cache' entries in field_intel_reports.json.
    """
    period = RESUPPLY_PERIOD[resource]
    if sector == "Wakanda" and resource == "Vibranium (kg)":
        period = 7 * 24

    amount     = RESUPPLY_AMOUNT[(sector, resource)]
    keep       = EVENT[(sector, resource)]["keep_prob"]
    lag        = EVENT[(sector, resource)]["lag"]
    init_stock = INITIAL_STOCK[(sector, resource)]

    schedule: dict[int, float] = {}

    # First delivery: random offset in [period/3, period] to stagger across sectors
    first_tick = int(RNG.uniform(period // 3, period))
    tick = first_tick

    while tick < TOTAL_TICKS:
        in_event = tick >= EVENT_START
        event_tick = tick - EVENT_START

        if in_event:
            # Dynamic keep probability — improves slightly in late crisis (exhaustion relief)
            progress = event_tick / (TOTAL_TICKS - EVENT_START)
            effective_keep = keep * (1.0 + 0.3 * progress)   # slightly more relief over time
            # Jitter the amount ±12 %
            delivery = amount * RNG.uniform(0.88, 1.12)
            if RNG.random() < effective_keep:
                schedule[tick] = delivery
        else:
            # Normal period: reliable delivery with ±10 % jitter on amount
            schedule[tick] = amount * RNG.uniform(0.90, 1.10)

        # Jitter next delivery by ±8 % of period
        next_gap = int(period * RNG.uniform(0.92, 1.08))
        tick += max(1, next_gap)

    return schedule


# ── Main simulation ───────────────────────────────────────────────────────────

def simulate() -> list[dict]:
    rows: list[dict] = []

    for sector in SECTORS:
        tz = TZ_OFFSET[sector]

        for resource in RESOURCES:
            stock       = INITIAL_STOCK[(sector, resource)]
            init_stock  = stock
            base        = BASE_USAGE[(sector, resource)]
            peak_mult   = EVENT[(sector, resource)]["peak_mult"]
            lag         = EVENT[(sector, resource)]["lag"]
            period      = RESUPPLY_PERIOD[resource]
            event_ticks = TOTAL_TICKS - EVENT_START  # 54 * 24 = 1296

            schedule = build_resupply_schedule(sector, resource)

            for tick in range(TOTAL_TICKS):
                ts = START + timedelta(hours=tick)

                # ── Usage rate this tick ────────────────────────────────────
                dn    = day_night_factor(tick, tz, resource)
                emult = 1.0
                if tick >= EVENT_START:
                    event_tick = tick - EVENT_START
                    emult = sigmoid_event_mult(event_tick, lag, peak_mult, event_ticks)

                usage = add_noise(base * dn * emult, sigma_pct=0.045)

                # ── Emergency cache discovery ───────────────────────────────
                # When in deep event crisis and stock critically low,
                # there's a small hourly chance of finding a hidden cache.
                # This models the 'secured a cache' reports.
                emergency = 0.0
                if (tick >= EVENT_START + 12 * 24          # at least 12 days into event
                        and stock < 0.08 * init_stock      # below 8 % of initial
                        and RNG.random() < 0.04):          # 4 % per-hour chance
                    emergency = init_stock * RNG.uniform(0.06, 0.12)  # 6–12 % cache

                # ── Scheduled resupply ──────────────────────────────────────
                resupply = schedule.get(tick, 0.0) + emergency

                # ── Update stock ────────────────────────────────────────────
                stock = max(0.0, stock - usage + resupply)

                # ── snap_event_detected ─────────────────────────────────────
                snap = (tick >= SNAP_THRESHOLD_TICK
                        and stock < 0.30 * init_stock)

                rows.append({
                    "timestamp":           ts.strftime("%Y-%m-%dT%H:%M:%S"),
                    "sector_id":           sector,
                    "resource_type":       resource,
                    "stock_level":         round(stock, 3),
                    "usage_rate_hourly":   round(usage, 4),
                    "snap_event_detected": snap,
                })

    return rows


# ── Output ────────────────────────────────────────────────────────────────────

def main() -> None:
    out = Path(__file__).parent.parent.parent / "plan" / "info" / "historical_avengers_data.csv"
    out.parent.mkdir(parents=True, exist_ok=True)

    print("Simulating 90-day telemetry (2160 ticks × 25 series = 54,000 rows)…")
    rows = simulate()

    fieldnames = ["timestamp", "sector_id", "resource_type",
                  "stock_level", "usage_rate_hourly", "snap_event_detected"]

    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Written {len(rows):,} rows → {out}")

    # ── Sanity-check: final stock levels ─────────────────────────────────────
    print(f"\nFinal stock levels at day 89 ({END.date()}):")
    print(f"  {'Sector':<24} {'Resource':<22} {'Final':>10} {'Initial':>10} {'%':>7}")
    print("  " + "-" * 75)

    last = {}
    for r in rows:
        key = (r["sector_id"], r["resource_type"])
        last[key] = r   # last row wins (chronological)

    for sector in SECTORS:
        for resource in RESOURCES:
            key = (sector, resource)
            final   = last[key]["stock_level"]
            initial = INITIAL_STOCK[key]
            pct     = final / initial * 100
            flag    = " ◄ CRITICAL" if pct < 15 else (" ◄ LOW" if pct < 30 else "")
            print(f"  {sector:<24} {resource:<22} {final:>10.1f} {initial:>10.1f} {pct:>6.1f}%{flag}")

    snap_rows = sum(1 for r in rows if r["snap_event_detected"])
    print(f"\nsnap_event_detected=True rows: {snap_rows:,} / {len(rows):,}"
          f" ({snap_rows/len(rows)*100:.1f}%)")


if __name__ == "__main__":
    main()
