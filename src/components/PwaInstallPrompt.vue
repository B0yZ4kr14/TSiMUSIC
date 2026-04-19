<template>
  <v-card
    v-if="showPrompt"
    class="pwa-install-prompt"
    elevation="8"
  >
    <div class="pwa-prompt-content">
      <img
        src="@/assets/icon.svg"
        alt="TSi MUSIC"
        class="pwa-prompt-icon"
      />
      <div class="pwa-prompt-text">
        <div class="pwa-prompt-title">Instalar TSi MUSIC</div>
        <div class="pwa-prompt-subtitle">
          Adicione à tela inicial para acesso rápido offline
        </div>
      </div>
    </div>
    <div class="pwa-prompt-actions">
      <v-btn
        variant="text"
        color="default"
        size="small"
        @click="dismissPrompt"
      >
        Agora não
      </v-btn>
      <v-btn
        variant="elevated"
        color="primary"
        size="small"
        @click="installPwa"
      >
        <v-icon icon="mdi-download" start />
        Instalar
      </v-btn>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

const showPrompt = ref(false);
let deferredPrompt: BeforeInstallPromptEvent | null = null;

const dismissPrompt = () => {
  showPrompt.value = false;
  localStorage.setItem("pwa-install-dismissed", Date.now().toString());
};

const installPwa = async () => {
  if (!deferredPrompt) return;
  deferredPrompt.prompt();
  const { outcome } = await deferredPrompt.userChoice;
  if (outcome === "accepted") {
    localStorage.setItem("pwa-install-accepted", "true");
  }
  deferredPrompt = null;
  showPrompt.value = false;
};

onMounted(() => {
  // Check if already installed or dismissed recently
  const dismissed = localStorage.getItem("pwa-install-dismissed");
  const accepted = localStorage.getItem("pwa-install-accepted");
  const isStandalone = window.matchMedia(
    "(display-mode: standalone)"
  ).matches;

  if (accepted || isStandalone) return;

  // Show again if dismissed more than 7 days ago
  if (dismissed) {
    const daysSince = (Date.now() - parseInt(dismissed)) / (1000 * 60 * 60 * 24);
    if (daysSince < 7) return;
  }

  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt = e as BeforeInstallPromptEvent;
    showPrompt.value = true;
  });

  // Also check if appinstalled event fires
  window.addEventListener("appinstalled", () => {
    localStorage.setItem("pwa-install-accepted", "true");
    showPrompt.value = false;
    deferredPrompt = null;
  });
});
</script>

<style scoped>
.pwa-install-prompt {
  position: fixed;
  bottom: 100px;
  right: 20px;
  z-index: 9999;
  max-width: 360px;
  padding: 16px;
  border-radius: 16px !important;
  background: linear-gradient(
    135deg,
    rgba(124, 58, 237, 0.15) 0%,
    rgba(15, 15, 17, 0.95) 100%
  ) !important;
  backdrop-filter: blur(16px);
  border: 1px solid rgba(124, 58, 237, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 16px rgba(124, 58, 237, 0.1);
  animation: pwa-slide-in 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes pwa-slide-in {
  from {
    transform: translateY(20px) scale(0.95);
    opacity: 0;
  }
  to {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

.pwa-prompt-content {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.pwa-prompt-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
}

.pwa-prompt-text {
  flex: 1;
}

.pwa-prompt-title {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.pwa-prompt-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 2px;
}

.pwa-prompt-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

@media (max-width: 600px) {
  .pwa-install-prompt {
    bottom: 80px;
    right: 12px;
    left: 12px;
    max-width: none;
  }
}
</style>
