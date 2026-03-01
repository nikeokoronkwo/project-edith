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
      // Build history: messages already in array (includes userMsg), excluding the
      // in-flight assistantMsg (status: 'streaming'). No need to concat separately.
      const history = messages.value
        .filter(m => m.status === 'done' && m.role !== 'tool')
        .slice(-20)
        .map(m => ({ role: m.role, content: m.content }))

      const response = await fetch('/api/edith', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: history }),
      })

      if (!response.ok) {
        const errText = await response.text().catch(() => 'Network error')
        throw new Error(`${response.status}: ${errText}`)
      }
      if (!response.body) throw new Error('No response body')

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
          const raw = line.slice(6)
          if (raw === '[DONE]') continue

          // AI SDK data stream format: <typeCode>:<jsonValue>
          const colonIdx = raw.indexOf(':')
          if (colonIdx === -1) continue
          const prefix = raw.slice(0, colonIdx)
          const valueStr = raw.slice(colonIdx + 1)

          try {
            const value = JSON.parse(valueStr)

            if (prefix === '0') {
              // text delta — value is a string
              assistantMsg.content += value
            } else if (prefix === 'b') {
              // tool_call_streaming_start — value: { toolCallId, toolName }
              assistantMsg.toolCalls!.push({
                id: value.toolCallId,
                name: value.toolName,
                status: 'running',
              })
              if (value.toolName === 'requestVisualReport') {
                mediaCapturePending.value = true
              }
            } else if (prefix === '9') {
              // tool_result — value: { toolCallId, result }
              const tc = assistantMsg.toolCalls!.find(t => t.id === value.toolCallId)
              if (tc) {
                tc.status = 'done'
                tc.result = value.result
              }
            } else if (prefix === 'd' || prefix === 'e') {
              // finish_message / step_finish
              assistantMsg.status = 'done'
              isLoading.value = false
              if (assistantMsg.content) speak(assistantMsg.content)
            } else if (prefix === '3') {
              // error — value is a string
              assistantMsg.content = typeof value === 'string' ? value : 'An error occurred'
              assistantMsg.status = 'error'
              isLoading.value = false
            }
          } catch (err) {
            console.warn('Failed to parse stream data:', err, 'raw:', raw)
          }
        }
      }

      // Ensure we don't leave the message in streaming state if stream ended without finish
      if (assistantMsg.status === 'streaming') {
        assistantMsg.status = assistantMsg.content ? 'done' : 'error'
        if (!assistantMsg.content) assistantMsg.content = 'No response received.'
      }
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
