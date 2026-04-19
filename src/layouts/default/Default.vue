<template>
  <v-app>
    <MainView v-if="store.frameless" />
    <template v-else>
      <MainView />
      <Footer />
      <PwaInstallPrompt />
      <OfflineIndicator />
      <KeyboardShortcutsHelp />
      <GlobalProgressBar />
      <VolumeIndicator />
    </template>
  </v-app>
  <reload-prompt />
</template>

<script lang="ts" setup>
import MainView from "./View.vue";
import Footer from "./Footer.vue";
import ReloadPrompt from "./ReloadPrompt.vue";
import PwaInstallPrompt from "@/components/PwaInstallPrompt.vue";
import OfflineIndicator from "@/components/OfflineIndicator.vue";
import KeyboardShortcutsHelp from "@/components/KeyboardShortcutsHelp.vue";
import GlobalProgressBar from "@/components/GlobalProgressBar.vue";
import VolumeIndicator from "@/components/VolumeIndicator.vue";
import { store } from "@/plugins/store";
import { watch } from "vue";
import api from "@/plugins/api";
import { useRoute } from "vue-router";
import { useKeyboardShortcuts } from "@/composables/useKeyboardShortcuts";
import { useDynamicTitle } from "@/composables/useDynamicTitle";

const route = useRoute();
useKeyboardShortcuts();
useDynamicTitle();

watch(
  // make sure it's retriggered when players array is populated
  [() => route.query.player, () => Object.keys(api.players).length],
  ([newActivePlayer]) => {
    if (!newActivePlayer) return;
    const newPlayerString = newActivePlayer.toString().toLowerCase();
    // newActivePlayer can be either player id or player name
    const newPlayerId = Object.values(api.players).find((p) => {
      return (
        p.player_id.toLowerCase() === newPlayerString ||
        p.name.toLowerCase() === newPlayerString
      );
    })?.player_id;

    if (newPlayerId) {
      store.activePlayerId = newPlayerId;
    }
  },
  { immediate: true },
);
watch(
  () => route.query.showFullscreenPlayer,
  (showFullscreenPlayer) => {
    store.showFullscreenPlayer = !!showFullscreenPlayer;
  },
  { immediate: true },
);
watch(
  () => route.query.frameless,
  (frameless) => {
    if (frameless !== undefined) {
      store.frameless = true;
    }
  },
  { immediate: true },
);
</script>

<style scoped>
.centeredoverlay :deep(.v-overlay__content) {
  left: 50%;
  right: 50%;
  top: 50%;
  bottom: 50%;
}
</style>
