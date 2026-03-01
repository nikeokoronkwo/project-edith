import { z } from 'zod';

export const reportSchema = z.object({
  heroAlias: z.string(),
  description: z.string(),
  affectedResources: z.array(z.string()),
  affectedLocations: z.array(z.string()),
  relatedReportIds: z.array(z.string()),
  timeStarted: z.string().datetime(),
  metadata: z.string(),
  // severity is optional on inbound reports (backend may compute/update later)
  severity: z.enum(['critical','warning','elevated','normal']).optional(),
});

export type Report = z.infer<typeof reportSchema>;

export const eventSchema = z.object({
  id: z.string(),
  event: z.string(),
  priority: z.number(),
  started: z.string(),
  timestamp: z.number().optional(),
  description: z.string().optional(),
  affectedResources: z.array(z.string()).optional(),
  affectedLocations: z.array(z.string()).optional(),
});

export type Event = z.infer<typeof eventSchema>;

export const analyticsDataSchema = z.object({
  timestamp: z.number(),
  resource: z.string(),
  sector: z.string(),
  value: z.number().optional(),
  country: z.string().optional(),
});

export type AnalyticsData = z.infer<typeof analyticsDataSchema>;

export const forecastSchema = z.object({
  resource: z.string(),
  sector: z.string().optional(),
  country: z.string().optional(),
  currentValue: z.number(),
  forecast: z.array(z.object({
    timestamp: z.number(),
    predicted: z.number(),
    lower: z.number().optional(),
    upper: z.number().optional(),
  })),
  description: z.string(),
  trend: z.enum(['increasing', 'decreasing', 'stable']),
  impact: z.enum(['high', 'medium', 'low']),
});

export type Forecast = z.infer<typeof forecastSchema>;

export const countryDataSchema = z.object({
  countryCode: z.string(),
  name: z.string(),
  coordinates: z.tuple([z.number(), z.number()]),
  resources: z.array(z.object({
    name: z.string(),
    value: z.number(),
    trend: z.enum(['up', 'down', 'stable']),
  })),
  events: z.number(),
});

export type CountryData = z.infer<typeof countryDataSchema>;

export const sectorAnalyticsSchema = z.object({
  sector: z.string(),
  resources: z.array(z.object({
    name: z.string(),
    totalValue: z.number(),
    recentTrend: z.array(z.object({
      timestamp: z.number(),
      value: z.number(),
    })),
  })),
  forecast: forecastSchema.optional(),
});

export type SectorAnalytics = z.infer<typeof sectorAnalyticsSchema>;

export const resourceAnalyticsSchema = z.object({
  resource: z.string(),
  byCountry: z.array(z.object({
    country: z.string(),
    value: z.number(),
    forecast: forecastSchema.optional(),
  })),
  totalValue: z.number(),
  trend: z.array(z.object({
    timestamp: z.number(),
    value: z.number(),
  })),
});

export type ResourceAnalytics = z.infer<typeof resourceAnalyticsSchema>;
