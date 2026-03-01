import { H3Event } from 'h3';
import {
  setupEventQueue,
  RABBITMQ_QUEUE_EVENTS,
  parseMessage,
} from '~~/server/utils/rabbitmq';
import type { ConsumeMessage } from 'amqplib';

export interface StreamEvent {
  id: string;
  event: string;
  priority: number;
  started: string;
  timestamp: number;
}

export default defineEventHandler(async (event: H3Event) => {
  const res = event.node.res;

  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'X-Accel-Buffering': 'no',
  });

  res.write(': Connected to events stream\n\n');

  const channel = await setupEventQueue();

  const consumer = await channel.consume(RABBITMQ_QUEUE_EVENTS, (msg: ConsumeMessage | null) => {
    if (!msg) return;

    const parsed = parseMessage<Omit<StreamEvent, 'timestamp'>>(msg);
    if (parsed && !res.writableEnded) {
      const content = parsed.content as StreamEvent;
      const data: StreamEvent = {
        ...content,
        timestamp: content.timestamp
          ?? (content.started ? new Date(content.started).getTime() : parsed.timestamp),
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
