<template>
  <div class="event-panel">
    <!-- Panel header -->
    <div class="panel-header">
      <div class="header-left">
        <span class="panel-label">PRIORITY EVENT REPORTS</span>
        <span class="live-dot" :class="{ streaming: isStreaming }" />
        <span class="live-text">{{ isStreaming ? 'LIVE' : 'STANDBY' }}</span>
      </div>
      <span class="event-count">{{ sortedEvents.length }} ACTIVE</span>
    </div>

    <!-- Filter bar -->
    <div class="filter-bar">
      <button
        v-for="f in FILTERS"
        :key="f.key"
        class="filter-btn"
        :class="{ active: activeFilter === f.key }"
        :style="activeFilter === f.key ? { borderColor: f.color, color: f.color } : {}"
        @click="activeFilter = f.key"
      >
        {{ f.label }}
      </button>
    </div>

    <!-- Event list: 3 rows visible, rest scrollable -->
    <div class="event-list-wrap">
      <div class="event-list" ref="listRef">
        <TransitionGroup name="event-slide">
          <div
            v-for="ev in filteredEvents"
            :key="ev.id"
            class="event-card"
            :class="[`priority-${ev.priority}`, { 'is-new': newEventIds.has(ev.id), 'is-open': expandedId === ev.id }]"
            :style="{ '--accent': priorityColor(ev.priority) }"
            @click="toggleExpand(ev.id)"
          >
            <!-- Left accent bar -->
            <div class="accent-bar" />

            <!-- Card body -->
            <div class="card-body">
              <!-- Always visible: badge + title + time -->
              <div class="card-row">
                <span
                  class="priority-badge"
                  :style="{ background: priorityBadgeBg(ev.priority), color: priorityColor(ev.priority) }"
                >{{ priorityLabel(ev.priority) }}</span>
                <span v-if="newEventIds.has(ev.id)" class="new-badge">● NEW</span>
                <p class="event-title">{{ ev.event }}</p>
                <span class="event-time">{{ timeAgo(ev.started) }}</span>
              </div>

              <!-- Expanded section -->
              <Transition name="expand">
                <div v-if="expandedId === ev.id" class="expanded-body">
                  <p v-if="ev.summary" class="event-summary">{{ ev.summary }}</p>
                  <div v-if="ev.locations.length || ev.resources.length" class="tag-row">
                    <span
                      v-for="loc in ev.locations.slice(0, 2)"
                      :key="'loc-' + loc"
                      class="tag tag-location"
                    >
                      <Icon name="heroicons:map-pin" class="tag-icon" />{{ loc }}
                    </span>
                    <span
                      v-for="res in ev.resources.slice(0, 2)"
                      :key="'res-' + res"
                      class="tag tag-resource"
                    >{{ res.replace(/_/g, ' ') }}</span>
                  </div>
                  <NuxtLink
                    :to="`/event/${ev.id}`"
                    class="view-link"
                    @click.stop
                  >
                    VIEW FULL REPORT
                    <Icon name="heroicons:arrow-right" class="view-icon" />
                  </NuxtLink>
                </div>
              </Transition>
            </div>

            <!-- Expand chevron -->
            <Icon
              name="heroicons:chevron-right"
              class="card-chevron"
              :class="{ 'is-open': expandedId === ev.id }"
            />
          </div>
        </TransitionGroup>

        <div v-if="filteredEvents.length === 0" class="empty-state">
          <Icon name="heroicons:shield-check" class="empty-icon" />
          <p class="empty-text">NO EVENTS IN THIS CATEGORY</p>
        </div>
      </div>

      <!-- Fade hint for more content below -->
      <div class="scroll-fade" aria-hidden="true" />
    </div>

    <!-- Footer -->
    <div class="panel-footer">
      <NuxtLink to="/events" class="view-all-link">
        VIEW ALL EVENTS
        <Icon name="heroicons:arrow-right" class="link-icon" />
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PriorityEvent } from '~~/server/api/events/index.get'

interface StreamEvent {
  id: string
  event: string
  priority: 1 | 2 | 3 | 4
  started: string
  timestamp: number
}

const PRIORITY_COLORS: Record<number, string> = {
  1: '#ef4444',
  2: '#f97316',
  3: '#eab308',
  4: '#00d4ff',
}

const PRIORITY_BADGE_BG: Record<number, string> = {
  1: 'rgba(239,68,68,0.15)',
  2: 'rgba(249,115,22,0.15)',
  3: 'rgba(234,179,8,0.15)',
  4: 'rgba(0,212,255,0.10)',
}

const PRIORITY_LABELS: Record<number, string> = {
  1: 'CRITICAL',
  2: 'HIGH',
  3: 'MEDIUM',
  4: 'LOW',
}

const FILTERS = [
  { key: 'all', label: 'ALL',      color: '#e8f0f8' },
  { key: '1',   label: 'CRITICAL', color: '#ef4444' },
  { key: '2',   label: 'HIGH',     color: '#f97316' },
  { key: '3',   label: 'MEDIUM',   color: '#eab308' },
  { key: '4',   label: 'LOW',      color: '#00d4ff' },
]

const NEW_BADGE_TTL = 8000

const listRef       = ref<HTMLElement | null>(null)
const activeFilter  = ref<string>('all')
const expandedId    = ref<string | null>(null)
const events        = ref<PriorityEvent[]>([])
const newEventIds   = ref<Set<string>>(new Set())
const isStreaming   = ref(false)

const { data: initialData } = await useFetch('/api/events')
if (initialData.value?.events) {
  events.value = initialData.value.events as PriorityEvent[]
}

const sortedEvents = computed(() =>
  [...events.value].sort((a, b) => {
    if (a.priority !== b.priority) return a.priority - b.priority
    return new Date(b.started).getTime() - new Date(a.started).getTime()
  })
)

const filteredEvents = computed(() => {
  if (activeFilter.value === 'all') return sortedEvents.value
  return sortedEvents.value.filter(e => String(e.priority) === activeFilter.value)
})

function priorityColor(p: number)    { return PRIORITY_COLORS[p] ?? '#e8f0f8' }
function priorityBadgeBg(p: number)  { return PRIORITY_BADGE_BG[p] ?? 'rgba(255,255,255,0.05)' }
function priorityLabel(p: number)    { return PRIORITY_LABELS[p] ?? 'UNKNOWN' }

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60_000)
  if (mins < 1)  return 'NOW'
  if (mins < 60) return `${mins}M`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24)  return `${hrs}H`
  return `${Math.floor(hrs / 24)}D`
}

function toggleExpand(id: string) {
  expandedId.value = expandedId.value === id ? null : id
}

function markNew(id: string) {
  newEventIds.value = new Set([...newEventIds.value, id])
  setTimeout(() => {
    const next = new Set(newEventIds.value)
    next.delete(id)
    newEventIds.value = next
  }, NEW_BADGE_TTL)
}

let sse: EventSource | null = null

onMounted(() => {
  sse = new EventSource('/api/streams/events')
  sse.onopen    = () => { isStreaming.value = true }
  sse.onerror   = () => { isStreaming.value = false }
  sse.onmessage = (e: MessageEvent) => {
    try {
      const incoming: StreamEvent = JSON.parse(e.data)
      if (!events.value.some(ev => ev.id === incoming.id)) {
        events.value.push({
          id: incoming.id, event: incoming.event,
          priority: incoming.priority as 1 | 2 | 3 | 4,
          started: incoming.started, summary: '', locations: [], resources: [], tags: [],
        })
        markNew(incoming.id)
      }
    } catch { /* ignore */ }
  }
})

onUnmounted(() => { sse?.close() })
</script>

<style scoped>
/* ── Panel shell ─────────────────────────────────────────────────────────── */
.event-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #080a0e;
  border: 1px solid rgba(0, 128, 230, 0.18);
  border-radius: 10px;
  overflow: hidden;
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 14px;
  background: rgba(0, 128, 230, 0.05);
  border-bottom: 1px solid rgba(0, 128, 230, 0.12);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 7px;
}

.panel-label {
  font-size: 8.5px;
  letter-spacing: 0.18em;
  font-weight: 700;
  color: #00d4ff;
}

.live-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #374151;
  flex-shrink: 0;
  transition: background 0.3s;
}

.live-dot.streaming {
  background: #22c55e;
  box-shadow: 0 0 5px #22c55e;
  animation: blink 2s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.25; }
}

.live-text {
  font-size: 7.5px;
  letter-spacing: 0.1em;
  color: #374151;
  transition: color 0.3s;
}

.live-dot.streaming + .live-text { color: #22c55e; }

.event-count {
  font-size: 7.5px;
  letter-spacing: 0.1em;
  color: #5a6a7a;
}

/* ── Filter bar ──────────────────────────────────────────────────────────── */
.filter-bar {
  display: flex;
  gap: 4px;
  padding: 6px 10px;
  border-bottom: 1px solid rgba(0, 128, 230, 0.08);
  background: rgba(0, 0, 0, 0.18);
  flex-shrink: 0;
}

.filter-btn {
  font-size: 7px;
  letter-spacing: 0.1em;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 2px;
  border: 1px solid rgba(255, 255, 255, 0.07);
  background: transparent;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.filter-btn:hover  { color: #e8f0f8; border-color: rgba(255,255,255,0.2); }
.filter-btn.active { background: rgba(255,255,255,0.04); }

/* ── List wrapper ────────────────────────────────────────────────────────── */
.event-list-wrap {
  position: relative;
  /* Compact: show exactly 3 collapsed rows (~48px each) + gaps + padding */
  max-height: 182px;
  overflow: hidden;
  flex-shrink: 0;
}

.scroll-fade {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40px;
  background: linear-gradient(to bottom, transparent, #080a0e 88%);
  pointer-events: none;
  z-index: 2;
}

/* ── Event list ──────────────────────────────────────────────────────────── */
.event-list {
  max-height: 182px;
  overflow-y: auto;
  padding: 6px 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  scrollbar-width: thin;
  scrollbar-color: rgba(0,128,230,0.18) transparent;
}

.event-list::-webkit-scrollbar       { width: 2px; }
.event-list::-webkit-scrollbar-track { background: transparent; }
.event-list::-webkit-scrollbar-thumb { background: rgba(0,128,230,0.22); border-radius: 2px; }

/* ── Event card ──────────────────────────────────────────────────────────── */
.event-card {
  display: flex;
  align-items: flex-start;
  background: #0c0f14;
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 5px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  overflow: hidden;
  flex-shrink: 0;
}

.event-card:hover {
  border-color: color-mix(in srgb, var(--accent) 35%, transparent);
  background: #0f131a;
}

.event-card.is-open {
  border-color: color-mix(in srgb, var(--accent) 50%, transparent);
  background: #0f131a;
}

.event-card.is-new { animation: flash-in 0.4s ease-out; }

@keyframes flash-in {
  0%   { background: rgba(255,255,255,0.07); }
  100% { background: #0c0f14; }
}

/* Accent bar */
.accent-bar {
  width: 3px;
  flex-shrink: 0;
  align-self: stretch;
  background: var(--accent);
  border-radius: 5px 0 0 5px;
}

.event-card.priority-1 .accent-bar { box-shadow: 0 0 6px var(--accent); }

/* Card body */
.card-body {
  flex: 1;
  padding: 7px 8px;
  display: flex;
  flex-direction: column;
  gap: 0;
  min-width: 0;
}

/* ── Collapsed row: badge + title + time ──────────────────────────────────── */
.card-row {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

.priority-badge {
  font-size: 6.5px;
  letter-spacing: 0.09em;
  font-weight: 700;
  padding: 2px 5px;
  border-radius: 2px;
  white-space: nowrap;
  flex-shrink: 0;
}

.new-badge {
  font-size: 6.5px;
  letter-spacing: 0.1em;
  font-weight: 700;
  color: #22c55e;
  flex-shrink: 0;
  animation: pulse-new 1s ease-in-out infinite alternate;
}

@keyframes pulse-new {
  from { opacity: 0.55; }
  to   { opacity: 1; }
}

.event-title {
  flex: 1;
  font-size: 10px;
  font-weight: 600;
  color: #dde8f4;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: 0.01em;
  min-width: 0;
}

.event-card.priority-1 .event-title { color: #fff; }

.event-time {
  font-size: 7px;
  color: #374151;
  flex-shrink: 0;
  letter-spacing: 0.06em;
}

/* ── Expanded section ────────────────────────────────────────────────────── */
.expanded-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-top: 7px;
  border-top: 1px solid rgba(255,255,255,0.05);
  margin-top: 7px;
}

.event-summary {
  font-size: 8px;
  color: #5a6a7a;
  line-height: 1.5;
  margin: 0;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 6.5px;
  letter-spacing: 0.08em;
  padding: 2px 5px;
  border-radius: 2px;
  white-space: nowrap;
}

.tag-location { background: rgba(0,128,230,0.12); color: #4a9de0; }
.tag-resource { background: rgba(201,162,52,0.10); color: #c9a234; text-transform: uppercase; }

.tag-icon { width: 7px; height: 7px; }

.view-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 7.5px;
  letter-spacing: 0.12em;
  font-weight: 700;
  color: var(--accent);
  text-decoration: none;
  opacity: 0.8;
  transition: opacity 0.15s;
  align-self: flex-start;
}

.view-link:hover  { opacity: 1; }
.view-icon        { width: 10px; height: 10px; }

/* ── Chevron ─────────────────────────────────────────────────────────────── */
.card-chevron {
  width: 12px;
  height: 12px;
  color: #2d3748;
  flex-shrink: 0;
  align-self: center;
  margin-right: 7px;
  margin-top: 7px;
  transition: color 0.15s, transform 0.2s;
}

.event-card:hover .card-chevron  { color: var(--accent); }
.card-chevron.is-open            { transform: rotate(90deg); color: var(--accent); }

/* ── Empty state ─────────────────────────────────────────────────────────── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px 16px;
  color: #2d3748;
}

.empty-icon  { width: 26px; height: 26px; }
.empty-text  { font-size: 8.5px; letter-spacing: 0.14em; margin: 0; }

/* ── Footer ──────────────────────────────────────────────────────────────── */
.panel-footer {
  padding: 8px 14px;
  border-top: 1px solid rgba(0,128,230,0.1);
  background: rgba(0,0,0,0.15);
  flex-shrink: 0;
}

.view-all-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  font-size: 8px;
  letter-spacing: 0.14em;
  font-weight: 700;
  color: #4b5563;
  text-decoration: none;
  transition: color 0.15s;
}

.view-all-link:hover            { color: #00d4ff; }
.link-icon                      { width: 11px; height: 11px; transition: transform 0.15s; }
.view-all-link:hover .link-icon { transform: translateX(3px); }

/* ── Transitions ─────────────────────────────────────────────────────────── */
.event-slide-enter-active { transition: all 0.25s ease-out; }
.event-slide-enter-from   { opacity: 0; transform: translateY(-6px); }

.expand-enter-active, .expand-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
  overflow: hidden;
}
.expand-enter-from, .expand-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
