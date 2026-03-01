/**
 * Nitro scheduled task: analytics:ticker
 *
 * Publishes incremental analytics updates to the RabbitMQ exchange every
 * scheduled run so the SSE stream (/api/streams/analytics) delivers live
 * data clients can append to their charts.
 *
 * Each run picks a random subset of resource/sector pairs, steps their
 * values forward by the expected slope + small noise, and publishes the
 * `AnalyticsStreamMessage` shape that the client composable understands.
 *
 * Schedule: configured in nuxt.config.ts (scheduledTasks).
 * Manual trigger: POST /_nitro/tasks/run/analytics:ticker
 */

import amqp from 'amqplib'
import { RABBITMQ_EXCHANGE } from '../utils/rabbitmq'

// ── Schema mirrors the REST endpoint ─────────────────────────────────────────
const RESOURCES = ['vibranium', 'arc_fuel', 'medical', 'energy_cells', 'serum'] as const
const SECTORS   = ['NORTH_AMERICA', 'EURASIA', 'EUROPE', 'SOUTH_ASIA', 'WEST_AFRICA'] as const

type Resource = typeof RESOURCES[number]
type Sector   = typeof SECTORS[number]

const RESOURCE_CONFIG: Record<Resource, { base: number; slope: number; threshold: number; unit: string }> = {
  vibranium:    { base: 78,  slope: -0.38, threshold: 10,  unit: 't'   },
  arc_fuel:     { base: 91,  slope: -0.65, threshold: 15,  unit: 'GJ'  },
  medical:      { base: 54,  slope: -0.12, threshold: 20,  unit: '%'   },
  energy_cells: { base: 62,  slope: -0.52, threshold: 5,   unit: 'MWh' },
  serum:        { base: 44,  slope: -0.08, threshold: 10,  unit: 'L'   },
}

const SECTOR_SLOPE_MOD: Record<Sector, number> = {
  NORTH_AMERICA: 1.0,
  EURASIA:       1.4,
  EUROPE:        0.9,
  SOUTH_ASIA:    0.7,
  WEST_AFRICA:   1.6,
}

// ── Module-level state: persists across task runs in the same process ─────────
// Tracks the "live" level for each resource::sector combination so each run
// continues from where the previous run left off.
const _levels: Map<string, number> = new Map()

function getLevel(resource: Resource, sector: Sector): number {
  const key = `${resource}::${sector}`
  if (!_levels.has(key)) {
    const cfg   = RESOURCE_CONFIG[resource]
    const smod  = SECTOR_SLOPE_MOD[sector]
    // Initialise at the end of the 48-h historical window (same as REST endpoint)
    const init  = Math.max(cfg.threshold, cfg.base + cfg.slope * smod * 48)
    _levels.set(key, init)
  }
  return _levels.get(key)!
}

function stepLevel(resource: Resource, sector: Sector, deltaSecs: number): number {
  const cfg   = RESOURCE_CONFIG[resource]
  const smod  = SECTOR_SLOPE_MOD[sector]
  const key   = `${resource}::${sector}`
  const slope = (cfg.slope * smod) / 3600   // units/sec

  const prev = getLevel(resource, sector)
  const noise = (Math.random() - 0.5) * 0.6
  const next  = Math.max(cfg.threshold, prev + slope * deltaSecs + noise)

  _levels.set(key, next)
  return Math.round(next * 100) / 100
}

// ── Task ──────────────────────────────────────────────────────────────────────
export default defineTask({
  meta: {
    name: 'analytics:ticker',
    description: 'Publish incremental analytics updates to RabbitMQ for live chart testing',
  },

  async run({ payload }) {
    const config     = useRuntimeConfig()
    const rabbitmqUrl = config.rabbitmqUrl

    // How many resource/sector pairs to publish per run (default: all 25)
    const pairsPerRun = (payload?.pairs as number) ?? 25
    // Simulated time elapsed since last run (seconds). Default: 60s (1 per minute).
    const deltaSecs   = (payload?.deltaSecs as number) ?? 60

    let connection: amqp.ChannelModel | null = null
    let channel:    amqp.Channel      | null = null

    try {
      connection = await amqp.connect(rabbitmqUrl)
      channel    = await connection.createChannel()
      await channel.assertExchange(RABBITMQ_EXCHANGE, 'fanout', { durable: true })

      // Build the full list of pairs and randomly select pairsPerRun of them
      const allPairs: [Resource, Sector][] = []
      for (const r of RESOURCES) {
        for (const s of SECTORS) allPairs.push([r, s])
      }

      // Shuffle and slice
      const shuffled = allPairs.sort(() => Math.random() - 0.5).slice(0, pairsPerRun)

      const now = Date.now()
      let published = 0

      for (const [resource, sector] of shuffled) {
        const cfg   = RESOURCE_CONFIG[resource]
        const smod  = SECTOR_SLOPE_MOD[sector]
        const slope = cfg.slope * smod

        const value = stepLevel(resource, sector, deltaSecs)

        // Time until critical at current slope
        const hoursLeft = slope < 0
          ? (value - cfg.threshold) / Math.abs(slope)
          : Infinity

        const message = {
          timestamp: now,
          resource,
          sector,
          value,
          metric:   cfg.unit,
          forecast: {
            slope,
            confidence_band:    0.08,
            critical_threshold: cfg.threshold,
            horizon_hours:      24,
          },
          // Extra debug field (ignored by client)
          hours_to_critical: isFinite(hoursLeft) ? Math.round(hoursLeft * 10) / 10 : null,
        }

        channel.publish(
          RABBITMQ_EXCHANGE,
          '',
          Buffer.from(JSON.stringify(message)),
          { persistent: false, expiration: '300000' }  // 5-min TTL — analytics data goes stale fast
        )
        published++
      }

      await channel.close()
      await connection.close()

      console.log(`[analytics:ticker] Published ${published} updates`)
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
