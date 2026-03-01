export interface PriorityEvent {
  id: string
  event: string
  priority: 1 | 2 | 3 | 4   // 1=CRITICAL, 2=HIGH, 3=MEDIUM, 4=LOW
  started: string
  summary: string
  locations: string[]
  resources: string[]
  tags: string[]
}

const MOCK_EVENTS: PriorityEvent[] = [
  {
    id: 'evt-001',
    event: 'Vibranium Supply Chain Collapse — Wakanda Border',
    priority: 1,
    started: new Date(Date.now() - 1000 * 60 * 18).toISOString(),
    summary: 'Armed incursion detected near Birnin Zana export corridor. All shipments suspended pending threat assessment.',
    locations: ['Wakanda', 'East Africa'],
    resources: ['vibranium', 'rare_metals'],
    tags: ['ARMED_CONFLICT', 'SUPPLY_DISRUPTION'],
  },
  {
    id: 'evt-002',
    event: 'Stark Energy Grid Interference — Eastern Seaboard',
    priority: 1,
    started: new Date(Date.now() - 1000 * 60 * 42).toISOString(),
    summary: 'Unexplained energy fluctuations consistent with arc reactor discharge. Seven grid nodes offline. Cause unknown.',
    locations: ['United States', 'New York'],
    resources: ['arc_fuel', 'energy_cells'],
    tags: ['GRID_FAILURE', 'ARC_REACTOR'],
  },
  {
    id: 'evt-003',
    event: 'Unauthorized Serum Synthesis — Budapest Lab Network',
    priority: 2,
    started: new Date(Date.now() - 1000 * 60 * 95).toISOString(),
    summary: 'Black market super-serum precursors intercepted at three locations. Laboratory network traced to former Hydra operatives.',
    locations: ['Hungary', 'Slovakia', 'Romania'],
    resources: ['serum', 'medical'],
    tags: ['HYDRA', 'BIOSYNTHESIS'],
  },
  {
    id: 'evt-004',
    event: 'Helicarrier Fuel Reserve Drop — Atlantic Station',
    priority: 2,
    started: new Date(Date.now() - 1000 * 60 * 140).toISOString(),
    summary: 'Helium-3 reserves at 23% capacity. Supply convoy delayed due to North Atlantic weather disruption.',
    locations: ['North Atlantic'],
    resources: ['arc_fuel', 'propulsion'],
    tags: ['SHIELD_FLEET', 'LOW_FUEL'],
  },
  {
    id: 'evt-005',
    event: 'Medical Nanite Production Slowdown — Mumbai',
    priority: 3,
    started: new Date(Date.now() - 1000 * 60 * 220).toISOString(),
    summary: 'Facility strike action reduces nanite output by 34%. Current stockpiles project to cover 18 days at operational rate.',
    locations: ['India', 'Mumbai'],
    resources: ['medical', 'nanites'],
    tags: ['LABOR', 'PRODUCTION_DELAY'],
  },
  {
    id: 'evt-006',
    event: 'Pym Particle Export Quota Exceeded — Geneva',
    priority: 3,
    started: new Date(Date.now() - 1000 * 60 * 310).toISOString(),
    summary: 'UN treaty quota on Pym particle compounds exceeded by 12%. Regulatory review initiated by Swiss authorities.',
    locations: ['Switzerland', 'Geneva'],
    resources: ['pym_particles'],
    tags: ['REGULATORY', 'TREATY_BREACH'],
  },
  {
    id: 'evt-007',
    event: 'Asgardian Alloy Tariff Review — Oslo Port',
    priority: 4,
    started: new Date(Date.now() - 1000 * 60 * 480).toISOString(),
    summary: 'Norwegian parliament tabled motion to reclassify uru alloy under strategic materials act. Quarterly review expected.',
    locations: ['Norway', 'Oslo'],
    resources: ['uru_alloy', 'rare_metals'],
    tags: ['TRADE_POLICY', 'ASGARDIAN'],
  },
  {
    id: 'evt-008',
    event: 'Quantum Realm Navigation Data Leak Patch',
    priority: 4,
    started: new Date(Date.now() - 1000 * 60 * 600).toISOString(),
    summary: 'Routine security patch applied to classified quantum navigation archives. No confirmed exfiltration detected.',
    locations: ['United States', 'San Francisco'],
    resources: ['quantum_data'],
    tags: ['SECURITY', 'PATCH'],
  },
]

export default defineEventHandler(async () => {
  return {
    events: MOCK_EVENTS,
    generated_at: new Date().toISOString(),
  }
})
