import { H3Event } from 'h3';
import {
  setupAnalyticsQueue,
  RABBITMQ_QUEUE_ANALYTICS,
  parseMessage,
  type RabbitMQMessage
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
  const stream = event.node.res;
  
  stream.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'X-Accel-Buffering': 'no'
  });

  stream.write(`: Connected to analytics stream\n\n`);

  try {
    const channel = await setupAnalyticsQueue();
    
    const consumer = await channel.consume(RABBITMQ_QUEUE_ANALYTICS, (msg: ConsumeMessage | null) => {
      if (msg) {
        const parsed = parseMessage<StreamAnalyticsData>(msg);
        if (parsed) {
          const analyticsData: StreamAnalyticsData = {
            ...parsed.content,
            timestamp: parsed.timestamp
          };
          stream.write(`data: ${JSON.stringify(analyticsData)}\n\n`);
        }
        channel.ack(msg);
      }
    });

    event.node.req.on('close', () => {
      channel.cancel(consumer.consumerTag);
    });
    
  } catch (error) {
    console.error('[Analytics Stream] Error:', error);
    stream.write(`error: ${JSON.stringify({ message: 'Stream error' })}\n\n`);
  }

  return new Promise(() => {});
});
