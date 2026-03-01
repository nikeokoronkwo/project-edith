// ── Shared types for the Globe component system ────────────────────────────────

export type SeverityLevel = 'critical' | 'warning' | 'elevated' | 'normal'

/** A region of interest displayed on the globe */
export interface GlobeRegion {
  /** Unique identifier (e.g. ISO_A3 country code or custom sector id) */
  id: string

  /** Display name */
  name: string

  /** ISO 3-letter country code for GeoJSON polygon matching */
  countryCode: string

  /** Severity level — drives color theming across globe + popup */
  severity: SeverityLevel

  /** Optional anchor coordinates (used for label placement) */
  lat?: number
  lng?: number

  /** Arbitrary payload from the API — the popup and graph will consume what's present */
  data?: {
    sector?:          string
    resource?:        string
    depletion_pct?:   number   // 0–100
    forecast_days?:   number   // days until critical threshold
    report_count?:    number
    timeseries?:      number[] // pre-fetched for the mini-graph
    [key: string]:    unknown
  }
}

/** Event emitted when a user clicks "View Analytics" in the popup */
export interface GlobeNavigateEvent {
  region: GlobeRegion
  targetPath: string   // e.g. /analytics/sector/EMEA
}