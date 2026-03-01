# Project Sentinel — System Architecture & Task Breakdown

> **Three core features. Everything else is additive. Ship these first.**

---

## The Three Features

### Feature A: "Danger Map" — Threat Ranking with Future Projection Slider
A ranked view of all sectors showing which is most critical right now. A time slider lets the commander drag into the future to see how the rankings shift based on projected depletion rates.

### Feature B: "Resource Timeline" — Stock + Usage Charts with Live Event Modifiers
Per-sector charts showing stock levels and usage rates over time. Field reports and snap events act as modifiers that visibly shift the forecast line in real time when processed.

### Feature C: "Field Intel Stream" — Anonymized Report Feed with Impact Popups
A live scrolling feed of processed field reports. Names are reverse-tokenized (not just "[REDACTED]" — they're replaced with reversible tokens like `[OPERATIVE-7F3A]`). Clicking a report shows a popup explaining how that event modified the forecast for the affected sector/resource.

---

## How They Connect

```
                    ┌──────────────────────────────┐
                    │     FEATURE A: Danger Map     │
                    │                               │
                    │  Reads: threat_score per       │
                    │  sector (computed from B + C)  │
                    │                               │
                    │  Slider calls forecast API     │
                    │  with future_hours param       │
                    └──────────┬───────────────────┘
                               │ threat_score uses
                               │ stock data + report data
        ┌──────────────────────┼──────────────────────┐
        │                      │                       │
        ▼                      ▼                       ▼
┌───────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  FEATURE B:   │    │   SHARED STATE   │    │  FEATURE C:     │
│  Resource     │◄──►│                  │◄──►│  Field Intel    │
│  Timeline     │    │  - stock levels  │    │  Stream         │
│               │    │  - usage rates   │    │                 │
│  Charts pull  │    │  - active mods   │    │  New report →   │
│  from DB +    │    │  - forecasts     │    │  redact → LLM   │
│  forecast API │    │                  │    │  → modifier →   │
│               │    │  WebSocket hub   │    │  pushes to B    │
│  Event mods   │    │  broadcasts      │    │                 │
│  shift the    │    │  state changes   │    │  Popup shows    │
│  forecast     │    │  to all features │    │  impact on B    │
│  line visibly │    │                  │    │                 │
└───────────────┘    └──────────────────┘    └─────────────────┘
```

**The data flow that ties them together:**

1. Feature C receives a new field report
2. Report goes through redaction pipeline (tokenization, not deletion)
3. Redacted text goes to LLM → extracts sector, resource, severity, event_type
4. The extracted data becomes a **modifier** that adjusts the forecast in Feature B
5. Feature B's updated forecast feeds into Feature A's threat score recalculation
6. All three features update via WebSocket — no page refresh

---

## Full System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (React + Vite)                     │
│                                                                      │
│  ┌──────────────┐  ┌───────────────────┐  ┌──────────────────────┐  │
│  │ Danger Map   │  │ Resource Timeline  │  │ Field Intel Stream   │  │
│  │              │  │                    │  │                      │  │
│  │ - Sector     │  │ - Recharts area    │  │ - Scrolling feed     │  │
│  │   cards      │  │   chart            │  │ - Report submission  │  │
│  │ - Threat     │  │ - Stock line       │  │   form               │  │
│  │   score      │  │ - Usage line       │  │ - Tokenized names    │  │
│  │ - Time       │  │ - Forecast cone    │  │ - Impact popup       │  │
│  │   slider     │  │ - Event markers    │  │ - Redaction diff     │  │
│  │ - Color      │  │ - Modifier arrows  │  │   viewer             │  │
│  │   coding     │  │ - Snap annotation  │  │                      │  │
│  └──────┬───────┘  └────────┬──────────┘  └──────────┬───────────┘  │
│         │                   │                         │              │
│         └───────────────────┼─────────────────────────┘              │
│                             │                                        │
│                      WebSocket Client                                │
│                      (socket.io-client)                              │
└─────────────────────────────┬────────────────────────────────────────┘
                              │
                              │ HTTP REST + WebSocket
                              │
┌─────────────────────────────▼────────────────────────────────────────┐
│                     BACKEND (Python FastAPI)                          │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                        API ROUTES                                │ │
│  │                                                                  │ │
│  │  GET  /api/sectors                  → all sectors + threat score  │ │
│  │  GET  /api/sectors/:id/forecast     → forecast at future hour T  │ │
│  │  GET  /api/telemetry                → stock + usage time series   │ │
│  │  GET  /api/telemetry/latest         → current readings per sector│ │
│  │  POST /api/reports                  → submit new field report    │ │
│  │  GET  /api/reports                  → processed report feed      │ │
│  │  GET  /api/reports/:id/impact       → what this report changed   │ │
│  │  GET  /api/modifiers                → active event modifiers     │ │
│  │  WS   /ws                           → real-time event stream     │ │
│  └──────────────────────────┬──────────────────────────────────────┘ │
│                             │                                        │
│  ┌──────────┐  ┌────────────▼───┐  ┌────────────┐  ┌─────────────┐ │
│  │FORECAST  │  │REPORT PIPELINE │  │THREAT      │  │ANOMALY      │ │
│  │SERVICE   │  │               │  │SCORER      │  │DETECTOR     │ │
│  │          │  │ 1. Tokenize   │  │            │  │             │ │
│  │ linear   │  │    PII        │  │ combines:  │  │ Z-score on  │ │
│  │ regress  │  │ 2. Redact     │  │ stock_pct  │  │ cross-sector│ │
│  │ + monte  │  │ 3. LLM call   │  │ burn_rate  │  │ correlation │ │
│  │ carlo    │  │ 4. Extract    │  │ report_den │  │             │ │
│  │          │  │    entities   │  │ supply_hlth│  │ flags snap  │ │
│  │ accepts  │  │ 5. Compute    │  │            │  │ events      │ │
│  │ modifier │  │    modifier   │  │ outputs    │  │             │ │
│  │ params   │  │ 6. Broadcast  │  │ 0-100 per  │  │             │ │
│  │          │  │    via WS     │  │ sector     │  │             │ │
│  └────┬─────┘  └──────┬───────┘  └─────┬──────┘  └──────┬──────┘ │
│       │               │                │                 │        │
│       └───────────────┼────────────────┼─────────────────┘        │
│                       │                │                           │
│                       ▼                ▼                           │
│              ┌─────────────────────────────────┐                  │
│              │         PostgreSQL               │                  │
│              │                                  │                  │
│              │  telemetry_readings              │                  │
│              │  reports                         │                  │
│              │  intel_extracted                 │                  │
│              │  event_modifiers                 │                  │
│              │  redaction_audit                 │                  │
│              │  token_vault (encrypted)         │                  │
│              └─────────────────────────────────┘                  │
└───────────────────────────────────────────────────────────────────┘
```

---

## The Modifier System (Core Mechanic)

This is the connective tissue between Feature B and Feature C. When a field report is processed, the LLM extracts structured data that becomes a **modifier** — a parameter adjustment to the forecast model.

### How modifiers work:

```
REPORT: "Heavy storm in Sector Alpha. Water supply route severed. No resupply expected for 48hrs."

LLM EXTRACTS:
{
  sector: "Sector Alpha",
  resource: "Clean Water",
  event_type: "SUPPLY_DISRUPTION",
  severity: 8,
  modifier: {
    type: "usage_rate_multiplier",    // or "resupply_halt", "stock_adjustment", "snap"
    value: 1.0,                       // no change to usage
    resupply_factor: 0.0,             // resupply drops to zero
    duration_hours: 48,               // for 48 hours
    confidence: 0.8                   // LLM's confidence in extraction
  }
}
```

### Modifier types your LLM should extract:

| Modifier Type | What It Does to Forecast | Triggered By |
|---|---|---|
| `usage_rate_multiplier` | Multiplies burn rate (1.5 = 50% faster depletion) | Combat, panic, population surge |
| `resupply_halt` | Sets resupply probability to 0 for N hours | Route destroyed, storm, siege |
| `resupply_boost` | Increases resupply probability/magnitude | Cache secured, convoy arrived |
| `stock_adjustment` | Directly adds/removes stock from current level | Explosion destroyed supplies, new cache found |
| `snap` | 50% stock cut + 5× volatility increase | Correlated multi-sector catastrophe |

### How Feature B visualizes modifiers:

The chart shows a forecast line projecting into the future. When a modifier arrives:

1. A vertical dashed line appears at the modifier's timestamp
2. The forecast line VISIBLY BENDS — the slope changes based on the modifier
3. A small annotation label explains the modifier: "⚠ Supply route severed — resupply halted 48hrs"
4. The confidence cone WIDENS because the modifier adds uncertainty
5. Old forecast (before modifier) shown as a faded ghost line so you can see the difference

### How Feature A uses modifiers:

The threat score recalculates whenever a modifier is applied:

```
threat_score(sector, future_hour) =
    0.30 × (1 - projected_stock_pct(future_hour, with_modifiers))
  + 0.25 × projected_burn_rate(future_hour, with_modifiers)
  + 0.25 × active_modifier_severity_sum
  + 0.20 × (1 - supply_chain_health)
```

When the slider moves to future_hour = +24, the threat scores recompute with all active modifiers projected forward. Sectors with active "resupply_halt" modifiers spike in danger. Sectors with "resupply_boost" modifiers improve.

---

## The Tokenization System (Feature C)

NOT simple redaction. Reversible tokenization that preserves analytical utility.

### How it works:

```
STEP 1 — TOKENIZE:
  Input:  "This is Agent Sarah Chen, 555-0147. Sector Alpha is out of fuel."
  Output: "This is [OPERATIVE-7F3A], [CONTACT-9B2E]. Sector Alpha is out of fuel."

STEP 2 — STORE TOKEN MAP (encrypted, server-side only):
  token_vault = {
    "OPERATIVE-7F3A": { real_value: "Agent Sarah Chen", type: "PERSON" },
    "CONTACT-9B2E":   { real_value: "555-0147", type: "PHONE" }
  }

STEP 3 — SEND TO LLM:
  Only the tokenized text leaves the server. LLM never sees real names.

STEP 4 — DISPLAY:
  Default view: tokens shown as styled badges [OPERATIVE-7F3A]
  Commander view (authenticated): can click token to reveal real name (fetched from vault)
```

### Redaction pipeline (3 layers):

```python
def tokenize_pii(text: str, report_id: str) -> tuple[str, list[dict]]:
    tokens = []

    # Layer 1: Regex — phone patterns
    # Catches: 555-0147, (555) 234-8891, 555-EAGLE-7
    phone_pattern = r'(\(?\d{3}\)?[-.\s]?[\w]{3,4}[-.\s]?[\w]{4,})'

    # Layer 2: Dictionary — known operative names from DB
    known_names = get_known_operatives()  # from token_vault or config

    # Layer 3: spaCy NER — catch unknown PERSON entities
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            # generate token, store in vault

    return tokenized_text, audit_log
```

### The Impact Popup (Feature C → Feature B connection):

When a user clicks a report in the feed, a popup shows:

```
┌─────────────────────────────────────────────────┐
│ REPORT #a691a8b2                                │
│ ─────────────────────────────────────────────── │
│ ORIGINAL (redacted):                            │
│ "Heavy combat in Sector Delta. [OPERATIVE-7F3A] │
│  reports Pym Particles supply chain severed."   │
│                                                 │
│ EXTRACTED:                                      │
│   Sector: Sector Delta                          │
│   Resource: Pym Particles                       │
│   Event: SUPPLY_DISRUPTION                      │
│   Severity: 8/10                                │
│                                                 │
│ IMPACT ON FORECAST:                             │
│   ▸ Pym Particles burn rate: +0% (unchanged)    │
│   ▸ Resupply probability: → 0% for 24hrs       │
│   ▸ Time-to-zero shifted: 72hrs → 31hrs        │
│   ▸ Sector Delta threat: 54 → 78 (+24)         │
│                                                 │
│ [mini chart showing forecast shift]             │
└─────────────────────────────────────────────────┘
```

---

## Database Schema

```sql
-- Core telemetry
CREATE TABLE telemetry_readings (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    sector_id VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    stock_level FLOAT NOT NULL,
    usage_rate_hourly FLOAT NOT NULL,
    sensor_id VARCHAR(20),
    snap_event BOOLEAN DEFAULT FALSE,
    resupply_event BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_telem_lookup ON telemetry_readings(sector_id, resource_type, timestamp);

-- Field reports
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    operative_id VARCHAR(20),
    raw_text TEXT NOT NULL,
    tokenized_text TEXT,             -- PII replaced with tokens
    priority VARCHAR(20),
    sector_origin VARCHAR(50),
    status VARCHAR(20) DEFAULT 'PENDING',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Token vault (PII stored encrypted)
CREATE TABLE token_vault (
    token_id VARCHAR(20) PRIMARY KEY,     -- e.g. "OPERATIVE-7F3A"
    report_id UUID REFERENCES reports(id),
    real_value TEXT NOT NULL,              -- encrypted at rest
    entity_type VARCHAR(20),              -- PERSON, PHONE, CALLSIGN, EMAIL
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- LLM extraction results
CREATE TABLE intel_extracted (
    id SERIAL PRIMARY KEY,
    report_id UUID REFERENCES reports(id),
    sector VARCHAR(50),
    resource VARCHAR(50),
    severity INT CHECK (severity BETWEEN 1 AND 10),
    event_type VARCHAR(30),
    summary TEXT,
    raw_llm_response JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Event modifiers (the bridge between reports and forecasts)
CREATE TABLE event_modifiers (
    id SERIAL PRIMARY KEY,
    report_id UUID REFERENCES reports(id),
    sector VARCHAR(50) NOT NULL,
    resource VARCHAR(50),               -- NULL = affects all resources in sector
    modifier_type VARCHAR(30) NOT NULL, -- usage_rate_multiplier, resupply_halt, etc.
    value FLOAT NOT NULL,
    duration_hours INT,
    confidence FLOAT,
    active BOOLEAN DEFAULT TRUE,
    starts_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_mod_active ON event_modifiers(sector, active, expires_at);

-- Redaction audit trail
CREATE TABLE redaction_audit (
    id SERIAL PRIMARY KEY,
    report_id UUID REFERENCES reports(id),
    original_fragment TEXT NOT NULL,
    token_replacement VARCHAR(20) NOT NULL,
    entity_type VARCHAR(20),
    detection_layer VARCHAR(20),        -- REGEX, DICTIONARY, NER
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## API Endpoints

### Feature A — Danger Map

```
GET /api/sectors
  Returns: [{ sector_id, current_threat_score, top_risk_resource, stock_summary }]
  Used by: initial render of danger map

GET /api/sectors/forecast?future_hours=24
  Returns: [{ sector_id, projected_threat_score, projected_stock_levels, active_modifiers }]
  Used by: when slider moves — recalculates threat with modifiers projected forward
  Computation: for each sector, run forecast model with all active modifiers applied
```

### Feature B — Resource Timeline

```
GET /api/telemetry?sector=X&resource=Y&from=T1&to=T2
  Returns: [{ timestamp, stock_level_avg, usage_rate_avg, sensor_confidence, snap_event }]
  Used by: historical portion of the chart
  Note: average across sensors, include confidence metric

GET /api/forecast/detailed?sector=X&resource=Y&hours_ahead=72
  Returns: {
    baseline: [{ hour, stock_projected }],
    with_modifiers: [{ hour, stock_projected }],
    confidence_band: [{ hour, p10, p50, p90 }],
    active_modifiers: [{ modifier_id, type, description, applied_at }]
  }
  Used by: forecast portion of the chart (the lines extending into the future)

GET /api/modifiers?sector=X&active=true
  Returns: [{ id, type, value, description, source_report_id, expires_at }]
  Used by: annotation markers on the chart
```

### Feature C — Field Intel Stream

```
POST /api/reports
  Body: { raw_text, priority, sector_origin }
  Returns: { report_id, status: "PENDING" }
  Triggers: the full pipeline (tokenize → LLM → modifier → broadcast)

GET /api/reports?limit=50&offset=0
  Returns: [{ report_id, timestamp, tokenized_text, priority, status, severity, event_type }]
  Used by: scrolling feed

GET /api/reports/:id/impact
  Returns: {
    extraction: { sector, resource, severity, event_type },
    modifier_applied: { type, value, duration },
    forecast_delta: { time_to_zero_before, time_to_zero_after, threat_score_delta },
    redaction_log: [{ original, token, layer }]
  }
  Used by: the impact popup

GET /api/tokens/:token_id (COMMANDER role only)
  Returns: { real_value, entity_type }
  Used by: clicking a token badge to reveal real name (auth-gated)
```

### WebSocket Events

```
WS /ws

Server → Client events:
  "report:status"     → { report_id, status: "REDACTING" | "PROCESSING" | "COMPLETE" }
  "report:processed"  → { report_id, extraction, modifier }
  "modifier:applied"  → { modifier_id, sector, resource, type, value }
  "threat:updated"    → { sector_id, new_threat_score, previous_score }
  "alert:snap"        → { affected_sectors, severity, timestamp }
```

---

## Tech Stack

| Component | Technology | Package/Version |
|---|---|---|
| **Frontend** | React 18 + Vite | `npm create vite@latest -- --template react` |
| Charts | Recharts | `recharts` — AreaChart, LineChart, ComposedChart |
| Real-time | Socket.IO client | `socket.io-client` |
| UI framework | Tailwind CSS | `tailwindcss` |
| State management | Zustand or React Context | `zustand` (lightweight, simple) |
| **Backend** | Python 3.11 + FastAPI | `fastapi`, `uvicorn` |
| WebSocket | FastAPI WebSocket + broadcast | built-in, or `python-socketio` for Socket.IO compat |
| ORM | SQLAlchemy 2.0 | `sqlalchemy[asyncio]` |
| **Database** | PostgreSQL 15 | local install or Docker |
| Migrations | Alembic | `alembic` |
| **PII/NLP** | spaCy | `spacy`, model: `en_core_web_sm` |
| Regex | Python `re` | built-in |
| Encryption | Fernet (symmetric) | `cryptography` — for token_vault |
| **LLM** | Claude or GPT-4o-mini | `anthropic` or `openai` SDK |
| **Forecasting** | NumPy + scikit-learn | `numpy`, `scikit-learn` |
| Monte Carlo | NumPy random | `numpy.random.normal` |

---

## Data Generation Spec

### telemetry.csv Requirements

```
Sectors (5):       Sector Alpha, Sector Bravo, Sector Charlie, Sector Delta, Sector Echo
Resources (5):     Clean Water (L), Medical Kits, Fuel (gal), Rations, Comms Equipment
Sensors per pair:  3 (sensor_A, sensor_B, sensor_C)

Mapping (each sector tracks 3 resources):
  Alpha:   Water, Medical, Fuel
  Bravo:   Medical, Fuel, Rations
  Charlie: Fuel, Rations, Comms
  Delta:   Water, Rations, Comms
  Echo:    Water, Medical, Comms

Starting stock: 500–2500 (varies by resource)
Time span: 14 days, hourly readings
Snap event: Day 3, hour 14:00 — hits Alpha, Bravo, Charlie simultaneously
Total rows: ~15,000 (5 sectors × 3 resources × 3 sensors × ~14 days × 24 hrs... sample/thin as needed)

Pre-snap behavior:
  - Smooth decline, usage mean=5, std=1.5
  - Sensor divergence std < 3% of mean
  - Small infrequent resupplies (every 8-12hrs, +30-80 units)

Post-snap behavior:
  - Net decline rate similar (~5/hr net)
  - Hour-to-hour delta std = 5-10× pre-snap (wild oscillation)
  - Resupply frequency increases but magnitude degrades over days
  - Sensor divergence spikes during snap, stays elevated after
  - Usage rate increases 25% when stock < 15% of starting level
```

### field_reports.json Requirements

```
Total: 200 reports
Timestamp range: Days 10–14 (last 4 days of telemetry)
Sectors referenced: same 5 sector names as telemetry
Resources referenced: same 5 resource names as telemetry

Template distribution:
  50 × "critically low" reports      (sector + resource + severity)
  40 × "supply chain disrupted"      (sector + resource + cause + duration)
  30 × "cache secured / resupply"    (sector + resource + positive event)
  40 × "situation dire"              (sector + resource + civilian impact)
  30 × "resource depleted" (PII)     (sector + resource + operative name + phone)
  10 × "anomaly detected"            (sector + threat type + precursor signal)

PII distribution (in raw_text body, not just metadata):
  60 reports with operative name in text
  60 reports with phone/callsign in text
  40 reports with BOTH name and phone
  140 reports with PII only in metadata

Cross-reference accuracy:
  ~80 reports reference sector-resource pairs that EXIST in telemetry (verifiable)
  ~80 reports reference pairs that DON'T exist in telemetry (blind spots)
  ~40 reports are ambiguous / general conditions

Priority intentionally wrong ~40% of the time
```

---

## Task Division (4-Person Team)

### Person 1: Frontend — Dashboard Shell + Feature A (Danger Map)

**Owns:** React app scaffold, routing, layout, Feature A component, WebSocket client

**Tasks:**
1. `npm create vite@latest` with React + Tailwind setup
2. Build the main dashboard layout (3-panel: danger map left, chart center, intel feed right)
3. Build `<DangerMap />` component:
   - Fetches `GET /api/sectors` on mount
   - Renders ranked sector cards with threat score, color-coded (green/yellow/orange/red)
   - Time slider (range input 0–72 hours) that calls `GET /api/sectors/forecast?future_hours=N`
   - Cards re-rank and re-color as slider moves
4. Set up Socket.IO client connection
   - Listen for `threat:updated` events → update sector cards in real-time
5. Shared state store (Zustand) for sectors, modifiers, selected sector

**Deliverables:** Working app shell with danger map that responds to slider and WebSocket updates.

---

### Person 2: Frontend — Feature B (Resource Timeline) + Feature C (Intel Stream)

**Owns:** Chart component, intel feed component, report submission form, impact popup

**Tasks:**
1. Build `<ResourceTimeline />` component:
   - Recharts `ComposedChart` with:
     - `AreaChart` for stock level (filled area)
     - `LineChart` for usage rate (secondary axis)
     - Dashed line for forecast projection
     - Shaded band for confidence interval (p10–p90)
     - Vertical annotation lines for modifier events with labels
     - Faded "ghost line" showing pre-modifier forecast
   - Dropdown selectors for sector + resource
   - Fetches `GET /api/telemetry` and `GET /api/forecast/detailed`
   - Listens for `modifier:applied` WebSocket event → re-fetches forecast
2. Build `<IntelStream />` component:
   - Scrolling feed of reports, newest at top
   - Each report card shows: timestamp, tokenized_text (with styled token badges), severity color, event_type icon
   - Token badges styled as `[OPERATIVE-7F3A]` with a distinct background color
3. Build `<ReportForm />` component:
   - Text input for raw_text, dropdowns for priority and sector
   - Submit → `POST /api/reports`
   - Show processing status animation: PENDING → REDACTING → PROCESSING → COMPLETE (driven by WebSocket `report:status` events)
4. Build `<ImpactPopup />` modal:
   - Triggered by clicking a report in the feed
   - Fetches `GET /api/reports/:id/impact`
   - Shows: extraction results, modifier applied, before/after forecast delta, redaction log with diff highlighting
   - Small inline mini-chart showing the forecast shift

**Deliverables:** Working charts that update when modifiers arrive, scrolling feed with popups.

---

### Person 3: Backend — API + Database + Forecast Engine

**Owns:** FastAPI app, all REST endpoints, PostgreSQL schema, forecast model, threat scorer

**Tasks:**
1. FastAPI project setup with SQLAlchemy models matching the schema above
2. Database seed script: load `telemetry.csv` → `telemetry_readings` table, load `field_reports.json` → `reports` table
3. Implement REST endpoints:
   - `GET /api/sectors` — aggregate latest telemetry, compute threat score
   - `GET /api/sectors/forecast?future_hours=N` — run forecast with active modifiers projected forward
   - `GET /api/telemetry` — query with filters, aggregate across sensors, return with confidence metric
   - `GET /api/forecast/detailed` — run Monte Carlo (100–500 sims), return baseline + modified + confidence bands
   - `GET /api/modifiers` — active modifiers query
   - `GET /api/reports` and `GET /api/reports/:id/impact`
4. Forecast service:
   - `forecast(sector, resource, hours_ahead, modifiers[])` function
   - Linear regression on last 48hrs for baseline slope
   - Monte Carlo: sample usage from normal(mean, std), apply modifiers at their start times, run N simulations
   - Return percentile bands
5. Threat scoring service:
   - `compute_threat(sector, future_hour)` using the formula above
6. WebSocket setup — broadcast events when reports are processed, modifiers applied, threats updated

**Deliverables:** Fully functional API that the frontend can call, with working forecast and threat calculations.

---

### Person 4: Backend — Report Pipeline + PII + LLM Integration + Data Generation

**Owns:** Redaction pipeline, LLM integration, modifier extraction, token vault, and generating both datasets

**Tasks:**
1. **Generate the datasets:**
   - Python script to create `telemetry.csv` with the spec above (pre-snap smooth, snap event, post-snap volatile, degrading resupply)
   - Python script to create `field_reports.json` from templates with proper PII distribution, cross-reference accuracy, and bad priority assignments
2. PII tokenization service:
   - `tokenize_pii(text, report_id) → (tokenized_text, audit_log)`
   - Layer 1: regex for phone patterns (numeric + alphanumeric callsigns)
   - Layer 2: dictionary of known operative names from `token_vault`
   - Layer 3: spaCy NER for unknown PERSON entities
   - Generate random token IDs (e.g., `OPERATIVE-` + 4 hex chars)
   - Store mapping in `token_vault` table (encrypted with Fernet)
   - Log each detection in `redaction_audit`
3. LLM integration service:
   - `extract_intel(tokenized_text) → { sector, resource, severity, event_type, modifier }`
   - Prompt engineering: system prompt that instructs the LLM to return JSON with modifier parameters
   - Error handling: retry on bad JSON, fallback to keyword extraction
   - Store result in `intel_extracted`
4. Modifier computation:
   - Based on LLM extraction, compute and store the appropriate modifier in `event_modifiers`
   - Map event_types to modifier_types:
     - `SUPPLY_DISRUPTION` → `resupply_halt` with duration from LLM
     - `DEPLETION` → `usage_rate_multiplier` of 1.3 (panic demand)
     - `RESUPPLY` → `resupply_boost`
     - `THREAT/ANOMALY` → `usage_rate_multiplier` of 1.5
5. Full pipeline orchestration:
   - `POST /api/reports` → tokenize → store → LLM extract → compute modifier → save modifier → broadcast via WebSocket

**Deliverables:** Generated datasets, working redaction with audit trail, LLM integration that produces modifiers.

---

## Integration Checkpoints

Before the final demo, verify these end-to-end flows:

```
□ Checkpoint 1: Person 3's API serves telemetry data → Person 2's chart renders it
□ Checkpoint 2: Person 4's seed script loads data → Person 3's DB serves it → Person 1's danger map shows sectors
□ Checkpoint 3: Person 2 submits report via form → Person 4's pipeline processes it → WebSocket event fires → Person 2's feed updates
□ Checkpoint 4: Person 4's pipeline produces modifier → Person 3's forecast incorporates it → Person 2's chart forecast line shifts → Person 1's threat scores update
□ Checkpoint 5: Full golden path: submit report → see it tokenized in feed → click for impact popup → chart bends → danger map re-ranks
```

---

## The 5-Minute Demo Script

```
[0:00 - 0:45] "Here's our Command & Control dashboard. On the left, sectors
               ranked by threat score. Sector Alpha is critical — the slider
               shows it hits zero in 18 hours. Center: the resource timeline
               showing stock depletion with our Monte Carlo forecast cone.
               Right: the live intel feed."

[0:45 - 2:00] "Watch what happens when a field report comes in."
               → Type/paste a report with PII into the form
               → Submit → show PENDING → REDACTING → PROCESSING → COMPLETE
               → Report appears in feed with tokenized names

[2:00 - 3:00] "Notice the chart just changed. The forecast line bent downward
               because this report told us the supply route to Sector Alpha
               was destroyed. Here's the modifier it generated."
               → Click report → show impact popup with before/after forecast
               → Point out the annotation on the chart

[3:00 - 4:00] "Now for security. Here's the original text with the operative's
               name and phone number. Here's what we sent to the AI — fully
               tokenized. And here's the audit log showing which layer caught
               each piece of PII. The AI never saw a real name."
               → Show redaction diff in the popup
               → Show audit log

[4:00 - 5:00] "And watch the danger map — Sector Alpha just jumped from 67
               to 84 threat score because of that single report. The slider
               shows it's now the #1 priority for the next 48 hours."
               → Move slider to show future projection shifting
               → Q&A
```