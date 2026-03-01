<template>
  <div>
    <DashboardWelcome />
    
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
      <!-- Left: Globe -->
      <div class="lg:col-span-2">
        <GlobeDisplay :regions="mockRegions" />
      </div>
      
      <!-- Right: Priority Events -->
      <div class="bg-[#0d2137] border border-slate-700 rounded-xl p-4">
        <h3 class="text-white font-semibold mb-4">Priority Event Reports</h3>
        <!-- Priority Events placeholder - Phase 4 -->
        <div class="text-slate-500 text-sm">
          Priority Events - Phase 4
        </div>
      </div>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
      <!-- Left: Anonymous Hero Reports -->
      <div class="lg:col-span-2 bg-[#0d2137] border border-slate-700 rounded-xl p-4">
        <h3 class="text-white font-semibold mb-4">Anonymous Hero Reports</h3>
        <!-- Hero Reports placeholder - Phase 4 -->
        <div class="text-slate-500 text-sm">
          Hero Reports - Phase 4
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import GlobeDisplay from '@/components/GlobeDisplay.vue'
import type { GlobeRegion } from '@/components/globe/types'

definePageMeta({
  layout: 'default'
})

const mockRegions: GlobeRegion[] = [
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
</script>
