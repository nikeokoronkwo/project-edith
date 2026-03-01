<template>
  <div class="fixed bottom-6 right-6 z-50">
    <Transition name="fade">
      <EdithChat v-if="state.isOpen" @close="close" />
    </Transition>

    <button
      @click="toggle"
      class="edith-btn"
      :class="{ 'is-open': state.isOpen }"
    >
      <Icon
        :name="state.isOpen ? 'heroicons:x-mark' : 'heroicons:microphone'"
        class="w-6 h-6 text-white group-hover:scale-110 transition-transform"
      />
    </button>
  </div>
</template>

<script setup lang="ts">
import { useEdithChat } from '@/composables/useEdith'

const { state, toggle, close } = useEdithChat()
</script>

<style scoped>
.edith-btn {
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 50%;
  background: var(--primary);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px color-mix(in srgb, var(--primary) 40%, transparent);
  transition: background 0.2s, box-shadow 0.2s, transform 0.2s;
}

.edith-btn:hover {
  background: color-mix(in srgb, var(--primary) 85%, #000);
  box-shadow: 0 6px 20px color-mix(in srgb, var(--primary) 50%, transparent);
}

.edith-btn.is-open {
  transform: rotate(90deg);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(12px) scale(0.96);
}
</style>