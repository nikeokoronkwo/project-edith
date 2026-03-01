<template>
  <div class="event-panel">
    <!-- Panel header -->
    <div class="panel-header">
      <div class="header-left">
        <span class="panel-label">PRIORITY EVENT REPORTS</span>
        <span class="live-dot" :class="{ streaming: isStreaming }" />
        <span class="live-text" :class="{ streaming: isStreaming }">{{ isStreaming ? 'LIVE' : 'STANDBY' }}</span>
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

    <!-- Event list -->
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
            <div class="accent-bar" />

            <div class="card-body">
              <div class="card-row">
                <span
                  class="priority-badge"
                  :style="{ background: priorityBadgeBg(ev.priority), color: priorityColor(ev.priority) }"
                >{{ priorityLabel(ev.priority) }}</span>
                <span v-if="newEventIds.has(ev.id)" class="new-badge">● NEW</span>
                <p class="event-title">{{ ev.event }}</p>
                <span class="event-time">{{ timeAgo(ev.started) }}</span>
              </div>

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
  4: '#3b82f6',
}

const PRIORITY_BADGE_BG: Record<number, string> = {
  1: 'rgba(239,68,68,0.12)',
  2: 'rgba(249,115,22,0.12)',
  3: 'rgba(234,179,8,0.12)',
  4: 'rgba(59,130,246,0.12)',
}

const PRIORITY_LABELS: Record<number, string> = {
  1: 'CRITICAL',
  2: 'HIGH',
  3: 'MEDIUM',
  4: 'LOW',
}

const FILTERS = [
  { key: 'all', label: 'ALL',      color: 'var(--foreground)' },
  { key: '1',   label: 'CRITICAL', color: '#ef4444' },
  { key: '2',   label: 'HIGH',     color: '#f97316' },
  { key: '3',   label: 'MEDIUM',   color: '#eab308' },
  { key: '4',   label: 'LOW',      color: '#3b82f6' },
]

const NEW_BADGE_TTL = 8000

const listRef      = ref<HTMLElement | null>(null)
const activeFilter = ref<string>('all')
const expandedId   = ref<string | null>(null)
const events       = ref<PriorityEvent[]>([])
const newEventIds  = ref<Set<string>>(new Set())
const isStreaming  = ref(false)

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

function priorityColor(p: number)   { return PRIORITY_COLORS[p] ?? 'var(--foreground)' }
function priorityBadgeBg(p: number) { return PRIORITY_BADGE_BG[p] ?? 'rgba(255,255,255,0.05)' }
function priorityLabel(p: number)   { return PRIORITY_LABELS[p] ?? 'UNKNOWN' }

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
/* ── Panel shell ──────────────────────────────────────────────────────────── */
.event-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
}

/* ── Header ───────────────────────────────────────────────────────────────── */
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 14px;
  background: color-mix(in srgb, var(--primary) 5%, transparent);
  border-bottom: 1px solid var(--border);
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
  color: var(--primary);
}

.live-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--muted-foreground);
  flex-shrink: 0;
  transition: background 0.3s;
}

.live-dot.streaming {
  background: var(--color-status-online);
  box-shadow: 0 0 5px var(--color-status-online);
  animation: blink 2s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.25; }
}

.live-text {
  font-size: 7.5px;
  letter-spacing: 0.1em;
  color: var(--muted-foreground);
  transition: color 0.3s;
}

.live-text.streaming { color: var(--color-status-online); }

.event-count {
  font-size: 7.5px;
  letter-spacing: 0.1em;
  color: var(--muted-foreground);
}

/* ── Filter bar ───────────────────────────────────────────────────────────── */
.filter-bar {
  display: flex;
  gap: 4px;
  padding: 6px 10px;
  border-bottom: 1px solid var(--border);
  background: color-mix(in srgb, var(--muted) 50%, transparent);
  flex-shrink: 0;
}

.filter-btn {
  font-size: 7px;
  letter-spacing: 0.1em;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 2px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--muted-foreground);
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s, background 0.15s;
  white-space: nowrap;
}

.filter-btn:hover {
  color: var(--foreground);
  border-color: color-mix(in srgb, var(--foreground) 30%, transparent);
}

.filter-btn.active {
  background: color-mix(in srgb, var(--foreground) 5%, transparent);
}

/* ── List wrapper ─────────────────────────────────────────────────────────── */
.event-list-wrap {
  position: relative;
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.scroll-fade {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 32px;
  background: linear-gradient(to bottom, transparent, var(--card) 85%);
  pointer-events: none;
  z-index: 2;
}

/* ── Event list ───────────────────────────────────────────────────────────── */
.event-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  scrollbar-width: thin;
  scrollbar-color: var(--primary, #c9a234) transparent;
}

.event-list::-webkit-scrollbar       { width: 3px; }
.event-list::-webkit-scrollbar-track { background: transparent; }
.event-list::-webkit-scrollbar-thumb { background: color-mix(in srgb, var(--primary, #c9a234) 40%, transparent); border-radius: 2px; }
.event-list::-webkit-scrollbar-thumb:hover { background: color-mix(in srgb, var(--primary, #c9a234) 60%, transparent); }

/* ── Event card ───────────────────────────────────────────────────────────── */
.event-card {
  display: flex;
  align-items: flex-start;
  background: color-mix(in srgb, var(--card-foreground, white) 2%, transparent);
  border: 1px solid var(--border);
  border-left: 4px solid var(--accent);
  border-radius: calc(var(--radius) - 1px);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  flex-shrink: 0;
}

.event-card:hover {
  border-color: var(--accent);
  background: color-mix(in srgb, var(--accent) 15%, transparent);
  box-shadow: 0 2px 8px color-mix(in srgb, var(--accent) 20%, transparent);
  transform: translateX(2px);
}

.event-card.is-open {
  border-color: var(--accent);
  background: color-mix(in srgb, var(--accent) 18%, transparent);
  box-shadow: 0 2px 10px color-mix(in srgb, var(--accent) 25%, transparent);
}

.event-card.is-new { animation: flash-in 0.5s ease-out; }

@keyframes flash-in {
  0%   { background: color-mix(in srgb, var(--accent) 35%, transparent); }
  100% { background: color-mix(in srgb, var(--card-foreground, white) 2%, transparent); }
}

/* Accent bar */
.accent-bar {
  display: none;
}

/* Card body */
.card-body {
  flex: 1;
  padding: 9px 10px;
  display: flex;
  flex-direction: column;
  gap: 0;
  min-width: 0;
}

/* ── Card row ─────────────────────────────────────────────────────────── */
.card-row {
  display: grid;
  grid-template-columns: auto auto 1fr auto;
  align-items: center;
  gap: 8px;
  min-width: 0;
  row-gap: 4px;
}

.priority-badge {
  font-size: 6.5px;
  letter-spacing: 0.1em;
  font-weight: 700;
  padding: 3px 6px;
  border-radius: 3px;
  white-space: nowrap;
  flex-shrink: 0;
  border: 1px solid color-mix(in srgb, var(--accent) 50%, transparent);
}

.new-badge {
  font-size: 6.5px;
  letter-spacing: 0.1em;
  font-weight: 700;
  color: var(--color-status-online);
  flex-shrink: 0;
  animation: pulse-new 1s ease-in-out infinite alternate;
  grid-column: 2;
}

@keyframes pulse-new {
  from { opacity: 0.55; }
  to   { opacity: 1; }
}

.event-title {
  font-size: 9.5px;
  font-weight: 600;
  color: var(--card-foreground);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: 0.02em;
  min-width: 0;
  grid-column: 1 / -1;
  padding-right: 4px;
}

.event-time {
  font-size: 7px;
  color: var(--muted-foreground);
  flex-shrink: 0;
  letter-spacing: 0.06em;
  justify-self: end;
  grid-column: 4;
  grid-row: 1;
}

/* ── Expanded section ─────────────────────────────────────────────────────── */
.expanded-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-top: 7px;
  border-top: 1px solid var(--border);
  margin-top: 7px;
}

.event-summary {
  font-size: 8px;
  color: var(--muted-foreground);
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

.tag-location {
  background: color-mix(in srgb, var(--primary) 12%, transparent);
  color: var(--primary);
}

.tag-resource {
  background: color-mix(in srgb, var(--muted-foreground) 15%, transparent);
  color: var(--muted-foreground);
  text-transform: uppercase;
}

.tag-icon { width: 7px; height: 7px; }

.view-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 7.5px;
  letter-spacing: 0.12em;
  font-weight: 700;
  color: var(--primary);
  text-decoration: none;
  opacity: 0.85;
  transition: opacity 0.15s;
  align-self: flex-start;
}

.view-link:hover { opacity: 1; }
.view-icon       { width: 10px; height: 10px; }

/* ── Chevron ──────────────────────────────────────────────────────────────── */
.card-chevron {
  width: 14px;
  height: 14px;
  color: var(--accent);
  flex-shrink: 0;
  align-self: flex-start;
  margin-left: auto;
  margin-top: 8px;
  transition: color 0.2s, transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0.7;
}

.event-card:hover .card-chevron { opacity: 1; color: var(--accent); }
.card-chevron.is-open           { transform: rotate(90deg); opacity: 1; color: var(--accent); }

/* ── Empty state ──────────────────────────────────────────────────────────── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 24px 16px;
  color: var(--muted-foreground);
  opacity: 0.5;
}

.empty-icon { width: 26px; height: 26px; }
.empty-text { font-size: 8.5px; letter-spacing: 0.14em; margin: 0; }

/* ── Footer ───────────────────────────────────────────────────────────────── */
.panel-footer {
  padding: 8px 14px;
  border-top: 1px solid var(--border);
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
  color: var(--muted-foreground);
  text-decoration: none;
  transition: color 0.15s;
}

.view-all-link:hover            { color: var(--primary); }
.link-icon                      { width: 11px; height: 11px; transition: transform 0.15s; }
.view-all-link:hover .link-icon { transform: translateX(3px); }

/* ── Transitions ──────────────────────────────────────────────────────────── */
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
