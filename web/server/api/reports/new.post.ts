import { H3Event } from 'h3';
import { auth } from '~~/server/utils/auth';
import jwt from 'jsonwebtoken';
import { z } from 'zod';

const createReportSchema = z.object({
  heroAlias: z.string().min(1, 'Hero alias is required'),
  description: z.string().min(1, 'Description is required'),
  affectedResources: z.array(z.string()).default([]),
  affectedLocations: z.array(z.string()).default([]),
  relatedReportIds: z.array(z.string()).default([]),
  timeStarted: z.string().datetime().optional(),
});

export type CreateReportInput = z.infer<typeof createReportSchema>;

interface ReportPayload {
  description: string;
  affectedResources: string[];
  affectedLocations: string[];
  relatedReportIds: string[];
  timeStarted: string;
  metadata: string;
}

export default defineEventHandler(async (event: H3Event) => {
  const body = await readBody(event);
  
  const validation = createReportSchema.safeParse(body);
  if (!validation.success) {
    throw createError({
      statusCode: 400,
      message: validation.error.errors.map(e => e.message).join(', ')
    });
  }

  const { heroAlias, description, affectedResources, affectedLocations, relatedReportIds, timeStarted } = validation.data;
  
  const reportId = `rpt_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`;
  const timestamp = new Date().toISOString();

  const config = useRuntimeConfig();
  const externalBackendUrl = config.externalBackendUrl;

  let authToken: string | undefined;
  let jwtPayload: Record<string, unknown> | null = null;

  const authHeader = getHeader(event, 'authorization');
  if (authHeader?.startsWith('Bearer ')) {
    authToken = authHeader.slice(7);
    
    try {
      const secret = config.jwtSecret;
      jwtPayload = jwt.verify(authToken, secret) as Record<string, unknown>;
    } catch (e) {
      console.error('[reports/new] JWT verification failed:', e);
    }
  }

  if (!jwtPayload) {
    const session = await auth.api.getSession({ headers: event.headers });
    if (session?.session) {
      const secret = config.jwtSecret;
      const token = jwt.sign(
        { 
          userId: session.user.id, 
          email: session.user.email,
          heroAlias 
        },
        secret,
        { expiresIn: '1h' }
      );
      authToken = token;
      jwtPayload = { userId: session.user.id, email: session.user.email, heroAlias };
    }
  }

  if (!authToken) {
    throw createError({
      statusCode: 401,
      message: 'Authentication required'
    });
  }

  const metadata = jwt.sign(
    { heroAlias, ...jwtPayload },
    config.jwtSecret,
    { expiresIn: '1h' }
  );

  const payload: ReportPayload = {
    description,
    affectedResources,
    affectedLocations,
    relatedReportIds,
    timeStarted: timeStarted || timestamp,
    metadata
  };

  try {
    const response = await $fetch<{ success: boolean; reportId?: string; message?: string }>(
      `${externalBackendUrl}/api/reports`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: payload
      }
    );

    // fire-and-forget publish into RabbitMQ so clients listening on the "reports" stream
    try {
      const { getRabbitMQChannel, RABBITMQ_EXCHANGE, setupReportsQueue } = await import('~~/server/utils/rabbitmq');
      const ch = await getRabbitMQChannel();
      // make sure the reports queue is asserted/bound so messages aren't dropped
      await setupReportsQueue();
      const msg = {
        id: response.reportId || reportId,
        heroAlias,
        description,
        timeStarted: timeStarted || timestamp,
        timestamp: timeStarted ? new Date(timeStarted).getTime() : Date.now(),
        affectedLocations,
        affectedResources,
        severity: 'normal' as const // default, backend could compute
      };
      ch.publish(RABBITMQ_EXCHANGE, '', Buffer.from(JSON.stringify(msg)));
    } catch (pubErr) {
      // log but don't block
      console.warn('[reports/new] failed to publish rabbitmq message', pubErr);
    }

    return {
      success: true,
      reportId: response.reportId || reportId,
      timestamp,
      message: 'Report submitted successfully'
    };
  } catch (error) {
    console.error('[reports/new] External backend error:', error);
    
    throw createError({
      statusCode: 502,
      message: 'Report processing failed — backend unavailable'
    });
  }
});
