<template>
  <!--
    Example: drop AppGlobe into your /dashboard page layout.
    Wrap in <ClientOnly> so Nuxt SSR doesn't try to run globe.gl server-side.
  -->
  <div class="dashboard-globe-panel">
    <div class="panel-header">
      <span class="panel-tag">GLOBAL RESOURCE MAP</span>
      <span class="panel-subtitle">LIVE // {{ activeRegions.length }} SECTORS MONITORED</span>
    </div>

    <ClientOnly>
      <AppGlobe
        :regions="activeRegions"
        :auto-rotate-speed="0.12"
        :height="460"
        @navigate="handleGlobeNavigate"
      />
      <template #fallback>
        <div class="globe-skeleton" style="height: 460px" />
      </template>
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
import AppGlobe from '~/components/globe/AppGlobe.vue'
import type { GlobeRegion } from '~/components/globe/types'

// Replace with useAsyncData / useFetch from your API
const activeRegions: GlobeRegion[] = [
  {
    id: 'USA',
    name: 'United States',
    countryCode: 'USA',
    severity: 'warning',
    data: { sector: 'NORTH_AMERICA', resource: 'vibranium', depletion_pct: 67, forecast_days: 14, report_count: 8 },
  },
  {
    id: 'RUS',
    name: 'Russia',
    countryCode: 'RUS',
    severity: 'critical',
    data: { sector: 'EURASIA', resource: 'energy_cells', depletion_pct: 91, forecast_days: 3, report_count: 22 },
  },
  {
    id: 'GBR',
    name: 'United Kingdom',
    countryCode: 'GBR',
    severity: 'elevated',
    data: { sector: 'EUROPE', resource: 'medical', depletion_pct: 45, forecast_days: 30, report_count: 5 },
  },
  {
    id: 'IND',
    name: 'India',
    countryCode: 'IND',
    severity: 'normal',
    data: { sector: 'SOUTH_ASIA', resource: 'arc_fuel', depletion_pct: 22, forecast_days: 90, report_count: 2 },
  },
  {
    id: 'NGA',
    name: 'Nigeria',
    countryCode: 'NGA',
    severity: 'critical',
    data: { sector: 'WEST_AFRICA', resource: 'vibranium', depletion_pct: 88, forecast_days: 5, report_count: 17 },
  },
]

function handleGlobeNavigate(region: GlobeRegion) {
  // navigateToAnalytics(region) — the component handles router.push internally
  // but you can override logic here if needed
  console.log('[Globe] Navigate to region:', region.id)
}
</script>

<style scoped>
.dashboard-globe-panel {
  background: #080a0e;
  border: 1px solid rgba(201, 162, 52, 0.2);
  border-radius: 6px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding: 10px 16px;
  border-bottom: 1px solid rgba(201, 162, 52, 0.12);
  font-family: 'JetBrains Mono', monospace;
}

.panel-tag {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.14em;
  color: #C9A234;
}

.panel-subtitle {
  font-size: 8.5px;
  letter-spacing: 0.1em;
  color: rgba(201, 162, 52, 0.4);
}

.globe-skeleton {
  background: repeating-linear-gradient(
    90deg,
    rgba(201, 162, 52, 0.03) 0px,
    rgba(201, 162, 52, 0.03) 1px,
    transparent 1px,
    transparent 24px
  ),
  repeating-linear-gradient(
    180deg,
    rgba(201, 162, 52, 0.03) 0px,
    rgba(201, 162, 52, 0.03) 1px,
    transparent 1px,
    transparent 24px
  );
}
</style>