import type {
  Report,
  Event,
  AnalyticsData,
  Forecast,
  CountryData,
  SectorAnalytics,
  ResourceAnalytics,
} from './types';

export interface ApiClientOptions {
  baseUrl?: string;
  authToken?: string;
}

export class ExternalApiClient {
  private baseUrl: string;
  private authToken?: string;

  constructor(options: ApiClientOptions = {}) {
    this.baseUrl = options.baseUrl || '';
    this.authToken = options.authToken;
  }

  setAuthToken(token: string | undefined) {
    this.authToken = token;
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }
    return headers;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Request failed' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Reports
  async createReport(report: Omit<Report, 'metadata'> & { metadata: string }): Promise<{ success: boolean; reportId: string; message: string }> {
    return this.request('/api/reports', {
      method: 'POST',
      body: JSON.stringify(report),
    });
  }

  async getReport(reportId: string): Promise<Report> {
    return this.request(`/api/reports/${reportId}`);
  }

  async listReports(limit = 50, offset = 0): Promise<{ reports: Report[]; total: number }> {
    return this.request(`/api/reports?limit=${limit}&offset=${offset}`);
  }

  // Events
  async getEvents(priority?: number, limit = 50): Promise<{ events: Event[] }> {
    const params = new URLSearchParams();
    if (priority !== undefined) params.set('priority', String(priority));
    params.set('limit', String(limit));
    return this.request(`/api/events?${params}`);
  }

  async getEvent(eventId: string): Promise<Event> {
    return this.request(`/api/events/${eventId}`);
  }

  // Analytics
  async getAnalytics(resource?: string, sector?: string, limit = 200): Promise<{ data: AnalyticsData[] }> {
    const params = new URLSearchParams();
    if (resource) params.set('resource', resource);
    if (sector) params.set('sector', sector);
    params.set('limit', String(limit));
    return this.request(`/api/analytics?${params}`);
  }

  async getSectorAnalytics(sector: string): Promise<SectorAnalytics> {
    return this.request(`/api/analytics/sector/${sector}`);
  }

  async getResourceAnalytics(resource: string): Promise<ResourceAnalytics> {
    return this.request(`/api/analytics/resource/${resource}`);
  }

  async getForecast(resource: string, sector?: string, country?: string, days = 30): Promise<Forecast> {
    const params = new URLSearchParams({ resource, days: String(days) });
    if (sector) params.set('sector', sector);
    if (country) params.set('country', country);
    return this.request(`/api/analytics/forecast?${params}`);
  }

  // Globe
  async getCountryData(): Promise<{ countries: CountryData[] }> {
    return this.request('/api/globe/countries');
  }

  async getCountryDetails(countryCode: string): Promise<CountryData> {
    return this.request(`/api/globe/countries/${countryCode}`);
  }
}

let apiClient: ExternalApiClient | null = null;

export function getExternalApiClient(options: ApiClientOptions = {}): ExternalApiClient {
  if (!apiClient || options.baseUrl) {
    apiClient = new ExternalApiClient(options);
  }
  return apiClient;
}

export function createExternalApiClient(options: ApiClientOptions = {}): ExternalApiClient {
  return new ExternalApiClient(options);
}
