<template>
  <div class="w-80 h-96 bg-[#0d2137] border border-slate-700 rounded-xl shadow-2xl flex flex-col overflow-hidden">
    <div class="h-12 bg-gradient-to-r from-[#1e3a5f] to-[#0d2137] flex items-center justify-between px-4 border-b border-slate-700">
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 rounded-full bg-[#0080e6] flex items-center justify-center animate-pulse">
          <Icon name="heroicons:sparkles" class="w-4 h-4 text-white" />
        </div>
        <div>
          <h3 class="text-white font-semibold text-sm">JARVIS</h3>
          <p class="text-xs text-green-400">Online</p>
        </div>
      </div>
      <button @click="emit('close')" class="text-slate-400 hover:text-white">
        <Icon name="heroicons:x-mark" class="w-5 h-5" />
      </button>
    </div>
    
    <div ref="messagesRef" class="flex-1 overflow-y-auto p-4 space-y-3">
      <div class="flex justify-start">
        <div class="max-w-[80%] bg-[#1e3a5f] rounded-lg px-3 py-2">
          <p class="text-sm text-white">Greetings, Agent. How may I assist you today?</p>
        </div>
      </div>
      
      <div 
        v-for="(msg, index) in messages" 
        :key="index"
        class="flex"
        :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div 
          class="max-w-[80%] rounded-lg px-3 py-2"
          :class="msg.role === 'user' ? 'bg-[#0080e6]' : 'bg-[#1e3a5f]'"
        >
          <p class="text-sm text-white">{{ msg.content }}</p>
        </div>
      </div>
      
      <div v-if="isLoading" class="flex justify-start">
        <div class="bg-[#1e3a5f] rounded-lg px-3 py-2">
          <div class="flex gap-1">
            <div class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 0ms" />
            <div class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 150ms" />
            <div class="w-2 h-2 bg-white rounded-full animate-bounce" style="animation-delay: 300ms" />
          </div>
        </div>
      </div>
    </div>
    
    <div class="p-3 border-t border-slate-700">
      <form @submit.prevent="sendMessage" class="flex gap-2">
        <input
          v-model="input"
          type="text"
          placeholder="Ask JARVIS..."
          class="flex-1 bg-[#0a1929] border border-slate-600 rounded-lg px-3 py-2 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-[#0080e6]"
          :disabled="isLoading"
        />
        <button
          type="submit"
          :disabled="!input.trim() || isLoading"
          class="p-2 bg-[#0080e6] hover:bg-[#0064b3] disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
        >
          <Icon name="heroicons:paper-airplane" class="w-4 h-4 text-white" />
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Message {
  role: 'user' | 'assistant'
  content: string
}

const emit = defineEmits<{
  close: []
}>()

const messages = ref<Message[]>([])
const input = ref('')
const isLoading = ref(false)
const messagesRef = ref<HTMLElement | null>(null)

async function sendMessage() {
  if (!input.value.trim() || isLoading.value) return
  
  const userMessage = input.value.trim()
  input.value = ''
  
  messages.value.push({ role: 'user', content: userMessage })
  isLoading.value = true
  
  await nextTick()
  scrollToBottom()
  
  setTimeout(() => {
    messages.value.push({
      role: 'assistant',
      content: getJarvisResponse(userMessage)
    })
    isLoading.value = false
    nextTick()
    scrollToBottom()
  }, 1000)
}

function getJarvisResponse(input: string): string {
  const lower = input.toLowerCase()
  
  if (lower.includes('analytics') || lower.includes('data')) {
    return 'I can pull up the latest analytics. What sector or resource would you like to examine?'
  }
  if (lower.includes('event') || lower.includes('incident')) {
    return 'Let me check the recent event reports. One moment...'
  }
  if (lower.includes('report') || lower.includes('submit')) {
    return 'I can help you submit a field report. Would you like me to open the report form?'
  }
  if (lower.includes('resource')) {
    return 'Which resource are you tracking? Vibranium, Pym Particles, or perhaps medical supplies?'
  }
  
  return 'I\'m analyzing that request. Could you provide more specific details?'
}

function scrollToBottom() {
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}
</script>
