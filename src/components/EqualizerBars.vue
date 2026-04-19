<template>
  <div v-if="isPlaying" class="equalizer-bars">
    <div
      v-for="i in 4"
      :key="i"
      class="equalizer-bar"
      :style="{ animationDelay: `${(i - 1) * 0.15}s` }"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { store } from "@/plugins/store";

const isPlaying = computed(() => {
  return store.activePlayer?.playback_state === "playing";
});
</script>

<style scoped>
.equalizer-bars {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  height: 16px;
  padding: 0 4px;
}

.equalizer-bar {
  width: 3px;
  background: linear-gradient(to top, #7c3aed, #a78bfa);
  border-radius: 2px;
  animation: equalizer-bounce 0.6s ease-in-out infinite alternate;
}

.equalizer-bar:nth-child(1) {
  height: 40%;
}
.equalizer-bar:nth-child(2) {
  height: 70%;
}
.equalizer-bar:nth-child(3) {
  height: 50%;
}
.equalizer-bar:nth-child(4) {
  height: 80%;
}

@keyframes equalizer-bounce {
  0% {
    transform: scaleY(0.4);
    opacity: 0.6;
  }
  100% {
    transform: scaleY(1);
    opacity: 1;
  }
}
</style>
