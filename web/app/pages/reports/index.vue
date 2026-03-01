<template>
  <div class="reports-root">
    <div class="header-bar">
      <h1 class="title">Field Reports</h1>
      <NuxtLink to="/reports/new" class="new-btn">
        <Icon name="heroicons:plus" class="w-4 h-4" />
        <span>New Report</span>
      </NuxtLink>
    </div>

    <div class="reports-list" ref="listRef">
      <TransitionGroup name="report-slide">
        <div
          v-for="rep in sortedReports"
          :key="rep.id"
          class="report-card"
          :class="{ 'is-new': newIds.has(rep.id), 'is-open': expandedId === rep.id }"
          @click="toggleExpand(rep.id)"
          @mouseenter="hoveredReportId = rep.id"
          @mouseleave="hoveredReportId = null"
        >
          <div class="card-body">
            <div class="card-row">
              <p class="report-title">{{ redact(rep.heroAlias) }}</p>
              <span class="report-time">{{ timeAgo(String(rep.timeStarted || rep.timestamp)) }}</span>
            </div>
            <Transition name="expand">
              <div v-if="expandedId === rep.id" class="expanded-body">
                <p class="report-desc">{{ rep.description }}</p>
              </div>
            </Transition>
          </div>
          <Icon
            name="heroicons:chevron-right"
            class="card-chevron"
            :class="{ 'is-open': expandedId === rep.id }"
          />

          <!-- Mini-graph tooltip on hover -->
          <Transition name="fade">
            <div v-if="hoveredReportId === rep.id" class="mini-graph-tooltip">
              <ReportMiniGraph
                :report-timestamp="String(rep.timeStarted || rep.timestamp)"
                :report-id="rep.id"
                :affected-resources="rep.affectedResources"
              />
            </div>
          </Transition>
        </div>
      </TransitionGroup>

      <div v-if="sortedReports.length === 0" class="empty-state">
        <Icon name="heroicons:shield-check" class="empty-icon" />
        <p class="empty-text">NO REPORTS AVAILABLE</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useReportsStream } from '@/composables/useReportsStream';
import ReportMiniGraph from '@/components/ReportMiniGraph.vue'
import type { StreamReport } from '@/composables/useReportsStream';

definePageMeta({ layout: 'default' });

const listRef = ref<HTMLElement | null>(null);
const expandedId = ref<string | null>(null);
const hoveredReportId = ref<string | null>(null);
const newIds = ref<Set<string>>(new Set());

const { data: initialData } = await useFetch<{ reports: StreamReport[] }>('/api/reports');
const reports = ref<StreamReport[]>(initialData.value?.reports || []);

const stream = useReportsStream({ maxReports: 100, autoConnect: true });

watch(stream.reports, (incoming) => {
  // merge new reports while preserving order and avoiding dupes
  for (const r of incoming) {
    if (!reports.value.some(x => x.id === r.id)) {
      reports.value.push(r);
      markNew(r.id);
    }
  }
});

const sortedReports = computed(() => {
  return [...reports.value].sort((a, b) => {
    const ta = new Date(a.timeStarted || a.timestamp).getTime();
    const tb = new Date(b.timeStarted || b.timestamp).getTime();
    return tb - ta;
  });
});

function redact(_s?: string) {
  return '[REDACTED]';
}

function timeAgo(iso: string = '') {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return 'NOW';
  if (mins < 60) return `${mins}M`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}H`;
  return `${Math.floor(hrs / 24)}D`;
}

function toggleExpand(id: string) {
  expandedId.value = expandedId.value === id ? null : id;
}

function markNew(id: string) {
  newIds.value = new Set([...newIds.value, id]);
  setTimeout(() => {
    const next = new Set(newIds.value);
    next.delete(id);
    newIds.value = next;
  }, 8000);
}
</script>

<style scoped>
.reports-root {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.title {
  font-size: 1.25rem;
  font-weight: 600;
}

.new-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: var(--shield-600);
  color: white;
  padding: 6px 12px;
  border-radius: var(--radius);
  font-size: 0.875rem;
  text-decoration: none;
}

.reports-list {
  flex: 1;
  overflow-y: auto;
}

.report-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
}

.report-card.is-new {
  background: rgba(59, 130, 246, 0.05);
}

.report-card:hover {
  background: var(--card-hover);
}

.card-body {
  flex: 1;
}

.card-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-title {
  font-weight: 500;
}

.report-time {
  font-size: 0.75rem;
  color: var(--muted-foreground);
}

.expanded-body {
  margin-top: 6px;
  font-size: 0.875rem;
  color: var(--foreground);
}

.card-chevron {
  transition: transform 0.2s;
}

.card-chevron.is-open {
  transform: rotate(90deg);
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: var(--muted-foreground);
}

.empty-icon {
  width: 40px;
  height: 40px;
  margin-bottom: 8px;
}

.mini-graph-tooltip {
  position: absolute;
  top: 100%;
  left: 0;
  right: auto;
  z-index: 100;
  margin-top: 4px;
  pointer-events: none;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>