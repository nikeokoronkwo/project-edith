<template>
  <div>
    <NuxtRouteAnnouncer />
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
    <Toaster position="top-right" class="pointer-events-auto" />
  </div>
</template>

<script setup lang="ts">
import { Toaster } from '@/components/ui/sonner'
import 'vue-sonner/style.css'

useHead({
  htmlAttrs: {
    class: 'dark'
  },
  title: 'Sentinel - SHIELD Economic Dashboard',
  meta: [
    { name: 'description', content: 'SHIELD Economic Analysis and Forecasting Dashboard' }
  ]
})
</script>
