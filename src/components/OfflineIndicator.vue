<template>
  <v-slide-y-transition>
    <div
      v-if="!isOnline"
      class="offline-indicator"
    >
      <v-icon icon="mdi-wifi-off" size="small" class="mr-2" />
      <span>Sem conexão com a internet</span>
    </div>
  </v-slide-y-transition>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";

const isOnline = ref(navigator.onLine);

const updateOnlineStatus = () => {
  isOnline.value = navigator.onLine;
};

onMounted(() => {
  window.addEventListener("online", updateOnlineStatus);
  window.addEventListener("offline", updateOnlineStatus);
});

onBeforeUnmount(() => {
  window.removeEventListener("online", updateOnlineStatus);
  window.removeEventListener("offline", updateOnlineStatus);
});
</script>

<style scoped>
.offline-indicator {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  background: linear-gradient(
    135deg,
    rgba(234, 179, 8, 0.9) 0%,
    rgba(202, 138, 4, 0.9) 100%
  );
  color: #000;
  font-size: 14px;
  font-weight: 500;
  backdrop-filter: blur(8px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}
</style>
