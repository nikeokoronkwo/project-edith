/**
 * useAnalyticsStream — global singleton analytics composable.
 *
 * Design goals:
 *  - ONE REST call to /api/analytics (initial 48-h history) per page load.
 *  - ONE SSE connection to /api/streams/analytics for the entire app lifetime.
 *  - All pages / components share the same reactive `allSeries` state through
 *    Nuxt's `useState` (survives client-side navigation).
 *  - Filtering by sector or resource is done entirely on the client.
 *  - Incoming SSE messages are micro-batched via requestAnimationFrame so that
 *    a burst of N messages triggers ONE Vue reactivity update instead of N,
 *    keeping the UI responsive under simulation load.
 */

import type { AnalyticsSeries, AnalyticsStreamMessage } from '~/utils/analyticsTypes'

const MAX_POINTS = 2000

const COLORS = [
  '#00d4ff','#0080e6','#ef4444','#f97316','#eab308',
  '#10b981','#a855f7','#ec4899','#14b8a6','#f43f5e',
]

// ── Module-level singletons (survive page navigation) ────────────────────────
let _sse:            EventSource | null                   = null
let _reconnectTimer: ReturnType<typeof setTimeout> | null = null

// Incoming messages are pushed here and flushed in one batch per animation frame
let _msgBuffer:    AnalyticsStreamMessage[] = []
let _rafScheduled: boolean                 = false

export function useAnalyticsStream() {
  const allSeries = useState<AnalyticsSeries[]>('analytics:series',    () => [])
  const resources = useState<string[]>          ('analytics:resources', () => [])
  const sectors   = useState<string[]>          ('analytics:sectors',   () => [])
  const connected = useState<boolean>           ('analytics:connected', () => false)
  const hydrated  = useState<boolean>           ('analytics:hydrated',  () => false)

  // ── Batch flush ──────────────────────────────────────────────────────────────
  // Called by requestAnimationFrame — drains the buffer and applies ALL pending
  // updates in a single Vue state mutation (one reactivity cycle, one repaint).
  function flushMessages() {
    _rafScheduled = false

    const batch = _msgBuffer.splice(0) // drain atomically
    if (batch.length === 0) return

    // Work on local copies so we only assign once at the end
    const next = allSeries.value.slice()
    const res  = new Set(resources.value)
    const sec  = new Set(sectors.value)
    let changed = false

    for (const msg of batch) {
      if (!msg.resource || !msg.sector || msg.value === undefined) continue

      const sid      = `${msg.resource}::${msg.sector}`
      const idx      = next.findIndex(s => s.id === sid)
      const newPoint = { timestamp: msg.timestamp, value: msg.value }

      if (idx === -1) {
        next.push({
          id:       sid,
          label:    `${msg.resource} / ${msg.sector}`,
          color:    COLORS[next.length % COLORS.length],
          unit:     '',
          data:     [newPoint],
          forecast: msg.forecast,
        })
        res.add(msg.resource)
        sec.add(msg.sector)
      } else {
        const s       = next[idx]
        const rawData = [...s.data, newPoint]
        next[idx] = {
          ...s,
          data:     rawData.length > MAX_POINTS ? rawData.slice(rawData.length - MAX_POINTS) : rawData,
          forecast: msg.forecast ? { ...s.forecast, ...msg.forecast } : s.forecast,
        }
      }
      changed = true
    }

    if (changed) {
      // Single assignment → single Vue reactivity cycle for the whole batch
      allSeries.value = next
      resources.value = [...res]
      sectors.value   = [...sec]
    }
  }

  // ── REST hydration ──────────────────────────────────────────────────────────
  async function hydrate() {
    if (import.meta.client) connect()
    if (hydrated.value) return
    hydrated.value = true
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
      hydrated.value = false
    }
  }

  // ── SSE connection (client-only singleton) ────────────────────────────────
  function connect() {
    if (import.meta.server) return
    if (_sse) return

    _sse = new EventSource('/api/streams/analytics')

    _sse.addEventListener('open', () => {
      connected.value = true
      console.log('[Analytics] SSE connected')
    })

    _sse.addEventListener('error', () => {
      connected.value = false
      _sse?.close()
      _sse = null
      if (_reconnectTimer) clearTimeout(_reconnectTimer)
      _reconnectTimer = setTimeout(connect, 5_000)
    })

    _sse.addEventListener('message', (ev) => {
      try {
        const msg: AnalyticsStreamMessage = JSON.parse(ev.data)
        if (!msg.resource || !msg.sector || msg.value === undefined) return

        // Buffer the message; schedule a single flush for this animation frame
        _msgBuffer.push(msg)
        if (!_rafScheduled) {
          _rafScheduled = true
          requestAnimationFrame(flushMessages)
        }
      } catch {}
    })
  }

  function disconnect() {
    if (_reconnectTimer) { clearTimeout(_reconnectTimer); _reconnectTimer = null }
    _sse?.close()
    _sse = null
    connected.value = false
    // Discard any buffered messages that weren't flushed yet
    _msgBuffer.length = 0
    _rafScheduled = false
  }

  // ── Filtering helpers ─────────────────────────────────────────────────────
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
    allSeries: readonly(allSeries),
    resources: readonly(resources),
    sectors:   readonly(sectors),
    connected: readonly(connected),
    hydrated:  readonly(hydrated),

    hydrate,
    connect,
    disconnect,

    seriesForSector,
    seriesForResource,
  }
}
