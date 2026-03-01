import { toast } from 'vue-sonner'

interface AlertEvent {
  id: string
  event: string
  priority: number
  started: string
  timestamp: number
}

// Module-level guard so only one SSE connection exists per app instance
let _initialized = false
const _seenIds = new Set<string>()

export function useEventAlerts() {
  if (_initialized) return
  _initialized = true

  let eventSource: EventSource | null = null

  function connect() {
    if (eventSource) return
    eventSource = new EventSource('/api/streams/events')

    eventSource.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data) as AlertEvent
        if (!data?.id || !data.priority) return
        if (_seenIds.has(data.id)) return
        _seenIds.add(data.id)

        if (data.priority === 1) {
          toast.error(`CRITICAL: ${data.event}`, {
            description: `Started: ${data.started ?? 'unknown'}`,
            duration: 8000,
          })
        } else if (data.priority === 2) {
          toast.warning(`HIGH: ${data.event}`, {
            description: `Started: ${data.started ?? 'unknown'}`,
            duration: 6000,
          })
        }
      } catch {
        // malformed message — ignore
      }
    }

    eventSource.onerror = () => {
      eventSource?.close()
      eventSource = null
      // reconnect after 5s
      setTimeout(connect, 5000)
    }
  }

  connect()
}
