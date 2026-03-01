<template>
  <Sidebar class="shield-sidebar">
    <!-- Scanline overlay -->
    <div class="scanlines" aria-hidden="true" />

    <SidebarHeader class="sidebar-header">
      <SidebarMenu>
        <SidebarMenuItem>
          <div class="flex items-center gap-2">
            <div class="shield-logo-wrap">
              <svg class="shield-logo" viewBox="0 0 48 48" fill="none">
                <polygon points="24,2 44,12 44,30 24,46 4,30 4,12" fill="#0d1117" stroke="#C9A234" stroke-width="1.5"/>
                <polygon points="24,7 39,15 39,29 24,41 9,29 9,15" fill="#0d1117" stroke="#C9A234" stroke-width="0.75" opacity="0.5"/>
                <circle cx="24" cy="24" r="7" fill="none" stroke="#C9A234" stroke-width="1.5"/>
                <line x1="24" y1="10" x2="24" y2="38" stroke="#C9A234" stroke-width="1" opacity="0.6"/>
                <line x1="10" y1="24" x2="38" y2="24" stroke="#C9A234" stroke-width="1" opacity="0.6"/>
              </svg>
            </div>
            <div class="header-text" v-if="!isCollapsed">
              <span class="org-label">S.H.I.E.L.D.</span>
              <span class="sys-label">COMMAND // SENTINEL</span>
            </div>
          </div>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>

    <!-- Status bar -->
    <div v-if="!isCollapsed" class="status-bar">
      <span class="status-dot" />
      <span class="status-text">UPLINK ACTIVE</span>
      <span class="status-ping">{{ currentTime }}</span>
    </div>

    <SidebarContent class="nav-list">
      <SidebarGroup class="nav-group">
        <SidebarGroupLabel v-if="!isCollapsed" class="divider-label">NAVIGATION</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in mainItems" :key="item.url">
              <SidebarMenuButton asChild>
                <NuxtLink :to="item.url" class="nav-item" :class="{ active: isActive(item.url) }">
                  <span class="nav-icon-wrap">
                    <Icon :name="item.icon" class="nav-icon" />
                    <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
                  </span>
                  <span v-if="!isCollapsed" class="nav-label">{{ item.title.toUpperCase() }}</span>
                  <span v-if="!isCollapsed && item.tag" class="nav-tag">{{ item.tag }}</span>
                  <span v-if="isActive(item.url)" class="active-bar" />
                </NuxtLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>

      <SidebarGroup class="nav-group">
        <SidebarGroupLabel v-if="!isCollapsed" class="divider-label">SYSTEM</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton asChild>
                <NuxtLink to="/events" class="nav-item" :class="{ active: isActive('/events') }">
                  <span class="nav-icon-wrap">
                    <Icon name="heroicons:bell-alert" class="nav-icon" />
                  </span>
                  <span v-if="!isCollapsed" class="nav-label">EVENTS</span>
                  <span v-if="isActive('/events')" class="active-bar" />
                </NuxtLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

    <SidebarFooter class="sidebar-footer">
      <!-- Agent Card -->
      <div v-if="!isCollapsed" class="agent-card">
        <div class="agent-avatar">
          <span>{{ agentInitials }}</span>
          <span class="avatar-ring" />
        </div>
<div class="agent-info">
          <span class="agent-name">{{ userName }}</span>
          <span class="agent-clearance">CLEARANCE: <em>LEVEL 8</em></span>
        </div>
        <div class="agent-status-dot" title="Secure session active" />
      </div>

      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton asChild>
            <button @click="handleSignOut" class="nav-item w-full">
              <span class="nav-icon-wrap">
                <Icon name="heroicons:arrow-right-on-rectangle" class="nav-icon" />
              </span>
              <span v-if="!isCollapsed" class="nav-label">LOGOUT</span>
            </button>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarFooter>
  </Sidebar>
</template>

<script setup lang="ts">
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from '@/components/ui/sidebar'
import { toast } from 'vue-sonner'

const { state } = useSidebar()
const router = useRouter()
const route = useRoute()

const isCollapsed = computed(() => state.value === 'collapsed')
const currentTime = ref('')

const session = authClient.useSession()

const name = computed(() => session.value?.data?.user.name || 'AGENT')

const userName = computed(() => {
  const initials = name.value.split(' ').map(n => n[0]).join('').toUpperCase()
  return `DIR. ${initials}`
})

const agentInitials = computed(() => {
  return name.value.split(' ').map(n => n[0]).join('').toUpperCase()
})

const mainItems = [
  { title: 'Dashboard', url: '/dashboard', icon: 'heroicons:home', tag: null, badge: null },
  { title: 'Analytics', url: '/analytics', icon: 'heroicons:chart-bar', tag: 'LIVE', badge: null },
  { title: 'Reports', url: '/reports/new', icon: 'heroicons:document-text', tag: null, badge: '12' },
]

function isActive(url: string) {
  return route.path === url || route.path.startsWith(url + '/')
}

let ticker: ReturnType<typeof setInterval>

function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('en-US', { hour12: false })
}

onMounted(() => {
  updateTime()
  ticker = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  clearInterval(ticker)
})

async function handleSignOut() {
  const { data, error } = await authClient.signOut()
  if (!error && data.success) {
    toast('Signed out successfully')
    router.push('/login')
  } else {
    toast('Failed to sign out')
  }
}
</script>

<style scoped>
.shield-sidebar {
  --gold: #0080e6;
  --gold-dim: #0064b3;
  --cyan: #00d4ff;
  --bg: #080a0e;
  --bg-surface: #0d1117;
  --bg-hover: #141923;
  --border: rgba(0, 128, 230, 0.15);
  --text-primary: #e8f0f8;
  --text-muted: #5a6a7a;
  
  background: var(--bg);
  border-right: 1px solid var(--border);
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

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

.sidebar-header,
.status-bar,
.nav-group,
.sidebar-footer {
  position: relative;
  z-index: 1;
}

.sidebar-header {
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
  filter: drop-shadow(0 0 6px rgba(0, 212, 255, 0.45));
  animation: pulse-glow 3s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { filter: drop-shadow(0 0 5px rgba(0, 212, 255, 0.4)); }
  50% { filter: drop-shadow(0 0 10px rgba(0, 212, 255, 0.75)); }
}

.header-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.org-label {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.14em;
  color: var(--cyan);
}

.sys-label {
  font-size: 9px;
  letter-spacing: 0.1em;
  color: var(--text-muted);
}

/* Status Bar */
.status-bar {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 7px 16px;
  background: rgba(0, 212, 255, 0.04);
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
  50% { opacity: 0.3; }
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

/* Divider */
.divider-label {
  font-size: 8.5px;
  letter-spacing: 0.15em;
  color: var(--text-muted);
  padding: 12px 14px 6px;
}

/* Nav Items */
.nav-list {
  padding: 4px 8px;
  flex: 1;
}

.nav-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
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
  background: linear-gradient(90deg, rgba(0, 212, 255, 0.07) 0%, transparent 100%);
  opacity: 0;
  transition: opacity 0.15s;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item:hover::before { opacity: 1; }

.nav-item.active {
  color: var(--cyan);
  background: rgba(0, 212, 255, 0.08);
}

.nav-item.active::before { opacity: 1; }

.nav-icon-wrap {
  position: relative;
  flex-shrink: 0;
  display: flex;
}

.nav-icon {
  transition: color 0.15s;
}

.nav-item.active .nav-icon {
  filter: drop-shadow(0 0 4px rgba(0, 212, 255, 0.6));
}

.nav-badge {
  position: absolute;
  top: -5px;
  right: -6px;
  background: #c0392b;
  color: #fff;
  font-size: 8px;
  font-weight: 700;
  border-radius: 8px;
  padding: 1px 4px;
  line-height: 1.3;
}

.nav-label {
  font-size: 10.5px;
  letter-spacing: 0.12em;
  font-weight: 600;
  white-space: nowrap;
  flex: 1;
}

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
  border-color: var(--cyan);
  color: var(--cyan);
  opacity: 0.8;
}

.active-bar {
  position: absolute;
  left: 0;
  top: 20%;
  bottom: 20%;
  width: 2px;
  background: var(--cyan);
  border-radius: 0 2px 2px 0;
  box-shadow: 0 0 8px var(--cyan);
}

/* Footer */
.sidebar-footer {
  padding: 8px;
}

.agent-card {
  margin: 8px 0;
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
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, transparent 60%);
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
  color: var(--cyan);
}

.avatar-ring {
  position: absolute;
  inset: -3px;
  border-radius: 50%;
  border: 1px dashed rgba(0, 212, 255, 0.3);
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
}

.agent-clearance {
  font-size: 8px;
  color: var(--text-muted);
  letter-spacing: 0.08em;
}

.agent-clearance em {
  font-style: normal;
  color: var(--cyan);
}

.agent-status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 5px #22c55e;
  flex-shrink: 0;
}
</style>
