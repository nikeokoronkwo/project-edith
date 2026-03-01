# EDITH — Backend Operations Guide

All Python scripts run from the repo root (`26/`) with the virtualenv active:

```bash
source .venv/bin/activate
export DATABASE_URL="postgresql://edith_user:edith_password@localhost:5433/edith_db"
export RABBITMQ_URL="amqp://guest:guest@localhost:5672"
export ANTHROPIC_API_KEY="sk-..."   # required by llm_extractor
```

---

## Directory layout

```
backend/          Server source — imported modules and the two long-running processes
scripts/
  setup/          One-time initialisation (run once per fresh DB)
  pipeline/       Batch data-processing (run after seeding)
  dev/            Development & testing utilities
plan/info/        Source data files (JSON, CSV)
SCHEMA.sql        PostgreSQL schema definition
docker-compose.yml
```

---

## 1. Infrastructure (start once, leave running)

```bash
docker compose up -d   # PostgreSQL on :5433, RabbitMQ on :5672
```

---

## 2. Server startup (essential — must stay running)

These two processes form the live backend. Run each in its own terminal.

### API server
```bash
cd backend
uvicorn api:app --host 0.0.0.0 --port 8080
```

**What it does:** FastAPI app — REST endpoints for reports, events, analytics; also
calls the report pipeline on `POST /api/reports`.

**Files it depends on (never move these):**
- `backend/api.py` — entrypoint
- `backend/db.py` — PostgreSQL helpers
- `backend/pipeline.py` — orchestrates tokenizer → LLM extractor
- `backend/tokenizer.py` — PII redaction (Layer 1–3)
- `backend/llm_extractor.py` — Anthropic LLM entity extraction

### RabbitMQ publisher
```bash
cd backend
python publisher.py
```

**What it does:** Three daemon threads that continuously poll the DB and push
telemetry ticks, new reports, and new intel events to the `shield_events` fanout
exchange every 5–30 seconds. The Nuxt SSE streams consume from this exchange.

---

## 3. One-time DB setup (`scripts/setup/`)

Run these in order on a fresh database.

```bash
# 1. Apply schema (idempotent — uses CREATE TABLE IF NOT EXISTS)
python scripts/setup/apply_schema.py

# 2. Seed historical telemetry (~50 K rows)
python scripts/setup/seed_telemetry.py

# 3. Shift telemetry timestamps so the latest point is "now"
python scripts/setup/skew_timestamps.py

# 4. Seed the 200 field intelligence reports
python scripts/setup/seed_reports.py

# 5a. Seed pre-computed LLM extraction results (fast — loads from JSON)
python scripts/setup/seed_intel_extracted.py

# — OR —

# 5b. Run the live pipeline against the DB (slow — calls Anthropic API)
python scripts/pipeline/run_tokenizer_to_db.py   # redacts PENDING reports
python scripts/pipeline/run_extractor_to_db.py   # extracts intel from REDACTED reports
```

> **Optional overrides** — all scripts accept a DB URL as the first positional argument:
> ```bash
> python scripts/setup/apply_schema.py "postgresql://user:pw@host:port/db"
> ```

---

## 4. Batch pipeline (`scripts/pipeline/`)

Use these to (re-)process reports already in the database without going through the API.

| Script | What it does |
|--------|--------------|
| `run_tokenizer_to_db.py` | Tokenizes all `PENDING` reports → writes `redacted_text`, sets status `REDACTED`, inserts `redaction_audit` rows |
| `run_extractor_to_db.py` | Runs LLM extraction on all `REDACTED` reports → inserts `intel_extracted` rows, sets status `COMPLETE`, publishes to RabbitMQ |

---

## 5. Development & testing (`scripts/dev/`)

| Script | What it does |
|--------|--------------|
| `simulate_event.py` | Generates a stream of reports + telemetry for a named MCU scenario and replays them live against the API/RabbitMQ |
| `skew_timestamps.py` | *(also in setup)* Shifts all `telemetry_readings` timestamps so the latest is "now" |
| `test_auth_simple.py` | Smoke-tests authenticated API endpoints with `requests` |
| `test_frontend.py` | Visits all Nuxt pages with Playwright and captures screenshots |
| `data.py` | Standalone async RabbitMQ data-stream prototype (not used by the server) |

### simulate_event.py quick reference
```bash
# List available scenarios
python scripts/dev/simulate_event.py --list

# Dry-run: dump generated files without hitting the API
python scripts/dev/simulate_event.py --scenario chitauri_invasion --mode dump

# Live replay: posts to API + publishes telemetry to RabbitMQ
python scripts/dev/simulate_event.py --scenario chitauri_invasion --mode live
```

---

## Environment variables summary

| Variable | Required by | Example |
|----------|-------------|---------|
| `DATABASE_URL` | All scripts + server | `postgresql://edith_user:edith_password@localhost:5433/edith_db` |
| `RABBITMQ_URL` | `publisher.py`, `simulate_event.py` | `amqp://guest:guest@localhost:5672` |
| `ANTHROPIC_API_KEY` | `llm_extractor.py`, `run_extractor_to_db.py` | `sk-ant-...` |
