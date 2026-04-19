<template>
  <v-dialog v-model="visible" max-width="480" persistent :scrim="true">
    <v-card class="shortcuts-help-card">
      <v-card-title class="shortcuts-help-title">
        <v-icon icon="mdi-keyboard" class="mr-2" />
        Atalhos de Teclado
      </v-card-title>
      <v-card-text>
        <div class="shortcuts-list">
          <div
            v-for="shortcut in shortcuts"
            :key="shortcut.key"
            class="shortcut-item"
          >
            <kbd class="shortcut-key">{{ shortcut.key }}</kbd>
            <span class="shortcut-desc">{{ shortcut.desc }}</span>
          </div>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" variant="elevated" @click="close">
          Entendi
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";

const visible = ref(false);

const shortcuts = [
  { key: "Espaço", desc: "Play / Pause" },
  { key: "→", desc: "Próxima faixa" },
  { key: "←", desc: "Faixa anterior" },
  { key: "↑", desc: "Aumentar volume" },
  { key: "↓", desc: "Diminuir volume" },
  { key: "F", desc: "Fullscreen player" },
  { key: "M", desc: "Mini player mode" },
  { key: "Esc", desc: "Fechar dialogs" },
  { key: "/", desc: "Busca" },
  { key: "?", desc: "Mostrar atalhos" },
];

const close = () => {
  visible.value = false;
  localStorage.setItem("shortcuts-help-shown", "true");
};

const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === "?" && !e.ctrlKey && !e.metaKey && !e.altKey) {
    const target = e.target as HTMLElement;
    if (
      target.tagName === "INPUT" ||
      target.tagName === "TEXTAREA" ||
      target.isContentEditable
    ) {
      return;
    }
    e.preventDefault();
    visible.value = !visible.value;
  }
};

onMounted(() => {
  window.addEventListener("keydown", handleKeyDown);
  // Show once on first visit
  if (!localStorage.getItem("shortcuts-help-shown")) {
    setTimeout(() => {
      visible.value = true;
    }, 3000);
  }
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleKeyDown);
});
</script>

<style scoped>
.shortcuts-help-card {
  background: linear-gradient(
    135deg,
    rgba(26, 26, 30, 0.98) 0%,
    rgba(15, 15, 17, 0.98) 100%
  ) !important;
  border: 1px solid rgba(124, 58, 237, 0.2);
  border-radius: 16px !important;
  backdrop-filter: blur(16px);
}

.shortcuts-help-title {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: 600;
  padding: 20px 24px 12px;
  color: #fff;
}

.shortcuts-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px 0;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background 0.2s;
}

.shortcut-item:hover {
  background: rgba(124, 58, 237, 0.1);
}

.shortcut-key {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 48px;
  padding: 4px 8px;
  background: rgba(124, 58, 237, 0.2);
  border: 1px solid rgba(124, 58, 237, 0.3);
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #a78bfa;
  font-family: monospace;
}

.shortcut-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
}
</style>
