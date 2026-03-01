<template>
  <div class="mini-graph-container">
    <div class="mini-header">
      <h4 class="mini-title">Impact at report time</h4>
      <span class="mini-time">{{ formatDate(reportTimestamp) }}</span>
    </div>

    <div class="mini-chart-area">
      <canvas v-if="hasData" ref="canvasRef" class="mini-canvas" />
      <div v-else-if="!hydrated" class="mini-status">LOADING…</div>
      <div v-else class="mini-status">NO DATA</div>
    </div>

    <div v-if="impactData" class="impact-metrics">
      <div class="impact-row">
        <span class="metric-label">Trend impact:</span>
        <span :class="['metric-value', impactData.isPositive ? 'positive' : 'negative']">
          {{ impactData.percentChange > 0 ? '+' : '' }}{{ impactData.percentChange.toFixed(1) }}%
        </span>
      </div>
      <div class="impact-row">
        <span class="metric-label">Before:</span>
        <span class="metric-value">{{ impactData.gradientBefore.toFixed(3) }}/pt</span>
      </div>
      <div class="impact-row">
        <span class="metric-label">After:</span>
        <span class="metric-value">{{ impactData.gradientAfter.toFixed(3) }}/pt</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed, watch } from 'vue'
import Chart from 'chart.js/auto'
import type { Chart as ChartInstance, Plugin } from 'chart.js'

interface Props {
  reportTimestamp: string
  reportId?: string
  affectedResources?: string[]
}

const props = defineProps<Props>()

const { allSeries, hydrate, hydrated } = useAnalyticsStream()

const canvasRef = ref<HTMLCanvasElement | null>(null)
let chartInstance: ChartInstance | null = null

// Window of data to show: ±90 minutes around the event
const WINDOW_BEFORE = 90 * 60_000
const WINDOW_AFTER  = 90 * 60_000

const reportTs = computed(() => new Date(props.reportTimestamp).getTime())

// Find series matching affectedResources, or fall back to first available series
const relevantSeries = computed(() => {
  const resources = props.affectedResources ?? []
  if (resources.length) {
    const matched = allSeries.value.filter(s =>
      resources.some(r => s.id.toLowerCase().startsWith(r.toLowerCase() + '::'))
    )
    if (matched.length) return matched.slice(0, 2)
  }
  return allSeries.value.slice(0, 2)
})

// Narrow to the time window around the report event
const windowedSeries = computed(() => {
  const ts = reportTs.value
  return relevantSeries.value.map(s => ({
    ...s,
    data: s.data.filter(d =>
      d.timestamp >= ts - WINDOW_BEFORE && d.timestamp <= ts + WINDOW_AFTER
    ),
  }))
})

const hasData = computed(() => windowedSeries.value.some(s => s.data.length > 1))

interface ImpactData {
  percentChange: number
  gradientBefore: number
  gradientAfter: number
  isPositive: boolean
}

// Before/after gradient based on data split at the report timestamp
const impactData = computed((): ImpactData | null => {
  const s = windowedSeries.value[0]
  if (!s || s.data.length < 4) return null
  const ts     = reportTs.value
  const before = s.data.filter(d => d.timestamp < ts)
  const after  = s.data.filter(d => d.timestamp > ts)
  if (before.length < 2 || after.length < 2) return null

  const gBefore = (before[before.length - 1].value - before[0].value) / before.length
  const gAfter  = (after[after.length - 1].value  - after[0].value)  / after.length
  const pct     = ((gAfter - gBefore) / (Math.abs(gBefore) || 1)) * 100

  return { percentChange: pct, gradientBefore: gBefore, gradientAfter: gAfter, isPositive: gAfter > gBefore }
})

// ── Custom plugin: vertical event marker ──────────────────────────────────────
const EVENT_LINE_PLUGIN: Plugin<'line'> = {
  id: 'reportEventLine',
  afterDraw(chart, _args, opts: any) {
    const ts: number = opts?.eventTs
    if (!ts) return
    const { ctx, chartArea, scales } = chart as any
    if (!chartArea || !scales.x) return
    const x = scales.x.getPixelForValue(ts)
    if (x < chartArea.left || x > chartArea.right) return

    ctx.save()
    ctx.beginPath()
    ctx.setLineDash([4, 3])
    ctx.moveTo(x, chartArea.top)
    ctx.lineTo(x, chartArea.bottom)
    ctx.strokeStyle = 'rgba(245,158,11,0.85)'
    ctx.lineWidth = 1.5
    ctx.stroke()
    ctx.setLineDash([])
    ctx.fillStyle = 'rgba(245,158,11,0.9)'
    ctx.font = '700 7px "JetBrains Mono", monospace'
    ctx.textAlign = 'center'
    ctx.fillText('EVENT', x, chartArea.top + 10)
    ctx.restore()
  },
}

function hexAlpha(hex: string, a: number): string {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r},${g},${b},${a})`
}

function buildChart() {
  if (!canvasRef.value || !hasData.value) return
  chartInstance?.destroy()
  chartInstance = null

  const ts   = reportTs.value
  const xMax = ts + WINDOW_AFTER
  const fallbackColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#a855f7']

  const datasets: any[] = []

  windowedSeries.value.forEach((s, i) => {
    if (!s.data.length) return
    const color = (s.color && s.color.startsWith('#')) ? s.color : fallbackColors[i % fallbackColors.length]

    // Pre-event: solid line
    const preData = s.data.filter(d => d.timestamp <= ts)
    if (preData.length) {
      datasets.push({
        label: s.label,
        data: preData.map(d => ({ x: d.timestamp, y: d.value })),
        borderColor: color,
        backgroundColor: hexAlpha(color, 0.07),
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 3,
        tension: 0.3,
        fill: false,
      })
    }

    // Post-event: slightly faded, dashed
    const postData = s.data.filter(d => d.timestamp >= ts)
    if (postData.length) {
      datasets.push({
        label: s.label + ' (after)',
        data: postData.map(d => ({ x: d.timestamp, y: d.value })),
        borderColor: hexAlpha(color, 0.55),
        backgroundColor: 'transparent',
        borderWidth: 1.5,
        borderDash: [3, 3],
        pointRadius: 0,
        tension: 0.3,
        fill: false,
      })
    }

    // Forecast extension from last data point using series slope
    if (s.forecast?.slope !== undefined && s.data.length) {
      const last       = s.data[s.data.length - 1]
      const slopePerMs = s.forecast.slope / 3_600_000
      const STEPS      = 20
      const fcPts = Array.from({ length: STEPS + 1 }, (_, k) => {
        const t = last.timestamp + (k / STEPS) * (xMax - last.timestamp)
        return { x: t, y: last.value + slopePerMs * (t - last.timestamp) }
      })
      datasets.push({
        label: s.label + ' ›',
        data: fcPts,
        borderColor: hexAlpha(color, 0.35),
        backgroundColor: 'transparent',
        borderWidth: 1,
        borderDash: [5, 4],
        pointRadius: 0,
        tension: 0.1,
        fill: false,
      })
    }
  })

  const allTs = windowedSeries.value.flatMap(s => s.data.map(d => d.timestamp))
  const xMin  = allTs.length ? Math.min(...allTs) : ts - WINDOW_BEFORE
  const fmt   = (ms: number) =>
    new Date(ms).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })

  chartInstance = new Chart(canvasRef.value, {
    type: 'line',
    data: { datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 0 },
      parsing: false,
      interaction: { mode: 'index', intersect: false },
      scales: {
        x: {
          type: 'linear',
          min: xMin,
          max: xMax,
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: {
            color: '#5a6a7a',
            font: { family: "'JetBrains Mono', monospace", size: 8 },
            maxTicksLimit: 5,
            callback: (v: any) => fmt(Number(v)),
          },
          border: { color: 'rgba(255,255,255,0.08)' },
        },
        y: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: {
            color: '#5a6a7a',
            font: { family: "'JetBrains Mono', monospace", size: 8 },
            maxTicksLimit: 4,
          },
          border: { color: 'rgba(255,255,255,0.08)' },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(8,10,14,0.92)',
          borderColor: 'rgba(0,128,230,0.3)',
          borderWidth: 1,
          titleColor: '#00d4ff',
          bodyColor: '#e8f0f8',
          titleFont: { family: "'JetBrains Mono', monospace", size: 8 },
          bodyFont:  { family: "'JetBrains Mono', monospace", size: 8 },
          padding: 6,
          callbacks: {
            title: (items: any[]) => fmt(items[0].parsed.x),
            label: (item: any) => {
              const lbl: string = item.dataset.label ?? ''
              if (lbl.endsWith('(upper)') || lbl.endsWith('(lower)') || lbl.endsWith(' ›')) return null as any
              const unit = relevantSeries.value[0]?.unit ?? ''
              return ` ${item.parsed.y.toFixed(1)}${unit ? ' ' + unit : ''}`
            },
          },
        },
        // Pass event timestamp to the custom plugin
        reportEventLine: { eventTs: ts },
      } as any,
    },
    plugins: [EVENT_LINE_PLUGIN],
  } as any)
}

onMounted(async () => {
  await hydrate()
  buildChart()
})

onUnmounted(() => {
  chartInstance?.destroy()
  chartInstance = null
})

// Rebuild when analytics data loads or report changes
watch(windowedSeries, () => {
  if (hasData.value) buildChart()
})

watch(() => props.reportTimestamp, () => {
  if (hasData.value) buildChart()
})

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('en-US', {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}
</script>

<style scoped>
.mini-graph-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
  background: rgba(8, 10, 14, 0.92);
  border-radius: 0.35rem;
  border: 1px solid rgba(0, 128, 230, 0.2);
}

.mini-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mini-title {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #00d4ff;
  margin: 0;
}

.mini-time {
  font-size: 0.65rem;
  color: #5a6a7a;
  font-family: 'JetBrains Mono', monospace;
}

.mini-chart-area {
  width: 280px;
  height: 120px;
}

.mini-canvas {
  width: 100%;
  height: 100%;
}

.mini-status {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  letter-spacing: 0.12em;
  color: #374151;
  font-family: 'JetBrains Mono', monospace;
}

.impact-metrics {
  display: flex;
  flex-direction: column;
  gap: 3px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding-top: 6px;
}

.impact-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  font-size: 0.65rem;
  color: #5a6a7a;
  font-family: 'JetBrains Mono', monospace;
}

.metric-value {
  font-size: 0.7rem;
  font-weight: 600;
  color: #e8f0f8;
  font-family: 'JetBrains Mono', monospace;
}

.metric-value.positive { color: #10b981; }
.metric-value.negative { color: #ef4444; }
</style>
