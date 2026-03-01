<script setup lang="ts">
import { authClient } from '@/utils/auth'

definePageMeta({
  layout: false
})

const { data: sessionData } = await authClient.useSession(useFetch)

onMounted(() => {
  if (sessionData.value) {
    navigateTo('/dashboard')
  } else {
    navigateTo('/login')
  }
})
</script>

<template></template>