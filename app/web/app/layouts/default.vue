<template>
  <SidebarProvider :defaultOpen="sidebarOpen">
    <AppSidebar />
    <SidebarInset>
      <AppHeader :title="pageTitle" @toggle-jarvis="toggleJarvis" />
      <div class="p-6 bg-[#0a1929] min-h-[calc(100vh-3.5rem)]">
        <slot />
      </div>
    </SidebarInset>
    <JarvisButton ref="jarvisRef" />
  </SidebarProvider>
</template>

<script setup lang="ts">
import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar'

const route = useRoute()
const sidebarOpen = useCookie<boolean>('sidebar_state')

const jarvisRef = ref<{ isOpen: boolean } | null>(null)

const pageTitle = computed(() => {
  const path = route.path
  if (path === '/dashboard') return 'Dashboard'
  if (path.startsWith('/analytics')) return 'Analytics'
  if (path.startsWith('/events')) return 'Events'
  if (path.startsWith('/reports')) return 'Reports'
  return 'Sentinel'
})

function toggleJarvis() {
  if (jarvisRef.value) {
    jarvisRef.value.isOpen = !jarvisRef.value.isOpen
  }
}
</script>
