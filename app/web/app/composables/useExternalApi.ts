import type { Event } from '#shared/types';
import { createExternalApiClient, type ApiClientOptions } from '#shared/api-client';

export function useExternalApi(options: ApiClientOptions = {}) {
  const config = useRuntimeConfig();
  const baseUrl = options.baseUrl || config.externalBackendUrl;
  
  const client = createExternalApiClient({
    baseUrl,
    authToken: options.authToken
  });

  return client;
}

export function useEventsApi() {
  const client = useExternalApi();

  async function getEvents(priority?: number, limit = 50) {
    try {
      return await client.getEvents(priority, limit);
    } catch (e) {
      console.error('[useEventsApi] Failed to fetch events:', e);
      return { events: [] as Event[] };
    }
  }

  async function getEvent(eventId: string) {
    try {
      return await client.getEvent(eventId);
    } catch (e) {
      console.error('[useEventsApi] Failed to fetch event:', e);
      return null;
    }
  }

  return {
    getEvents,
    getEvent
  };
}

export function useReportsApi() {
  const client = useExternalApi();

  async function getReports(limit = 50, offset = 0) {
    try {
      return await client.listReports(limit, offset);
    } catch (e) {
      console.error('[useReportsApi] Failed to fetch reports:', e);
      return { reports: [], total: 0 };
    }
  }

  async function getReport(reportId: string) {
    try {
      return await client.getReport(reportId);
    } catch (e) {
      console.error('[useReportsApi] Failed to fetch report:', e);
      return null;
    }
  }

  return {
    getReports,
    getReport
  };
}

export function useAnalyticsApi() {
  const client = useExternalApi();

  async function getAnalytics(resource?: string, sector?: string, limit = 200) {
    try {
      return await client.getAnalytics(resource, sector, limit);
    } catch (e) {
      console.error('[useAnalyticsApi] Failed to fetch analytics:', e);
      return { data: [] };
    }
  }

  async function getSectorAnalytics(sector: string) {
    try {
      return await client.getSectorAnalytics(sector);
    } catch (e) {
      console.error('[useAnalyticsApi] Failed to fetch sector analytics:', e);
      return null;
    }
  }

  async function getResourceAnalytics(resource: string) {
    try {
      return await client.getResourceAnalytics(resource);
    } catch (e) {
      console.error('[useAnalyticsApi] Failed to fetch resource analytics:', e);
      return null;
    }
  }

  async function getForecast(resource: string, sector?: string, country?: string, days = 30) {
    try {
      return await client.getForecast(resource, sector, country, days);
    } catch (e) {
      console.error('[useAnalyticsApi] Failed to fetch forecast:', e);
      return null;
    }
  }

  return {
    getAnalytics,
    getSectorAnalytics,
    getResourceAnalytics,
    getForecast
  };
}

export function useGlobeApi() {
  const client = useExternalApi();

  async function getCountryData() {
    try {
      return await client.getCountryData();
    } catch (e) {
      console.error('[useGlobeApi] Failed to fetch country data:', e);
      return { countries: [] };
    }
  }

  async function getCountryDetails(countryCode: string) {
    try {
      return await client.getCountryDetails(countryCode);
    } catch (e) {
      console.error('[useGlobeApi] Failed to fetch country details:', e);
      return null;
    }
  }

  return {
    getCountryData,
    getCountryDetails
  };
}
