// Mapping of location names → ISO_A3 country codes (used by the globe layer)
// Covers MCU/Avengers fictional places, real country names, and major cities.
export const LOCATION_ISO_MAP: Record<string, string> = {
  // ── MCU / Avengers fictional locations ──────────────────────────────────────
  'Avengers Compound':   'USA',
  'Avengers Tower':      'USA',
  'Stark Tower':         'USA',
  'Stark Industries':    'USA',
  'SHIELD Helicarrier':  'USA',
  'SHIELD HQ':           'USA',
  'Wakanda':             'COD',   // approximate: DR Congo region
  'Birnin Zana':         'COD',
  'Sokovia':             'SVK',   // Slovakia approximates Sokovia
  'New Asgard':          'NOR',
  'Asgard':              'NOR',
  'Latveria':            'ROU',
  'Sanctum Sanctorum':   'USA',
  'Kamar-Taj':           'NPL',   // Nepal
  'Knowhere':            'USA',   // deep space — fallback to USA
  'Sakaar':              'USA',
  'Xandar':              'USA',
  'Nidavellir':          'NOR',
  'Vormir':              'USA',
  'Titan':               'USA',
  'Genosha':             'ZAF',   // South Africa region
  'Madripoor':           'SGP',   // Singapore-like
  'Trans-Sabalian':      'RUS',
  'Transia':             'BGR',   // Bulgaria-like

  // ── Real country names ───────────────────────────────────────────────────────
  'United States':       'USA',
  'United States of America': 'USA',
  'USA':                 'USA',
  'US':                  'USA',
  'United Kingdom':      'GBR',
  'UK':                  'GBR',
  'Britain':             'GBR',
  'England':             'GBR',
  'France':              'FRA',
  'Germany':             'DEU',
  'Russia':              'RUS',
  'China':               'CHN',
  'Japan':               'JPN',
  'India':               'IND',
  'Brazil':              'BRA',
  'Canada':              'CAN',
  'Australia':           'AUS',
  'Italy':               'ITA',
  'Spain':               'ESP',
  'South Korea':         'KOR',
  'Mexico':              'MEX',
  'Indonesia':           'IDN',
  'Netherlands':         'NLD',
  'Saudi Arabia':        'SAU',
  'Turkey':              'TUR',
  'Switzerland':         'CHE',
  'Sweden':              'SWE',
  'Norway':              'NOR',
  'Denmark':             'DNK',
  'Finland':             'FIN',
  'Poland':              'POL',
  'Czech Republic':      'CZE',
  'Czechia':             'CZE',
  'Slovakia':            'SVK',
  'Austria':             'AUT',
  'Belgium':             'BEL',
  'Portugal':            'PRT',
  'Greece':              'GRC',
  'Romania':             'ROU',
  'Hungary':             'HUN',
  'Bulgaria':            'BGR',
  'Ukraine':             'UKR',
  'Nigeria':             'NGA',
  'South Africa':        'ZAF',
  'Kenya':               'KEN',
  'Egypt':               'EGY',
  'Ethiopia':            'ETH',
  'Ghana':               'GHA',
  'Tanzania':            'TZA',
  'Uganda':              'UGA',
  'Morocco':             'MAR',
  'Algeria':             'DZA',
  'Israel':              'ISR',
  'Iran':                'IRN',
  'Iraq':                'IRQ',
  'Pakistan':            'PAK',
  'Bangladesh':          'BGD',
  'Vietnam':             'VNM',
  'Thailand':            'THA',
  'Malaysia':            'MYS',
  'Philippines':         'PHL',
  'Singapore':           'SGP',
  'Argentina':           'ARG',
  'Colombia':            'COL',
  'Chile':               'CHL',
  'Peru':                'PER',
  'Venezuela':           'VEN',
  'New Zealand':         'NZL',

  // ── Major cities → country ───────────────────────────────────────────────────
  'New York':            'USA',
  'Manhattan':           'USA',
  'Lower Manhattan':     'USA',
  'Brooklyn':            'USA',
  'Queens':              'USA',
  'Los Angeles':         'USA',
  'Chicago':             'USA',
  'Washington':          'USA',
  'Washington D.C.':     'USA',
  'Washington DC':       'USA',
  'Houston':             'USA',
  'San Francisco':       'USA',
  'Boston':              'USA',
  'Miami':               'USA',
  'Seattle':             'USA',
  'Las Vegas':           'USA',
  'London':              'GBR',
  'Baker Street':        'GBR',
  'Paris':               'FRA',
  'Berlin':              'DEU',
  'Munich':              'DEU',
  'Moscow':              'RUS',
  'Tokyo':               'JPN',
  'Osaka':               'JPN',
  'Beijing':             'CHN',
  'Shanghai':            'CHN',
  'Hong Kong':           'CHN',
  'Mumbai':              'IND',
  'Delhi':               'IND',
  'Sydney':              'AUS',
  'Melbourne':           'AUS',
  'Toronto':             'CAN',
  'Vancouver':           'CAN',
  'São Paulo':           'BRA',
  'Rio de Janeiro':      'BRA',
  'Amsterdam':           'NLD',
  'Rotterdam':           'NLD',
  'Brussels':            'BEL',
  'Vienna':              'AUT',
  'Zurich':              'CHE',
  'Geneva':              'CHE',
  'Stockholm':           'SWE',
  'Oslo':                'NOR',
  'Copenhagen':          'DNK',
  'Helsinki':            'FIN',
  'Warsaw':              'POL',
  'Prague':              'CZE',
  'Bratislava':          'SVK',
  'Budapest':            'HUN',
  'Bucharest':           'ROU',
  'Sofia':               'BGR',
  'Athens':              'GRC',
  'Rome':                'ITA',
  'Madrid':              'ESP',
  'Barcelona':           'ESP',
  'Lisbon':              'PRT',
  'Cairo':               'EGY',
  'Lagos':               'NGA',
  'Johannesburg':        'ZAF',
  'Cape Town':           'ZAF',
  'Nairobi':             'KEN',
  'Addis Ababa':         'ETH',
  'Seoul':               'KOR',
  'Singapore':           'SGP',
  'Dubai':               'ARE',
  'Tel Aviv':            'ISR',
  'Tehran':              'IRN',
  'Baghdad':             'IRQ',
  'Karachi':             'PAK',
  'Dhaka':               'BGD',
  'Hanoi':               'VNM',
  'Bangkok':             'THA',
  'Kuala Lumpur':        'MYS',
  'Manila':              'PHL',
  'Jakarta':             'IDN',
  'Buenos Aires':        'ARG',
  'Bogotá':              'COL',
  'Santiago':            'CHL',
  'Lima':                'PER',
  'Auckland':            'NZL',

  // ── World regions (approximate to dominant/representative country) ───────────
  'East Africa':         'KEN',
  'West Africa':         'NGA',
  'North Africa':        'EGY',
  'Sub-Saharan Africa':  'NGA',
  'Middle East':         'SAU',
  'South Asia':          'IND',
  'Southeast Asia':      'SGP',
  'East Asia':           'CHN',
  'Central Asia':        'KAZ',
  'Eastern Europe':      'POL',
  'Western Europe':      'DEU',
  'Northern Europe':     'SWE',
  'Southern Europe':     'ITA',
  'North America':       'USA',
  'South America':       'BRA',
  'Latin America':       'MEX',
  'Caribbean':           'CUB',
  'Oceania':             'AUS',
  'Central America':     'GTM',
}

/**
 * Look up an ISO_A3 country code from a location string.
 * Handles: exact name matches, case-insensitive matches, direct ISO_A3 passthrough,
 * and ISO_A2 → ISO_A3 conversion.
 */
export function lookupIso(location: string): string | undefined {
  if (!location) return undefined

  // Exact match (fastest path)
  const exact = LOCATION_ISO_MAP[location]
  if (exact) return exact

  // Case-insensitive match
  const lower = location.toLowerCase()
  const key   = Object.keys(LOCATION_ISO_MAP).find(k => k.toLowerCase() === lower)
  if (key) return LOCATION_ISO_MAP[key]

  // Direct ISO_A3 passthrough (3 uppercase letters already a valid-looking code)
  if (/^[A-Z]{3}$/.test(location)) return location

  // ISO_A2 → ISO_A3 via a small lookup table for common cases
  const A2_TO_A3: Record<string, string> = {
    US: 'USA', GB: 'GBR', FR: 'FRA', DE: 'DEU', JP: 'JPN', CN: 'CHN',
    IN: 'IND', BR: 'BRA', CA: 'CAN', AU: 'AUS', RU: 'RUS', IT: 'ITA',
    ES: 'ESP', KR: 'KOR', MX: 'MEX', ID: 'IDN', NL: 'NLD', SA: 'SAU',
    TR: 'TUR', CH: 'CHE', SE: 'SWE', NO: 'NOR', DK: 'DNK', FI: 'FIN',
    PL: 'POL', CZ: 'CZE', SK: 'SVK', AT: 'AUT', BE: 'BEL', PT: 'PRT',
    GR: 'GRC', RO: 'ROU', HU: 'HUN', BG: 'BGR', UA: 'UKR', NG: 'NGA',
    ZA: 'ZAF', KE: 'KEN', EG: 'EGY', ET: 'ETH', IL: 'ISR', IR: 'IRN',
    IQ: 'IRQ', PK: 'PAK', BD: 'BGD', VN: 'VNM', TH: 'THA', MY: 'MYS',
    PH: 'PHL', SG: 'SGP', AR: 'ARG', CO: 'COL', CL: 'CHL', PE: 'PER',
    NZ: 'NZL', NG: 'NGA', AE: 'ARE',
  }
  const a2 = location.toUpperCase().slice(0, 2)
  if (/^[A-Z]{2}$/.test(a2) && A2_TO_A3[a2]) return A2_TO_A3[a2]

  return undefined
}

// Keep legacy export for backward compatibility
export const AVENGERS_LOCATION_ISO = LOCATION_ISO_MAP

// ── ISO_A3 → Analytics Sector mapping ────────────────────────────────────────
// Sectors: NORTH_AMERICA | EUROPE | EURASIA | SOUTH_ASIA | WEST_AFRICA
export const ISO_TO_SECTOR: Record<string, string> = {
  // NORTH_AMERICA
  USA: 'NORTH_AMERICA', CAN: 'NORTH_AMERICA', MEX: 'NORTH_AMERICA',
  GTM: 'NORTH_AMERICA', CUB: 'NORTH_AMERICA', BLZ: 'NORTH_AMERICA',
  HND: 'NORTH_AMERICA', SLV: 'NORTH_AMERICA', NIC: 'NORTH_AMERICA',
  CRI: 'NORTH_AMERICA', PAN: 'NORTH_AMERICA', JAM: 'NORTH_AMERICA',
  HTI: 'NORTH_AMERICA', DOM: 'NORTH_AMERICA', PRI: 'NORTH_AMERICA',
  // South America → NORTH_AMERICA (no dedicated SA sector)
  BRA: 'NORTH_AMERICA', ARG: 'NORTH_AMERICA', COL: 'NORTH_AMERICA',
  CHL: 'NORTH_AMERICA', PER: 'NORTH_AMERICA', VEN: 'NORTH_AMERICA',
  ECU: 'NORTH_AMERICA', BOL: 'NORTH_AMERICA', PRY: 'NORTH_AMERICA',
  URY: 'NORTH_AMERICA', GUY: 'NORTH_AMERICA', SUR: 'NORTH_AMERICA',

  // EUROPE
  GBR: 'EUROPE', FRA: 'EUROPE', DEU: 'EUROPE', ITA: 'EUROPE', ESP: 'EUROPE',
  NLD: 'EUROPE', BEL: 'EUROPE', CHE: 'EUROPE', AUT: 'EUROPE', SWE: 'EUROPE',
  NOR: 'EUROPE', DNK: 'EUROPE', FIN: 'EUROPE', POL: 'EUROPE', CZE: 'EUROPE',
  SVK: 'EUROPE', HUN: 'EUROPE', ROU: 'EUROPE', BGR: 'EUROPE', GRC: 'EUROPE',
  PRT: 'EUROPE', UKR: 'EUROPE', ISR: 'EUROPE', TUR: 'EUROPE', ARE: 'EUROPE',
  SAU: 'EUROPE', IRN: 'EUROPE', IRQ: 'EUROPE', SYR: 'EUROPE', JOR: 'EUROPE',
  LBN: 'EUROPE', HRV: 'EUROPE', SRB: 'EUROPE', BIH: 'EUROPE', MKD: 'EUROPE',
  MNE: 'EUROPE', ALB: 'EUROPE', LTU: 'EUROPE', LVA: 'EUROPE', EST: 'EUROPE',
  SVN: 'EUROPE', LUX: 'EUROPE', MLT: 'EUROPE', CYP: 'EUROPE',

  // EURASIA
  RUS: 'EURASIA', CHN: 'EURASIA', JPN: 'EURASIA', KOR: 'EURASIA',
  VNM: 'EURASIA', THA: 'EURASIA', MYS: 'EURASIA', PHL: 'EURASIA',
  IDN: 'EURASIA', SGP: 'EURASIA', AUS: 'EURASIA', NZL: 'EURASIA',
  KAZ: 'EURASIA', MNG: 'EURASIA', PRK: 'EURASIA', TWN: 'EURASIA',
  HKG: 'EURASIA', MAC: 'EURASIA', MMR: 'EURASIA', KHM: 'EURASIA',
  LAO: 'EURASIA', BRN: 'EURASIA', TLS: 'EURASIA', PNG: 'EURASIA',
  UZB: 'EURASIA', TKM: 'EURASIA', KGZ: 'EURASIA', TJK: 'EURASIA',
  AFG: 'EURASIA', AZE: 'EURASIA', GEO: 'EURASIA', ARM: 'EURASIA',

  // SOUTH_ASIA
  IND: 'SOUTH_ASIA', PAK: 'SOUTH_ASIA', BGD: 'SOUTH_ASIA',
  NPL: 'SOUTH_ASIA', LKA: 'SOUTH_ASIA', BTN: 'SOUTH_ASIA', MDV: 'SOUTH_ASIA',

  // WEST_AFRICA (covers all Africa)
  NGA: 'WEST_AFRICA', GHA: 'WEST_AFRICA', KEN: 'WEST_AFRICA', ZAF: 'WEST_AFRICA',
  EGY: 'WEST_AFRICA', ETH: 'WEST_AFRICA', TZA: 'WEST_AFRICA', UGA: 'WEST_AFRICA',
  MAR: 'WEST_AFRICA', DZA: 'WEST_AFRICA', COD: 'WEST_AFRICA', AGO: 'WEST_AFRICA',
  MOZ: 'WEST_AFRICA', MDG: 'WEST_AFRICA', CMR: 'WEST_AFRICA', CIV: 'WEST_AFRICA',
  NER: 'WEST_AFRICA', BFA: 'WEST_AFRICA', MLI: 'WEST_AFRICA', MWI: 'WEST_AFRICA',
  ZMB: 'WEST_AFRICA', SEN: 'WEST_AFRICA', SOM: 'WEST_AFRICA', ZWE: 'WEST_AFRICA',
  GIN: 'WEST_AFRICA', RWA: 'WEST_AFRICA', BEN: 'WEST_AFRICA', BDI: 'WEST_AFRICA',
  TUN: 'WEST_AFRICA', LBY: 'WEST_AFRICA', SDN: 'WEST_AFRICA', SSD: 'WEST_AFRICA',
  TCD: 'WEST_AFRICA', CAF: 'WEST_AFRICA', COG: 'WEST_AFRICA', GAB: 'WEST_AFRICA',
  GNQ: 'WEST_AFRICA', SLE: 'WEST_AFRICA', LBR: 'WEST_AFRICA', TGO: 'WEST_AFRICA',
  MRT: 'WEST_AFRICA', NAM: 'WEST_AFRICA', BWA: 'WEST_AFRICA', LSO: 'WEST_AFRICA',
  SWZ: 'WEST_AFRICA', ERI: 'WEST_AFRICA', DJI: 'WEST_AFRICA', GMB: 'WEST_AFRICA',
}
