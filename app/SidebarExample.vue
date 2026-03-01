<template>
  <aside :class="['shield-sidebar', { collapsed }]" role="navigation" aria-label="SHIELD Command Navigation">
    <!-- Scanline overlay -->
    <div class="scanlines" aria-hidden="true" />

    <!-- Header -->
    <div class="sidebar-header">
      <div class="shield-logo-wrap">
        <svg class="shield-logo" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="SHIELD logo">
          <polygon points="24,2 44,12 44,30 24,46 4,30 4,12" fill="#0d1117" stroke="#C9A234" stroke-width="1.5"/>
          <polygon points="24,7 39,15 39,29 24,41 9,29 9,15" fill="#0d1117" stroke="#C9A234" stroke-width="0.75" opacity="0.5"/>
          <circle cx="24" cy="24" r="7" fill="none" stroke="#C9A234" stroke-width="1.5"/>
          <line x1="24" y1="10" x2="24" y2="38" stroke="#C9A234" stroke-width="1" opacity="0.6"/>
          <line x1="10" y1="24" x2="38" y2="24" stroke="#C9A234" stroke-width="1" opacity="0.6"/>
        </svg>
      </div>

      <Transition name="fade-label">
        <div v-if="!collapsed" class="header-text">
          <span class="org-label">S.H.I.E.L.D.</span>
          <span class="sys-label">COMMAND // CORTEX</span>
        </div>
      </Transition>

      <button class="collapse-btn" @click="collapsed = !collapsed" :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'">
        <ChevronLeft v-if="!collapsed" :size="14" />
        <ChevronRight v-else :size="14" />
      </button>
    </div>

    <!-- Status bar -->
    <Transition name="fade-label">
      <div v-if="!collapsed" class="status-bar">
        <span class="status-dot" />
        <span class="status-text">UPLINK ACTIVE</span>
        <span class="status-ping">{{ currentTime }}</span>
      </div>
    </Transition>

    <!-- Divider -->
    <div class="section-divider">
      <span class="divider-label" v-if="!collapsed">NAVIGATION</span>
      <div class="divider-line" />
    </div>

    <!-- Nav Items -->
    <nav class="nav-list">
      <NavItem
        v-for="item in navItems"
        :key="item.id"
        :item="item"
        :active="activeItem === item.id"
        :collapsed="collapsed"
        @click="activeItem = item.id"
      />
    </nav>

    <!-- Bottom section -->
    <div class="sidebar-footer">
      <div class="section-divider">
        <span class="divider-label" v-if="!collapsed">SYSTEM</span>
        <div class="divider-line" />
      </div>

      <NavItem
        :item="settingsItem"
        :active="activeItem === settingsItem.id"
        :collapsed="collapsed"
        @click="activeItem = settingsItem.id"
      />

      <Transition name="fade-label">
        <div v-if="!collapsed" class="agent-card">
          <div class="agent-avatar">
            <span>NF</span>
            <span class="avatar-ring" />
          </div>
          <div class="agent-info">
            <span class="agent-name">DIR. N. FURY</span>
            <span class="agent-clearance">CLEARANCE: <em>LEVEL 10</em></span>
          </div>
          <div class="agent-status-dot" title="Secure session active" />
        </div>
      </Transition>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import {
  ChevronLeft,
  ChevronRight,
  BarChart3,
  ScrollText,
  TrendingUp,
  Settings2,
} from 'lucide-vue-next'

// ── Nav Item sub-component (inline) ──────────────────────────────────────────
const NavItem = {
  props: ['item', 'active', 'collapsed'],
  emits: ['click'],
  template: `
    <button
      :class="['nav-item', { active, collapsed }]"
      @click="$emit('click')"
      :title="collapsed ? item.label : undefined"
      :aria-current="active ? 'page' : undefined"
    >
      <span class="nav-icon-wrap">
        <component :is="item.icon" :size="18" class="nav-icon" />
        <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
      </span>
      <Transition name="fade-label">
        <span v-if="!collapsed" class="nav-label">{{ item.label }}</span>
      </Transition>
      <Transition name="fade-label">
        <span v-if="!collapsed && item.tag" class="nav-tag">{{ item.tag }}</span>
      </Transition>
      <span v-if="active" class="active-bar" aria-hidden="true" />
    </button>
  `,
}

// ── State ─────────────────────────────────────────────────────────────────────
const collapsed = ref(false)
const activeItem = ref('analytics')
const currentTime = ref('')

const navItems = [
  { id: 'analytics', label: 'ANALYTICS', icon: BarChart3, tag: 'LIVE',   badge: null },
  { id: 'reports',   label: 'REPORTS',   icon: ScrollText, tag: null,    badge: '12' },
  { id: 'forecasts', label: 'FORECASTS', icon: TrendingUp, tag: 'BETA',  badge: null },
]

const settingsItem = { id: 'settings', label: 'SETTINGS', icon: Settings2, tag: null, badge: null }

// ── Clock ─────────────────────────────────────────────────────────────────────
let ticker: ReturnType<typeof setInterval>

function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('en-US', { hour12: false })
}

onMounted(() => { updateTime(); ticker = setInterval(updateTime, 1000) })
onUnmounted(() => clearInterval(ticker))
</script>

<style scoped>
/* ── Tokens ──────────────────────────────────────────────────────────────────── */
.shield-sidebar {
  --gold:       #C9A234;
  --gold-dim:   #7a6120;
  --red:        #c0392b;
  --bg:         #080a0e;
  --bg-surface: #0d1117;
  --bg-hover:   #141923;
  --border:     rgba(201,162,52,0.18);
  --text-primary: #e8e0cc;
  --text-muted:   #5a6275;
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;

  position: relative;
  display: flex;
  flex-direction: column;
  width: 240px;
  min-height: 100vh;
  background: var(--bg);
  border-right: 1px solid var(--border);
  font-family: var(--font-mono);
  overflow: hidden;
  transition: width 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}

.shield-sidebar.collapsed {
  width: 64px;
}

/* ── Scanlines ───────────────────────────────────────────────────────────────── */
.scanlines {
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    to bottom,
    transparent 0px,
    transparent 3px,
    rgba(0, 0, 0, 0.08) 3px,
    rgba(0, 0, 0, 0.08) 4px
  );
  pointer-events: none;
  z-index: 0;
}

/* All content above scanlines */
.sidebar-header,
.status-bar,
.section-divider,
.nav-list,
.sidebar-footer {
  position: relative;
  z-index: 1;
}

/* ── Header ──────────────────────────────────────────────────────────────────── */
.sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 14px 16px;
  border-bottom: 1px solid var(--border);
}

.shield-logo-wrap {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.shield-logo {
  width: 32px;
  height: 32px;
  filter: drop-shadow(0 0 6px rgba(201,162,52,0.45));
  animation: pulse-glow 3s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { filter: drop-shadow(0 0 5px rgba(201,162,52,0.4)); }
  50%       { filter: drop-shadow(0 0 10px rgba(201,162,52,0.75)); }
}

.header-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.org-label {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.14em;
  color: var(--gold);
  white-space: nowrap;
}

.sys-label {
  font-size: 9px;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  white-space: nowrap;
}

.collapse-btn {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border: 1px solid var(--border);
  border-radius: 3px;
  background: var(--bg-surface);
  color: var(--gold-dim);
  cursor: pointer;
  transition: all 0.15s;
}

.collapse-btn:hover {
  border-color: var(--gold);
  color: var(--gold);
  background: var(--bg-hover);
}

/* ── Status Bar ──────────────────────────────────────────────────────────────── */
.status-bar {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 7px 16px;
  background: rgba(201,162,52,0.04);
  border-bottom: 1px solid var(--border);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 6px #22c55e;
  animation: blink 2s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.3; }
}

.status-text {
  font-size: 9px;
  letter-spacing: 0.12em;
  color: #22c55e;
  flex: 1;
}

.status-ping {
  font-size: 9px;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}

/* ── Divider ─────────────────────────────────────────────────────────────────── */
.section-divider {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px 6px;
}

.divider-label {
  font-size: 8.5px;
  letter-spacing: 0.15em;
  color: var(--text-muted);
  white-space: nowrap;
  flex-shrink: 0;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: var(--border);
}

/* ── Nav Items ───────────────────────────────────────────────────────────────── */
.nav-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 4px 8px;
  flex: 1;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  text-align: left;
  width: 100%;
  transition: all 0.15s;
  overflow: hidden;
}

.nav-item::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(201,162,52,0.07) 0%, transparent 100%);
  opacity: 0;
  transition: opacity 0.15s;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item:hover::before { opacity: 1; }

.nav-item.active {
  color: var(--gold);
  background: rgba(201,162,52,0.08);
}

.nav-item.active::before { opacity: 1; }

.nav-item.collapsed {
  justify-content: center;
  padding: 10px;
}

/* Icon wrap */
.nav-icon-wrap {
  position: relative;
  flex-shrink: 0;
  display: flex;
}

.nav-icon {
  transition: color 0.15s;
}

.nav-item.active .nav-icon {
  filter: drop-shadow(0 0 4px rgba(201,162,52,0.6));
}

/* Badge */
.nav-badge {
  position: absolute;
  top: -5px;
  right: -6px;
  background: var(--red);
  color: #fff;
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0;
  border-radius: 8px;
  padding: 1px 4px;
  line-height: 1.3;
}

/* Label */
.nav-label {
  font-size: 10.5px;
  letter-spacing: 0.12em;
  font-weight: 600;
  white-space: nowrap;
  flex: 1;
}

/* Tag */
.nav-tag {
  font-size: 8px;
  letter-spacing: 0.1em;
  padding: 1px 5px;
  border-radius: 2px;
  border: 1px solid currentColor;
  opacity: 0.6;
  white-space: nowrap;
}

.nav-item.active .nav-tag {
  border-color: var(--gold);
  color: var(--gold);
  opacity: 0.8;
}

/* Active bar */
.active-bar {
  position: absolute;
  left: 0;
  top: 20%;
  bottom: 20%;
  width: 2px;
  background: var(--gold);
  border-radius: 0 2px 2px 0;
  box-shadow: 0 0 8px var(--gold);
}

/* ── Footer ──────────────────────────────────────────────────────────────────── */
.sidebar-footer {
  padding-bottom: 16px;
}

.agent-card {
  margin: 8px 8px 0;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}

.agent-card::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(201,162,52,0.05) 0%, transparent 60%);
  pointer-events: none;
}

.agent-avatar {
  position: relative;
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  border: 1px solid var(--gold-dim);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 700;
  color: var(--gold);
  letter-spacing: 0.05em;
}

.avatar-ring {
  position: absolute;
  inset: -3px;
  border-radius: 50%;
  border: 1px dashed rgba(201,162,52,0.3);
  animation: spin 12s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.agent-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.agent-name {
  font-size: 9.5px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.agent-clearance {
  font-size: 8px;
  color: var(--text-muted);
  letter-spacing: 0.08em;
}

.agent-clearance em {
  font-style: normal;
  color: var(--gold);
}

.agent-status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 5px #22c55e;
  flex-shrink: 0;
}

/* ── Transitions ─────────────────────────────────────────────────────────────── */
.fade-label-enter-active,
.fade-label-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.fade-label-enter-from,
.fade-label-leave-to {
  opacity: 0;
  transform: translateX(-6px);
}
</style>