export interface StreamAnalyticsData {
  timestamp: number;
  resource: string;
  sector: string;
  value?: number;
  [key: string]: unknown;
}

export interface AnalyticsDataPoint extends StreamAnalyticsData {
  id: string;
}

export interface UseAnalyticsStreamOptions {
  maxDataPoints?: number;
  autoConnect?: boolean;
  resource?: string;
  sector?: string;
}

export function useAnalyticsStream(options: UseAnalyticsStreamOptions = {}) {
  const { 
    maxDataPoints = 200, 
    autoConnect = true,
    resource,
    sector 
  } = options;
  
  const data = ref<AnalyticsDataPoint[]>([]);
  const isConnected = ref(false);
  const error = ref<Error | null>(null);
  const isLoading = ref(false);
  
  let eventSource: EventSource | null = null;

  function connect() {
    if (eventSource) return;
    
    isLoading.value = true;
    error.value = null;
    
    let url = '/api/streams/analytics';
    const params = new URLSearchParams();
    if (resource) params.set('resource', resource);
    if (sector) params.set('sector', sector);
    if (params.toString()) url += `?${params.toString()}`;
    
    eventSource = new EventSource(url);
    
    eventSource.onopen = () => {
      isConnected.value = true;
      isLoading.value = false;
    };
    
    eventSource.onmessage = (event) => {
      try {
        const rawData = JSON.parse(event.data) as StreamAnalyticsData;
        
        if (resource && rawData.resource !== resource) return;
        if (sector && rawData.sector !== sector) return;
        
        const dataPoint: AnalyticsDataPoint = {
          ...rawData,
          id: `${rawData.timestamp}-${Math.random().toString(36).slice(2, 9)}`
        };
        
        data.value = [...data.value, dataPoint].slice(-maxDataPoints);
      } catch (e) {
        console.error('[Analytics Stream] Failed to parse message:', e);
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
    data.value = [];
  }
  
  function getDataByResource(resourceName: string) {
    return computed(() => 
      data.value.filter(d => d.resource === resourceName)
    );
  }
  
  function getDataBySector(sectorName: string) {
    return computed(() => 
      data.value.filter(d => d.sector === sectorName)
    );
  }
  
  function getLatestByResource(resourceName: string) {
    return computed(() => {
      const filtered = data.value.filter(d => d.resource === resourceName);
      return filtered[filtered.length - 1] || null;
    });
  }
  
  if (autoConnect) {
    onMounted(connect);
    onUnmounted(disconnect);
  }
  
  return {
    data,
    isConnected,
    error,
    isLoading,
    connect,
    disconnect,
    clear,
    getDataByResource,
    getDataBySector,
    getLatestByResource
  };
}

export function useLazyAnalyticsStream(maxDataPoints = 200) {
  const { data: initialData, pending } = useFetch<StreamAnalyticsData[]>('/api/analytics', {
    default: () => []
  });
  
  const data = ref<AnalyticsDataPoint[]>(
    (initialData.value || []).map((d, i) => ({
      ...d,
      id: `initial-${i}`
    }))
  );
  
  const stream = useAnalyticsStream({ 
    maxDataPoints,
    autoConnect: false 
  });
  
  watch(stream.data, (newData) => {
    data.value = newData;
  }, { deep: true });
  
  return {
    data,
    isConnected: stream.isConnected,
    error: stream.error,
    isLoading: computed(() => pending.value || stream.isLoading.value),
    connect: stream.connect,
    disconnect: stream.disconnect,
    getDataByResource: stream.getDataByResource,
    getDataBySector: stream.getDataBySector,
    getLatestByResource: stream.getLatestByResource
  };
}
