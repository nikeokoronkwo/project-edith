import random
import heapq
import asyncio
import itertools
import json

from enum import Enum
from datetime import datetime, timedelta

import aio_pika  # real RabbitMQ client

# --- 1. ENUMS & DICTIONARY MAPPING ---

class MarvelEvent(Enum):
    THANOS = 'thanos'
    CATASTROPHE = 'catastrophe'

def handle_thanos(resources, sector_id):
    """Halves all resources across all sectors."""
    for key, (val, slope) in resources.items():
        resources[key] = (val / 2.0, slope)

def handle_catastrophe(resources, sector_id):
    """Halves resources only in the affected sector."""
    for key, (val, slope) in resources.items():
        if key[0] == sector_id: 
            resources[key] = (val / 2.0, slope)

EVENT_HANDLERS = {
    MarvelEvent.THANOS.value: handle_thanos,
    MarvelEvent.CATASTROPHE.value: handle_catastrophe
}

# --- 2. INITIALIZATION ---

SECTORS = ['New Asgard', 'Wakanda', 'Sokovia', 'Sanctum Sanctorum', 'Avengers Compound']
RESOURCE_IDS = ['Vibranium (kg)', 'Arc Reactor Cores', 'Pym Particles', 'Clean Water (L)', 'Medical Kits']
TICK_INTERVAL_MINUTES = 12

resources = {(sector, res): (1000.0, 5.0) for sector in SECTORS for res in RESOURCE_IDS}

# Shared state for our continuous simulation
timeline = []
tiebreaker = itertools.count()

# --- 3. I/O & MOCK LISTENERS ---

async def save_to_postgres(timestamp: datetime, current_resources: dict):
    # Dummy save function
    pass

# old mock listener kept for reference; you can remove once real listener works
def _mock_rabbitmq_listener():
    """Backstop generator used in early development only."""
    event_time = datetime(2026, 1, 15, 14, 30)
    event_data = {
        'timestamp': event_time,
        'sector_id': 'Wakanda',
        'event_type': 'catastrophe'
    }
    print(f"[MOCK] Received event for {event_time}")
    heapq.heappush(timeline, (event_time, next(tiebreaker), 'rabbitmq_event', event_data))

async def rabbitmq_listener():
    """Connects to RabbitMQ and pushes incoming messages onto the timeline queue."""
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    # fairly small prefetch since we only care about order
    await channel.set_qos(prefetch_count=1)

    exchange = await channel.declare_exchange(
        "reports.direct", aio_pika.ExchangeType.DIRECT, durable=True
    )
    queue = await channel.declare_queue("report.events", durable=True)
    await queue.bind(exchange, routing_key="report.new")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    data = json.loads(message.body.decode())
                except Exception:
                    print("[RABBITMQ] failed to decode message, skipping")
                    continue
                # optionally compute or override timestamp here
                event_time = data.get('timestamp', datetime.now())
                heapq.heappush(
                    timeline,
                    (event_time, next(tiebreaker), 'rabbitmq_event', data)
                )

# --- 4. CORE CONTINUOUS ENGINE ---

async def process_continuous_timeline(start_time: datetime):
    """
    Runs continuously. Fast-forwards through past events, 
    then paces itself with real-time once caught up.
    """
    print(f"Starting continuous engine from {start_time}...")
    
    # Prime the pump with our very first tick
    heapq.heappush(timeline, (start_time, next(tiebreaker), 'tick', {}))
    
    while True:
        if not timeline:
            # Yield control if queue is empty (unlikely with continuous ticks)
            await asyncio.sleep(0.1)
            continue
            
        # 1. Peek at the next event
        next_timestamp = timeline[0][0]
        now = datetime.now()
        
        # 2. Real-Time Sync Logic
        # If the event is in the future, wait for real-time to catch up
        if next_timestamp > now:
            sleep_seconds = (next_timestamp - now).total_seconds()
            await asyncio.sleep(sleep_seconds)
            
        # 3. Pop and process the event
        timestamp, _, action_type, event_data = heapq.heappop(timeline)
        
        if action_type == 'rabbitmq_event':
            e_type = event_data.get('event_type')
            s_id = event_data.get('sector_id')
            
            print(f"[{timestamp}] EVENT EXECUTED: {e_type.upper()} in {s_id}")
            
            # Dictionary Routing (Clean and Modular!)
            handler = EVENT_HANDLERS.get(e_type)
            if handler:
                handler(resources, s_id)
            else:
                print(f"Warning: Unknown event type '{e_type}'")
                
        elif action_type == 'tick':
            for key, (val, slope) in resources.items():
                trend_direction = 1 if slope > 0 else (-1 if slope < 0 else 0)
                bias = 0.01 * trend_direction
                
                # Math fixes applied
                noise_val = slope * random.uniform(-0.5 + bias, 0.5 + bias)
                noise_slope = random.uniform(-0.1, 0.1)
                
                new_val = max(0.0, val + slope + noise_val)
                resources[key] = (new_val, slope + noise_slope)
                
            await save_to_postgres(timestamp, resources.copy())
            
            # 4. Schedule the NEXT tick continuously
            next_tick = timestamp + timedelta(minutes=TICK_INTERVAL_MINUTES)
            heapq.heappush(timeline, (next_tick, next(tiebreaker), 'tick', {}))

async def main():
    sim_start = datetime(2026, 1, 1, 0, 0)
    
    # Run the listener and processor concurrently
    await asyncio.gather(
        rabbitmq_listener(),  # live consumer
        process_continuous_timeline(sim_start)
    )

if __name__ == "__main__":
    asyncio.run(main())