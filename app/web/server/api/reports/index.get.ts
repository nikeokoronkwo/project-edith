import { z } from 'zod';

export type SeverityLevel = 'critical' | 'warning' | 'elevated' | 'normal';

export interface ReportSummary {
  id: string;
  heroAlias: string;
  description: string;
  timeStarted: string;
  timestamp?: number;
  affectedLocations: string[];        // textual locations reported by hero
  severity: SeverityLevel;           // mock severity for coloring
}

// simple mock list; in an actual app this would hit the external backend or database
const MOCK_REPORTS: ReportSummary[] = [
  {
    id: 'rpt-001',
    heroAlias: 'Night Shift',
    description: 'Sightings of multiple unidentified drones around Stark Industries. Recon recommended.',
    timeStarted: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    affectedLocations: ['Avengers Compound'],
    severity: 'warning',
  },
  {
    id: 'rpt-002',
    heroAlias: 'Silver Sentinel',
    description: 'Arc reactor leak reported in lower Manhattan; containment teams en route.',
    timeStarted: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
    affectedLocations: ['Avengers Compound'],
    severity: 'elevated',
  },
  {
    id: 'rpt-003',
    heroAlias: 'Ghostwalker',
    description: 'Unauthorized Wakandan tech shipment intercepted near Rotterdam port.',
    timeStarted: new Date(Date.now() - 1000 * 60 * 220).toISOString(),
    affectedLocations: ['Wakanda'],
    severity: 'normal',
  }
];

export default defineEventHandler(() => {
  return {
    reports: MOCK_REPORTS,
    total: MOCK_REPORTS.length,
    generated_at: new Date().toISOString()
  };
});
