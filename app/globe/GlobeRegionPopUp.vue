<template>
  <div class="region-popup" role="tooltip" :aria-label="`Region data for ${region.name}`">
    <!-- Header -->
    <div class="popup-header">
      <div class="popup-header-left">
        <span class="severity-pip" :class="`sev-${region.severity ?? 'normal'}`" />
        <span class="region-name">{{ region.name }}</span>
      </div>
      <span class="region-code">{{ region.countryCode }}</span>
    </div>

    <!-- Status badges -->
    <div class="popup-badges">
      <span class="badge" :class="`badge-${region.severity ?? 'normal'}`">
        {{ severityLabel }}
      </span>
      <span class="badge badge-muted" v-if="region.data?.sector">
        {{ region.data.sector }}
      </span>
      <span class="badge badge-muted" v-if="region.data?.resource">
        {{ region.data.resource }}
      </span>
    </div>

    <!-- Mini graph -->
    <GlobeRegionMiniGraph :region="region" :label="graphLabel" />

    <!-- Quick stats row -->
    <div class="popup-stats">
      <div class="stat-cell" v-for="stat in quickStats" :key="stat.label">
        <span class="stat-label">{{ stat.label }}</span>
        <span class="stat-value" :class="stat.cls">{{ stat.value }}</span>
      </div>
    </div>

    <!-- CTA -->
    <button class="popup-cta" @click="$emit('navigate', region)" tabindex="0">
      VIEW ANALYTICS
      <svg width="10" height="10" viewBox="0 0 10 10" fill="none" aria-hidden="true">
        <path d="M2 5h6M5 2l3 3-3 3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>

    <!-- Corner accents -->
    <span class="popup-corner tl" aria-hidden="true" />
    <span class="popup-corner tr" aria-hidden="true" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import GlobeRegionMiniGraph from './GlobeRegionMiniGraph.vue'
import type { GlobeRegion } from './types'

// ── Props & emits ─────────────────────────────────────────────────────────────
const props = defineProps<{
  region: GlobeRegion
}>()

defineEmits<{
  (e: 'navigate', region: GlobeRegion): void
}>()

// ── Derived ───────────────────────────────────────────────────────────────────
const severityLabel = computed(() => ({
  critical: '⚠ CRITICAL',
  warning:  '! WARNING',
  elevated: '↑ ELEVATED',
  normal:   '✓ NOMINAL',
}[props.region.severity ?? 'normal']))

const graphLabel = computed(() =>
  props.region.data?.resource
    ? props.region.data.resource.toUpperCase() + ' INDEX'
    : 'RESOURCE INDEX',
)

// Dummy quick-stats — replace with real data from region.data
const quickStats = computed(() => {
  const r = props.region
  return [
    {
      label: 'DEPLETION',
      value: r.data?.depletion_pct != null ? `${r.data.depletion_pct}%` : '--',
      cls: r.severity === 'critical' ? 'val-red' : r.severity === 'warning' ? 'val-amber' : 'val-green',
    },
    {
      label: 'FORECAST',
      value: r.data?.forecast_days != null ? `${r.data.forecast_days}d` : '--',
      cls: '',
    },
    {
      label: 'REPORTS',
      value: r.data?.report_count != null ? String(r.data.report_count) : '--',
      cls: 'val-gold',
    },
  ]
})
</script>

<style scoped>
.region-popup {
  position: relative;
  width: 220px;
  background: rgba(8, 10, 14, 0.96);
  border: 1px solid rgba(201, 162, 52, 0.28);
  border-radius: 4px;
  padding: 12px 12px 10px;
  display: flex;
  flex-direction: column;
  gap: 9px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  box-shadow:
    0 0 0 1px rgba(201, 162, 52, 0.08),
    0 8px 32px rgba(0, 0, 0, 0.7),
    0 0 24px rgba(201, 162, 52, 0.06) inset;
  backdrop-filter: blur(8px);
  pointer-events: none; /* parent enables this on hover */
}

/* Corner accents */
.popup-corner {
  position: absolute;
  width: 8px;
  height: 8px;
  border-color: rgba(201, 162, 52, 0.6);
  border-style: solid;
}
.popup-corner.tl { top: -1px; left: -1px;  border-width: 1.5px 0 0 1.5px; }
.popup-corner.tr { top: -1px; right: -1px; border-width: 1.5px 1.5px 0 0; }

/* Header */
.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.popup-header-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.severity-pip {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.sev-critical { background: #c0392b; box-shadow: 0 0 5px #c0392b; }
.sev-warning  { background: #e67e22; box-shadow: 0 0 5px #e67e22; }
.sev-elevated { background: #f1c40f; box-shadow: 0 0 5px #f1c40f; }
.sev-normal   { background: #22c55e; box-shadow: 0 0 5px #22c55e; }

.region-name {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #e8e0cc;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 140px;
}

.region-code {
  font-size: 9px;
  letter-spacing: 0.15em;
  color: rgba(201, 162, 52, 0.5);
}

/* Badges */
.popup-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.badge {
  font-size: 8px;
  letter-spacing: 0.1em;
  padding: 2px 6px;
  border-radius: 2px;
  border: 1px solid;
}

.badge-critical { border-color: rgba(192,57,43,0.5); color: #c0392b; background: rgba(192,57,43,0.1); }
.badge-warning  { border-color: rgba(230,126,34,0.5); color: #e67e22; background: rgba(230,126,34,0.1); }
.badge-elevated { border-color: rgba(241,196,15,0.5); color: #f1c40f; background: rgba(241,196,15,0.1); }
.badge-normal   { border-color: rgba(34,197,94,0.4); color: #22c55e; background: rgba(34,197,94,0.08); }
.badge-muted    { border-color: rgba(201,162,52,0.2); color: rgba(201,162,52,0.55); background: transparent; }

/* Quick stats */
.popup-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  background: rgba(201, 162, 52, 0.1);
  border: 1px solid rgba(201, 162, 52, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.stat-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 5px 6px;
  background: rgba(8, 10, 14, 0.8);
  align-items: center;
}

.stat-label {
  font-size: 7.5px;
  letter-spacing: 0.1em;
  color: rgba(201, 162, 52, 0.4);
}

.stat-value {
  font-size: 11px;
  font-weight: 700;
  color: #e8e0cc;
}

.val-red   { color: #c0392b; }
.val-amber { color: #e67e22; }
.val-green { color: #22c55e; }
.val-gold  { color: #C9A234; }

/* CTA */
.popup-cta {
  pointer-events: all;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  width: 100%;
  padding: 6px;
  background: rgba(201, 162, 52, 0.08);
  border: 1px solid rgba(201, 162, 52, 0.25);
  border-radius: 3px;
  font-family: inherit;
  font-size: 8.5px;
  font-weight: 700;
  letter-spacing: 0.14em;
  color: #C9A234;
  cursor: pointer;
  transition: all 0.15s;
}

.popup-cta:hover {
  background: rgba(201, 162, 52, 0.16);
  border-color: rgba(201, 162, 52, 0.5);
  box-shadow: 0 0 8px rgba(201, 162, 52, 0.15);
}
</style>