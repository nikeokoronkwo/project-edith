-- TABLE 1: Reports (what Person 4's pipeline reads from and writes back to)
CREATE TABLE reports (
    report_id       UUID PRIMARY KEY,               -- from the JSON's report_id field
    timestamp       TIMESTAMPTZ NOT NULL,            -- from the JSON's timestamp field
    
    -- PII columns (restricted access)
    operative_name  TEXT,                             -- hero_alias, stored as-is, access-gated
    operative_contact TEXT,                           -- secure_contact, stored as-is, access-gated
    
    -- The text
    raw_text        TEXT NOT NULL,                    -- original text WITH PII, encrypted or access-restricted
    redacted_text   TEXT,                             -- NULL on insert, populated after pipeline runs
    
    -- Metadata
    priority        VARCHAR(30),                      -- from JSON priority field (unreliable, as we discussed)
    
    -- Pipeline status
    status          VARCHAR(20) DEFAULT 'PENDING',    -- PENDING → REDACTED → PROCESSED → COMPLETE
    
    created_at      TIMESTAMPTZ DEFAULT NOW()
);


-- TABLE 2: Extraction results (populated by LLM after redaction)
CREATE TABLE intel_extracted (
    id              SERIAL PRIMARY KEY,
    report_id       UUID REFERENCES reports(report_id),  -- links back to the report
    
    -- What the LLM pulled out of the redacted text
    sector          VARCHAR(50),                      -- which sector the report is about
    resource        VARCHAR(50),                      -- which resource is affected
    severity        INT CHECK (severity BETWEEN 1 AND 10),
    event_type      VARCHAR(30),                      -- DEPLETION, DISRUPTION, RESUPPLY, THREAT, etc.
    summary         TEXT,                             -- LLM's one-line summary of the report
    
    -- The modifier (what this report means for forecasting)
    modifier_type   VARCHAR(30),                      -- usage_rate_multiplier, resupply_halt, etc.
    modifier_value  FLOAT,                            -- the multiplier or adjustment value
    modifier_duration_hours INT,                      -- how long the modifier lasts
    
    -- Housekeeping
    raw_llm_response JSONB,                           -- full LLM response for debugging
    created_at      TIMESTAMPTZ DEFAULT NOW()
);


-- TABLE 3: Redaction audit (what got caught and by which layer)
CREATE TABLE redaction_audit (
    id                  SERIAL PRIMARY KEY,
    report_id           UUID REFERENCES reports(report_id),
    original_fragment   TEXT NOT NULL,                 -- what was found: "Thor Odinson"
    replacement         TEXT NOT NULL,                 -- what it became: "[REDACTED]"
    entity_type         VARCHAR(20),                   -- PERSON, PHONE
    detection_layer     VARCHAR(20),                   -- REGEX, NER
    created_at          TIMESTAMPTZ DEFAULT NOW()
);


-- TABLE 4: Telemetry readings (resource stock levels per sector over time)
CREATE TABLE telemetry_readings (
    id                  SERIAL PRIMARY KEY,
    timestamp           TIMESTAMPTZ NOT NULL,
    sector_id           VARCHAR(50) NOT NULL,
    resource_type       VARCHAR(50) NOT NULL,
    stock_level         FLOAT NOT NULL,
    usage_rate_hourly   FLOAT NOT NULL,
    snap_event_detected BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

