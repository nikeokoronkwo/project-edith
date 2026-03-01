<template>
  <div class="chart-panel" :class="{ compact }">

    <!-- ── Header ─────────────────────────────────────────────────────────── -->
    <div v-if="!compact" class="chart-header">
      <div class="chart-title-row">
        <span class="chart-title">{{ title }}</span>
        <span v-if="displayUnit" class="chart-unit">{{ displayUnit }}</span>
      </div>
      <div class="chart-meta">
        <span
          v-for="stat in forecastStats"
          :key="stat.seriesId"
          class="meta-stat"
          :style="{ color: stat.color }"
        >
          <span class="stat-label">{{ stat.label }}</span>
          <span class="stat-value">{{ stat.value }}</span>
        </span>
        <span class="meta-live" :class="{ active: isStreaming }">
          <span class="live-dot" />
          {{ isStreaming ? 'LIVE' : 'OFFLINE' }}
        </span>
      </div>
    </div>

    <!-- ── Chart ──────────────────────────────────────────────────────────── -->
    <div class="chart-wrap">
      <ClientOnly>
        <Line
          v-if="!loading && hasData"
          ref="lineRef"
          :data="chartData"
          :options="chartOptions"
          :plugins="chartPlugins"
          class="chart-canvas"
        />
        <template #fallback>
          <div class="chart-skeleton" />
        </template>
      </ClientOnly>

      <div v-if="loading" class="chart-skeleton" />

      <div v-if="!loading && !hasData" class="chart-empty">
        <Icon name="heroicons:chart-bar" class="empty-icon" />
        <p class="empty-text">NO DATA</p>
      </div>
    </div>

    <!-- ── Forecast strip ─────────────────────────────────────────────────── -->
    <div v-if="forecastStats.length && !compact" class="forecast-strip">
      <div
        v-for="stat in forecastStats"
        :key="'strip-' + stat.seriesId"
        class="strip-item"
      >
        <span class="strip-dot" :style="{ background: stat.color }" />
        <span class="strip-label">{{ stat.seriesLabel }}</span>
        <span class="strip-trend" :style="{ color: stat.slopeColor }">{{ stat.trend }}</span>
        <span class="strip-critical" v-if="stat.critical">{{ stat.critical }}</span>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler,
  type ChartData,
  type ChartOptions,
  type Plugin,
} from 'chart.js'
import type { AnalyticsSeries } from '~/utils/analyticsTypes'

ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend, Filler)

// ── Props ─────────────────────────────────────────────────────────────────────
const props = withDefaults(defineProps<{
  series: AnalyticsSeries[]
  title?: string
  /** Override unit shown in header — defaults to first series unit */
  unit?: string
  /** Fraction of x-axis where "NOW" sits (0–1). Default 0.62 */
  nowRatio?: number
  loading?: boolean
  isStreaming?: boolean
  /** Compact mode: hides header, forecast strip, and tick labels */
  compact?: boolean
}>(), {
  title:       'ANALYTICS',
  nowRatio:    0.62,
  loading:     false,
  isStreaming: false,
  compact:     false,
})

// ── Chart ref ─────────────────────────────────────────────────────────────────
const lineRef = ref<InstanceType<typeof Line> | null>(null)

// ── Timing ────────────────────────────────────────────────────────────────────
const hasData = computed(() => props.series.some(s => s.data.length > 0))

/** Latest actual timestamp across all series */
const tNow = computed<number>(() => {
  const ts = props.series.flatMap(s => s.data.map(d => d.timestamp))
  return ts.length ? Math.max(...ts) : Date.now()
})

/** Earliest actual timestamp across all series */
const tStart = computed<number>(() => {
  const ts = props.series.flatMap(s => s.data.map(d => d.timestamp))
  return ts.length ? Math.min(...ts) : Date.now() - 86400_000
})

const historySpanMs = computed(() => tNow.value - tStart.value)

/** Forecast span derived from nowRatio: forecastSpan = historySpan × (1-r)/r */
const forecastSpanMs = computed<number>(() => {
  const maxHorizonMs = Math.max(
    0,
    ...props.series.map(s => (s.forecast?.horizon_hours ?? 0) * 3_600_000)
  )
  return maxHorizonMs || (historySpanMs.value * (1 - props.nowRatio) / props.nowRatio)
})

const xMin = computed(() => tStart.value)
const xMax = computed(() => tNow.value + forecastSpanMs.value)

// ── Helpers ───────────────────────────────────────────────────────────────────
const displayUnit = computed(
  () => props.unit ?? props.series.find(s => s.unit)?.unit ?? ''
)

function formatTick(ms: number): string {
  const d = new Date(ms)
  const hh = d.getHours().toString().padStart(2, '0')
  const mm = d.getMinutes().toString().padStart(2, '0')
  const dd = d.getDate().toString().padStart(2, '0')
  const MON = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
  const mo  = MON[d.getMonth()]
  const span = xMax.value - xMin.value
  if (span < 3 * 86400_000)  return `${hh}:${mm}`
  if (span < 14 * 86400_000) return `${dd} ${mo}`
  return `${dd} ${mo}`
}

function formatDuration(ms: number): string {
  const h = ms / 3_600_000
  if (h < 1)   return `${Math.round(h * 60)}m`
  if (h < 48)  return `${Math.round(h)}h`
  return `${Math.round(h / 24)}d`
}

// ── Forecast computation ──────────────────────────────────────────────────────
function buildForecastPoints(series: AnalyticsSeries): { x: number; y: number }[] {
  const fc = series.forecast
  if (!fc || !series.data.length) return []
  const last = series.data[series.data.length - 1]
  const slopePerMs  = fc.slope / 3_600_000   // units/hour → units/ms
  const threshold   = fc.critical_threshold ?? 0
  const endTs       = tNow.value + forecastSpanMs.value
  const STEPS       = 40
  const pts: { x: number; y: number }[] = []
  for (let i = 0; i <= STEPS; i++) {
    const t = last.timestamp + (i / STEPS) * (endTs - last.timestamp)
    const v = last.value + slopePerMs * (t - last.timestamp)
    pts.push({ x: t, y: Math.max(threshold, v) })
  }
  return pts
}

function buildConfidenceBand(
  series: AnalyticsSeries,
  forecastPts: { x: number; y: number }[],
  sign: 1 | -1
): { x: number; y: number }[] {
  const band = series.forecast?.confidence_band ?? 0
  if (!band || !forecastPts.length) return []
  return forecastPts.map(p => ({ x: p.x, y: p.y * (1 + sign * band) }))
}

// ── Chart data ────────────────────────────────────────────────────────────────
const chartData = computed<ChartData<'line'>>(() => {
  const datasets: ChartData<'line'>['datasets'] = []

  for (const series of props.series) {
    if (!series.data.length) continue
    const color = series.color

    // 1. Historical — solid line
    datasets.push({
      label:           series.label,
      data:            series.data.map(d => ({ x: d.timestamp, y: d.value })),
      borderColor:     color,
      backgroundColor: 'transparent',
      borderWidth:     2,
      pointRadius:     0,
      pointHoverRadius: 4,
      tension:         0.3,
    } as any)

    const forecastPts = buildForecastPoints(series)
    if (!forecastPts.length) continue

    // 2. Upper confidence bound (transparent fill)
    const upper = buildConfidenceBand(series, forecastPts, 1)
    const lower = buildConfidenceBand(series, forecastPts, -1)

    if (upper.length) {
      datasets.push({
        label:            `${series.label} (upper)`,
        data:             upper,
        borderColor:      'transparent',
        backgroundColor:  hexAlpha(color, 0.08),
        borderWidth:      0,
        pointRadius:      0,
        pointHoverRadius: 0,
        fill:             '+1',
        tension:          0.3,
        hidden:           false,
      } as any)
    }

    if (lower.length) {
      datasets.push({
        label:            `${series.label} (lower)`,
        data:             lower,
        borderColor:      'transparent',
        backgroundColor:  'transparent',
        borderWidth:      0,
        pointRadius:      0,
        pointHoverRadius: 0,
        fill:             false,
        tension:          0.3,
      } as any)
    }

    // 3. Forecast — dashed line (skip first point so it doesn't overlap the last historical dot)
    datasets.push({
      label:            `${series.label} ›`,
      data:             forecastPts.slice(1),
      borderColor:      hexAlpha(color, 0.65),
      backgroundColor:  'transparent',
      borderWidth:      1.5,
      borderDash:       [5, 4],
      pointRadius:      0,
      pointHoverRadius: 0,
      tension:          0.1,
    } as any)
  }

  return { datasets }
})

// ── Chart options ─────────────────────────────────────────────────────────────
const chartOptions = computed<ChartOptions<'line'>>(() => ({
  responsive:           true,
  maintainAspectRatio:  false,
  animation:            { duration: 280 },
  interaction:          { mode: 'index', intersect: false },
  parsing:              false,   // datasets already use {x,y} objects

  scales: {
    x: {
      type: 'linear',
      min:  xMin.value,
      max:  xMax.value,
      grid: {
        color:       'rgba(0,128,230,0.06)',
        drawBorder:  false,
      },
      ticks: {
        display:      !props.compact,
        color:        '#4b5563',
        font:         { family: "'JetBrains Mono', monospace", size: 8 },
        maxTicksLimit: 8,
        callback:     (val: number | string) => formatTick(Number(val)),
      },
      border: { color: 'rgba(0,128,230,0.15)' },
    },
    y: {
      grid: {
        color:      'rgba(0,128,230,0.06)',
        drawBorder: false,
      },
      ticks: {
        display:   !props.compact,
        color:     '#4b5563',
        font:      { family: "'JetBrains Mono', monospace", size: 8 },
        maxTicksLimit: 6,
      },
      border: { color: 'rgba(0,128,230,0.15)' },
    },
  } as any,

  plugins: {
    legend: {
      display: props.series.length > 1 && !props.compact,
      position: 'top',
      align:    'start',
      labels: {
        color:     '#5a6a7a',
        font:      { family: "'JetBrains Mono', monospace", size: 8 },
        boxWidth:  10,
        boxHeight: 2,
        padding:   12,
        // Hide internal confidence-band and forecast-line labels
        filter: (item) => !item.text.endsWith('(upper)') && !item.text.endsWith('(lower)') && !item.text.endsWith(' ›'),
      },
    },
    tooltip: {
      backgroundColor: '#0d1117',
      borderColor:     'rgba(0,128,230,0.3)',
      borderWidth:     1,
      titleColor:      '#00d4ff',
      bodyColor:       '#e8f0f8',
      titleFont:       { family: "'JetBrains Mono', monospace", size: 8 },
      bodyFont:        { family: "'JetBrains Mono', monospace", size: 8 },
      padding:         8,
      titleMarginBottom: 4,
      callbacks: {
        title: (items) => formatTick(items[0].parsed.x),
        label: (item) => {
          const lbl = item.dataset.label ?? ''
          // Always suppress band datasets
          if (lbl.endsWith('(upper)') || lbl.endsWith('(lower)')) return null as any
          // Suppress forecast line entries when hovering over the historical region
          if (lbl.endsWith(' ›') && item.parsed.x <= tNow.value) return null as any
          const unit = displayUnit.value
          const tag  = lbl.endsWith(' ›') ? ' [FORECAST]' : ''
          return ` ${item.parsed.y.toFixed(1)} ${unit}${tag}`
        },
      },
    },
  },
}))

// ── NOW line — custom Chart.js plugin ─────────────────────────────────────────
// We use a WeakMap so each chart instance holds its own nowTime without
// polluting global plugin state.
const _nowMap = new WeakMap<object, number>()

const NOW_LINE: Plugin<'line'> = {
  id: 'shieldNowLine',
  afterDraw(chart) {
    const nowTime = _nowMap.get(chart)
    if (nowTime === undefined) return
    const { ctx, chartArea, scales } = chart
    if (!chartArea || !(scales as any).x) return

    const nowX = (scales as any).x.getPixelForValue(nowTime)
    if (nowX < chartArea.left || nowX > chartArea.right) return

    ctx.save()

    // Dashed vertical line
    ctx.beginPath()
    ctx.setLineDash([3, 4])
    ctx.moveTo(nowX, chartArea.top)
    ctx.lineTo(nowX, chartArea.bottom)
    ctx.strokeStyle = 'rgba(0, 212, 255, 0.5)'
    ctx.lineWidth   = 1.5
    ctx.stroke()

    // "NOW" label
    ctx.setLineDash([])
    ctx.fillStyle = 'rgba(0, 212, 255, 0.72)'
    ctx.font      = 'bold 7.5px "JetBrains Mono", monospace'
    ctx.textAlign = 'left'
    ctx.fillText('NOW', nowX + 5, chartArea.top + 13)

    // Shaded forecast region
    ctx.fillStyle = 'rgba(0, 128, 230, 0.025)'
    ctx.fillRect(nowX, chartArea.top, chartArea.right - nowX, chartArea.bottom - chartArea.top)

    ctx.restore()
  },
}

const chartPlugins = [NOW_LINE]

// Keep the WeakMap entry in sync as tNow changes
function syncNowLine() {
  const chart = (lineRef.value as any)?.chart
  if (chart) _nowMap.set(chart, tNow.value)
}

watch(tNow, () => {
  syncNowLine()
  const chart = (lineRef.value as any)?.chart
  chart?.draw()
})

onMounted(() => nextTick(syncNowLine))

// ── Forecast stats (header + strip) ──────────────────────────────────────────
interface ForecastStat {
  seriesId:    string
  seriesLabel: string
  color:       string
  label:       string
  value:       string
  trend:       string
  slopeColor:  string
  critical:    string | null
}

const forecastStats = computed<ForecastStat[]>(() =>
  props.series
    .filter(s => s.forecast && s.data.length)
    .map(s => {
      const fc          = s.forecast!
      const last        = s.data[s.data.length - 1]
      const threshold   = fc.critical_threshold ?? 0
      const slopePerHr  = fc.slope
      const trendDir    = slopePerHr < 0 ? '↓' : '↑'
      const trendAbs    = Math.abs(slopePerHr).toFixed(2)
      const trend       = `${trendDir} ${trendAbs} ${s.unit ?? ''}/h`
      const slopeColor  = slopePerHr < -0.3 ? '#ef4444' : slopePerHr < 0 ? '#f97316' : '#22c55e'

      // Time until critical threshold
      let critical: string | null = null
      if (slopePerHr < 0 && last.value > threshold) {
        const hoursLeft = (last.value - threshold) / Math.abs(slopePerHr)
        critical = `CRITICAL IN ${formatDuration(hoursLeft * 3_600_000)}`
      }

      return {
        seriesId:    s.id,
        seriesLabel: s.label,
        color:       s.color,
        label:       s.label.split('/')[0].trim().toUpperCase(),
        value:       `${last.value.toFixed(1)} ${s.unit ?? ''}`,
        trend,
        slopeColor,
        critical,
      }
    })
)

// ── Utility ───────────────────────────────────────────────────────────────────
function hexAlpha(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r},${g},${b},${alpha})`
}
</script>

<style scoped>
/* ── Panel shell ─────────────────────────────────────────────────────────── */
.chart-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #080a0e;
  border: 1px solid rgba(0, 128, 230, 0.18);
  border-radius: 10px;
  overflow: hidden;
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 14px;
  border-bottom: 1px solid rgba(0, 128, 230, 0.1);
  background: rgba(0, 128, 230, 0.04);
  flex-shrink: 0;
  gap: 12px;
  flex-wrap: wrap;
}

.chart-title-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.chart-title {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.18em;
  color: #00d4ff;
}

.chart-unit {
  font-size: 7.5px;
  letter-spacing: 0.08em;
  color: #5a6a7a;
  padding: 1px 5px;
  border: 1px solid rgba(0, 128, 230, 0.2);
  border-radius: 2px;
}

.chart-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.meta-stat {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.stat-label {
  font-size: 6.5px;
  letter-spacing: 0.1em;
  color: #4b5563;
}

.stat-value {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.06em;
}

.meta-live {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 7.5px;
  letter-spacing: 0.12em;
  color: #4b5563;
  transition: color 0.3s;
}

.meta-live.active { color: #22c55e; }

.live-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #374151;
  flex-shrink: 0;
  transition: background 0.3s, box-shadow 0.3s;
}

.meta-live.active .live-dot {
  background: #22c55e;
  box-shadow: 0 0 5px #22c55e;
  animation: blink 2s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.2; }
}

/* ── Chart area ──────────────────────────────────────────────────────────── */
.chart-wrap {
  flex: 1;
  min-height: 0;
  position: relative;
  padding: 12px 14px 6px;
}

.chart-canvas {
  width: 100% !important;
  height: 100% !important;
}

.chart-skeleton {
  position: absolute;
  inset: 0;
  background:
    repeating-linear-gradient(90deg,
      rgba(0,128,230,0.03) 0, rgba(0,128,230,0.03) 1px,
      transparent 1px, transparent 40px),
    repeating-linear-gradient(180deg,
      rgba(0,128,230,0.03) 0, rgba(0,128,230,0.03) 1px,
      transparent 1px, transparent 40px);
  animation: skeleton-pulse 2s ease-in-out infinite alternate;
}

@keyframes skeleton-pulse {
  from { opacity: 0.4; }
  to   { opacity: 1; }
}

.chart-empty {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #2d3748;
}

.empty-icon { width: 28px; height: 28px; }
.empty-text { font-size: 8.5px; letter-spacing: 0.14em; margin: 0; }

/* ── Forecast strip ──────────────────────────────────────────────────────── */
.forecast-strip {
  display: flex;
  gap: 0;
  flex-wrap: wrap;
  border-top: 1px solid rgba(0, 128, 230, 0.08);
  background: rgba(0, 0, 0, 0.12);
  flex-shrink: 0;
  overflow-x: auto;
}

.strip-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-right: 1px solid rgba(0, 128, 230, 0.07);
  white-space: nowrap;
  flex-shrink: 0;
}

.strip-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.strip-label {
  font-size: 7.5px;
  letter-spacing: 0.08em;
  color: #5a6a7a;
  text-transform: uppercase;
}

.strip-trend {
  font-size: 8px;
  font-weight: 600;
  letter-spacing: 0.06em;
}

.strip-critical {
  font-size: 7px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #ef4444;
  padding: 1px 5px;
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 2px;
}

/* ── Compact mode ────────────────────────────────────────────────────────── */
.chart-panel.compact .chart-wrap {
  padding: 4px 6px 2px;
}
</style>
