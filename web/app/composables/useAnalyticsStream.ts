/**
 * useAnalyticsStream — global singleton analytics composable.
 *
 * Design goals:
 *  - ONE REST call to /api/analytics (initial 48-h history) per page load.
 *  - ONE SSE connection to /api/streams/analytics for the entire app lifetime.
 *  - All pages / components share the same reactive `allSeries` state through
 *    Nuxt's `useState` (survives client-side navigation).
 *  - Filtering by sector or resource is done entirely on the client; the SSE
 *    channel carries updates for all resource × sector combinations together
 *    and callers subscribe to the slice they care about.
 *
 * Usage:
 *   const { connected, seriesForSector, seriesForResource } = useAnalyticsStream()
 *   const seriesList = seriesForSector(sectorId)   // reactive computed
 */

import type { AnalyticsSeries, AnalyticsStreamMessage } from '~/utils/analyticsTypes'

// ── Module-level SSE handle (client-only, survives navigation) ────────────────
let _sse:             EventSource | null                  = null
let _reconnectTimer:  ReturnType<typeof setTimeout> | null = null

export function useAnalyticsStream() {
  // ── Shared state (Nuxt useState = one instance per key across all callers) ──
  const allSeries = useState<AnalyticsSeries[]>('analytics:series',    () => [])
  const resources = useState<string[]>           ('analytics:resources', () => [])
  const sectors   = useState<string[]>           ('analytics:sectors',   () => [])
  const connected = useState<boolean>            ('analytics:connected', () => false)
  const hydrated  = useState<boolean>            ('analytics:hydrated',  () => false)

  // ── REST hydration ──────────────────────────────────────────────────────────
  // Safe to call multiple times — the guard prevents duplicate fetches.
  // Always attempts to open the SSE connection on the client after data is ready.
  async function hydrate() {
    if (import.meta.client) connect()   // ensure SSE is up whenever hydrate is called
    if (hydrated.value) return
    hydrated.value = true               // set early to prevent concurrent calls
    try {
      const data = await $fetch<{
        series:    AnalyticsSeries[]
        resources: string[]
        sectors:   string[]
      }>('/api/analytics')
      allSeries.value = data.series
      resources.value = data.resources
      sectors.value   = data.sectors
    } catch (err) {
      console.error('[Analytics] Hydration failed:', err)
      hydrated.value = false            // allow retry on next call
    }
  }

  // ── SSE connection (client-only singleton) ───────────────────────────────────
  function connect() {
    if (import.meta.server) return
    if (_sse) return                  // already connected

    _sse = new EventSource('/api/streams/analytics')

    _sse.addEventListener('open', () => {
      connected.value = true
      console.log('[Analytics] SSE connected')
    })

    _sse.addEventListener('error', () => {
      connected.value = false
      _sse?.close()
      _sse = null
      // Reconnect after 5 s
      if (_reconnectTimer) clearTimeout(_reconnectTimer)
      _reconnectTimer = setTimeout(connect, 5_000)
    })

    _sse.addEventListener('message', (ev) => {
      try {
        const msg: AnalyticsStreamMessage = JSON.parse(ev.data)

        // Ignore messages that don't carry the analytics shape
        if (!msg.resource || !msg.sector || msg.value === undefined) return

        const sid = `${msg.resource}::${msg.sector}`
        const idx = allSeries.value.findIndex(s => s.id === sid)

        const newPoint = { timestamp: msg.timestamp, value: msg.value }
        const MAX_POINTS = 2000

        if (idx === -1) {
          // Unknown series — create it so it appears on the chart immediately
          const COLORS = [
            '#00d4ff','#0080e6','#ef4444','#f97316','#eab308',
            '#10b981','#a855f7','#ec4899','#14b8a6','#f43f5e',
          ]
          const newSeries: AnalyticsSeries = {
            id:       sid,
            label:    `${msg.resource} / ${msg.sector}`,
            color:    COLORS[allSeries.value.length % COLORS.length],
            unit:     '',
            data:     [newPoint],
            forecast: msg.forecast,
          }
          allSeries.value = [...allSeries.value, newSeries]
          if (!resources.value.includes(msg.resource))
            resources.value = [...resources.value, msg.resource]
          if (!sectors.value.includes(msg.sector))
            sectors.value = [...sectors.value, msg.sector]
        } else {
          // Replace the series object so all computed filters re-evaluate
          const s       = allSeries.value[idx]
          const rawData = [...s.data, newPoint]
          const trimmed = rawData.length > MAX_POINTS
            ? rawData.slice(rawData.length - MAX_POINTS)
            : rawData
          const updated: AnalyticsSeries = {
            ...s,
            data:     trimmed,
            forecast: msg.forecast ? { ...s.forecast, ...msg.forecast } : s.forecast,
          }
          const next = allSeries.value.slice()
          next[idx]  = updated
          allSeries.value = next
        }
      } catch {}
    })
  }

  function disconnect() {
    if (_reconnectTimer) { clearTimeout(_reconnectTimer); _reconnectTimer = null }
    _sse?.close()
    _sse = null
    connected.value = false
  }

  // ── Filtering helpers ────────────────────────────────────────────────────────
  // Accept a plain string or a Ref/ComputedRef so callers can pass route params directly.

  function seriesForSector(sector: MaybeRef<string>) {
    return computed(() => {
      const s = toValue(sector)
      return allSeries.value.filter(sr => sr.id.endsWith(`::${s}`))
    })
  }

  function seriesForResource(resource: MaybeRef<string>) {
    return computed(() => {
      const r = toValue(resource)
      return allSeries.value.filter(sr => sr.id.startsWith(`${r}::`))
    })
  }

  return {
    // State (read-only to external consumers)
    allSeries: readonly(allSeries),
    resources: readonly(resources),
    sectors:   readonly(sectors),
    connected: readonly(connected),
    hydrated:  readonly(hydrated),

    // Lifecycle
    hydrate,
    connect,
    disconnect,

    // Per-view slices
    seriesForSector,
    seriesForResource,
  }
}
