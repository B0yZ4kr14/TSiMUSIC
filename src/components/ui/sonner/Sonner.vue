<script lang="ts" setup>
import { cn } from "@/lib/utils";
import {
  CircleCheckIcon,
  InfoIcon,
  Loader2Icon,
  OctagonXIcon,
  TriangleAlertIcon,
  XIcon,
} from "lucide-vue-next";
import type { ToasterProps } from "vue-sonner";
import { Toaster as Sonner } from "vue-sonner";

const props = defineProps<ToasterProps>();
</script>

<template>
  <Sonner
    :class="cn('toaster group', props.class)"
    :style="{
      '--normal-bg': 'rgba(26, 26, 30, 0.95)',
      '--normal-text': '#ffffff',
      '--normal-border': 'rgba(124, 58, 237, 0.3)',
      '--border-radius': '12px',
      '--success-bg': 'rgba(34, 197, 94, 0.15)',
      '--success-text': '#4ade80',
      '--success-border': 'rgba(34, 197, 94, 0.3)',
      '--error-bg': 'rgba(239, 68, 68, 0.15)',
      '--error-text': '#f87171',
      '--error-border': 'rgba(239, 68, 68, 0.3)',
      '--warning-bg': 'rgba(234, 179, 8, 0.15)',
      '--warning-text': '#facc15',
      '--warning-border': 'rgba(234, 179, 8, 0.3)',
      '--info-bg': 'rgba(59, 130, 246, 0.15)',
      '--info-text': '#60a5fa',
      '--info-border': 'rgba(59, 130, 246, 0.3)',
    }"
    v-bind="props"
  >
    <template #success-icon>
      <CircleCheckIcon class="size-4" />
    </template>
    <template #info-icon>
      <InfoIcon class="size-4" />
    </template>
    <template #warning-icon>
      <TriangleAlertIcon class="size-4" />
    </template>
    <template #error-icon>
      <OctagonXIcon class="size-4" />
    </template>
    <template #loading-icon>
      <div>
        <Loader2Icon class="size-4 animate-spin" />
      </div>
    </template>
    <template #close-icon>
      <XIcon class="size-4" />
    </template>
  </Sonner>
</template>
