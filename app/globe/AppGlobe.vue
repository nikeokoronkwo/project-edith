<template>
  <div
    ref="wrapperRef"
    class="globe-wrapper"
    @mousemove="onMouseMove"
    @mouseleave="onMouseLeave"
  >
    <!-- globe.gl renders here — SSR safe via v-if + ClientOnly equivalent -->
    <div ref="globeEl" class="globe-canvas" />

    <!-- Popup overlay: Vue-rendered, positioned by mouse coords -->
    <Transition name="popup-fade">
      <GlobeRegionPopup
        v-if="hoveredRegion"
        :region="hoveredRegion"
        :style="popupStyle"
        class="popup-overlay"
        @navigate="onNavigate"
      />
    </Transition>

    <!-- HUD: corner brackets -->
    <div class="hud-corner hud-tl" aria-hidden="true">
      <span class="hud-line hud-line-h" />
      <span class="hud-line hud-line-v" />
    </div>
    <div class="hud-corner hud-tr" aria-hidden="true">
      <span class="hud-line hud-line-h" />
      <span class="hud-line hud-line-v" />
    </div>
    <div class="hud-corner hud-bl" aria-hidden="true">
      <span class="hud-line hud-line-h" />
      <span class="hud-line hud-line-v" />
    </div>
    <div class="hud-corner hud-br" aria-hidden="true">
      <span class="hud-line hud-line-h" />
      <span class="hud-line hud-line-v" />
    </div>

    <!-- HUD: status strip -->
    <div class="hud-status" aria-live="polite">
      <span class="status-led" :class="{ active: globeReady }" />
      <span class="status-text">
        {{ globeReady ? `GLOBAL MONITOR ACTIVE // ${regions.length} SECTORS` : 'INITIALIZING…' }}
      </span>
      <span class="status-coords" v-if="hoveredRegion">
        {{ hoveredRegion.name.toUpperCase() }}
      </span>
    </div>

    <!-- HUD: legend -->
    <div class="hud-legend" aria-label="Severity legend">
      <div class="legend-item" v-for="lv in legendItems" :key="lv.label">
        <span class="legend-dot" :class="`sev-${lv.key}`" />
        <span class="legend-label">{{ lv.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { GlobeRegion } from './types'

// ── Types ─────────────────────────────────────────────────────────────────────
interface GeoFeature {
  properties: { ISO_A3: string; ADMIN: string }
  geometry: any
}

// ── Props ─────────────────────────────────────────────────────────────────────
const props = withDefaults(defineProps<{
  /** Highlighted regions from the API */
  regions?: GlobeRegion[]
  /** Slow auto-rotation speed (deg/frame). 0 = disabled */
  autoRotateSpeed?: number
  /** Height of the globe container in px */
  height?: number
}>(), {
  regions: () => [],
  autoRotateSpeed: 0.15,
  height: 480,
})

// ── Emits ─────────────────────────────────────────────────────────────────────
const emit = defineEmits<{
  (e: 'navigate', region: GlobeRegion): void
}>()

// ── Internal state ────────────────────────────────────────────────────────────
const wrapperRef   = ref<HTMLElement | null>(null)
const globeEl      = ref<HTMLElement | null>(null)
const globeReady   = ref(false)
const hoveredRegion = ref<GlobeRegion | null>(null)
const mousePos     = ref({ x: 0, y: 0 })

// Globe instance — typed loosely since globe.gl has no official TS defs
let globeInstance: any = null
let countries: GeoFeature[] = []

const router = useRouter()

// ── Legend ────────────────────────────────────────────────────────────────────
const legendItems = [
  { key: 'critical', label: 'CRITICAL' },
  { key: 'warning',  label: 'WARNING'  },
  { key: 'elevated', label: 'ELEVATED' },
  { key: 'normal',   label: 'NOMINAL'  },
]

// ── Popup positioning ─────────────────────────────────────────────────────────
const POPUP_W = 228
const POPUP_H = 260 // approximate

const popupStyle = computed(() => {
  if (!wrapperRef.value) return {}
  const rect = wrapperRef.value.getBoundingClientRect()
  const containerW = rect.width
  const containerH = rect.height

  let x = mousePos.value.x + 18
  let y = mousePos.value.y - 30

  // Clamp to container
  if (x + POPUP_W > containerW) x = mousePos.value.x - POPUP_W - 10
  if (y + POPUP_H > containerH) y = containerH - POPUP_H - 8
  if (y < 8) y = 8

  return {
    left: `${x}px`,
    top:  `${y}px`,
  }
})

// ── Mouse tracking ────────────────────────────────────────────────────────────
function onMouseMove(e: MouseEvent) {
  if (!wrapperRef.value) return
  const rect = wrapperRef.value.getBoundingClientRect()
  mousePos.value = {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top,
  }
}

function onMouseLeave() {
  hoveredRegion.value = null
}

// ── Region lookup ─────────────────────────────────────────────────────────────
function regionForFeature(feature: GeoFeature): GlobeRegion | undefined {
  const code = feature.properties.ISO_A3
  return props.regions.find(r => r.countryCode === code)
}

// ── Color helpers ─────────────────────────────────────────────────────────────
const SEVERITY_FILL: Record<string, string> = {
  critical: 'rgba(192, 57,  43,  0.35)',
  warning:  'rgba(230, 126, 34,  0.30)',
  elevated: 'rgba(241, 196, 15,  0.25)',
  normal:   'rgba(34,  197, 94,  0.20)',
}

const SEVERITY_STROKE: Record<string, string> = {
  critical: 'rgba(192, 57,  43,  0.8)',
  warning:  'rgba(230, 126, 34,  0.75)',
  elevated: 'rgba(241, 196, 15,  0.70)',
  normal:   'rgba(34,  197, 94,  0.65)',
}

function polyFill(feat: GeoFeature) {
  const r = regionForFeature(feat)
  return r ? SEVERITY_FILL[r.severity] ?? SEVERITY_FILL.normal : 'rgba(201, 162, 52, 0.04)'
}

function polyStroke(feat: GeoFeature) {
  const r = regionForFeature(feat)
  return r ? SEVERITY_STROKE[r.severity] ?? SEVERITY_STROKE.normal : 'rgba(201, 162, 52, 0.15)'
}

function polyAltitude(feat: GeoFeature) {
  const r = regionForFeature(feat)
  if (!r) return 0.001
  return r.severity === 'critical' ? 0.018 : r.severity === 'warning' ? 0.012 : 0.006
}

// ── Dot grid for dot-matrix surface ──────────────────────────────────────────
// Generates a lat/lng grid that globe.gl renders as tiny points,
// recreating the dot-matrix aesthetic from the reference screenshot.
function buildDotGrid(step = 2.5) {
  const pts: { lat: number; lng: number }[] = []
  for (let lat = -88; lat <= 88; lat += step) {
    // Adjust step per latitude to keep even spacing (approximate)
    const lngStep = step / Math.max(0.1, Math.cos((lat * Math.PI) / 180))
    for (let lng = -180; lng < 180; lng += lngStep) {
      pts.push({ lat, lng })
    }
  }
  return pts
}

// ── Globe init ────────────────────────────────────────────────────────────────
async function initGlobe() {
  if (!globeEl.value || typeof window === 'undefined') return

  // Dynamic import — keeps SSR safe
  const [{ default: Globe }, geoData] = await Promise.all([
    import('globe.gl'),
    fetch(
      'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson',
    ).then(r => r.json()),
  ])

  countries = geoData.features as GeoFeature[]

  const dotGrid = buildDotGrid(2.5)
  const width   = globeEl.value.clientWidth  || 600
  const height  = props.height

  globeInstance = Globe({ animateIn: false })(globeEl.value)
    .width(width)
    .height(height)
    // ── Globe appearance ──────────────────────────────────────────────────────
    .globeImageUrl(null as unknown as string) // no texture — pure dark globe
    .backgroundColor('rgba(0,0,0,0)')
    .showAtmosphere(true)
    .atmosphereColor('rgba(201, 162, 52, 0.18)')
    .atmosphereAltitude(0.15)
    // ── Dot grid layer (dot-matrix aesthetic) ─────────────────────────────────
    .pointsData(dotGrid)
    .pointLat('lat')
    .pointLng('lng')
    .pointAltitude(0.0)
    .pointRadius(0.18)          // tiny dots
    .pointColor(() => 'rgba(201, 162, 52, 0.20)')
    .pointsMerge(true)          // single merged mesh → fast
    // ── Country polygons layer ────────────────────────────────────────────────
    .polygonsData(countries)
    .polygonCapColor(polyFill)
    .polygonSideColor(() => 'rgba(0,0,0,0)')
    .polygonStrokeColor(polyStroke)
    .polygonAltitude(polyAltitude)
    .polygonLabel(() => '')     // we handle labels ourselves
    .onPolygonHover((feat: GeoFeature | null) => {
      hoveredRegion.value = feat ? (regionForFeature(feat) ?? null) : null
    })
    .onPolygonClick((feat: GeoFeature) => {
      const r = regionForFeature(feat)
      if (r) onNavigate(r)
    })

  // ── Globe material (dark surface) ─────────────────────────────────────────
  // Access Three.js scene to set globe mesh color
  const scene = globeInstance.scene?.()
  if (scene) {
    scene.traverse((obj: any) => {
      if (obj.isMesh && obj.geometry?.type === 'SphereGeometry') {
        obj.material.color.setHex(0x060810)
      }
    })
  }

  // ── Auto-rotation ─────────────────────────────────────────────────────────
  if (props.autoRotateSpeed > 0) {
    globeInstance.controls().autoRotate      = true
    globeInstance.controls().autoRotateSpeed = props.autoRotateSpeed
    globeInstance.controls().enableZoom      = false
    globeInstance.controls().enablePan       = false
  }

  // ── Initial camera ────────────────────────────────────────────────────────
  globeInstance.pointOfView({ lat: 20, lng: 10, altitude: 2.2 }, 0)

  globeReady.value = true
}

// ── Re-render polygons when regions prop changes ───────────────────────────────
watch(
  () => props.regions,
  () => {
    if (!globeInstance) return
    globeInstance
      .polygonCapColor(polyFill)
      .polygonStrokeColor(polyStroke)
      .polygonAltitude(polyAltitude)
  },
  { deep: true },
)

// ── Resize observer ───────────────────────────────────────────────────────────
let ro: ResizeObserver | null = null

// ── Navigate handler ─────────────────────────────────────────────────────────
function onNavigate(region: GlobeRegion) {
  emit('navigate', region)
  // Default: push to analytics sector route
  // Adjust the path pattern to match your Nuxt router setup
  const path = region.data?.sector
    ? `/analytics/sector/${encodeURIComponent(region.data.sector)}`
    : `/analytics/resource/${encodeURIComponent(region.countryCode)}`
  router.push(path).catch(() => {})
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────
onMounted(async () => {
  await nextTick()
  await initGlobe()

  // Responsive resize
  if (wrapperRef.value) {
    ro = new ResizeObserver(([entry]) => {
      if (globeInstance) {
        globeInstance.width(entry.contentRect.width)
      }
    })
    ro.observe(wrapperRef.value)
  }
})

onUnmounted(() => {
  ro?.disconnect()
  globeInstance?._destructor?.()
  globeInstance = null
})
</script>

<style scoped>
/* ── Tokens (mirror your app's CSS vars if already defined globally) ── */
.globe-wrapper {
  --gold:         #C9A234;
  --gold-dim:     rgba(201, 162, 52, 0.25);
  --bg:           #080a0e;
  --text-muted:   rgba(201, 162, 52, 0.45);
  --font-mono:    'JetBrains Mono', 'Fira Code', monospace;

  position: relative;
  width: 100%;
  height: v-bind('`${height}px`');
  background: var(--bg);
  border: 1px solid var(--gold-dim);
  border-radius: 6px;
  overflow: hidden;
  isolation: isolate;
}

/* ── Globe canvas ────────────────────────────────────────────────────────── */
.globe-canvas {
  width: 100%;
  height: 100%;
}

/* Ensure globe.gl canvas fills container */
.globe-canvas :deep(canvas) {
  display: block !important;
}

/* ── Popup overlay ───────────────────────────────────────────────────────── */
.popup-overlay {
  position: absolute;
  z-index: 20;
  pointer-events: none; /* CTA inside handles its own pointer-events */
}

/* ── HUD corners ─────────────────────────────────────────────────────────── */
.hud-corner {
  position: absolute;
  width: 16px;
  height: 16px;
  z-index: 10;
}

.hud-tl { top: 10px; left: 10px; }
.hud-tr { top: 10px; right: 10px; }
.hud-bl { bottom: 32px; left: 10px; }
.hud-br { bottom: 32px; right: 10px; }

.hud-line {
  position: absolute;
  background: rgba(201, 162, 52, 0.55);
}
.hud-line-h { width: 100%; height: 1.5px; top: 0; left: 0; }
.hud-line-v { width: 1.5px; height: 100%; top: 0; left: 0; }

.hud-tr .hud-line-h { left: auto; right: 0; }
.hud-tr .hud-line-v { left: auto; right: 0; }
.hud-bl .hud-line-h { top: auto; bottom: 0; }
.hud-br .hud-line-h { top: auto; bottom: 0; left: auto; right: 0; }
.hud-br .hud-line-v { left: auto; right: 0; top: auto; bottom: 0; }
.hud-bl .hud-line-v { top: auto; bottom: 0; }

/* ── HUD status strip ────────────────────────────────────────────────────── */
.hud-status {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 14px;
  background: rgba(8, 10, 14, 0.75);
  border-top: 1px solid var(--gold-dim);
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.12em;
  color: var(--text-muted);
  z-index: 10;
}

.status-led {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(201, 162, 52, 0.2);
  transition: background 0.3s, box-shadow 0.3s;
}

.status-led.active {
  background: #22c55e;
  box-shadow: 0 0 6px #22c55e;
  animation: blink 2.5s step-end infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.4; }
}

.status-text { flex: 1; }

.status-coords {
  color: var(--gold);
  font-weight: 700;
}

/* ── HUD legend ──────────────────────────────────────────────────────────── */
.hud-legend {
  position: absolute;
  top: 14px;
  right: 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  z-index: 10;
  background: rgba(8, 10, 14, 0.65);
  border: 1px solid var(--gold-dim);
  border-radius: 3px;
  padding: 6px 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.legend-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.sev-critical { background: #c0392b; box-shadow: 0 0 4px #c0392b; }
.sev-warning  { background: #e67e22; box-shadow: 0 0 4px #e67e22; }
.sev-elevated { background: #f1c40f; box-shadow: 0 0 4px #f1c40f; }
.sev-normal   { background: #22c55e; box-shadow: 0 0 4px #22c55e; }

.legend-label {
  font-family: var(--font-mono);
  font-size: 8px;
  letter-spacing: 0.1em;
  color: var(--text-muted);
}

/* ── Popup transition ────────────────────────────────────────────────────── */
.popup-fade-enter-active,
.popup-fade-leave-active {
  transition: opacity 0.12s ease, transform 0.12s ease;
}

.popup-fade-enter-from,
.popup-fade-leave-to {
  opacity: 0;
  transform: scale(0.96) translateY(4px);
}
</style>