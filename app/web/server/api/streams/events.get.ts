import { H3Event } from 'h3';
import {
  setupEventQueue,
  RABBITMQ_QUEUE_EVENTS,
  parseMessage,
  type RabbitMQMessage
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
  const stream = event.node.res;
  
  stream.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'X-Accel-Buffering': 'no'
  });

  stream.write(`: Connected to events stream\n\n`);

  try {
    const channel = await setupEventQueue();
    
    const consumer = await channel.consume(RABBITMQ_QUEUE_EVENTS, (msg: ConsumeMessage | null) => {
      if (msg) {
        const parsed = parseMessage<Omit<StreamEvent, 'timestamp'>>(msg);
        if (parsed) {
          const content = parsed.content as StreamEvent;
          const eventData: StreamEvent = {
            ...content,
            timestamp: content.timestamp
              ?? (content.started ? new Date(content.started).getTime() : parsed.timestamp),
          };
          stream.write(`data: ${JSON.stringify(eventData)}\n\n`);
        }
        channel.ack(msg);
      }
    });

    event.node.req.on('close', () => {
      channel.cancel(consumer.consumerTag);
    });
    
  } catch (error) {
    console.error('[Events Stream] Error:', error);
    stream.write(`error: ${JSON.stringify({ message: 'Stream error' })}\n\n`);
  }

  return new Promise(() => {});
});
