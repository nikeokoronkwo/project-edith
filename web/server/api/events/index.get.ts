export interface PriorityEvent {
  id: string
  event: string
  priority: 1 | 2 | 3 | 4
  started: string
  summary: string
  locations: string[]
  resources: string[]
  tags: string[]
}

export default defineEventHandler(async () => {
  const config = useRuntimeConfig()
  const backendUrl = config.externalBackendUrl

  try {
    const data = await $fetch<{ events: any[] }>(
      `${backendUrl}/api/events?limit=200`
    )

    return {
      events: data.events.map((e: any) => ({
        id: e.id,
        event: e.event,
        priority: e.priority,
        started: e.started,
        timestamp: e.timestamp,
        summary: e.description || e.event,
        locations: e.affectedLocations || [],
        resources: e.affectedResources || [],
        tags: [],
      })),
      generated_at: new Date().toISOString(),
    }
  } catch (err) {
    console.error('[GET /api/events] Backend fetch failed:', err)
    return { events: [], generated_at: new Date().toISOString() }
  }
})
