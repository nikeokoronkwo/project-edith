// ── Shared analytics types ────────────────────────────────────────────────────
// Used by AnalyticsChart.vue, analytics pages, and the SSE stream handler.

export interface AnalyticsDataPoint {
  timestamp: number  // unix ms
  value: number
}

/**
 * Forecast object attached to an analytics series (or a stream message).
 *
 * Backend must provide AT MINIMUM: `slope`
 *
 * Additional fields needed from backend (flag with backend team):
 *   - slope            : units per HOUR  (confirm unit — assumed hourly)
 *   - confidence_band  : fraction ±  (e.g. 0.12 = ±12%) for range-area shading
 *   - critical_threshold: absolute value at which resource is "depleted"
 *                         (required for the "X days until critical" countdown)
 *   - horizon_hours    : how many hours ahead to render the forecast line;
 *                         if omitted the component auto-sizes to the history window
 *   - metric           : display name / unit string for the y-axis (e.g. "tonnes", "GJ")
 */
export interface AnalyticsForecast {
  slope: number                // units / hour  (positive = growing, negative = depleting)
  confidence_band?: number     // 0–1 fraction  (e.g. 0.10 = ±10%)
  critical_threshold?: number  // absolute low-water mark (default 0)
  horizon_hours?: number       // explicit forecast window; auto if omitted
}

export interface AnalyticsSeries {
  id: string
  label: string
  color: string               // hex
  data: AnalyticsDataPoint[]
  forecast?: AnalyticsForecast
  unit?: string               // y-axis label unit, e.g. "t" or "%"
}

// ── Stream message shape (extends the base StreamAnalyticsData) ───────────────
export interface AnalyticsStreamMessage {
  timestamp: number
  resource: string
  sector: string
  value: number
  metric?: string
  forecast?: AnalyticsForecast
}
