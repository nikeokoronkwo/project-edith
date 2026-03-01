import amqp, { type Channel, type ConsumeMessage, type ChannelModel } from 'amqplib';

let connection: ChannelModel | null = null;
let channel: Channel | null = null;

export const RABBITMQ_EXCHANGE = 'shield_events';
export const RABBITMQ_QUEUE_EVENTS = 'events_stream';
export const RABBITMQ_QUEUE_ANALYTICS = 'analytics_stream';

export async function getRabbitMQConnection(): Promise<ChannelModel> {
  if (connection) return connection;
  
  const config = useRuntimeConfig();
  const rabbitmqUrl = config.rabbitmqUrl;
  
  connection = await amqp.connect(rabbitmqUrl);
  
  connection.on('error', (err: Error) => {
    console.error('[RabbitMQ] Connection error:', err);
    connection = null;
    channel = null;
  });
  
  connection.on('close', () => {
    console.log('[RabbitMQ] Connection closed');
    connection = null;
    channel = null;
  });
  
  return connection;
}

export async function getRabbitMQChannel(): Promise<Channel> {
  if (channel) return channel;
  
  const conn = await getRabbitMQConnection();
  channel = await conn.createChannel();
  
  await channel.assertExchange(RABBITMQ_EXCHANGE, 'fanout', { durable: true });
  
  return channel;
}

export async function setupEventQueue(): Promise<Channel> {
  const ch = await getRabbitMQChannel();
  
  await ch.assertQueue(RABBITMQ_QUEUE_EVENTS, { 
    durable: true,
    arguments: { 'x-message-ttl': 86400000 }
  });
  
  await ch.bindQueue(RABBITMQ_QUEUE_EVENTS, RABBITMQ_EXCHANGE, '');
  
  return ch;
}

export async function setupAnalyticsQueue(): Promise<Channel> {
  const ch = await getRabbitMQChannel();
  
  await ch.assertQueue(RABBITMQ_QUEUE_ANALYTICS, { 
    durable: true,
    arguments: { 'x-message-ttl': 86400000 }
  });
  
  await ch.bindQueue(RABBITMQ_QUEUE_ANALYTICS, RABBITMQ_EXCHANGE, '');
  
  return ch;
}

export interface RabbitMQMessage<T = Record<string, unknown>> {
  content: T;
  timestamp: number;
}

export function parseMessage<T>(msg: ConsumeMessage | null): RabbitMQMessage<T> | null {
  if (!msg) return null;
  
  try {
    const content = JSON.parse(msg.content.toString());
    return {
      content,
      timestamp: Date.now()
    };
  } catch (e) {
    console.error('[RabbitMQ] Failed to parse message:', e);
    return null;
  }
}

export async function consumeQueue(
  queueName: string,
  callback: (msg: ConsumeMessage) => void
): Promise<void> {
  const ch = await getRabbitMQChannel();
  
  await ch.consume(queueName, (msg: ConsumeMessage | null) => {
    if (msg) {
      callback(msg);
      ch.ack(msg);
    }
  });
}

export async function closeRabbitMQ(): Promise<void> {
  if (channel) {
    await channel.close();
    channel = null;
  }
  if (connection) {
    await connection.close();
    connection = null;
  }
}
