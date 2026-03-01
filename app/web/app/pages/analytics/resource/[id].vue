<template>
  <div class="detail-root">

    <!-- ── Toolbar ─────────────────────────────────────────────────────────── -->
    <div class="page-toolbar">
      <div class="breadcrumb-nav">
        <NuxtLink to="/analytics" class="bc-link">ANALYTICS</NuxtLink>
        <span class="bc-sep">/</span>
        <span class="bc-dim">RESOURCES</span>
        <span class="bc-sep">/</span>
        <span class="bc-current">{{ formatResource(resourceId) }}</span>
      </div>
      <div class="toolbar-right">
        <div class="pill-nav">
          <NuxtLink
            v-for="res in resources"
            :key="res"
            :to="`/analytics/resource/${res}`"
            class="nav-chip"
            :class="{ active: res === resourceId }"
          >{{ formatResource(res) }}</NuxtLink>
        </div>
        <span class="stream-badge" :class="{ active: connected }">
          <span class="stream-dot" />{{ connected ? 'LIVE' : 'OFFLINE' }}
        </span>
      </div>
    </div>

    <!-- ── Stats row ───────────────────────────────────────────────────────── -->
    <div class="stats-row">
      <div
        v-for="s in seriesList"
        :key="s.id"
        class="stat-card"
        :style="{ borderLeftColor: s.color }"
      >
        <span class="stat-name">{{ formatSector(sectorFromId(s.id)) }}</span>
        <span class="stat-val" :style="{ color: s.color }">
          {{ lastVal(s) }}<span class="stat-unit"> {{ s.unit }}</span>
        </span>
        <span class="stat-trend" :style="{ color: trendColor(s) }">{{ trendLabel(s) }}</span>
        <span v-if="criticalTime(s)" class="stat-crit">{{ criticalTime(s) }}</span>
      </div>
    </div>

    <!-- ── Main chart ──────────────────────────────────────────────────────── -->
    <div class="main-chart-area">
      <AnalyticsChart
        :series="seriesList"
        :title="`${formatResource(resourceId)} — ALL SECTORS`"
        :is-streaming="connected"
        :loading="!hydrated"
        :now-ratio="0.62"
      />
    </div>

  </div>
</template>

<script setup lang="ts">
import type { AnalyticsSeries } from '~/utils/analyticsTypes'

const route      = useRoute()
const resourceId = computed(() => (route.params.id as string).toLowerCase())

const { connected, hydrated, resources, seriesForResource } = useAnalyticsStream()

const seriesList = seriesForResource(resourceId)

// ── Helpers ────────────────────────────────────────────────────────────────
function formatSector(s: string)   { return s.replace(/_/g, ' ') }
function formatResource(r: string) { return r.replace(/_/g, ' ').toUpperCase() }
function sectorFromId(id: string)  { return id.split('::')[1] }

function lastVal(s: AnalyticsSeries): string {
  return s.data.length ? s.data[s.data.length - 1].value.toFixed(1) : '—'
}

function trendLabel(s: AnalyticsSeries): string {
  if (!s.forecast) return '—'
  const dir = s.forecast.slope < 0 ? '↓' : '↑'
  return `${dir} ${Math.abs(s.forecast.slope).toFixed(2)} /h`
}

function trendColor(s: AnalyticsSeries): string {
  if (!s.forecast) return '#5a6a7a'
  return s.forecast.slope < -0.3 ? '#ef4444' : s.forecast.slope < 0 ? '#f97316' : '#22c55e'
}

function criticalTime(s: AnalyticsSeries): string | null {
  const fc = s.forecast
  if (!fc || !s.data.length || fc.slope >= 0) return null
  const last = s.data[s.data.length - 1]
  const thr  = fc.critical_threshold ?? 0
  if (last.value <= thr) return 'CRITICAL'
  const h = (last.value - thr) / Math.abs(fc.slope)
  if (h > 168) return null
  if (h < 24)  return `CRIT IN ${Math.round(h)}h`
  return `CRIT IN ${Math.round(h / 24)}d`
}
</script>

<style scoped>
.detail-root {
  display: flex;
  flex-direction: column;
  gap: 14px;
  height: calc(100vh - 3.5rem - 48px);
}

/* ── Toolbar ─────────────────────────────────────────────────────────────── */
.page-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  flex-shrink: 0;
}

.breadcrumb-nav {
  display: flex;
  align-items: center;
  gap: 7px;
}

.bc-link {
  font-size: 9px;
  letter-spacing: 0.14em;
  color: #5a6a7a;
  text-decoration: none;
  transition: color 0.15s;
}

.bc-link:hover { color: #00d4ff; }

.bc-dim {
  font-size: 9px;
  letter-spacing: 0.14em;
  color: #374151;
}

.bc-sep { color: #2d3748; font-size: 9px; }

.bc-current {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.18em;
  color: #00d4ff;
  text-transform: uppercase;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.pill-nav {
  display: flex;
  align-items: center;
  gap: 5px;
  flex-wrap: wrap;
}

.nav-chip {
  font-size: 7.5px;
  letter-spacing: 0.1em;
  color: #5a6a7a;
  padding: 2px 8px;
  border: 1px solid rgba(0, 128, 230, 0.2);
  border-radius: 3px;
  text-decoration: none;
  text-transform: uppercase;
  white-space: nowrap;
  transition: all 0.15s;
}

.nav-chip:hover  { color: #e8f0f8; border-color: rgba(0, 128, 230, 0.4); }
.nav-chip.active { color: #00d4ff; border-color: rgba(0, 212, 255, 0.45); background: rgba(0, 212, 255, 0.07); }

.stream-badge {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 8px;
  letter-spacing: 0.12em;
  color: #4b5563;
}

.stream-badge.active { color: #22c55e; }

.stream-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #374151;
  flex-shrink: 0;
}

.stream-badge.active .stream-dot {
  background: #22c55e;
  box-shadow: 0 0 5px #22c55e;
  animation: blink 2s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.2; }
}

/* ── Stats row ───────────────────────────────────────────────────────────── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  flex-shrink: 0;
}

@media (max-width: 1100px) {
  .stats-row { grid-template-columns: repeat(3, 1fr); }
}

.stat-card {
  padding: 9px 12px;
  background: #080a0e;
  border: 1px solid rgba(0, 128, 230, 0.15);
  border-left: 3px solid;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.stat-name {
  font-size: 7.5px;
  letter-spacing: 0.14em;
  color: #5a6a7a;
  text-transform: uppercase;
}

.stat-val {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.04em;
  line-height: 1.1;
}

.stat-unit {
  font-size: 9px;
  font-weight: 400;
  opacity: 0.7;
}

.stat-trend {
  font-size: 8px;
  letter-spacing: 0.08em;
}

.stat-crit {
  font-size: 7px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #ef4444;
  padding: 1px 5px;
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 2px;
  align-self: flex-start;
  margin-top: 2px;
}

/* ── Main chart ──────────────────────────────────────────────────────────── */
.main-chart-area {
  flex: 1;
  min-height: 0;
}
</style>
