import amqp from 'amqplib';
import { RABBITMQ_EXCHANGE } from '../utils/rabbitmq';

export default defineTask({
  meta: {
    name: 'rabbitmq:publish-test',
    description: 'Publish test messages to RabbitMQ to verify streaming works'
  },
  run: async ({ payload }) => {
    const config = useRuntimeConfig();
    const rabbitmqUrl = config.rabbitmqUrl;

    let connection: amqp.ChannelModel | null = null;
    let channel: amqp.Channel | null = null;

    try {
      console.log('[rabbitmq:publish-test] Connecting to RabbitMQ...');
      connection = await amqp.connect(rabbitmqUrl);
      channel = await connection.createChannel();

      await channel.assertExchange(RABBITMQ_EXCHANGE, 'fanout', { durable: true });

      const eventCount = (payload?.count as number) || 5;
      const analyticsCount = (payload?.analyticsCount as number) || 10;

      console.log(`[rabbitmq:publish-test] Publishing ${eventCount} events and ${analyticsCount} analytics data points...`);

      const events = [];
      for (let i = 0; i < eventCount; i++) {
        const event = {
          id: `test-event-${Date.now()}-${i}`,
          event: `Test Event ${i + 1}`,
          priority: Math.floor(Math.random() * 3) + 1,
          started: new Date().toISOString()
        };
        events.push(event);
        channel.publish(RABBITMQ_EXCHANGE, '', Buffer.from(JSON.stringify(event)));
      }

      const analytics = [];
      const resources = ['Vibranium (kg)', 'Arc Reactor Cores', 'Medical Kits', 'Clean Water (L)', 'Pym Particles'];
      const sectors = ['Wakanda', 'Avengers Compound', 'Sokovia', 'New Asgard', 'Sanctum Sanctorum'];

      for (let i = 0; i < analyticsCount; i++) {
        const data = {
          timestamp: Date.now(),
          resource: resources[Math.floor(Math.random() * resources.length)],
          sector: sectors[Math.floor(Math.random() * sectors.length)],
          value: Math.floor(Math.random() * 1000) + 100
        };
        analytics.push(data);
        channel.publish(RABBITMQ_EXCHANGE, '', Buffer.from(JSON.stringify(data)));
      }

      // also publish a few sample reports so the reports stream can be tested
      const reports = [];
      const severities = ['critical','warning','elevated','normal'];
      for (let i = 0; i < 3; i++) {
        const rpt = {
          id: `test-report-${Date.now()}-${i}`,
          heroAlias: `Test Hero ${i + 1}`,
          description: `This is a test report number ${i + 1}`,
          timeStarted: new Date().toISOString(),
          affectedLocations: ['Avengers Compound'],
          severity: severities[Math.floor(Math.random() * severities.length)]
        };
        reports.push(rpt);
        channel.publish(RABBITMQ_EXCHANGE, '', Buffer.from(JSON.stringify(rpt)));
      }

      console.log(`[rabbitmq:publish-test] Published ${events.length} events and ${analytics.length} analytics messages`);

      await channel.close();
      await connection.close();

      return {
        result: {
          success: true,
          message: `Published ${events.length} events and ${analytics.length} analytics messages`,
          events: events.map(e => e.id),
          analyticsCount
        } as any
      };
    } catch (error) {
      console.error('[rabbitmq:publish-test] Error:', error);
      
      if (channel) await channel.close().catch(() => {});
      if (connection) await connection.close().catch(() => {});
      
      return {
        result: {
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error'
        } as any
      };
    }
  }
});
