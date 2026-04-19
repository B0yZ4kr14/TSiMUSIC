<template>
  <div v-if="visible" class="player-clock">
    {{ time }}
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";

const visible = ref(true);
const time = ref("");
let interval: ReturnType<typeof setInterval> | null = null;

const updateTime = () => {
  const now = new Date();
  time.value = now.toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });
};

onMounted(() => {
  updateTime();
  interval = setInterval(updateTime, 1000);
});

onBeforeUnmount(() => {
  if (interval) clearInterval(interval);
});
</script>

<style scoped>
.player-clock {
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 18px;
  font-weight: 300;
  color: rgba(255, 255, 255, 0.7);
  font-variant-numeric: tabular-nums;
  letter-spacing: 1px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  pointer-events: none;
  z-index: 10;
}
</style>
