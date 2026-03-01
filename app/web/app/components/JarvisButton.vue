<template>
  <div class="fixed bottom-6 right-6 z-50">
    <Transition name="fade">
      <JarvisChat v-if="isOpen" @close="isOpen = false" />
    </Transition>
    
    <button
      @click="isOpen = !isOpen"
      class="w-14 h-14 rounded-full bg-gradient-to-br from-[#0080e6] to-[#1e3a5f] shadow-lg hover:shadow-xl transition-all flex items-center justify-center group"
      :class="{ 'rotate-90': isOpen }"
    >
      <Icon 
        :name="isOpen ? 'heroicons:x-mark' : 'heroicons:microphone'" 
        class="w-6 h-6 text-white group-hover:scale-110 transition-transform" 
      />
    </button>
  </div>
</template>

<script setup lang="ts">
const isOpen = ref(false)

defineExpose({ isOpen })
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}
</style>
