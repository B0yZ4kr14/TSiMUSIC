<template>
  <div class="audio-visualizer">
    <canvas ref="canvas" />
  </div>
</template>

<script setup lang="ts">
import { store } from "@/plugins/store";
import { PlaybackState } from "@/plugins/api/interfaces";
import { onMounted, onBeforeUnmount, ref, watch } from "vue";

const canvas = ref<HTMLCanvasElement | null>(null);
let animationId = 0;
const BAR_COUNT = 64;
const SMOOTHING = 0.15;
const targetValues = new Array(BAR_COUNT).fill(0.05);
const currentValues = new Array(BAR_COUNT).fill(0.05);

const isPlaying = () => store.activePlayer?.playback_state === PlaybackState.PLAYING;

const draw = () => {
  const c = canvas.value;
  if (!c) return;
  const ctx = c.getContext("2d");
  if (!ctx) return;

  const dpr = window.devicePixelRatio || 1;
  const rect = c.getBoundingClientRect();

  // Resize canvas to match display size with DPR
  if (c.width !== Math.floor(rect.width * dpr) || c.height !== Math.floor(rect.height * dpr)) {
    c.width = Math.floor(rect.width * dpr);
    c.height = Math.floor(rect.height * dpr);
  }

  const w = c.width;
  const h = c.height;

  ctx.clearRect(0, 0, w, h);

  const barWidth = w / BAR_COUNT;
  const gap = Math.max(1, barWidth * 0.25);
  const drawWidth = barWidth - gap;

  const time = Date.now() * 0.003;

  for (let i = 0; i < BAR_COUNT; i++) {
    const t = i / (BAR_COUNT - 1);

    if (isPlaying()) {
      // Organic simulation using multiple sine waves + random noise
      const noise =
        Math.sin(time + i * 0.2) *
        Math.cos(time * 0.7 + i * 0.1) *
        (0.5 + 0.5 * Math.sin(time * 0.4 + t * Math.PI));
      const random = Math.random() * 0.3;
      const value = Math.abs(noise) * 0.6 + random;
      targetValues[i] = Math.max(0.05, Math.min(1, value));
    } else {
      // Static low level when paused
      targetValues[i] = 0.05 + Math.sin(i * 0.5 + time * 0.1) * 0.03;
    }

    // Easing / smoothing
    currentValues[i] += (targetValues[i] - currentValues[i]) * SMOOTHING;

    const barHeight = currentValues[i] * h;
    const x = i * barWidth + gap / 2;
    const y = h - barHeight;

    // Gradient purple #7c3aed -> #a78bfa
    const gradient = ctx.createLinearGradient(0, h, 0, 0);
    gradient.addColorStop(0, "rgba(124, 58, 237, 0.85)");
    gradient.addColorStop(1, "rgba(167, 139, 250, 0.45)");

    ctx.fillStyle = gradient;

    // Glow effect
    ctx.shadowBlur = 12;
    ctx.shadowColor = "rgba(124, 58, 237, 0.35)";

    // Rounded top bars
    const radius = Math.min(drawWidth / 2, barHeight / 2, 4);
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + drawWidth - radius, y);
    ctx.quadraticCurveTo(x + drawWidth, y, x + drawWidth, y + radius);
    ctx.lineTo(x + drawWidth, h);
    ctx.lineTo(x, h);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
    ctx.fill();

    // Reset shadow for next bar to avoid compounding
    ctx.shadowBlur = 0;
  }
};

const animate = () => {
  draw();
  animationId = requestAnimationFrame(animate);
};

onMounted(() => {
  animate();
});

onBeforeUnmount(() => {
  if (animationId) cancelAnimationFrame(animationId);
});

// Redraw immediately when play state changes to avoid stale frames
watch(
  () => store.activePlayer?.playback_state,
  () => {
    draw();
  },
);
</script>

<style scoped>
.audio-visualizer {
  position: absolute;
  bottom: 120px;
  left: 0;
  right: 0;
  height: 150px;
  pointer-events: none;
  z-index: 1;
}

.audio-visualizer canvas {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
