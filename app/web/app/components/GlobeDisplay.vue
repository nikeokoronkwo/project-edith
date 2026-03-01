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
        :height="460"
        :enable-zoom="true"
        @navigate="handleNavigate"
        @region-hover="handleRegionHover"
      >
        <!-- Custom popup slot example (optional) -->
        <!-- <template #popup="{ region, navigate }">
          Your custom popup component here
          <div class="custom-popup">
            <h3>{{ region.name }}</h3>
            <button @click="navigate(region)">View</button>
          </div>
        </template> -->
      </AppGlobe>
      <template #fallback>
        <div class="globe-skeleton" style="height: 460px" />
      </template>
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
import AppGlobe from './globe/AppGlobe.vue'
import type { GlobeRegion } from './globe/types'

const props = defineProps<{
  /** Regions/sectors data from backend API */
  regions?: GlobeRegion[]
}>()

const emit = defineEmits<{
  (e: 'navigate', region: GlobeRegion): void
  (e: 'regionHover', region: GlobeRegion | null): void
}>()

const regions = computed(() => props.regions || [])

function handleNavigate(region: GlobeRegion) {
  emit('navigate', region)
}

function handleRegionHover(region: GlobeRegion | null) {
  emit('regionHover', region)
}
</script>

<style scoped>
.globe-panel {
  background: #080a0e;
  border: 1px solid rgba(201, 162, 52, 0.2);
  border-radius: 6px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding: 10px 16px;
  border-bottom: 1px solid rgba(201, 162, 52, 0.12);
  font-family: 'JetBrains Mono', monospace;
}

.panel-tag {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.14em;
  color: #C9A234;
}

.panel-subtitle {
  font-size: 8.5px;
  letter-spacing: 0.1em;
  color: rgba(201, 162, 52, 0.4);
}

.globe-skeleton {
  background: repeating-linear-gradient(
    90deg,
    rgba(201, 162, 52, 0.03) 0px,
    rgba(201, 162, 52, 0.03) 1px,
    transparent 1px,
    transparent 24px
  ),
  repeating-linear-gradient(
    180deg,
    rgba(201, 162, 52, 0.03) 0px,
    rgba(201, 162, 52, 0.03) 1px,
    transparent 1px,
    transparent 24px
  );
}
</style>
