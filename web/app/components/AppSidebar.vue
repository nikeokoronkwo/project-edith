<template>
  <Sidebar class="shield-sidebar">
    <SidebarHeader class="sidebar-header">
      <SidebarMenu>
        <SidebarMenuItem>
          <div class="flex items-center gap-2.5">
            <div class="shield-logo-wrap">
              <svg class="shield-logo" viewBox="0 0 48 48" fill="none">
                <polygon points="24,2 44,12 44,30 24,46 4,30 4,12" fill="transparent" stroke="currentColor" stroke-width="1.5"/>
                <polygon points="24,7 39,15 39,29 24,41 9,29 9,15" fill="transparent" stroke="currentColor" stroke-width="0.75" opacity="0.4"/>
                <circle cx="24" cy="24" r="7" fill="none" stroke="currentColor" stroke-width="1.5"/>
                <line x1="24" y1="10" x2="24" y2="38" stroke="currentColor" stroke-width="1" opacity="0.5"/>
                <line x1="10" y1="24" x2="38" y2="24" stroke="currentColor" stroke-width="1" opacity="0.5"/>
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
      <span class="status-dot status-dot-blink" />
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
      <div v-if="!isCollapsed" class="agent-card">
        <div class="agent-avatar">
          <span>{{ agentInitials }}</span>
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

const reportCount = ref<string | null>(null)

onMounted(async () => {
  try {
    const data = await $fetch<{ total: number }>('/api/reports')
    if (data.total > 0) reportCount.value = String(data.total)
  } catch { /* badge is non-critical */ }
})

const mainItems = computed(() => [
  { title: 'Dashboard', url: '/dashboard', icon: 'heroicons:home', tag: null, badge: null },
  { title: 'Analytics', url: '/analytics', icon: 'heroicons:chart-bar', tag: 'LIVE', badge: null },
  { title: 'Reports', url: '/reports', icon: 'heroicons:document-text', tag: null, badge: reportCount.value },
])

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
  background: var(--sidebar);
  border-right: 1px solid var(--sidebar-border);
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

.sidebar-header {
  padding: 18px 14px 14px;
  border-bottom: 1px solid var(--sidebar-border);
}

.shield-logo-wrap {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.shield-logo {
  width: 28px;
  height: 28px;
  color: var(--sidebar-primary);
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
  color: var(--sidebar-primary);
}

.sys-label {
  font-size: 9px;
  letter-spacing: 0.1em;
  color: var(--muted-foreground);
}

/* Status Bar */
.status-bar {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 6px 16px;
  background: color-mix(in srgb, var(--sidebar-primary) 5%, transparent);
  border-bottom: 1px solid var(--sidebar-border);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-status-online);
  box-shadow: 0 0 5px var(--color-status-online);
  animation: blink 2s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.25; }
}

.status-text {
  font-size: 9px;
  letter-spacing: 0.12em;
  color: var(--color-status-online);
  flex: 1;
}

.status-ping {
  font-size: 9px;
  color: var(--muted-foreground);
  font-variant-numeric: tabular-nums;
}

/* Section dividers */
.divider-label {
  font-size: 8.5px;
  letter-spacing: 0.15em;
  color: var(--muted-foreground);
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
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--muted-foreground);
  cursor: pointer;
  text-align: left;
  width: 100%;
  transition: background 0.15s, color 0.15s;
  overflow: hidden;
}

.nav-item:hover {
  background: var(--sidebar-accent);
  color: var(--sidebar-foreground);
}

.nav-item.active {
  color: var(--sidebar-primary);
  background: color-mix(in srgb, var(--sidebar-primary) 10%, transparent);
}

.nav-icon-wrap {
  position: relative;
  flex-shrink: 0;
  display: flex;
}

.nav-icon {
  width: 16px;
  height: 16px;
  transition: color 0.15s;
}

.nav-badge {
  position: absolute;
  top: -5px;
  right: -6px;
  background: var(--destructive);
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
  border-color: var(--sidebar-primary);
  color: var(--sidebar-primary);
  opacity: 0.8;
}

.active-bar {
  position: absolute;
  left: 0;
  top: 20%;
  bottom: 20%;
  width: 2px;
  background: var(--sidebar-primary);
  border-radius: 0 2px 2px 0;
}

/* Footer */
.sidebar-footer {
  padding: 8px;
  border-top: 1px solid var(--sidebar-border);
}

.agent-card {
  margin: 8px 0;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: var(--sidebar-accent);
  border: 1px solid var(--sidebar-border);
  border-radius: var(--radius-sm);
}

.agent-avatar {
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--sidebar-primary) 15%, transparent);
  border: 1px solid var(--sidebar-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 700;
  color: var(--sidebar-primary);
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
  color: var(--sidebar-foreground);
}

.agent-clearance {
  font-size: 8px;
  color: var(--muted-foreground);
  letter-spacing: 0.08em;
}

.agent-clearance em {
  font-style: normal;
  color: var(--sidebar-primary);
}

.agent-status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-status-online);
  box-shadow: 0 0 5px var(--color-status-online);
  flex-shrink: 0;
}
</style>
