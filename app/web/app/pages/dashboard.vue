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
            <div class="text-muted-foreground text-[8.5px] tracking-widest text-center mt-6 opacity-50">
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
import { lookupIso } from '@/shared/utils/locationMap'
import { useReportsApi } from '@/composables/useExternalApi'
import { useReportsStream } from '@/composables/useReportsStream'

definePageMeta({ layout: 'default' })

// severity ranking helpers
const severityRank: Record<string, number> = { critical: 4, warning: 3, elevated: 2, normal: 1 }
const rankToSeverity = (avg: number): GlobeRegion['severity'] => {
  if (avg >= 3.5) return 'critical'
  if (avg >= 2.5) return 'warning'
  if (avg >= 1.5) return 'elevated'
  return 'normal'
}

// holds the region data for the globe
const mockRegions: GlobeRegion[] = []

// fetch reports and aggregate severity by iso code
async function loadRegions() {
  try {
    const reportsApi = useReportsApi()
    const resp = await reportsApi.getReports(100, 0)
    const severityMap: Record<string, { total: number; count: number }> = {}

    resp.reports.forEach((r: any) => {
      (r.affectedLocations || []).forEach((loc: string) => {
        const iso = lookupIso(loc) || loc.toUpperCase().slice(0,3)
        const sev = r.severity || 'normal'
        const rank = severityRank[sev] || 1
        if (!severityMap[iso]) severityMap[iso] = { total: 0, count: 0 }
        severityMap[iso].total += rank
        severityMap[iso].count += 1
      })
    })

    mockRegions.length = 0
    const nameLookup = new Intl.DisplayNames(['en'], { type: 'region' })
    for (const [iso, { total, count }] of Object.entries(severityMap)) {
      const avg = total / count
      mockRegions.push({
        id: iso,
        name: nameLookup.of(iso) || iso,
        countryCode: iso,
        severity: rankToSeverity(avg),
        data: {
          report_count: count,
          severityAvg: avg
        }
      })
    }
  } catch (e) {
    console.error('Failed to load report regions', e)
  }
}

// also refresh when new reports arrive via SSE
const reportsStream = useReportsStream({ maxReports: 200, autoConnect: true })
watch(reportsStream.reports, () => {
  loadRegions()
}, { deep: true })

loadRegions()
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
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.hero-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 14px;
  background: color-mix(in srgb, var(--primary) 5%, transparent);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.hero-label {
  font-size: 8.5px;
  letter-spacing: 0.18em;
  font-weight: 700;
  color: var(--primary);
}

.hero-count {
  font-size: 7.5px;
  letter-spacing: 0.1em;
  color: var(--muted-foreground);
}

.hero-body {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
</style>
