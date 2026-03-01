#!/usr/bin/env python3
"""
MCU Event Data Generator for SHIELD Resource Analysis
Generates realistic time-series CSV and field intel JSONL data for major MCU events
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import csv

LOCATIONS = [
    "Avengers Compound",
    "Sokovia",
    "Wakanda",
    "New Asgard",
    "Sanctum Sanctorum",
]

RESOURCES = [
    "Arc Reactor Cores",
    "Pym Particles",
    "Clean Water (L)",
    "Medical Kits",
    "Vibranium (kg)",
]

THREAT_LEVELS = ["LOW", "MODERATE", "HIGH", "CRITICAL"]

HEROES = {
    "Tony Stark": {"alias": "Iron Man", "contact": "555-0101 (Iron Line)"},
    "Steve Rogers": {"alias": "Captain America", "contact": "555-1941 (Shield Freq)"},
    "Thor Odinson": {"alias": "Thor", "contact": "555-GOD-OF-THUNDER"},
    "Bruce Banner": {"alias": "Hulk", "contact": "555-HULK-SMASH"},
    "Natasha Romanoff": {
        "alias": "Black Widow",
        "contact": "555-0199 (Black Widow Comms)",
    },
    "Clint Barton": {"alias": "Hawkeye", "contact": "555-ARROW-ONE"},
    "Wanda Maximoff": {"alias": "Scarlet Witch", "contact": "555-MIND-FLAY"},
    "Sam Wilson": {"alias": "Falcon", "contact": "555-WING-MAN"},
    "T'Challa": {"alias": "Black Panther", "contact": "555-WAKANDA-1"},
    "Carol Danvers": {"alias": "Captain Marvel", "contact": "555-SPACE-ST"},
    "Scott Lang": {"alias": "Ant-Man", "contact": "555-SIZE-CHANGE"},
    "Hope Van Dyne": {"alias": "Wasp", "contact": "555-WASP-DRON"},
    "Hank Pym": {"alias": "Original Ant-Man", "contact": "555-PYM-PART"},
}

EVENT_CONFIGS = {
    "chitauri_invasion": {
        "name": "Chitauri Invasion",
        "year": 2012,
        "start_date": datetime(2012, 5, 4, 8, 0, 0),
        "duration_hours": 48,
        "pre_event_hours": 24,
        "post_event_hours": 72,
        "primary_locations": ["Avengers Compound"],
        "affected_locations": ["Avengers Compound", "Sanctum Sanctorum"],
        "resource_impact": {
            "Arc Reactor Cores": {
                "consumption_multiplier": 8.0,
                "supply_disruption": 0.7,
            },
            "Pym Particles": {"consumption_multiplier": 2.0, "supply_disruption": 0.3},
            "Clean Water (L)": {
                "consumption_multiplier": 5.0,
                "supply_disruption": 0.6,
            },
            "Medical Kits": {"consumption_multiplier": 15.0, "supply_disruption": 0.8},
            "Vibranium (kg)": {"consumption_multiplier": 3.0, "supply_disruption": 0.4},
        },
        "hero_participation": [
            "Tony Stark",
            "Steve Rogers",
            "Thor Odinson",
            "Bruce Banner",
            "Natasha Romanoff",
            "Clint Barton",
        ],
        "priority_dist": {"Routine": 30, "High": 40, "Avengers Level Threat": 30},
    },
    "sokovia_attack": {
        "name": "Sokovia Attack (Ultron)",
        "year": 2015,
        "start_date": datetime(2015, 5, 1, 10, 0, 0),
        "duration_hours": 72,
        "pre_event_hours": 24,
        "post_event_hours": 96,
        "primary_locations": ["Sokovia"],
        "affected_locations": ["Sokovia", "Avengers Compound", "Sanctum Sanctorum"],
        "resource_impact": {
            "Arc Reactor Cores": {
                "consumption_multiplier": 12.0,
                "supply_disruption": 0.9,
            },
            "Pym Particles": {
                "consumption_multiplier": 10.0,
                "supply_disruption": 0.85,
            },
            "Clean Water (L)": {
                "consumption_multiplier": 8.0,
                "supply_disruption": 0.8,
            },
            "Medical Kits": {"consumption_multiplier": 20.0, "supply_disruption": 0.95},
            "Vibranium (kg)": {"consumption_multiplier": 6.0, "supply_disruption": 0.7},
        },
        "hero_participation": [
            "Tony Stark",
            "Steve Rogers",
            "Thor Odinson",
            "Bruce Banner",
            "Natasha Romanoff",
            "Clint Barton",
            "Wanda Maximoff",
        ],
        "priority_dist": {"Routine": 25, "High": 35, "Avengers Level Threat": 40},
    },
    "thanos_snap": {
        "name": "Thanos Snap (Infinity War)",
        "year": 2018,
        "start_date": datetime(2018, 10, 15, 14, 0, 0),
        "duration_hours": 168,
        "pre_event_hours": 24,
        "post_event_hours": 168,
        "primary_locations": ["Wakanda", "Avengers Compound"],
        "affected_locations": [
            "Avengers Compound",
            "Sokovia",
            "Wakanda",
            "New Asgard",
            "Sanctum Sanctorum",
        ],
        "resource_impact": {
            "Arc Reactor Cores": {
                "consumption_multiplier": 0.2,
                "supply_disruption": 0.95,
            },
            "Pym Particles": {"consumption_multiplier": 0.1, "supply_disruption": 0.98},
            "Clean Water (L)": {
                "consumption_multiplier": 0.3,
                "supply_disruption": 0.9,
            },
            "Medical Kits": {"consumption_multiplier": 0.4, "supply_disruption": 0.85},
            "Vibranium (kg)": {
                "consumption_multiplier": 0.2,
                "supply_disruption": 0.92,
            },
        },
        "hero_participation": [
            "T'Challa",
            "Bruce Banner",
            "Steve Rogers",
            "Thor Odinson",
        ],
        "priority_dist": {"Routine": 60, "High": 25, "Avengers Level Threat": 15},
    },
    "hulk_blip": {
        "name": "Hulk Blip (Endgame)",
        "year": 2023,
        "start_date": datetime(2023, 10, 1, 12, 0, 0),
        "duration_hours": 240,
        "pre_event_hours": 24,
        "post_event_hours": 168,
        "primary_locations": ["Avengers Compound"],
        "affected_locations": [
            "Avengers Compound",
            "Sokovia",
            "Wakanda",
            "New Asgard",
            "Sanctum Sanctorum",
        ],
        "resource_impact": {
            "Arc Reactor Cores": {
                "consumption_multiplier": 25.0,
                "supply_disruption": 0.8,
            },
            "Pym Particles": {
                "consumption_multiplier": 20.0,
                "supply_disruption": 0.75,
            },
            "Clean Water (L)": {
                "consumption_multiplier": 30.0,
                "supply_disruption": 0.85,
            },
            "Medical Kits": {"consumption_multiplier": 35.0, "supply_disruption": 0.9},
            "Vibranium (kg)": {
                "consumption_multiplier": 15.0,
                "supply_disruption": 0.7,
            },
        },
        "hero_participation": [
            "Tony Stark",
            "Steve Rogers",
            "Thor Odinson",
            "Bruce Banner",
            "Natasha Romanoff",
            "Carol Danvers",
            "T'Challa",
            "Sam Wilson",
        ],
        "priority_dist": {"Routine": 20, "High": 30, "Avengers Level Threat": 50},
    },
    "emergence": {
        "name": "The Emergence (Eternals)",
        "year": 2024,
        "start_date": datetime(2024, 11, 1, 6, 0, 0),
        "duration_hours": 48,
        "pre_event_hours": 24,
        "post_event_hours": 72,
        "primary_locations": ["Sanctum Sanctorum"],
        "affected_locations": ["Sanctum Sanctorum", "Avengers Compound", "Wakanda"],
        "resource_impact": {
            "Arc Reactor Cores": {
                "consumption_multiplier": 6.0,
                "supply_disruption": 0.5,
            },
            "Pym Particles": {"consumption_multiplier": 4.0, "supply_disruption": 0.4},
            "Clean Water (L)": {
                "consumption_multiplier": 10.0,
                "supply_disruption": 0.7,
            },
            "Medical Kits": {"consumption_multiplier": 12.0, "supply_disruption": 0.65},
            "Vibranium (kg)": {
                "consumption_multiplier": 5.0,
                "supply_disruption": 0.45,
            },
        },
        "hero_participation": ["Wanda Maximoff"],
        "priority_dist": {"Routine": 35, "High": 40, "Avengers Level Threat": 25},
    },
    "wakanda_forever": {
        "name": "Wakanda Forever",
        "year": 2024,
        "start_date": datetime(2024, 12, 15, 16, 0, 0),
        "duration_hours": 36,
        "pre_event_hours": 24,
        "post_event_hours": 72,
        "primary_locations": ["Wakanda"],
        "affected_locations": ["Wakanda", "Avengers Compound"],
        "resource_impact": {
            "Arc Reactor Cores": {
                "consumption_multiplier": 7.0,
                "supply_disruption": 0.6,
            },
            "Pym Particles": {"consumption_multiplier": 3.0, "supply_disruption": 0.35},
            "Clean Water (L)": {
                "consumption_multiplier": 9.0,
                "supply_disruption": 0.75,
            },
            "Medical Kits": {"consumption_multiplier": 18.0, "supply_disruption": 0.9},
            "Vibranium (kg)": {
                "consumption_multiplier": 25.0,
                "supply_disruption": 0.95,
            },
        },
        "hero_participation": ["T'Challa", "Steve Rogers", "Sam Wilson"],
        "priority_dist": {"Routine": 25, "High": 35, "Avengers Level Threat": 40},
    },
    "quantumania": {
        "name": "Quantumania (Kang)",
        "year": 2025,
        "start_date": datetime(2025, 8, 1, 10, 0, 0),
        "duration_hours": 60,
        "pre_event_hours": 24,
        "post_event_hours": 96,
        "primary_locations": ["Sanctum Sanctorum", "Avengers Compound"],
        "affected_locations": ["Sanctum Sanctorum", "Avengers Compound", "Wakanda"],
        "resource_impact": {
            "Arc Reactor Cores": {
                "consumption_multiplier": 15.0,
                "supply_disruption": 0.85,
            },
            "Pym Particles": {
                "consumption_multiplier": 30.0,
                "supply_disruption": 0.98,
            },
            "Clean Water (L)": {
                "consumption_multiplier": 7.0,
                "supply_disruption": 0.55,
            },
            "Medical Kits": {"consumption_multiplier": 10.0, "supply_disruption": 0.6},
            "Vibranium (kg)": {
                "consumption_multiplier": 8.0,
                "supply_disruption": 0.65,
            },
        },
        "hero_participation": [
            "Scott Lang",
            "Hope Van Dyne",
            "Steve Rogers",
            "Thor Odinson",
        ],
        "priority_dist": {"Routine": 30, "High": 35, "Avengers Level Threat": 35},
    },
}

BASE_INVENTORY = {
    "Arc Reactor Cores": 500,
    "Pym Particles": 250,
    "Clean Water (L)": 10000,
    "Medical Kits": 400,
    "Vibranium (kg)": 200,
}

BASE_CONSUMPTION = {
    "Arc Reactor Cores": 1.5,
    "Pym Particles": 1.0,
    "Clean Water (L)": 50.0,
    "Medical Kits": 3.0,
    "Vibranium (kg)": 0.5,
}

BASE_SUPPLY = {
    "Arc Reactor Cores": 2.0,
    "Pym Particles": 1.2,
    "Clean Water (L)": 60.0,
    "Medical Kits": 4.0,
    "Vibranium (kg)": 0.6,
}


def get_threat_level(
    days_remaining: float, consumption_rate: float, phase: str = "event"
) -> str:
    """Determine threat level based on days remaining and consumption rate"""
    if phase == "pre_event":
        return "LOW"
    if phase == "event":
        if days_remaining < 1.0:
            return "CRITICAL"
        elif days_remaining < 3.0:
            return "HIGH"
        elif days_remaining < 7.0:
            return "MODERATE"
    if days_remaining < 1.0:
        return "CRITICAL"
    elif days_remaining < 3.0:
        return "HIGH"
    elif days_remaining < 7.0:
        return "MODERATE"
    return "LOW"


def determine_event_phase(timestamp: datetime, config: Dict) -> str:
    """Determine if we're in pre-event, event, or post-event phase"""
    event_start = config["start_date"]
    pre_end = event_start
    event_end = event_start + timedelta(hours=config["duration_hours"])
    post_end = event_end + timedelta(hours=config["post_event_hours"])

    if timestamp < pre_end:
        return "pre_event"
    elif timestamp < event_end:
        return "event"
    elif timestamp < post_end:
        return "post_event"
    return "recovery"


def generate_csv_data(config: Dict, interval_minutes: int = 5) -> List[Dict]:
    """Generate time-series CSV data for an event"""
    rows = []

    total_hours = (
        config["pre_event_hours"]
        + config["duration_hours"]
        + config["post_event_hours"]
    )
    total_intervals = int(total_hours * 60 / interval_minutes)

    current_inventory = {
        loc: {res: BASE_INVENTORY[res] for res in RESOURCES} for loc in LOCATIONS
    }

    for i in range(total_intervals):
        timestamp = (
            config["start_date"]
            - timedelta(hours=config["pre_event_hours"])
            + timedelta(minutes=i * interval_minutes)
        )
        phase = determine_event_phase(timestamp, config)

        for location in LOCATIONS:
            for resource in RESOURCES:
                impact = config["resource_impact"][resource]

                if phase == "pre_event":
                    consumption = BASE_CONSUMPTION[resource] * (
                        0.9 + random.random() * 0.2
                    )
                    supply = BASE_SUPPLY[resource] * (0.9 + random.random() * 0.2)
                elif phase == "event":
                    is_affected = location in config["affected_locations"]
                    if is_affected:
                        multiplier = impact["consumption_multiplier"]
                        disruption = impact["supply_disruption"]
                        consumption = (
                            BASE_CONSUMPTION[resource]
                            * multiplier
                            * (0.7 + random.random() * 0.6)
                        )
                        supply = (
                            BASE_SUPPLY[resource]
                            * (1 - disruption)
                            * (0.5 + random.random() * 1.0)
                        )
                    else:
                        consumption = BASE_CONSUMPTION[resource] * (
                            0.8 + random.random() * 0.4
                        )
                        supply = BASE_SUPPLY[resource] * (0.8 + random.random() * 0.4)
                else:
                    multiplier = impact["consumption_multiplier"]
                    recovery_factor = min(
                        1.0, (i / (config["post_event_hours"] * 60 / interval_minutes))
                    )
                    consumption = (
                        BASE_CONSUMPTION[resource]
                        * (1 + (multiplier - 1) * recovery_factor * 0.3)
                        * (0.8 + random.random() * 0.4)
                    )
                    supply = BASE_SUPPLY[resource] * (0.8 + random.random() * 0.4)

                supply = max(0, supply)
                consumption = max(0, consumption)

                current_inventory[location][resource] = max(
                    0, current_inventory[location][resource] - consumption + supply
                )

                hours_in_interval = interval_minutes / 60
                net_consumption = consumption - supply
                if net_consumption > 0:
                    daily_consumption = net_consumption / hours_in_interval * 24
                    days_remaining = (
                        current_inventory[location][resource] / daily_consumption
                        if daily_consumption > 0
                        else float("inf")
                    )
                else:
                    days_remaining = 999.9
                days_remaining = min(days_remaining, 999.9)

                threat_level = get_threat_level(days_remaining, 0, phase)

                rows.append(
                    {
                        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        "location": location,
                        "resource_type": resource,
                        "inventory_level": round(
                            current_inventory[location][resource], 2
                        ),
                        "consumption_rate": round(consumption, 2),
                        "supply_rate": round(supply, 2),
                        "days_remaining": round(days_remaining, 2),
                        "threat_level": threat_level,
                    }
                )

    return rows


def generate_field_reports(
    config: Dict, csv_data: List[Dict], num_reports: int = 500
) -> List[Dict]:
    """Generate field intel reports based on the event data"""
    reports = []

    event_start = config["start_date"]
    event_end = event_start + timedelta(hours=config["duration_hours"])
    post_end = event_end + timedelta(hours=config["post_event_hours"])

    heroes = list(HEROES.keys())
    priority_dist = config["priority_dist"]

    keywords = {
        "critical": ["critically low", "urgent", "dire", "lose the perimeter"],
        "out": ["out of", "depleted", "empty", "exhausted"],
        "combat": [
            "heavy combat",
            "under attack",
            "hostiles",
            "supply chain is compromised",
        ],
        "supply": [
            "secured a cache",
            "resupplied",
            "reinforcements",
            "sending coordinates",
        ],
    }

    for _ in range(num_reports):
        timestamp = (
            event_start
            - timedelta(hours=config["pre_event_hours"])
            + timedelta(
                seconds=random.randint(
                    0,
                    int(
                        (
                            post_end
                            - event_start
                            + timedelta(hours=config["pre_event_hours"])
                        ).total_seconds()
                    ),
                )
            )
        )

        phase = determine_event_phase(timestamp, config)

        location = random.choice(config["affected_locations"])
        resource = random.choice(RESOURCES)

        if phase == "pre_event":
            priority = random.choices(
                ["Routine", "High", "Avengers Level Threat"], weights=[60, 30, 10]
            )[0]
            if random.random() < 0.3:
                raw_text = (
                    f"Normal operations at {location}. {resource} at adequate levels."
                )
            else:
                raw_text = (
                    f"Routine patrol complete at {location}. No anomalies detected."
                )
        elif phase == "event":
            priority = random.choices(
                ["Routine", "High", "Avengers Level Threat"],
                weights=[
                    priority_dist["Routine"],
                    priority_dist["High"],
                    priority_dist["Avengers Level Threat"],
                ],
            )[0]

            report_type = random.choices(
                ["critical", "out", "combat", "supply"], weights=[25, 20, 35, 20]
            )[0]

            if report_type == "critical":
                raw_text = f"Urgent: {location} is critically low on {resource}. The civilians are worried."
            elif report_type == "out":
                raw_text = f"Just a heads up, {location} is out of {resource}. This is {random.choice(heroes)}, call me back at {HEROES[random.choice(heroes)]['contact']}."
            elif report_type == "combat":
                raw_text = f"Heavy combat in {location}. {resource} supply chain is compromised. Need backup."
            else:
                raw_text = f"Status update from {location}. We secured a cache of {resource}. Sending coordinates now."
        else:
            priority = random.choices(
                ["Routine", "High", "Avengers Level Threat"], weights=[50, 35, 15]
            )[0]

            if random.random() < 0.4:
                raw_text = f"Recovery operations ongoing at {location}. {resource} levels stabilizing."
            else:
                raw_text = f"Post-event assessment complete at {location}. {resource} needs replenishment."

        hero = random.choice(heroes)

        reports.append(
            {
                "report_id": str(uuid.uuid4()),
                "metadata": {
                    "hero_alias": HEROES[hero]["alias"],
                    "secure_contact": HEROES[hero]["contact"],
                },
                "raw_text": raw_text,
                "timestamp": timestamp.isoformat(),
                "priority": priority,
            }
        )

    return sorted(reports, key=lambda x: x["timestamp"])


def save_csv_data(rows: List[Dict], filepath: str):
    """Save CSV data to file"""
    if not rows:
        return

    fieldnames = [
        "timestamp",
        "location",
        "resource_type",
        "inventory_level",
        "consumption_rate",
        "supply_rate",
        "days_remaining",
        "threat_level",
    ]

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated CSV with {len(rows)} rows: {filepath}")


def save_jsonl_data(reports: List[Dict], filepath: str):
    """Save JSONL data to file"""
    with open(filepath, "w") as f:
        for report in reports:
            f.write(json.dumps(report) + "\n")

    print(f"Generated JSONL with {len(reports)} reports: {filepath}")


def main():
    """Main function to generate all event data"""

    print("=" * 60)
    print("MCU EVENT DATA GENERATOR FOR SHIELD ANALYSIS")
    print("=" * 60)

    for event_key, config in EVENT_CONFIGS.items():
        print(f"\n{'=' * 60}")
        print(f"Generating data for: {config['name']} ({config['year']})")
        print(f"{'=' * 60}")

        interval_minutes = 5
        csv_data = generate_csv_data(config, interval_minutes)

        num_reports = max(500, len(csv_data) // 50)
        jsonl_data = generate_field_reports(config, csv_data, num_reports)

        base_dir = f"data/{event_key}"
        csv_path = f"{base_dir}/resource_timeseries.csv"
        jsonl_path = f"{base_dir}/field_intel_reports.jsonl"

        save_csv_data(csv_data, csv_path)
        save_jsonl_data(jsonl_data, jsonl_path)

        print(f"\nEvent Summary:")
        print(f"  - Start: {config['start_date'].strftime('%Y-%m-%d %H:%M')}")
        print(f"  - Duration: {config['duration_hours']} hours")
        print(f"  - Total CSV rows: {len(csv_data)}")
        print(f"  - Total JSONL reports: {len(jsonl_data)}")
        print(f"  - Primary locations: {', '.join(config['primary_locations'])}")
        print(f"  - Affected locations: {', '.join(config['affected_locations'])}")
        print(f"  - Heroes involved: {', '.join(config['hero_participation'][:3])}...")

    print("\n" + "=" * 60)
    print("ALL EVENT DATA GENERATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
