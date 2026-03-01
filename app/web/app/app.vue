<template>
  <div>
    <NuxtRouteAnnouncer />
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>

<script setup lang="ts">
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
