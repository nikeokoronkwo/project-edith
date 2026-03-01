import amqp, { type Channel, type ConsumeMessage, type ChannelModel } from 'amqplib';

// Connection is expensive — share one per server process.
// Channels are cheap — each consumer gets its own so they never block each other.
let connection: ChannelModel | null = null;

export const RABBITMQ_EXCHANGE       = 'shield_events';
export const RABBITMQ_QUEUE_EVENTS   = 'events_stream';
export const RABBITMQ_QUEUE_ANALYTICS = 'analytics_stream';
export const RABBITMQ_QUEUE_REPORTS  = 'reports_stream';

export async function getRabbitMQConnection(): Promise<ChannelModel> {
  if (connection) return connection;

  const config = useRuntimeConfig();
  connection = await amqp.connect(config.rabbitmqUrl);

  connection.on('error', (err: Error) => {
    console.error('[RabbitMQ] Connection error:', err);
    connection = null;
  });

  connection.on('close', () => {
    console.log('[RabbitMQ] Connection closed');
    connection = null;
  });

  return connection;
}

/**
 * Create a fresh dedicated channel from the shared connection.
 * Each SSE consumer should call this so they never block each other.
 * The caller is responsible for calling ch.close() when done.
 */
export async function createDedicatedChannel(prefetch = 50): Promise<Channel> {
  const conn = await getRabbitMQConnection();
  const ch   = await conn.createChannel();

  await ch.assertExchange(RABBITMQ_EXCHANGE, 'fanout', { durable: true });

  // Limit how many unacked messages RabbitMQ will push at once.
  // Without this, a burst of thousands of queued messages arrives
  // simultaneously and monopolises the event loop.
  await ch.prefetch(prefetch);

  return ch;
}

export async function setupEventQueue(): Promise<Channel> {
  const ch = await createDedicatedChannel();
  await ch.assertQueue(RABBITMQ_QUEUE_EVENTS, {
    durable: true,
    arguments: { 'x-message-ttl': 86400000 },
  });
  await ch.bindQueue(RABBITMQ_QUEUE_EVENTS, RABBITMQ_EXCHANGE, '');
  return ch;
}

export async function setupAnalyticsQueue(): Promise<Channel> {
  const ch = await createDedicatedChannel();
  await ch.assertQueue(RABBITMQ_QUEUE_ANALYTICS, {
    durable: true,
    arguments: { 'x-message-ttl': 86400000 },
  });
  await ch.bindQueue(RABBITMQ_QUEUE_ANALYTICS, RABBITMQ_EXCHANGE, '');
  return ch;
}

export async function setupReportsQueue(): Promise<Channel> {
  const ch = await createDedicatedChannel();
  await ch.assertQueue(RABBITMQ_QUEUE_REPORTS, {
    durable: true,
    arguments: { 'x-message-ttl': 86400000 },
  });
  await ch.bindQueue(RABBITMQ_QUEUE_REPORTS, RABBITMQ_EXCHANGE, '');
  return ch;
}

export interface RabbitMQMessage<T = Record<string, unknown>> {
  content: T;
  timestamp: number;
}

export function parseMessage<T>(msg: ConsumeMessage | null): RabbitMQMessage<T> | null {
  if (!msg) return null;
  try {
    return {
      content: JSON.parse(msg.content.toString()),
      timestamp: Date.now(),
    };
  } catch (e) {
    console.error('[RabbitMQ] Failed to parse message:', e);
    return null;
  }
}

/** Convenience helper — creates its own channel so it doesn't share with SSE handlers. */
export async function consumeQueue(
  queueName: string,
  callback: (msg: ConsumeMessage) => void,
): Promise<Channel> {
  const ch = await createDedicatedChannel();
  await ch.consume(queueName, (msg: ConsumeMessage | null) => {
    if (msg) {
      callback(msg);
      ch.ack(msg);
    }
  });
  return ch;
}

export async function closeRabbitMQ(): Promise<void> {
  if (connection) {
    await connection.close();
    connection = null;
  }
}
