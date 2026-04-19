import api from "@/plugins/api";
import { store } from "@/plugins/store";
import { onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";

/**
 * Global keyboard shortcuts for TSi MUSIC player controls
 *
 * Shortcuts:
 * - Space: Play/Pause
 * - ArrowRight: Next track
 * - ArrowLeft: Previous track
 * - ArrowUp: Volume up
 * - ArrowDown: Volume down
 * - F: Toggle fullscreen player
 * - M: Toggle mini player mode
 * - Escape: Close fullscreen player / dialogs
 * - / or Ctrl+K: Focus global search
 */
export function useKeyboardShortcuts() {
  const router = useRouter();

  const handleKeyDown = (event: KeyboardEvent) => {
    // Ignore shortcuts when typing in input fields
    const target = event.target as HTMLElement;
    if (
      target.tagName === "INPUT" ||
      target.tagName === "TEXTAREA" ||
      target.isContentEditable
    ) {
      return;
    }

    const playerId = store.activePlayer?.player_id;
    if (!playerId) return;

    switch (event.key) {
      case " ":
        event.preventDefault();
        api.playerCommandPlayPause(playerId);
        break;

      case "ArrowRight":
        if (!event.ctrlKey && !event.metaKey && !event.altKey && !event.shiftKey) {
          event.preventDefault();
          api.playerCommandNext(playerId);
        }
        break;

      case "ArrowLeft":
        if (!event.ctrlKey && !event.metaKey && !event.altKey && !event.shiftKey) {
          event.preventDefault();
          api.playerCommandPrevious(playerId);
        }
        break;

      case "ArrowUp":
        if (!event.ctrlKey && !event.metaKey && !event.altKey && !event.shiftKey) {
          event.preventDefault();
          api.playerCommandVolumeUp(playerId);
        }
        break;

      case "ArrowDown":
        if (!event.ctrlKey && !event.metaKey && !event.altKey && !event.shiftKey) {
          event.preventDefault();
          api.playerCommandVolumeDown(playerId);
        }
        break;

      case "f":
      case "F":
        event.preventDefault();
        store.showFullscreenPlayer = !store.showFullscreenPlayer;
        break;

      case "m":
      case "M":
        event.preventDefault();
        store.miniPlayerMode = !store.miniPlayerMode;
        localStorage.setItem("miniPlayerMode", store.miniPlayerMode.toString());
        break;

      case "Escape":
        if (store.showFullscreenPlayer) {
          event.preventDefault();
          store.showFullscreenPlayer = false;
        } else if (store.dialogActive) {
          event.preventDefault();
          store.dialogActive = false;
        }
        break;

      case "/":
        if (!event.ctrlKey && !event.metaKey) {
          event.preventDefault();
          // Focus global search if available
          const searchInput = document.querySelector(
            '[data-testid="global-search"] input, .global-search input, input[type="search"]'
          ) as HTMLInputElement;
          if (searchInput) {
            searchInput.focus();
          } else {
            // Navigate to search page
            router.push("/search");
          }
        }
        break;

      case "k":
        if (event.ctrlKey || event.metaKey) {
          event.preventDefault();
          router.push("/search");
        }
        break;
    }
  };

  onMounted(() => {
    window.addEventListener("keydown", handleKeyDown);
  });

  onUnmounted(() => {
    window.removeEventListener("keydown", handleKeyDown);
  });
}
