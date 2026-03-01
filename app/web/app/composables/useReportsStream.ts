import type { Ref } from 'vue';

export interface StreamReport {
  id: string;
  heroAlias?: string;
  description?: string;
  timeStarted?: string;
  timestamp: number;
  affectedLocations?: string[];
  severity?: 'critical' | 'warning' | 'elevated' | 'normal';
}

export interface UseReportsStreamOptions {
  maxReports?: number;
  autoConnect?: boolean;
}

export function useReportsStream(options: UseReportsStreamOptions = {}) {
  const { maxReports = 50, autoConnect = true } = options;
  
  const reports: Ref<StreamReport[]> = ref([]);
  const isConnected = ref(false);
  const error = ref<Error | null>(null);
  const isLoading = ref(false);
  
  let eventSource: EventSource | null = null;

  function connect() {
    if (eventSource) return;
    
    isLoading.value = true;
    error.value = null;
    
    eventSource = new EventSource('/api/streams/reports');
    
    eventSource.onopen = () => {
      isConnected.value = true;
      isLoading.value = false;
    };
    
    eventSource.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data) as StreamReport;
        reports.value = [...reports.value, data].slice(-maxReports);
      } catch (e) {
        console.error('[Reports Stream] Failed to parse message:', e);
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
    reports.value = [];
  }
  
  if (autoConnect) {
    onMounted(connect);
    onUnmounted(disconnect);
  }
  
  return {
    reports,
    isConnected,
    error,
    isLoading,
    connect,
    disconnect,
    clear
  };
}

export function useLazyReportsStream(maxReports = 50) {
  const { data: initialReports, pending } = useFetch<{ reports: StreamReport[] }>('/api/reports', {
    default: () => ({ reports: [] })
  });
  
  const reports = ref<StreamReport[]>(initialReports.value?.reports || []);
  
  const stream = useReportsStream({ maxReports, autoConnect: false });
  
  watch(stream.reports, (newList) => {
    reports.value = newList;
  }, { deep: true });
  
  return {
    reports,
    isConnected: stream.isConnected,
    error: stream.error,
    isLoading: computed(() => pending.value || stream.isLoading.value),
    connect: stream.connect,
    disconnect: stream.disconnect
  };
}
