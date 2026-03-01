// server/api/edith.post.ts
// conversational AI endpoint for EDITH assistant

import { streamText, tool } from 'ai'
// using local Ollama for inference; will be started via docker-compose later
import { z } from 'zod'

// Tool implementations
const getCurrentSituation = tool({
  description: 'Get current important events, active incidents, and live trends',
  parameters: z.object({
    timeWindowHours: z.number().default(24),
  }),
  execute: async ({ timeWindowHours }, { request }) => {
    const kv = hubKV()

    const [latestResources, latestSectors] = await Promise.all([
      kv.get<Record<string, unknown>>('snapshot:resources'),
      kv.get<Record<string, unknown>>('snapshot:sectors'),
    ])

    const reports = await $fetch(`/api/reports?hours=${timeWindowHours}&limit=30`)

    return {
      latestSnapshot: { resources: latestResources, sectors: latestSectors },
      reports,
      asOf: new Date().toISOString(),
    }
  },
})

const submitReport = tool({
  description: 'Submit a new incident or situation report. Returns incomplete if credentials missing.',
  parameters: z.object({
    reporterName: z.string().optional(),
    reporterPhone: z.string().optional(),
    content: z.string(),
    location: z.string().optional(),
    severity: z.enum(['low', 'medium', 'high', 'critical']).optional(),
    mediaUrl: z.string().optional(),
  }),
  execute: async (params) => {
    const missing: string[] = []
    if (!params.reporterName) missing.push('full name')
    if (!params.reporterPhone) missing.push('phone number')
    if (missing.length > 0) return { status: 'incomplete', missing }

    try {
      const result = await $fetch('/api/reports/new', {
        method: 'POST',
        body: params,
      })
      return { status: 'submitted', ...result }
    } catch (e: any) {
      return { status: 'error', message: e.message }
    }
  },
})

const analyzeResourceOrSector = tool({
  description: 'Analyze trends, forecasts, and reports for a named resource or sector',
  parameters: z.object({
    subject: z.string(),
    subjectType: z.enum(['resource', 'sector']),
    includeForecasts: z.boolean().default(true),
  }),
  execute: async ({ subject, subjectType, includeForecasts }) => {
    const kv = hubKV()
    const slug = subject.toLowerCase().replace(/\s+/g, '-')

    const latestDatapoint = await kv.get(`snapshot:${subjectType}:${slug}`)

    const [historical, relatedReports] = await Promise.all([
      $fetch(`/api/${subjectType}s/${slug}/history`).catch(() => null),
      $fetch(`/api/reports?subject=${encodeURIComponent(subject)}&limit=20`).catch(() => []),
    ])

    const activeEvents = (relatedReports as any[]).filter(
      r => r.severity === 'high' || r.severity === 'critical'
    )

    return {
      subject,
      subjectType,
      latestDatapoint,
      historical,
      relatedReports,
      activeEvents,
      hasActiveEvents: activeEvents.length > 0,
      includeForecasts,
    }
  },
})

const summarizeRecentReports = tool({
  description: 'Get general trends and summary from recent field reports',
  parameters: z.object({
    category: z.string().optional(),
    limit: z.number().default(25),
  }),
  execute: async ({ category, limit }) => {
    const query = new URLSearchParams({ limit: String(limit) })
    if (category) query.set('category', category)
    return $fetch(`/api/reports?${query}`)
  },
})

const requestVisualReport = tool({
  description: 'Signal the frontend to open the video/audio capture UI for a visual field report',
  parameters: z.object({
    context: z.string().optional().describe('What kind of situation or area to capture'),
  }),
  execute: async ({ context }) => {
    return {
      action: 'OPEN_MEDIA_CAPTURE',
      context: context ?? 'General field observation',
      message: 'Opening camera feed. Please record what you want to report.',
    }
  },
})

const SYSTEM_PROMPT = `You are EDITH — a tactical situational awareness assistant for field operations.
You are concise, precise, and prioritise critical information. Respond in natural language.

Key behaviors:
- When analyzing resources or sectors: ALWAYS surface active event reports FIRST before trends
- When collecting reports: gather name + phone before confirming — ask for ONE missing field at a time
- State uncertainty clearly when data is limited or stale
- For forecasts: note confidence level and data freshness
- Format numbers clearly (units, %change, timestamps)
- Keep responses focused — avoid unnecessary hedging

Current UTC time: ${new Date().toISOString()}`

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const { messages } = body

  if (!messages || !Array.isArray(messages)) {
    throw createError({ statusCode: 400, message: 'messages required' })
  }

  const result = streamText({
    // use the local Ollama server; model name can be changed via OLLAMA_MODEL env var
    model: process.env.OLLAMA_MODEL || 'ollama:llama3.2',
    providerOptions: {
      ollama: {
        baseUrl: process.env.OLLAMA_URL || 'http://localhost:11434',
      },
    },
    system: SYSTEM_PROMPT,
    messages: messages.slice(-24),
    tools: {
      getCurrentSituation,
      submitReport,
      analyzeResourceOrSector,
      summarizeRecentReports,
      requestVisualReport,
    },
    maxRetries: 5,
  })

  // if the LLM call fails, propagate error so client can show fallback
  try {
    return result.toTextStreamResponse()
  } catch (e: any) {
    console.error('LLM stream error', e)
    throw createError({ statusCode: 502, message: 'AI backend error' })
  }
})