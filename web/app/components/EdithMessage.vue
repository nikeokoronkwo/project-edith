<template>
  <div
    :class="[
      'edith-message bubble',
      message.role === 'user' ? 'bubble-user' : 'bubble-assistant',
      message.status === 'error' ? 'bubble-error' : ''
    ]"
  >
    <!-- Typing indicator when streaming with no content yet -->
    <div v-if="message.status === 'streaming' && !message.content" class="typing-indicator">
      <span></span><span></span><span></span>
    </div>
    <p v-else class="content">{{ message.content }}</p>
    <div v-if="message.toolCalls?.length" class="tool-calls">
      <div v-for="tc in message.toolCalls" :key="tc.id" class="tool-call">
        <span class="tc-name">{{ tc.name }}</span>
        <span :class="['tc-status', tc.status === 'running' ? 'tc-running' : 'tc-done']">
          {{ tc.status === 'running' ? '…' : '✓' }}
        </span>
        <pre v-if="tc.result">{{ JSON.stringify(tc.result, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Message } from '@/composables/useEdith'

defineProps<{ message: Message }>()
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
  background: color-mix(in srgb, var(--primary) 20%, transparent);
  align-self: flex-end;
}

.bubble-assistant {
  background: var(--card);
  align-self: flex-start;
}

.bubble-error {
  background: rgba(229, 62, 62, 0.1);
  border: 1px solid #e53e3e;
  color: #fc8181;
}

.content {
  white-space: pre-wrap;
}

.tool-calls {
  margin-top: 6px;
  font-size: 0.75rem;
  color: var(--muted-foreground);
}

.tool-call {
  margin-bottom: 2px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tc-name {
  font-weight: 600;
}

.tc-running {
  opacity: 0.6;
  animation: pulse 1s infinite;
}

.tc-done {
  color: #38a169;
}

/* Typing indicator */
.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
  height: 20px;
  padding: 2px 0;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--muted-foreground);
  animation: bounce 1.2s ease-in-out infinite;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.6; }
  30% { transform: translateY(-6px); opacity: 1; }
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}
</style>
