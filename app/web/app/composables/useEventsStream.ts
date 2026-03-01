import type { Ref } from 'vue';

export interface StreamEvent {
  id: string;
  event: string;
  priority: number;
  started: string;
  timestamp: number;
}

export interface UseEventsStreamOptions {
  maxEvents?: number;
  autoConnect?: boolean;
}

export function useEventsStream(options: UseEventsStreamOptions = {}) {
  const { maxEvents = 50, autoConnect = true } = options;
  
  const events = ref<StreamEvent[]>([]);
  const isConnected = ref(false);
  const error = ref<Error | null>(null);
  const isLoading = ref(false);
  
  let eventSource: EventSource | null = null;

  function connect() {
    if (eventSource) return;
    
    isLoading.value = true;
    error.value = null;
    
    eventSource = new EventSource('/api/streams/events');
    
    eventSource.onopen = () => {
      isConnected.value = true;
      isLoading.value = false;
    };
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as StreamEvent;
        events.value = [...events.value, data].slice(-maxEvents);
      } catch (e) {
        console.error('[Events Stream] Failed to parse message:', e);
      }
    };
    
    eventSource.onerror = (e) => {
      error.value = new Error('Connection lost');
      isConnected.value = false;
      isLoading.value = false;
      disconnect();
      setTimeout(connect, 5000);
    };
  }
  
  function disconnect() {
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
    isConnected.value = false;
  }
  
  function clear() {
    events.value = [];
  }
  
  if (autoConnect) {
    onMounted(connect);
    onUnmounted(disconnect);
  }
  
  return {
    events,
    isConnected,
    error,
    isLoading,
    connect,
    disconnect,
    clear
  };
}

export function useLazyEventsStream(maxEvents = 50) {
  const { data: initialData, pending } = useFetch<{ events: StreamEvent[] }>('/api/events', {
    default: () => ({ events: [] })
  });
  
  const events = ref<StreamEvent[]>(initialData.value?.events || []);
  
  const stream = useEventsStream({ 
    maxEvents,
    autoConnect: false 
  });
  
  watch(stream.events, (newEvents) => {
    events.value = newEvents;
  }, { deep: true });
  
  return {
    events,
    isConnected: stream.isConnected,
    error: stream.error,
    isLoading: computed(() => pending.value || stream.isLoading.value),
    connect: stream.connect,
    disconnect: stream.disconnect
  };
}
