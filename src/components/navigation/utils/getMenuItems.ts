import ArtistIcon from "@/components/icons/ArtistIcon.vue";
import GenreIcon from "@/components/icons/GenreIcon.vue";
import { DEFAULT_MENU_ITEMS } from "@/constants";
import { store } from "@/plugins/store";
import {
  BookAudio,
  Compass,
  Disc3,
  Folder,
  ListMusic,
  Music2,
  PartyPopper,
  Podcast,
  Radio,
  Search,
  Settings,
} from "lucide-vue-next";
import { Component } from "vue";

export interface MenuItem {
  label: string;
  icon: Component;
  path: string;
  isLibraryNode: boolean;
  hidden?: boolean;
  disabled?: boolean;
}

export const getMenuItems = function () {
  // Read from user preferences first, fallback to localStorage for migration
  const userMenuItems = store.currentUser?.preferences?.menu_items;
  const storedMenuConf = localStorage.getItem("frontend.settings.menu_items");

  let enabledItems: string[];
  if (userMenuItems) {
    // If user preferences has menu_items, use it (it could be array or comma-separated string)
    enabledItems = Array.isArray(userMenuItems)
      ? userMenuItems
      : userMenuItems.split(",");
  } else if (storedMenuConf) {
    // Fallback to localStorage during migration
    enabledItems = storedMenuConf.split(",");
  } else {
    // Final fallback to defaults
    enabledItems = DEFAULT_MENU_ITEMS;
  }
  const items: MenuItem[] = [];
  // we loop through DEFAULT_MENU_ITEMS to respect default order;
  // new items added to DEFAULT_MENU_ITEMS automatically appear unless explicitly disabled
  for (const enabledMenuItemStr of DEFAULT_MENU_ITEMS) {
    // Check if item is enabled (user preferences or localStorage migration fallback)
    if (!enabledItems.includes(enabledMenuItemStr)) continue;
    if (enabledMenuItemStr === "discover") {
      items.push({
        label: "discover",
        icon: Compass,
        path: "/discover",
        isLibraryNode: false,
      });
    }
    if (enabledMenuItemStr === "search") {
      items.push({
        label: "search",
        icon: Search,
        path: "/search",
        isLibraryNode: false,
      });
    }
    if (enabledMenuItemStr === "party") {
      items.push({
        label: "party_mode",
        icon: PartyPopper,
        path: "/party",
        isLibraryNode: false,
        hidden: !store.enabledPlugins.has("party"),
      });
    }
    if (enabledMenuItemStr === "artists") {
      items.push({
        label: "artists",
        icon: ArtistIcon,
        path: "/artists",
        isLibraryNode: true,
      });
    }
    if (enabledMenuItemStr === "albums") {
      items.push({
        label: "albums",
        icon: Disc3,
        path: "/albums",
        isLibraryNode: true,
      });
    }
    if (enabledMenuItemStr === "tracks") {
      items.push({
        label: "tracks",
        icon: Music2,
        path: "/tracks",
        isLibraryNode: true,
      });
    }
    if (enabledMenuItemStr === "playlists") {
      items.push({
        label: "playlists",
        icon: ListMusic,
        path: "/playlists",
        isLibraryNode: true,
      });
    }
    if (enabledMenuItemStr === "audiobooks") {
      items.push({
        label: "audiobooks",
        icon: BookAudio,
        path: "/audiobooks",
        isLibraryNode: true,
        disabled: store.libraryAudiobooksCount === 0,
      });
    }
    if (enabledMenuItemStr === "podcasts") {
      items.push({
        label: "podcasts",
        icon: Podcast,
        path: "/podcasts",
        isLibraryNode: true,
        disabled: store.libraryPodcastsCount === 0,
      });
    }
    if (enabledMenuItemStr === "radios") {
      items.push({
        label: "radios",
        icon: Radio,
        path: "/radios",
        isLibraryNode: true,
      });
    }
    if (enabledMenuItemStr === "genres") {
      items.push({
        label: "genres",
        icon: GenreIcon,
        path: "/genres",
        isLibraryNode: true,
      });
    }
    if (enabledMenuItemStr === "browse") {
      items.push({
        label: "browse",
        icon: Folder,
        path: "/browse",
        isLibraryNode: true,
      });
    }
    if (enabledMenuItemStr === "settings") {
      items.push({
        label: "settings.settings",
        icon: Settings,
        path: "/settings",
        isLibraryNode: true,
      });
    }
  }
  return items;
};
