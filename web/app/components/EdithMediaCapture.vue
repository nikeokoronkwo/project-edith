<template>
  <div v-if="modelValue" class="media-capture-modal">
    <div class="overlay" @click="close" />
    <div class="capture-box">
      <video ref="videoRef" autoplay playsinline muted class="preview" />
      <div class="controls">
        <button @click="stopCapture">Stop</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'

const props = withDefaults(defineProps<{ modelValue: boolean }>(), { modelValue: false })
const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void; (e: 'captured', url: string): void }>()

const videoRef = ref<HTMLVideoElement | null>(null)
let mediaStream: MediaStream | null = null

async function startCapture() {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    if (videoRef.value) videoRef.value.srcObject = mediaStream
  } catch (e) {
    console.error('capture failed', e)
    close()
  }
}

function stopCapture() {
  if (mediaStream) {
    mediaStream.getTracks().forEach(t => t.stop())
    mediaStream = null
  }
  // TODO: upload blob
  emit('captured', 'https://example.com/media/placeholder')
  close()
}

function close() {
  emit('update:modelValue', false)
}

watch(() => props.modelValue, (v) => {
  if (v) startCapture()
  else stopCapture()
})

onUnmounted(() => {
  stopCapture()
})
</script>

<style scoped>
.media-capture-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
}
.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.6);
}
.capture-box {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: var(--card);
  padding: 12px;
  border-radius: var(--radius);
}
.preview {
  width: 320px;
  max-width: 80vw;
  border: 1px solid var(--border);
}
.controls {
  margin-top: 8px;
  text-align: center;
}
</style>