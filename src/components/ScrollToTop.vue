<template>
  <v-btn
    v-show="visible"
    icon
    class="scroll-to-top"
    color="primary"
    @click="scrollToTop"
  >
    <v-icon icon="mdi-chevron-up" />
  </v-btn>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";

const visible = ref(false);
let scrollContainer: HTMLElement | null = null;

const handleScroll = () => {
  if (!scrollContainer) return;
  visible.value = scrollContainer.scrollTop > 400;
};

const scrollToTop = () => {
  if (!scrollContainer) return;
  scrollContainer.scrollTo({
    top: 0,
    behavior: "smooth",
  });
};

onMounted(() => {
  // Find the scrollable content section
  scrollContainer = document.querySelector(".content-section");
  if (scrollContainer) {
    scrollContainer.addEventListener("scroll", handleScroll);
  }
});

onBeforeUnmount(() => {
  if (scrollContainer) {
    scrollContainer.removeEventListener("scroll", handleScroll);
  }
});
</script>

<style scoped>
.scroll-to-top {
  position: fixed;
  bottom: 100px;
  right: 20px;
  z-index: 999;
  background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%) !important;
  box-shadow: 0 4px 16px rgba(124, 58, 237, 0.4);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  animation: scroll-top-in 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.scroll-to-top:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(124, 58, 237, 0.5);
}

@keyframes scroll-top-in {
  from {
    transform: scale(0.8);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

@media (max-width: 600px) {
  .scroll-to-top {
    bottom: 80px;
    right: 12px;
  }
}
</style>
