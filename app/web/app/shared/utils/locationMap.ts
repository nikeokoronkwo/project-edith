// Mapping of common Avengers-related locations to ISO_A3 country codes
// Fictional places are approximated to real countries for the globe.
export const AVENGERS_LOCATION_ISO: Record<string, string> = {
  'Avengers Compound': 'USA',       // base of operations roughly in New York
  'Stark Tower': 'USA',
  'Wakanda': 'USA',                 // Wakanda doesn't exist; use USA as placeholder
  'Sokovia': 'SVK',                 // Slovakia approximates Sokovia (in MCU)
  'New Asgard': 'NOR',              // Norway
  'Asgard': 'NOR',
  'Latveria': 'ROU',                // Romania-like
  'Sanctum Sanctorum': 'USA',       // New York
  'Baker Street': 'GBR',            // London Sherlock? fallback
  'East Africa': 'KEN',
  'Rotterdam': 'NLD',
  'Manhattan': 'USA',
  'Lower Manhattan': 'USA',
  // add more known aliases here
};

// If a location string doesn't match exactly, this helper will attempt a case-insensitive lookup
export function lookupIso(location: string): string | undefined {
  if (!location) return undefined;
  const exact = AVENGERS_LOCATION_ISO[location];
  if (exact) return exact;
  const key = Object.keys(AVENGERS_LOCATION_ISO).find(k => k.toLowerCase() === location.toLowerCase());
  if (key) return AVENGERS_LOCATION_ISO[key];
  return undefined;
}
