<template>
  <div class="min-h-screen bg-iron-900 flex items-center justify-center">
    <div class="glass-panel p-8 max-w-md text-center">
      <div class="text-6xl mb-4">⚠️</div>
      <h1 class="text-4xl font-bold text-shield-400 mb-2">Error {{ error?.statusCode }}</h1>
      <p class="text-gray-400 mb-6">{{ error?.message || 'An unexpected error occurred' }}</p>
      <button 
        @click="handleError"
        class="bg-shield-500 hover:bg-shield-600 text-white px-6 py-2 rounded-lg transition-colors"
      >
        Return to Safety
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  error: { statusCode: number; message: string } | null
}>()

const handleError = () => clearError({ redirect: '/dashboard' })
</script>
