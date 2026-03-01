<template>
  <div class="mini-graph">
    <div class="graph-label">{{ label }}</div>
    <svg ref="svgRef" class="graph-svg" :viewBox="`0 0 ${width} ${height}`" preserveAspectRatio="none">
      <!-- Grid lines -->
      <line 
        v-for="i in 4" 
        :key="'h'+i"
        :x1="0" 
        :y1="(height / 5) * i" 
        :x2="width" 
        :y2="(height / 5) * i" 
        class="grid-line"
      />
      <line 
        v-for="i in 5" 
        :key="'v'+i"
        :x1="(width / 6) * i" 
        :y1="0" 
        :x2="(width / 6) * i" 
        :y2="height" 
        class="grid-line"
      />
      
      <!-- Area fill -->
      <path :d="areaPath" class="graph-area" />
      
      <!-- Line -->
      <path :d="linePath" class="graph-line" />
      
      <!-- Data points -->
      <circle 
        v-for="(point, i) in points" 
        :key="'pt'+i"
        :cx="point.x" 
        :cy="point.y" 
        r="1.5" 
        class="graph-point"
      />
      
      <!-- Forecast area (dashed) -->
      <path :d="forecastAreaPath" class="graph-forecast" />
      <path :d="forecastLinePath" class="graph-forecast-line" />
    </svg>
    
    <!-- Axis labels -->
    <div class="axis-labels">
      <span class="axis-label">{{ timeLabels[0] }}</span>
      <span class="axis-label">{{ timeLabels[1] }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { GlobeRegion } from './types'

const props = defineProps<{
  region: GlobeRegion
  label: string
}>()

const svgRef = ref<SVGSVGElement | null>(null)
const width = 196
const height = 60

// Generate mock data if not provided
const data = computed(() => {
  return props.region.data?.timeseries || generateMockData()
})

function generateMockData(): number[] {
  const base = 50 + Math.random() * 30
  return Array.from({ length: 12 }, (_, i) => {
    const trend = props.region.severity === 'critical' ? -3 : props.region.severity === 'warning' ? -1 : 0
    return Math.max(10, Math.min(100, base + trend * i + (Math.random() - 0.5) * 15))
  })
}

const points = computed(() => {
  const d = data.value
  return d.map((val, i) => ({
    x: (i / (d.length - 1)) * width,
    y: height - (val / 100) * height
  }))
})

const linePath = computed(() => {
  if (points.value.length < 2) return ''
  return 'M ' + points.value.map(p => `${p.x},${p.y}`).join(' L ')
})

const areaPath = computed(() => {
  if (points.value.length < 2) return ''
  const baseline = height
  return `M 0,${baseline} L ${points.value.map(p => `${p.x},${p.y}`).join(' L ')} L ${width},${baseline} Z`
})

// Forecast (last 3 points extended)
const forecastPoints = computed(() => {
  const d = data.value
  const lastVals = d.slice(-3)
  const trend = (lastVals[2] - lastVals[0]) / 2
  return [
    points.value[points.value.length - 1],
    {
      x: width * 0.85,
      y: Math.max(0, height - ((lastVals[2] + trend) / 100) * height)
    },
    {
      x: width,
      y: Math.max(0, height - ((lastVals[2] + trend * 2) / 100) * height)
    }
  ]
})

const forecastLinePath = computed(() => {
  if (forecastPoints.value.length < 2) return ''
  return 'M ' + forecastPoints.value.map(p => `${p.x},${p.y}`).join(' L ')
})

const forecastAreaPath = computed(() => {
  if (forecastPoints.value.length < 2) return ''
  const lastPoint = points.value[points.value.length - 1]
  return `M ${lastPoint.x},${height} L ${forecastPoints.value.map(p => `${p.x},${p.y}`).join(' L ')} L ${width},${height} Z`
})

const timeLabels = computed(() => {
  const now = new Date()
  return [
    `${now.getMonth() + 1}/${now.getFullYear().toString().slice(2)}`,
    `${(now.getMonth() + 4) % 12 + 1}/${(now.getMonth() + 4) >= 12 ? now.getFullYear() + 1 : now.getFullYear().toString().slice(2)}`
  ]
})
</script>

<style scoped>
.mini-graph {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.graph-label {
  font-size: 7px;
  letter-spacing: 0.12em;
  color: rgba(201, 162, 52, 0.5);
}

.graph-svg {
  width: 100%;
  height: 60px;
}

.grid-line {
  stroke: rgba(201, 162, 52, 0.08);
  stroke-width: 0.5;
}

.graph-area {
  fill: rgba(201, 162, 52, 0.1);
}

.graph-line {
  fill: none;
  stroke: rgba(201, 162, 52, 0.5);
  stroke-width: 1.2;
}

.graph-point {
  fill: #C9A234;
}

.graph-forecast {
  fill: rgba(201, 162, 52, 0.04);
}

.graph-forecast-line {
  fill: none;
  stroke: rgba(201, 162, 52, 0.25);
  stroke-width: 1;
  stroke-dasharray: 2 2;
}

.axis-labels {
  display: flex;
  justify-content: space-between;
}

.axis-label {
  font-size: 6px;
  letter-spacing: 0.1em;
  color: rgba(201, 162, 52, 0.3);
}
</style>
