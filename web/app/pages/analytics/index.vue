<template>
  <div class="analytics-root">

    <!-- ── Toolbar ─────────────────────────────────────────────────────────── -->
    <div class="an-toolbar">
      <div class="an-breadcrumb">
        <span class="bc-current">ANALYTICS</span>
        <span class="bc-sep">/</span>
        <span class="bc-label">SECTOR OVERVIEW</span>
      </div>
      <div class="an-toolbar-right">
        <div class="res-nav">
          <NuxtLink
            v-for="res in resources"
            :key="res"
            :to="`/analytics/resource/${res}`"
            class="res-nav-chip"
          >{{ formatResource(res) }}</NuxtLink>
        </div>
        <span class="stream-badge" :class="{ active: connected }">
          <span class="stream-dot" />{{ connected ? 'LIVE' : 'OFFLINE' }}
        </span>
      </div>
    </div>

    <!-- ── Loading ─────────────────────────────────────────────────────────── -->
    <div v-if="!hydrated" class="loading-state">
      <span class="loading-label">LOADING SECTOR DATA...</span>
    </div>

    <!-- ── Sector grid ─────────────────────────────────────────────────────── -->
    <div v-else class="sector-grid">
      <NuxtLink
        v-for="sector in sectors"
        :key="sector"
        :to="`/analytics/sector/${sector}`"
        class="sector-card"
      >
        <div class="sc-header">
          <span class="sc-name">{{ formatSector(sector) }}</span>
          <span class="sc-status" :class="`st-${getStatus(sector).toLowerCase()}`">
            {{ getStatus(sector) }}
          </span>
        </div>

        <div class="sc-chart">
          <AnalyticsChart
            :series="sectorSeries(sector)"
            compact
            :is-streaming="connected"
          />
        </div>

        <div class="sc-footer">
          <span
            v-for="s in sectorSeries(sector)"
            :key="s.id"
            class="sc-pill"
            :style="{ color: s.color }"
          >
            {{ formatResource(resourceFromId(s.id)) }}<span class="sc-pill-val"> {{ lastVal(s) }}{{ s.unit }}</span>
          </span>
        </div>
      </NuxtLink>
    </div>

  </div>
</template>

<script setup lang="ts">
import type { AnalyticsSeries } from '~/utils/analyticsTypes'

const { allSeries, resources, sectors, connected, hydrated } = useAnalyticsStream()

// ── Helpers ────────────────────────────────────────────────────────────────
function formatSector(s: string)   { return s.replace(/_/g, ' ') }
function formatResource(r: string) { return r.replace(/_/g, ' ').toUpperCase() }
function resourceFromId(id: string){ return id.split('::')[0] }

function sectorSeries(sector: string): AnalyticsSeries[] {
  return allSeries.value.filter(s => s.id.endsWith(`::${sector}`))
}

function lastVal(s: AnalyticsSeries): string {
  return s.data.length ? s.data[s.data.length - 1].value.toFixed(1) : '—'
}

function getStatus(sector: string): string {
  let min = Infinity
  for (const s of sectorSeries(sector)) {
    if (!s.forecast || !s.data.length) continue
    const fc   = s.forecast
    const last = s.data[s.data.length - 1]
    const thr  = fc.critical_threshold ?? 0
    if (fc.slope < 0 && last.value > thr) {
      min = Math.min(min, (last.value - thr) / Math.abs(fc.slope))
    }
  }
  if (min < 24)  return 'CRITICAL'
  if (min < 72)  return 'HIGH'
  if (min < 168) return 'ELEVATED'
  return 'NOMINAL'
}
</script>

<style scoped>
.analytics-root {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* ── Toolbar ─────────────────────────────────────────────────────────────── */
.an-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  flex-shrink: 0;
}

.an-breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bc-current {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.18em;
  color: #00d4ff;
}

.bc-sep   { color: #2d3748; font-size: 10px; }
.bc-label { font-size: 10px; letter-spacing: 0.14em; color: #5a6a7a; }

.an-toolbar-right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.res-nav {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.res-nav-chip {
  font-size: 7.5px;
  letter-spacing: 0.12em;
  color: #5a6a7a;
  padding: 3px 8px;
  border: 1px solid rgba(0, 128, 230, 0.2);
  border-radius: 3px;
  text-decoration: none;
  text-transform: uppercase;
  transition: all 0.15s;
}

.res-nav-chip:hover {
  color: #00d4ff;
  border-color: rgba(0, 212, 255, 0.4);
  background: rgba(0, 212, 255, 0.05);
}

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

/* ── Loading ─────────────────────────────────────────────────────────────── */
.loading-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-label {
  font-size: 9px;
  letter-spacing: 0.18em;
  color: #2d3748;
}

/* ── Sector grid ─────────────────────────────────────────────────────────── */
.sector-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

@media (max-width: 1100px) {
  .sector-grid { grid-template-columns: repeat(2, 1fr); }
}

/* ── Sector card ─────────────────────────────────────────────────────────── */
.sector-card {
  display: flex;
  flex-direction: column;
  background: #080a0e;
  border: 1px solid rgba(0, 128, 230, 0.18);
  border-radius: 10px;
  overflow: hidden;
  text-decoration: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.sector-card:hover {
  border-color: rgba(0, 212, 255, 0.35);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.06);
}

.sc-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-bottom: 1px solid rgba(0, 128, 230, 0.1);
  background: rgba(0, 128, 230, 0.04);
  flex-shrink: 0;
}

.sc-name {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.16em;
  color: #e8f0f8;
  text-transform: uppercase;
}

.sc-status {
  font-size: 7px;
  font-weight: 700;
  letter-spacing: 0.12em;
  padding: 2px 7px;
  border-radius: 2px;
  border: 1px solid currentColor;
}

.st-critical { color: #ef4444; background: rgba(239, 68, 68, 0.08); }
.st-high     { color: #f97316; background: rgba(249, 115, 22, 0.08); }
.st-elevated { color: #eab308; background: rgba(234, 179, 8, 0.08); }
.st-nominal  { color: #22c55e; background: rgba(34, 197, 94, 0.08); }

.sc-chart {
  height: 130px;
  flex-shrink: 0;
}

.sc-footer {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 10px;
  padding: 7px 10px;
  border-top: 1px solid rgba(0, 128, 230, 0.08);
  background: rgba(0, 0, 0, 0.15);
  flex-shrink: 0;
}

.sc-pill {
  font-size: 7px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  white-space: nowrap;
}

.sc-pill-val {
  opacity: 0.7;
  font-weight: 700;
}
</style>
