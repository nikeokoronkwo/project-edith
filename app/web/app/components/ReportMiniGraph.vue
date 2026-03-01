<template>
  <div class="mini-graph-container">
    <div class="mini-header">
      <h4 class="mini-title">Impact at report time</h4>
      <span class="mini-time">{{ formatDate(reportTimestamp) }}</span>
    </div>

    <div class="mini-chart-area">
      <canvas ref="canvasRef" class="mini-canvas" />
    </div>

    <div class="impact-metrics">
      <div v-if="impactData" class="impact-row">
        <span class="metric-label">Trend impact:</span>
        <span :class="['metric-value', impactData.isPositive ? 'positive' : 'negative']">
          {{ impactData.percentChange > 0 ? '+' : '' }}{{ impactData.percentChange.toFixed(1) }}%
        </span>
      </div>
      <div v-if="impactData" class="impact-row">
        <span class="metric-label">Before:</span>
        <span class="metric-value">{{ impactData.gradientBefore.toFixed(2) }}</span>
      </div>
      <div v-if="impactData" class="impact-row">
        <span class="metric-label">After:</span>
        <span class="metric-value">{{ impactData.gradientAfter.toFixed(2) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import Chart from 'chart.js/auto'
import type { Chart as ChartJS } from 'chart.js/auto'

interface Props {
  reportTimestamp: string
  reportId?: string
  affectedResources?: string[]
}

const props = defineProps<Props>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
let chartInstance: ChartJS | null = null

interface ImpactData {
  percentChange: number
  gradientBefore: number
  gradientAfter: number
  isPositive: boolean
}

const impactData = ref<ImpactData | null>(null)

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function generateMiniGraph() {
  if (!canvasRef.value) return

  // Simulate fetching analytics data at report timestamp
  // In production, this would call an API endpoint like /api/analytics/at-timestamp
  const reportDate = new Date(props.reportTimestamp)
  const oneHourBefore = new Date(reportDate.getTime() - 3600000)
  const oneHourAfter = new Date(reportDate.getTime() + 3600000)

  // Generate mock data points (in production this comes from server)
  const labels = []
  const dataPoints = []
  for (let i = -60; i <= 60; i += 5) {
    const date = new Date(reportDate.getTime() + i * 60000)
    labels.push(date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }))
    // Simulate trend: slight upward before report, steeper after
    const trend = i < 0 ? 50 + i * 0.3 : 50 + i * 0.6 + Math.random() * 5
    dataPoints.push(trend)
  }

  // Calculate impact metrics
  const beforeValues = dataPoints.slice(0, 6)
  const afterValues = dataPoints.slice(7, 13)

  const gradientBefore = (beforeValues[5] - beforeValues[0]) / 6
  const gradientAfter = (afterValues[5] - afterValues[0]) / 6
  const percentChange = ((gradientAfter - gradientBefore) / Math.abs(gradientBefore || 1)) * 100

  impactData.value = {
    percentChange,
    gradientBefore,
    gradientAfter,
    isPositive: gradientAfter > gradientBefore,
  }

  if (chartInstance) {
    chartInstance.destroy()
  }

  chartInstance = new Chart(canvasRef.value, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Resource Level',
          data: dataPoints,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59,130,246,0.1)',
          borderWidth: 2,
          pointRadius: 2,
          pointBackgroundColor: '#3b82f6',
          pointBorderColor: '#fff',
          tension: 0.2,
        },
        {
          label: 'Report Event',
          data: Array(dataPoints.length).fill(null),
          pointRadius: Array(dataPoints.length)
            .fill(0)
            .map((_, i) => (i === 12 ? 8 : 0)),
          pointBackgroundColor: '#f59e0b',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          showLine: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          enabled: true,
          backgroundColor: 'rgba(0,0,0,0.8)',
          padding: 6,
          titleFont: { size: 11 },
          bodyFont: { size: 10 },
        },
      },
      scales: {
        x: {
          display: true,
          grid: { display: false },
          ticks: {
            font: { size: 9 },
            maxTicksLimit: 4,
          },
        },
        y: {
          display: true,
          grid: { color: 'rgba(255,255,255,0.1)' },
          ticks: {
            font: { size: 9 },
            maxTicksLimit: 4,
          },
        },
      },
    },
  })
}

onMounted(() => {
  generateMiniGraph()
})

watch(() => props.reportTimestamp, () => {
  generateMiniGraph()
})
</script>

<style scoped>
.mini-graph-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
  background: rgba(13, 17, 23, 0.8);
  border-radius: 0.35rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.mini-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mini-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.mini-time {
  font-size: 0.7rem;
  color: var(--muted-foreground);
}

.mini-chart-area {
  width: 280px;
  height: 120px;
}

.mini-canvas {
  width: 100%;
  height: 100%;
}

.impact-metrics {
  display: flex;
  flex-direction: column;
  gap: 4px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 6px;
}

.impact-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  font-size: 0.7rem;
  color: var(--muted-foreground);
}

.metric-value {
  font-size: 0.75rem;
  font-weight: 500;
  color: #fff;
}

.metric-value.positive {
  color: #10b981;
}

.metric-value.negative {
  color: #ef4444;
}
</style>