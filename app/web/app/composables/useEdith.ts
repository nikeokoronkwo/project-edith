import { ref, computed } from 'vue'
import { toast } from 'vue-sonner' // for error notifications

export type MessageRole = 'user' | 'assistant' | 'tool'
export type MessageStatus = 'sending' | 'streaming' | 'done' | 'error'

export interface ToolCall {
  id: string
  name: string
  status: 'running' | 'done' | 'error'
  result?: unknown
}

export interface Message {
  id: string
  role: MessageRole
  content: string
  status: MessageStatus
  toolCalls?: ToolCall[]
  timestamp: Date
  mediaUrl?: string
}

export interface EdithState {
  isOpen: boolean
  isListening: boolean
  isRecording: boolean
  pendingCredentials: { name?: string; phone?: string } | null
}

function generateId() {
  return Math.random().toString(36).slice(2, 10)
}

export function useEdithChat() {
  const messages = ref<Message[]>([])
  const input = ref('')
  const state = ref<EdithState>({
    isOpen: false,
    isListening: false,
    isRecording: false,
    pendingCredentials: null,
  })
  const isLoading = ref(false)
  const mediaCapturePending = ref(false)

  function speak(text: string) {
    if (!('speechSynthesis' in window)) return
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = 1.05
    utterance.pitch = 0.9
    window.speechSynthesis.speak(utterance)
  }

  let recognition: any = null
  function startListening() {
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SR) return
    recognition = new SR()
    recognition.continuous = false
    recognition.interimResults = true
    recognition.onstart = () => { state.value.isListening = true }
    recognition.onend = () => { state.value.isListening = false }
    recognition.onresult = (e: any) => {
      const transcript = Array.from(e.results)
        .map((r: any) => r[0].transcript)
        .join('')
      input.value = transcript
      if (e.results[e.results.length - 1].isFinal) {
        sendMessage()
      }
    }
    recognition.start()
  }

  function stopListening() {
    recognition?.stop()
    state.value.isListening = false
  }

  async function sendMessage(overrideContent?: string) {
    const content = overrideContent ?? input.value.trim()
    if (!content || isLoading.value) return

    input.value = ''
    isLoading.value = true

    const userMsg: Message = {
      id: generateId(),
      role: 'user',
      content,
      status: 'done',
      timestamp: new Date(),
    }
    messages.value.push(userMsg)

    const assistantMsg: Message = {
      id: generateId(),
      role: 'assistant',
      content: '',
      status: 'streaming',
      timestamp: new Date(),
      toolCalls: [],
    }
    messages.value.push(assistantMsg)

    try {
      const response = await fetch('/api/edith', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: messages.value
            .filter(m => m.status === 'done' && m.role !== 'tool')
            .slice(-20)
            .map(m => ({ role: m.role, content: m.content }))
            .concat([{ role: 'user', content }]),
        }),
      })

      if (!response.ok) throw new Error('Network error')
      if (!response.body) throw new Error('No body')

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const data = line.slice(6)
          if (data === '[DONE]') continue

          try {
            const parsed = JSON.parse(data)

            if (parsed.type === 'text-delta') {
              assistantMsg.content += parsed.textDelta
            }
            if (parsed.type === 'tool-call-streaming-start') {
              assistantMsg.toolCalls!.push({
                id: parsed.toolCallId,
                name: parsed.toolName,
                status: 'running',
              })
              if (parsed.toolName === 'requestVisualReport') {
                mediaCapturePending.value = true
              }
            }
            if (parsed.type === 'tool-result') {
              const tc = assistantMsg.toolCalls!.find(t => t.id === parsed.toolCallId)
              if (tc) {
                tc.status = 'done'
                tc.result = parsed.result
              }
            }
            if (parsed.type === 'finish') {
              assistantMsg.status = 'done'
              isLoading.value = false
              if (assistantMsg.content) speak(assistantMsg.content)
            }
          } catch (err) {
            console.warn('Failed to parse stream data:', err, 'raw:', data)
          }
        }
      }

      assistantMsg.status = 'done'
    } catch (err: any) {
      console.error('EDITH error:', err)
      const msg = err?.message || 'Connection lost. Please try again.'
      assistantMsg.content = msg
      assistantMsg.status = 'error'
      toast.error(`EDITH error: ${msg}`)
    } finally {
      isLoading.value = false
    }
  }

  function open() { state.value.isOpen = true }
  function close() { state.value.isOpen = false }
  function toggle() { state.value.isOpen = !state.value.isOpen }
  function clearMessages() { messages.value = [] }

  const lastMessage = computed(() => messages.value[messages.value.length - 1])

  return {
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
  }
}
