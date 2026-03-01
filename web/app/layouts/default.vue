<template>
  <SidebarProvider :defaultOpen="sidebarOpen">
    <AppSidebar />
    <SidebarInset>
      <AppHeader :title="pageTitle" />
      <div class="p-6 bg-background min-h-[calc(100vh-3.5rem)]">
        <slot />
      </div>
    </SidebarInset>
    <EdithButton />
    <Sonner position="top-right" />
  </SidebarProvider>
</template>

<script setup lang="ts">
import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar'
import EdithButton from '@/components/EdithButton.vue'
import Sonner from '@/components/ui/sonner/Sonner.vue'

const route = useRoute()
const sidebarOpen = useCookie<boolean>('sidebar_state')

// Fire global toasts for high-priority events from the SSE events stream
useEventAlerts()

const pageTitle = computed(() => {
  const path = route.path
  if (path === '/dashboard') return 'Dashboard'
  if (path.startsWith('/analytics')) return 'Analytics'
  if (path.startsWith('/events')) return 'Events'
  if (path.startsWith('/reports')) return 'Reports'
  return 'Edith'
})
</script>
