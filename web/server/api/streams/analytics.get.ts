import { H3Event } from 'h3';
import {
  setupAnalyticsQueue,
  RABBITMQ_QUEUE_ANALYTICS,
  parseMessage,
} from '~~/server/utils/rabbitmq';
import type { ConsumeMessage } from 'amqplib';

export interface StreamAnalyticsData {
  timestamp: number;
  resource: string;
  sector: string;
  value?: number;
  [key: string]: unknown;
}

export default defineEventHandler(async (event: H3Event) => {
  const res = event.node.res;

  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'X-Accel-Buffering': 'no',
  });

  res.write(': Connected to analytics stream\n\n');

  // Each SSE connection gets its own dedicated channel so bursts on one
  // stream never block or starve another connection.
  const channel = await setupAnalyticsQueue();

  const consumer = await channel.consume(RABBITMQ_QUEUE_ANALYTICS, (msg: ConsumeMessage | null) => {
    if (!msg) return;

    const parsed = parseMessage<StreamAnalyticsData>(msg);
    if (parsed && !res.writableEnded) {
      const data: StreamAnalyticsData = { ...parsed.content, timestamp: parsed.timestamp };
      res.write(`data: ${JSON.stringify(data)}\n\n`);
    }

    channel.ack(msg);
  });

  // On disconnect: close the channel (auto-cancels the consumer and releases
  // the AMQP slot). Calling channel.cancel() alone leaves the channel open.
  event.node.req.on('close', () => {
    channel.close().catch(() => {});
  });

  return new Promise(() => {});
});
