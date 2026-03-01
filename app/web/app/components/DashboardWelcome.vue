<template>
  <div class="flex items-center gap-3">
    <div class="w-10 h-10 rounded-full bg-[#1e3a5f] flex items-center justify-center">
      <Icon name="heroicons:user" class="w-5 h-5 text-white" />
    </div>
    <div>
      <h2 class="text-lg font-semibold text-white">Welcome back, {{ userName }}</h2>
      <p class="text-sm text-slate-400">SHIELD Economic Analysis System</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const session = authClient.useSession()

const userName = computed(() => {
  const name = session.value?.data?.user.name
  if (name) {
    const firstName = name.split(' ')[0]
    return firstName
  }
  return 'Agent'
})
</script>
