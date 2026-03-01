/**
 * Nitro scheduled task: analytics:ticker
 *
 * Fetches the latest telemetry readings from the FastAPI backend and publishes
 * them to the RabbitMQ exchange so the SSE stream (/api/streams/analytics)
 * delivers live data to clients.
 *
 * Each tick publishes exactly ONE point per resource×sector series (the most
 * recent reading), with a real linear-regression slope so clients can render
 * accurate forecast lines.
 *
 * Schedule: configured in nuxt.config.ts (scheduledTasks).
 */

import amqp from 'amqplib'
import { RABBITMQ_EXCHANGE } from '../../utils/rabbitmq'

interface BackendRow {
  timestamp?: number
  resource: string
  sector: string
  value: number
}

/** Linear regression slope (value per hour) over an array of {timestamp, value} pairs */
function computeSlope(rows: BackendRow[]): number {
  const n = rows.length
  if (n < 2) return 0
  // x = index (evenly spaced in time order), y = value
  const xMean = (n - 1) / 2
  const yMean = rows.reduce((s, r) => s + r.value, 0) / n
  let num = 0, den = 0
  for (let i = 0; i < n; i++) {
    num += (i - xMean) * (rows[i].value - yMean)
    den += (i - xMean) ** 2
  }
  if (!den) return 0
  // slope is per-index; convert to per-hour using the actual time span
  const spanMs = (rows[n - 1].timestamp ?? 0) - (rows[0].timestamp ?? 0)
  const spanHours = spanMs > 0 ? spanMs / 3_600_000 : 1
  const stepsPerHour = (n - 1) / spanHours
  return (num / den) * stepsPerHour
}

export default defineTask({
  meta: {
    name: 'analytics:ticker',
    description: 'Fetch latest telemetry from backend and publish incremental updates to RabbitMQ',
  },

  async run() {
    const config = useRuntimeConfig()
    const rabbitmqUrl = config.rabbitmqUrl
    const backendUrl  = config.externalBackendUrl

    let connection: amqp.ChannelModel | null = null
    let channel: amqp.Channel | null = null

    try {
      const resp = await $fetch<{ data: BackendRow[] }>(
        `${backendUrl}/api/analytics?limit=200`
      )

      if (!resp.data?.length) {
        return { result: { success: true, published: 0, reason: 'no data from backend' } }
      }

      // Group by resource×sector, sort each group chronologically
      const groups: Record<string, BackendRow[]> = {}
      for (const row of resp.data) {
        const key = `${row.resource}::${row.sector}`
        if (!groups[key]) groups[key] = []
        groups[key].push(row)
      }
      for (const key of Object.keys(groups)) {
        groups[key].sort((a, b) => (a.timestamp ?? 0) - (b.timestamp ?? 0))
      }

      connection = await amqp.connect(rabbitmqUrl)
      channel    = await connection.createChannel()
      await channel.assertExchange(RABBITMQ_EXCHANGE, 'fanout', { durable: true })

      let published = 0

      for (const [, rows] of Object.entries(groups)) {
        const latest = rows[rows.length - 1]
        const slope  = computeSlope(rows)

        const message = {
          timestamp: latest.timestamp || Date.now(),
          resource:  latest.resource,
          sector:    latest.sector,
          value:     latest.value,
          metric:    '',
          forecast: {
            slope,
            confidence_band:     0.08,
            critical_threshold:  10,
            horizon_hours:       24,
          },
        }

        channel.publish(
          RABBITMQ_EXCHANGE,
          '',
          Buffer.from(JSON.stringify(message)),
          { persistent: false, expiration: '300000' }
        )
        published++
      }

      await channel.close()
      await connection.close()

      console.log(`[analytics:ticker] Published ${published} series updates`)
      return {
        result: { success: true, published, timestamp: new Date().toISOString() }
      }
    } catch (err) {
      console.error('[analytics:ticker] Error:', err)
      if (channel)    await channel.close().catch(() => {})
      if (connection) await connection.close().catch(() => {})
      return {
        result: { success: false, error: err instanceof Error ? err.message : String(err) }
      }
    }
  },
})
