<template>
  <div class="dashboard-root">
    <DashboardWelcome />

    <!-- Main grid: fills remaining height so nothing scrolls -->
    <div class="main-grid">
      <!-- Left: Globe (2/3) -->
      <div class="globe-col">
        <GlobeDisplay :regions="mockRegions" />
      </div>

      <!-- Right: stacked panels (1/3) -->
      <div class="right-col">
        <!-- Top-right: Priority Events -->
        <PriorityEventList />

        <!-- Bottom-right: Anonymous Hero Reports -->
        <div class="hero-panel">
          <div class="hero-header">
            <span class="hero-label">ANONYMOUS HERO REPORTS</span>
            <span class="hero-count">12 PENDING</span>
          </div>
          <div class="hero-body">
            <div class="text-[#4b5563] text-[8.5px] tracking-widest text-center mt-6">
              HERO REPORTS — PHASE 4.4
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import GlobeDisplay from '@/components/GlobeDisplay.vue'
import PriorityEventList from '@/components/PriorityEventList.vue'
import type { GlobeRegion } from '@/components/globe/types'

definePageMeta({ layout: 'default' })

const mockRegions: GlobeRegion[] = [
  {
    id: 'USA', name: 'United States', countryCode: 'USA', severity: 'warning',
    data: { sector: 'NORTH_AMERICA', resource: 'vibranium', depletion_pct: 67, forecast_days: 14, report_count: 8 },
  },
  {
    id: 'RUS', name: 'Russia', countryCode: 'RUS', severity: 'critical',
    data: { sector: 'EURASIA', resource: 'energy_cells', depletion_pct: 91, forecast_days: 3, report_count: 22 },
  },
  {
    id: 'GBR', name: 'United Kingdom', countryCode: 'GBR', severity: 'elevated',
    data: { sector: 'EUROPE', resource: 'medical', depletion_pct: 45, forecast_days: 30, report_count: 5 },
  },
  {
    id: 'IND', name: 'India', countryCode: 'IND', severity: 'normal',
    data: { sector: 'SOUTH_ASIA', resource: 'arc_fuel', depletion_pct: 22, forecast_days: 90, report_count: 2 },
  },
  {
    id: 'NGA', name: 'Nigeria', countryCode: 'NGA', severity: 'critical',
    data: { sector: 'WEST_AFRICA', resource: 'vibranium', depletion_pct: 88, forecast_days: 5, report_count: 17 },
  },
]
</script>

<style scoped>
/*
  Layout math (header = 56px, content padding p-6 = 24px each side):
    Available height = 100vh - 56px - 24px (top) - 24px (bottom) = 100vh - 104px
    DashboardWelcome ≈ 44px  +  gap 12px  = 56px
    Main grid height = 100vh - 104px - 56px = 100vh - 160px
*/

.dashboard-root {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 104px);
  gap: 12px;
  overflow: hidden;
}

.main-grid {
  flex: 1;
  min-height: 0;          /* allow flex child to shrink */
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 14px;
}

/* ── Globe column ── */
.globe-col {
  min-height: 0;
  height: 100%;
}

/* ── Right column ── */
.right-col {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 0;
  overflow: hidden;
}

/* ── Hero reports panel ── */
.hero-panel {
  flex: 1;
  min-height: 0;
  background: #080a0e;
  border: 1px solid rgba(0, 128, 230, 0.18);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.hero-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 14px;
  background: rgba(0, 128, 230, 0.05);
  border-bottom: 1px solid rgba(0, 128, 230, 0.12);
  flex-shrink: 0;
}

.hero-label {
  font-size: 8.5px;
  letter-spacing: 0.18em;
  font-weight: 700;
  color: #00d4ff;
}

.hero-count {
  font-size: 7.5px;
  letter-spacing: 0.1em;
  color: #5a6a7a;
}

.hero-body {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
</style>
