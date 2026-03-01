/**
 * GET /api/analytics
 * Returns 48 hours of hourly historical data for all resources × sectors,
 * plus per-series forecast metadata (slope, etc.).
 *
 * The SSE stream (/api/streams/analytics) then pushes incremental updates
 * that the client appends to the relevant series.
 */
import type { AnalyticsDataPoint, AnalyticsForecast, AnalyticsSeries } from '~/utils/analyticsTypes'

const RESOURCES = ['vibranium', 'arc_fuel', 'medical', 'energy_cells', 'serum'] as const
const SECTORS   = ['NORTH_AMERICA', 'EURASIA', 'EUROPE', 'SOUTH_ASIA', 'WEST_AFRICA'] as const

type Resource = typeof RESOURCES[number]
type Sector   = typeof SECTORS[number]

// Starting values (0-100 scale) and slopes (units/hour) per resource
const RESOURCE_CONFIG: Record<Resource, { base: number; slope: number; threshold: number; unit: string }> = {
  vibranium:    { base: 78,  slope: -0.38, threshold: 10,  unit: 't'  },
  arc_fuel:     { base: 91,  slope: -0.65, threshold: 15,  unit: 'GJ' },
  medical:      { base: 54,  slope: -0.12, threshold: 20,  unit: '%'  },
  energy_cells: { base: 62,  slope: -0.52, threshold: 5,   unit: 'MWh'},
  serum:        { base: 44,  slope: -0.08, threshold: 10,  unit: 'L'  },
}

// Sector modifiers (multiplied onto slope so each sector depletes at a different rate)
const SECTOR_SLOPE_MOD: Record<Sector, number> = {
  NORTH_AMERICA: 1.0,
  EURASIA:       1.4,
  EUROPE:        0.9,
  SOUTH_ASIA:    0.7,
  WEST_AFRICA:   1.6,
}

const SERIES_COLORS = [
  '#00d4ff', '#0080e6', '#ef4444', '#f97316', '#eab308',
  '#10b981', '#a855f7', '#ec4899', '#14b8a6', '#f43f5e',
]

function noise(amplitude = 1): number {
  return (Math.random() - 0.5) * amplitude * 2
}

function buildSeries(resource: Resource, sector: Sector, colorIdx: number): AnalyticsSeries {
  const cfg   = RESOURCE_CONFIG[resource]
  const smod  = SECTOR_SLOPE_MOD[sector]
  const slope = cfg.slope * smod                    // units/hour for this series

  const HISTORY_HOURS = 48
  const NOW    = Date.now()
  const T_START = NOW - HISTORY_HOURS * 3600_000

  const data: AnalyticsDataPoint[] = []
  for (let h = 0; h <= HISTORY_HOURS; h++) {
    const ts  = T_START + h * 3600_000
    const val = Math.max(
      cfg.threshold,
      cfg.base + slope * h + noise(2.5)
    )
    data.push({ timestamp: ts, value: Math.round(val * 100) / 100 })
  }

  const forecast: AnalyticsForecast = {
    slope,
    confidence_band:   0.08,           // ±8% — request from backend if dynamic
    critical_threshold: cfg.threshold,
    horizon_hours:     24,             // show 24 h of forecast
  }

  return {
    id:       `${resource}::${sector}`,
    label:    `${resource.replace('_', ' ')} / ${sector.replace('_', ' ')}`,
    color:    SERIES_COLORS[colorIdx % SERIES_COLORS.length],
    unit:     cfg.unit,
    data,
    forecast,
  }
}

export default defineEventHandler(async () => {
  const seriesList: AnalyticsSeries[] = []
  let idx = 0
  for (const resource of RESOURCES) {
    for (const sector of SECTORS) {
      seriesList.push(buildSeries(resource, sector, idx++))
    }
  }

  return {
    series:       seriesList,
    generated_at: new Date().toISOString(),
    resources:    RESOURCES,
    sectors:      SECTORS,
  }
})
