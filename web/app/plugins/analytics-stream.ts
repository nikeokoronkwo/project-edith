/**
 * analytics-stream plugin
 *
 * Hydrates the global analytics state (REST call) on first page load — on
 * both server and client — then opens the SSE connection on the client.
 *
 * Because useAnalyticsStream() guards against duplicate hydration via the
 * `hydrated` useState flag, the REST call only fires once even though this
 * plugin runs on both sides of the SSR boundary.
 */
export default defineNuxtPlugin(async () => {
  const stream = useAnalyticsStream()

  // Fetch initial 48-h history (runs on server + client, deduplicated by flag)
  await stream.hydrate()

  // Open the SSE connection (client-only — the function is a no-op on server)
  stream.connect()
})
