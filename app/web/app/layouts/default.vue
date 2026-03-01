<template>
  <SidebarProvider :defaultOpen="sidebarOpen">
    <AppSidebar />
    <SidebarInset>
      <AppHeader :title="pageTitle" />
      <div class="p-6 bg-background min-h-[calc(100vh-3.5rem)]">
        <slot />
      </div>
    </SidebarInset>
    <JarvisButton />
  </SidebarProvider>
</template>

<script setup lang="ts">
import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar'

const route = useRoute()
const sidebarOpen = useCookie<boolean>('sidebar_state')

const pageTitle = computed(() => {
  const path = route.path
  if (path === '/dashboard') return 'Dashboard'
  if (path.startsWith('/analytics')) return 'Analytics'
  if (path.startsWith('/events')) return 'Events'
  if (path.startsWith('/reports')) return 'Reports'
  return 'Sentinel'
})
</script>
