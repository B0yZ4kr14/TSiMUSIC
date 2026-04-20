/**
 * main.ts
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Polyfill for Safari 15 / iOS 15 (AbortSignal.timeout not supported)
declare global {
  interface AbortSignalConstructor {
    timeout?(ms: number): AbortSignal;
  }
}

if (typeof AbortSignal !== "undefined" && !AbortSignal.timeout) {
  AbortSignal.timeout = (ms: number): AbortSignal => {
    const controller = new AbortController();
    setTimeout(
      () => controller.abort(new DOMException("TimeoutError", "TimeoutError")),
      ms,
    );
    return controller.signal;
  };
}

// Global styles
import "@/styles/global.css";
import "@/styles/style.css";

// Components
import App from "./App.vue";

// Composables
import { createApp } from "vue";

// Plugins
import { registerPlugins } from "@/plugins";

// Install Sendspin WebSocket interceptor for authenticated connections
import { installSendspinInterceptor } from "@/plugins/sendspin-connection";
import "./styles/tsimusic-premium.css";
installSendspinInterceptor();

const app = createApp(App);

registerPlugins(app);

app.mount("#app");

// ═══════════════════════════════════════════════════════════════
// Security: dynamic OG/Twitter meta tags based on current origin
// Prevents certificate warnings when accessed via IP vs hostname
// ═══════════════════════════════════════════════════════════════
(function setDynamicMetaTags() {
  const origin = window.location.origin;
  const ogImage = `${origin}/og-image.png`;

  const ogUrlMeta = document.getElementById("og-url") as HTMLMetaElement | null;
  const ogImageMeta = document.getElementById("og-image") as HTMLMetaElement | null;
  const twitterImageMeta = document.getElementById("twitter-image") as HTMLMetaElement | null;
  const canonicalLink = document.querySelector("link[rel=\"canonical\"]") as HTMLLinkElement | null;

  if (ogUrlMeta) ogUrlMeta.content = origin + "/";
  if (ogImageMeta) ogImageMeta.content = ogImage;
  if (twitterImageMeta) twitterImageMeta.content = ogImage;
  if (canonicalLink) canonicalLink.href = origin + "/";
})();
