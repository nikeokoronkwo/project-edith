export default defineEventHandler(async () => {
  const config = useRuntimeConfig()
  const backendUrl = config.externalBackendUrl

  try {
    const data = await $fetch<{ reports: any[]; total: number }>(
      `${backendUrl}/api/reports?limit=200&offset=0`
    )

    return {
      reports: data.reports.map((r: any) => ({
        id: r.reportId || r.report_id || r.metadata,
        heroAlias: r.heroAlias || 'Unknown',
        description: r.description || '',
        timeStarted: r.timeStarted || '',
        timestamp: r.timeStarted ? new Date(r.timeStarted).getTime() : Date.now(),
        affectedLocations: r.affectedLocations || [],
        affectedResources: r.affectedResources || [],
        severity: r.severity || 'normal',
      })),
      total: data.total,
      generated_at: new Date().toISOString(),
    }
  } catch (err) {
    console.error('[GET /api/reports] Backend fetch failed:', err)
    return { reports: [], total: 0, generated_at: new Date().toISOString() }
  }
})
