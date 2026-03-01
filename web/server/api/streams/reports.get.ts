import { H3Event } from 'h3';
import {
  setupReportsQueue,
  RABBITMQ_QUEUE_REPORTS,
  parseMessage,
} from '~~/server/utils/rabbitmq';
import type { ConsumeMessage } from 'amqplib';

export interface StreamReport {
  id: string;
  heroAlias?: string;
  description?: string;
  timeStarted?: string;
  timestamp: number;
  affectedLocations?: string[];
  affectedResources?: string[];
  severity?: 'critical' | 'warning' | 'elevated' | 'normal';
}

export default defineEventHandler(async (event: H3Event) => {
  const res = event.node.res;

  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'X-Accel-Buffering': 'no',
  });

  res.write(': Connected to reports stream\n\n');

  const channel = await setupReportsQueue();

  const consumer = await channel.consume(RABBITMQ_QUEUE_REPORTS, (msg: ConsumeMessage | null) => {
    if (!msg) return;

    const parsed = parseMessage<Omit<StreamReport, 'timestamp'>>(msg);
    if (parsed && !res.writableEnded) {
      const content = parsed.content as StreamReport;
      const data: StreamReport = {
        ...content,
        timestamp: content.timestamp
          ?? (content.timeStarted ? new Date(content.timeStarted).getTime() : parsed.timestamp),
      };
      res.write(`data: ${JSON.stringify(data)}\n\n`);
    }

    channel.ack(msg);
  });

  event.node.req.on('close', () => {
    channel.close().catch(() => {});
  });

  return new Promise(() => {});
});
