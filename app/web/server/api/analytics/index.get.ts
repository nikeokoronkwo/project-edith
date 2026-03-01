/**
 * GET /api/analytics
 *
 * Proxies to the FastAPI backend, fetches telemetry readings, and transforms
 * the flat list into AnalyticsSeries[] grouped by resource × sector.
 * The SSE stream (/api/streams/analytics) pushes incremental updates.
 */
import type { AnalyticsDataPoint, AnalyticsForecast, AnalyticsSeries } from '~/utils/analyticsTypes'

const SERIES_COLORS = [
  '#00d4ff', '#0080e6', '#ef4444', '#f97316', '#eab308',
  '#10b981', '#a855f7', '#ec4899', '#14b8a6', '#f43f5e',
]

export default defineEventHandler(async () => {
  const config = useRuntimeConfig()
  const backendUrl = config.externalBackendUrl

  try {
    const data = await $fetch<{ data: any[] }>(
      `${backendUrl}/api/analytics?limit=5000`
    )

    const grouped: Record<string, { resource: string; sector: string; points: AnalyticsDataPoint[] }> = {}
    const resourceSet = new Set<string>()
    const sectorSet = new Set<string>()

    for (const row of data.data) {
      const key = `${row.resource}::${row.sector}`
      resourceSet.add(row.resource)
      sectorSet.add(row.sector)

      if (!grouped[key]) {
        grouped[key] = { resource: row.resource, sector: row.sector, points: [] }
      }
      grouped[key].points.push({ timestamp: row.timestamp, value: row.value })
    }

    const resources = Array.from(resourceSet).sort()
    const sectors = Array.from(sectorSet).sort()

    let colorIdx = 0
    const seriesList: AnalyticsSeries[] = []

    for (const [id, group] of Object.entries(grouped)) {
      group.points.sort((a, b) => a.timestamp - b.timestamp)

      const vals = group.points.map(p => p.value)
      const n = vals.length

      let slope = 0
      if (n >= 2) {
        const xMean = (n - 1) / 2
        const yMean = vals.reduce((a, b) => a + b, 0) / n
        let num = 0, den = 0
        for (let i = 0; i < n; i++) {
          num += (i - xMean) * (vals[i] - yMean)
          den += (i - xMean) ** 2
        }
        slope = den ? num / den : 0
      }

      const forecast: AnalyticsForecast = {
        slope,
        confidence_band: 0.08,
        critical_threshold: 10,
        horizon_hours: 24,
      }

      seriesList.push({
        id,
        label: `${group.resource} / ${group.sector}`,
        color: SERIES_COLORS[colorIdx++ % SERIES_COLORS.length],
        unit: '',
        data: group.points,
        forecast,
      })
    }

    return {
      series: seriesList,
      generated_at: new Date().toISOString(),
      resources,
      sectors,
    }
  } catch (err) {
    console.error('[GET /api/analytics] Backend fetch failed:', err)
    return { series: [], generated_at: new Date().toISOString(), resources: [], sectors: [] }
  }
})
