<template>
  <!-- command-palette style container -->
  <div class="edith-chat-overlay" @click.self="close">
    <div class="edith-chat-container" aria-label="Edith AI assistant">
      <button class="close-btn" @click="close">
        <Icon name="heroicons:x-mark" class="w-5 h-5 text-white" />
      </button>
      <div class="search-row">
        <Input
          ref="inputRef"
          v-model="input"
          @keydown.enter.prevent="() => sendMessage()"
          placeholder="Ask EDITH or type a command..."
          class="edith-search-input"
          autofocus
          :disabled="isLoading"
        />
        <Button
          size="icon"
          variant="ghost"
          @click="toggleListening"
          :class="{ 'listening-active': state.isListening }"
          title="Click to speak or use keyboard"
        >
          <Icon
            :name="state.isListening ? 'heroicons:mic-solid' : 'heroicons:microphone'"
            class="w-5 h-5"
          />
        </Button>
        <Button
          size="icon"
          variant="ghost"
          @click="toggleAudio"
          title="Toggle audio feedback"
        >
          <Icon
            :name="audioEnabled ? 'heroicons:speaker-wave' : 'heroicons:speaker-x-mark'"
            class="w-5 h-5"
          />
        </Button>
        <Button size="icon" variant="ghost" @click="() => sendMessage()" :disabled="isLoading">
          <template #default>
            <Icon v-if="!isLoading" name="heroicons:paper-airplane" class="w-5 h-5" />
            <Icon v-else name="heroicons:arrow-path" class="w-5 h-5 animate-spin" />
          </template>
        </Button>
      </div>
      <div class="edith-results" ref="messagesRef">
        <!-- error banner: only when last message is an error with no visible content already -->
        <div v-if="lastMessage?.status === 'error' && !lastMessage.content" class="error-banner">
          EDITH encountered an error. Check your connection or try again.
        </div>
        <!-- when empty, show suggestions list similar to palette screenshot -->
        <template v-if="messages.length === 0">
          <ul class="suggestions">
            <li>Ask about resources</li>
            <li>Open media capture</li>
            <li>Submit a field report</li>
          </ul>
        </template>
        <EdithMessage v-for="msg in messages" :key="msg.id" :message="msg" />
      </div>

      <EdithMediaCapture v-model="mediaCapturePending" @captured="onMediaCaptured" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, onBeforeMount, onUnmounted, nextTick, watch } from 'vue'
import { useEdithChat } from '@/composables/useEdith'
import EdithMessage from './EdithMessage.vue'
import EdithMediaCapture from './EdithMediaCapture.vue'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

const {
  messages,
  input,
  state,
  isLoading,
  mediaCapturePending,
  lastMessage,
  sendMessage,
  startListening,
  stopListening,
  speak,
  open,
  close,
  toggle,
  clearMessages,
} = useEdithChat()

const messagesRef = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)
const audioEnabled = ref(true)

function toggleListening() {
  if (state.value.isListening) {
    stopListening()
  } else {
    startListening()
  }
}

function toggleAudio() {
  audioEnabled.value = !audioEnabled.value
  localStorage.setItem('edith-audio-enabled', String(audioEnabled.value))
}

function onKeyDown(e: KeyboardEvent) {
  if (e.key === 'Escape') close()
}

function onMediaCaptured(url: string) {
  sendMessage(`Here is visual data: ${url}`)
}

onBeforeMount(() => {
  const saved = localStorage.getItem('edith-audio-enabled')
  if (saved !== null) audioEnabled.value = saved === 'true'
  window.addEventListener('keydown', onKeyDown)
})

onUnmounted(() => window.removeEventListener('keydown', onKeyDown))

onMounted(() => {
  nextTick(() => {
    inputRef.value?.focus()
  })

  watch(messages, () => {
    nextTick(() => {
      if (messagesRef.value) {
        messagesRef.value.scrollTop = messagesRef.value.scrollHeight
      }
    })
    if (audioEnabled.value && lastMessage.value?.role === 'assistant' && lastMessage.value?.content) {
      speak(lastMessage.value.content)
    }
  })
})
</script>

<style scoped>
.edith-chat-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.edith-chat-container {
  width: 500px;
  max-height: 80vh;
  background: rgba(13,17,23,0.95);
  border-radius: 0.5rem;
  box-shadow: 0 20px 40px rgba(0,0,0,0.5);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.search-row {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px;
}
.search-row[disabled] {
  opacity: 0.6;
  pointer-events: none;
}

button.listening-active {
  color: var(--destructive);
}

.edith-search-input {
  flex: 1;
  padding: 12px 16px;
  border: none;
  outline: none;
  background: rgba(255,255,255,0.05);
  color: #fff;
  font-size: 1rem;
}

.edith-results {
  flex: 1;
  overflow-y: auto;
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.suggestions {
  list-style: none;
  padding: 0;
  margin: 0;
  color: #aaa;
}

.suggestions li {
  padding: 4px 0;
}

.close-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: transparent;
  border: none;
  cursor: pointer;
}

/* reuse message styles but adjust spacing if needed */


.error-banner {
  background: rgba(229,62,62,0.15);
  color: #fc8181;
  padding: 6px 12px;
  font-size: 0.875rem;
  text-align: center;
  border-radius: 0.375rem;
  border: 1px solid rgba(229,62,62,0.4);
}
</style>