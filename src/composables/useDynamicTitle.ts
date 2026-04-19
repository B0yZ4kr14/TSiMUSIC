import { store } from "@/plugins/store";
import { computed, watch } from "vue";

/**
 * Updates the browser tab title dynamically based on playback state
 * Shows current track info when playing, defaults to "TSi MUSIC" when stopped
 */
export function useDynamicTitle() {
  const defaultTitle = "TSi MUSIC";

  const title = computed(() => {
    const player = store.activePlayer;
    const queueItem = store.curQueueItem;

    if (!player || player.powered === false) {
      return defaultTitle;
    }

    const state = player.playback_state;
    if (state === "playing" && queueItem?.media_item) {
      const name = queueItem.media_item.name;
      const artist =
        (queueItem.media_item as any).artists?.[0]?.name ||
        "Artista desconhecido";
      return `${name} — ${artist} | ${defaultTitle}`;
    }

    if (state === "paused" && queueItem?.media_item) {
      return `⏸ ${queueItem.media_item.name} | ${defaultTitle}`;
    }

    return defaultTitle;
  });

  watch(
    title,
    (newTitle) => {
      document.title = newTitle;
    },
    { immediate: true }
  );
}
