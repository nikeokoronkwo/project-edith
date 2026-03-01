<template>
  <div class="globe-panel">
    <div class="panel-header">
      <span class="panel-tag">GLOBAL RESOURCE MAP</span>
      <span class="panel-subtitle">LIVE // {{ regions.length }} SECTORS MONITORED</span>
    </div>

    <ClientOnly>
      <AppGlobe
        :regions="regions"
        :auto-rotate-speed="0.12"
        :height="globeHeight"
        :enable-zoom="true"
        @navigate="handleNavigate"
        @region-hover="handleRegionHover"
      />
      <template #fallback>
        <div class="globe-skeleton" :style="{ height: globeHeight + 'px' }" />
      </template>
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
import { useWindowSize } from '@vueuse/core'
import AppGlobe from './globe/AppGlobe.vue'
import type { GlobeRegion } from './globe/types'

const props = defineProps<{
  regions?: GlobeRegion[]
}>()

const emit = defineEmits<{
  (e: 'navigate', region: GlobeRegion): void
  (e: 'regionHover', region: GlobeRegion | null): void
}>()

const regions = computed(() => props.regions || [])

const { height: windowHeight } = useWindowSize()
const globeHeight = computed(() => Math.max(320, windowHeight.value - 195))

function handleNavigate(region: GlobeRegion) {
  emit('navigate', region)
}

function handleRegionHover(region: GlobeRegion | null) {
  emit('regionHover', region)
}
</script>

<style scoped>
.globe-panel {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  font-family: 'JetBrains Mono', monospace;
}

.panel-tag {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.14em;
  color: var(--primary);
}

.panel-subtitle {
  font-size: 8.5px;
  letter-spacing: 0.1em;
  color: var(--muted-foreground);
}

.globe-skeleton {
  flex: 1;
  background: var(--muted);
}
</style>
