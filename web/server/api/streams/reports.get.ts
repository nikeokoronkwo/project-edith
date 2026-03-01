import { H3Event } from 'h3';
import {
  setupReportsQueue,
  RABBITMQ_QUEUE_REPORTS,
  parseMessage,
  type RabbitMQMessage
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
  const stream = event.node.res;
  
  stream.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'X-Accel-Buffering': 'no'
  });

  stream.write(`: Connected to reports stream\n\n`);

  try {
    const channel = await setupReportsQueue();
    
    const consumer = await channel.consume(RABBITMQ_QUEUE_REPORTS, (msg: ConsumeMessage | null) => {
      if (msg) {
        const parsed = parseMessage<Omit<StreamReport, 'timestamp'>>(msg);
        if (parsed) {
          const content = parsed.content as StreamReport;
          const reportData: StreamReport = {
            ...content,
            timestamp: content.timestamp
              ?? (content.timeStarted ? new Date(content.timeStarted).getTime() : parsed.timestamp),
          };
          stream.write(`data: ${JSON.stringify(reportData)}\n\n`);
        }
        channel.ack(msg);
      }
    });

    event.node.req.on('close', () => {
      channel.cancel(consumer.consumerTag);
    });
    
  } catch (error) {
    console.error('[Reports Stream] Error:', error);
    stream.write(`error: ${JSON.stringify({ message: 'Stream error' })}\n\n`);
  }

  return new Promise(() => {});
});
