<template>
  <div v-if="visible" class="global-progress-bar">
    <div class="global-progress-bar__fill" :style="{ width: progress + '%' }" />
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

const visible = ref(false);
const progress = ref(0);
let interval: ReturnType<typeof setInterval> | null = null;
let timeout: ReturnType<typeof setTimeout> | null = null;

const router = useRouter();

const start = () => {
  visible.value = true;
  progress.value = 0;

  if (interval) clearInterval(interval);
  if (timeout) clearTimeout(timeout);

  interval = setInterval(() => {
    if (progress.value < 80) {
      progress.value += Math.random() * 15;
    } else if (progress.value < 95) {
      progress.value += Math.random() * 2;
    }
  }, 200);
};

const done = () => {
  progress.value = 100;
  if (interval) clearInterval(interval);
  timeout = setTimeout(() => {
    visible.value = false;
    progress.value = 0;
  }, 300);
};

onMounted(() => {
  router.beforeEach(() => {
    start();
  });
  router.afterEach(() => {
    done();
  });
});

onBeforeUnmount(() => {
  if (interval) clearInterval(interval);
  if (timeout) clearTimeout(timeout);
});
</script>

<style scoped>
.global-progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  z-index: 10001;
  background: rgba(124, 58, 237, 0.1);
}

.global-progress-bar__fill {
  height: 100%;
  background: linear-gradient(90deg, #7c3aed 0%, #a78bfa 100%);
  box-shadow: 0 0 8px rgba(124, 58, 237, 0.5);
  transition: width 0.2s ease;
}
</style>
