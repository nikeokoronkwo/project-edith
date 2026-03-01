<template>
  <header class="h-14 border-b border-border bg-card flex items-center gap-2 px-4">
    <SidebarTrigger class="text-muted-foreground hover:text-foreground" />
    <h1 class="text-foreground font-semibold tracking-wide text-sm">{{ title }}</h1>
  </header>
</template>

<script setup lang="ts">
import { SidebarTrigger } from '@/components/ui/sidebar'

defineProps<{
  title?: string
}>()
</script>
