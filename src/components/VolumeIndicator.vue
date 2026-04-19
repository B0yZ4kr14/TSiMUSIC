<template>
  <v-fade-transition>
    <div v-if="visible" class="volume-indicator">
      <v-icon :icon="icon" size="48" color="primary" />
      <div class="volume-indicator__bar">
        <div
          class="volume-indicator__fill"
          :style="{ width: volumePercent + '%' }"
        />
      </div>
      <div class="volume-indicator__value">{{ volumePercent }}%</div>
    </div>
  </v-fade-transition>
</template>

<script setup lang="ts">
import { store } from "@/plugins/store";
import { computed, ref, watch } from "vue";

const visible = ref(false);
let timeout: ReturnType<typeof setTimeout> | null = null;

const volumePercent = computed(() => {
  const player = store.activePlayer;
  if (!player || player.volume_level === undefined) return 0;
  return Math.round(player.volume_level * 100);
});

const icon = computed(() => {
  if (volumePercent.value === 0) return "mdi-volume-mute";
  if (volumePercent.value < 30) return "mdi-volume-low";
  if (volumePercent.value < 70) return "mdi-volume-medium";
  return "mdi-volume-high";
});

// Watch for volume changes to show indicator
let lastVolume = volumePercent.value;

watch(volumePercent, (newVal) => {
  if (newVal !== lastVolume) {
    lastVolume = newVal;
    visible.value = true;
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => {
      visible.value = false;
    }, 1500);
  }
});
</script>

<style scoped>
.volume-indicator {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10002;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 32px;
  background: linear-gradient(
    135deg,
    rgba(26, 26, 30, 0.95) 0%,
    rgba(15, 15, 17, 0.95) 100%
  );
  border: 1px solid rgba(124, 58, 237, 0.3);
  border-radius: 20px;
  backdrop-filter: blur(16px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4), 0 0 32px rgba(124, 58, 237, 0.1);
}

.volume-indicator__bar {
  width: 160px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.volume-indicator__fill {
  height: 100%;
  background: linear-gradient(90deg, #7c3aed 0%, #a78bfa 100%);
  border-radius: 3px;
  transition: width 0.2s ease;
}

.volume-indicator__value {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}
</style>
