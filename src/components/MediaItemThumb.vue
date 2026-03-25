<template>
  <v-img
    loading="lazy"
    :height="size || '100%'"
    :width="size || '100%'"
    aspect-ratio="1"
    :src="currentSrc"
    :class="{ rounded: rounded }"
    contain
    :lazy-src="theme.current.value.dark ? imgCoverDark : imgCoverLight"
    @error="onImageError"
  />
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import type {
  ItemMapping,
  MediaItemType,
  QueueItem,
} from "@/plugins/api/interfaces";
import { ImageType, MediaType } from "@/plugins/api/interfaces";
import { useTheme } from "vuetify";
import {
  imgCoverDark,
  imgCoverLight,
  iconFolder,
} from "@/components/QualityDetailsBtn.vue";
import { getImageThumbForItem } from "@/helpers/utils";

export interface Props {
  item?: MediaItemType | ItemMapping | QueueItem;
  size?: string | number;
  fallback?: string;
  rounded?: boolean;
  thumbnail?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  item: undefined,
  size: "100%",
  fallback: undefined,
  rounded: true,
  thumbnail: true,
});

const theme = useTheme();

function getThumbSize() {
  if (typeof props.size == "number") {
    return props.size;
  } else if (props.thumbnail) return 256;
  else return 0;
}
const thumbSize = getThumbSize();

const fallbackImage = computed(() => {
  if (props.fallback) return props.fallback;
  if (
    props.item &&
    "media_type" in props.item &&
    props.item.media_type == MediaType.FOLDER
  )
    return iconFolder;
  if (!props.item) return "";
  if (!props.item.name) return "";
  return getAvatarImage(
    props.item.name,
    theme.current.value.dark,
    thumbSize || 256,
  );
});

const imgData = computed(() =>
  props.item
    ? getImageThumbForItem(props.item, ImageType.THUMB, thumbSize) ||
      fallbackImage.value
    : fallbackImage.value,
);

// Track current image source, allowing fallback on error
const currentSrc = ref(imgData.value);
const hasError = ref(false);

// Reset when item changes
watch(
  () => props.item,
  () => {
    hasError.value = false;
    currentSrc.value = imgData.value;
  },
);

// Also update when imgData changes (e.g., image loaded later)
watch(imgData, (newVal) => {
  if (!hasError.value) {
    currentSrc.value = newVal;
  }
});

function onImageError() {
  // On error (e.g., 204 No Content from backend), fall back to avatar image
  if (!hasError.value && currentSrc.value !== fallbackImage.value) {
    hasError.value = true;
    currentSrc.value = fallbackImage.value;
  }
}
</script>

<script lang="ts">
//// utility functions for images

export const getAvatarImage = function (
  name: string,
  dark = false,
  size = 256,
): string {
  // get url to avatar image for a string or sentence
  if (dark)
    return `https://ui-avatars.com/api/?name=${name}&size=${
      size || 256
    }&bold=true&background=1d1d1d&color=383838`;
  else
    return `https://ui-avatars.com/api/?name=${name}&size=${
      size || 256
    }&bold=true&background=a0a0a0&color=cccccc`;
};
</script>

<style scoped>
.v-avatar.v-avatar--density-default {
  height: 100% !important;
  width: 100% !important;
}
</style>
