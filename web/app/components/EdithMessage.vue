<template>
  <div
    :class="[
      'edith-message bubble',
      message.role === 'user' ? 'bubble-user' : 'bubble-assistant',
      message.status === 'error' ? 'bubble-error' : ''
    ]"
  >
    <p class="content">{{ message.content }}</p>
    <div v-if="message.toolCalls?.length" class="tool-calls">
      <div v-for="tc in message.toolCalls" :key="tc.id" class="tool-call">
        <span class="tc-name">{{ tc.name }}:</span>
        <span class="tc-status">{{ tc.status }}</span>
        <pre v-if="tc.result">{{ JSON.stringify(tc.result, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Message } from '@/composables/useEdith'

const props = defineProps<{ message: Message }>()
</script>

<style scoped>
.edith-message {
  margin-bottom: 8px;
}

.bubble {
  padding: 8px 12px;
  border-radius: 0.5rem;
  max-width: 100%;
  white-space: pre-wrap;
}
.bubble-user {
  background: var(--primary)/20;
  align-self: flex-end;
}
.bubble-assistant {
  background: var(--card);
  align-self: flex-start;
}

/* error indication */
.bubble-error {
  background: rgba(229,62,62,0.1);
  border: 1px solid #e53e3e;
  color: #9b2c2c;
}
.content {
  white-space: pre-wrap;
}
.tool-calls {
  margin-top: 4px;
  font-size: 0.75rem;
  color: var(--muted-foreground);
}
.tool-call .tc-name {
  font-weight: 600;
}
.tool-call {
  margin-bottom: 2px;
}
</style>