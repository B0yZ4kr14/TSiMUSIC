#!/usr/bin/env python3
"""Auditoria completa de tradução en.json vs pt_BR.json"""

import json
import re
from collections import defaultdict
from pathlib import Path

EN_PATH = Path("/tmp/ma-frontend-valid/src/translations/en.json")
PT_PATH = Path("/tmp/ma-frontend-valid/src/translations/pt_BR.json")
OUT_PATH = Path("/tmp/ma-frontend-valid/TRANSLATION_AUDIT.md")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def flatten(obj, prefix=""):
    """Retorna dict com chave dot-notation -> valor string"""
    result = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                result.update(flatten(v, new_key))
            elif isinstance(v, str):
                result[new_key] = v
            # ignora outros tipos (não há no JSON)
    return result


def extract_placeholders(text):
    # captura {0}, {1}, {name} etc.
    return set(re.findall(r"\{[^}]+\}", text))


# Termos técnicos/propriedades que podem permanecer em inglês sem serem "misturados"
TECH_TERMS = {
    "tsi music", "home assistant", "webrtc", "dtls-srtp", "stun", "turn",
    "oauth", "qr", "uri", "url", "id", "api", "dsp", "eq", "apo", "rew",
    "mdi", "pcm", "r128", "ebu-r128", "lufs", "db", "kbps", "khz",
    "ms", "ha", "os", "cpu", "ram", "ip", "ssid", "json", "yaml",
    "rew", "dts", "drc", "ac3", "eac3", "flac", "mp3", "aac", "ogg",
    "vorbis", "opus", "wav", "aiff", "wma", "alac", "m4a", "mp4",
    "webplayer", "sendspin", "chromecast", "airplay", "sonos", "spotify",
    "tidal", "deezer", "qobuz", "youtube", "soundcloud", "bandcamp",
    "plex", "jellyfin", "subsonic", "navidrome", "kodi", "squeezelite",
    "snapcast", "upnp", "dlna", "cast", "group", "sync", "stereo",
    "mono", "left", "right", "all", "fl", "fr", "bl", "br", "sl", "sr",
    "c", "lfe", "off", "on", "auto", "light", "dark", "enabled", "disabled",
    "true", "false", "yes", "no", "ok", "cancel", "close", "save", "delete",
    "edit", "add", "remove", "play", "pause", "stop", "next", "previous",
    "shuffle", "repeat", "volume", "mute", "power", "menu", "settings",
    "search", "filter", "sort", "view", "list", "grid", "thumb", "compact",
    "panel", "discovery", "flow", "crossfade", "gapless", "bit", "depth",
    "rate", "sample", "channel", "gain", "limiter", "preamp", "tone",
    "bass", "mid", "treble", "equalizer", "parametric", "peak", "shelf",
    "pass", "notch", "low", "high", "band", "q", "frequency", "hz",
    "khz", "db", "ms", "s", "min", "h", "d", "w", "mo", "y",
    "localhost", "http", "https", "tcp", "udp", "rtp", "rtsp", "rtmp",
    "hls", "dash", "icecast", "shoutcast", "radio", "browser",
    "addon", "integration", "automation", "scene", "script", "sensor",
    "switch", "light", "media_player", "notify", "tts", "stt",
    "wake_word", "intent", "conversation", "tag", "zone", "area",
    "device", "entity", "state", "attribute", "service", "event",
    "condition", "action", "trigger", "delay", "wait", "repeat",
    "choose", "parallel", "sequence", "variables", "template",
    "mqtt", "zigbee", "zwave", "ble", "thread", "matter", "coap",
    "mdns", "dns", "dhcp", "ntp", "ssh", "ssl", "tls", "vpn",
    "vlan", "lan", "wan", "nat", "firewall", "router", "switch",
    "access_point", "mesh", "node", "gateway", "bridge", "repeater",
    "server", "client", "peer", "host", "port", "socket", "packet",
    "frame", "payload", "header", "body", "request", "response",
    "get", "post", "put", "patch", "delete", "options", "head",
    "ws", "wss", "sse", "polling", "webhook", "callback", "token",
    "jwt", "oauth2", "saml", "ldap", "radius", "totp", "hotp",
    "mfa", "2fa", "pin", "password", "user", "admin", "guest",
    "role", "permission", "policy", "group", "team", "org",
    "account", "profile", "avatar", "session", "cookie", "cache",
    "local_storage", "indexed_db", "session_storage", "manifest",
    "service_worker", "pwa", "spa", "ssr", "csr", "hydration",
    "component", "directive", "pipe", "module", "provider", "injector",
    "observable", "subject", "behavior_subject", "replay_subject",
    "async_pipe", "date_pipe", "json_pipe", "slice_pipe", "i18n",
    "locale", "currency", "decimal", "percent", "plural", "select",
    "interpolations", "placeholder", "icu", "message", "id",
    "source", "target", "meaning", "description", "notes", "context",
    "chunk", "bundle", "asset", "entry", "output", "public_path",
    "loader", "plugin", "resolver", "parser", "transform", "sourcemap",
    "minify", "uglify", "terser", "esbuild", "rollup", "webpack",
    "vite", "parcel", "snowpack", "turbo", "bun", "deno", "node",
    "npm", "yarn", "pnpm", "package", "lock", "semver", "dependency",
    "dev_dependency", "peer_dependency", "optional_dependency",
    "bundled_dependency", "workspace", "monorepo", "lerna", "nx",
    "turborepo", "changeset", "release", "changelog", "version",
    "tag", "branch", "commit", "merge", "rebase", "cherry_pick",
    "stash", "patch", "diff", "blame", "log", "status", "fetch",
    "pull", "push", "clone", "fork", "pr", "issue", "milestone",
    "label", "wiki", "page", "discussion", "action", "workflow",
    "runner", "artifact", "cache", "secret", "variable", "env",
    "matrix", "strategy", "job", "step", "needs", "if", "run",
    "uses", "with", "outputs", "inputs", "secrets", "github_token",
    "gitea", "gitlab", "bitbucket", "azure", "aws", "gcp", "oci",
    "docker", "container", "image", "volume", "network", "compose",
    "kubernetes", "k8s", "helm", "chart", "pod", "deployment",
    "service", "ingress", "configmap", "secret", "pvc", "pv",
    "namespace", "node", "cluster", "context", "kubeconfig",
    "terraform", "pulumi", "ansible", "puppet", "chef", "salt",
    "vagrant", "packer", "vault", "consul", "nomad", "boundary",
    "waypoint", "sentinel", "hcl", "tfvars", "state", "plan",
    "apply", "destroy", "import", "refresh", "taint", "untaint",
    "workspace", "module", "provider", "resource", "data", "locals",
    "output", "variable", "dynamic", "for_each", "count", "lifecycle",
    "provisioner", "connection", "backend", "remote", "local",
    "cloud", "enterprise", "community", "oss", "gpl", "mit",
    "apache", "bsd", "mozilla", "lgpl", "agpl", "elastic",
    "sspl", "unlicense", "wtfpl", "cc0", "cc_by", "cc_by_sa",
    "cc_by_nc", "cc_by_nd", "cc_by_nc_sa", "cc_by_nc_nd",
    "proprietary", "commercial", "trial", "demo", "freemium",
    "open_source", "closed_source", "source_available", "fair",
    "blueoak", "osl", "epl", "cpl", "ipl", "mpl", "ms_pl",
    "ms_rl", "sil", "ofl", "ufl", "ada", "python", "js", "ts",
    "jsx", "tsx", "vue", "svelte", "astro", "solid", "qwik",
    "angular", "react", "next", "nuxt", "remix", "gatsby",
    "eleventy", "hugo", "jekyll", "hexo", "docusaurus", "vitepress",
    "astro", "sveltekit", "solidstart", "qwikcity", " Redwood",
    "blitz", "t3", "trpc", "prisma", "drizzle", "knex", "sequelize",
    "typeorm", "mikroorm", "waterline", "mongoose", "mongodb",
    "postgres", "mysql", "mariadb", "sqlite", "redis", "elasticsearch",
    "meilisearch", "algolia", "typesense", "supabase", "firebase",
    "appwrite", "parse", "hoodie", "kinto", "couchdb", "pouchdb",
    "rxdb", "watermelondb", "realm", "coredata", "sqflite",
    "expo", "react_native", "ionic", "capacitor", "cordova",
    "flutter", "dart", "kotlin", "swift", "objc", "java",
    "scala", "groovy", "clojure", "erlang", "elixir", "haskell",
    "ocaml", "fsharp", "rust", "go", "zig", "nim", "crystal",
    "julia", "r", "matlab", "octave", "sql", "plsql", "tsql",
    "graphql", "relay", "apollo", "urql", "vue_urql", "svelte_urql",
    "solid_urql", "react_query", "swr", "rtk_query", "vue_query",
    "tanstack", "ag_grid", "react_table", "material_ui", "mui",
    "antd", "chakra", "mantine", "radix", "shadcn", "tailwind",
    "bootstrap", "bulma", "foundation", "semantic_ui", "quasar",
    "vuetify", "element_plus", "primevue", "primefaces", "primereact",
    "primeng", "ionic_ui", "onsen_ui", "nativebase", "gluestack",
    "tamagui", "dripsy", "restyle", "styled_components", "emotion",
    "linaria", "vanilla_extract", "css_modules", "postcss", "sass",
    "less", "stylus", "purgecss", "autoprefixer", "cssnano",
    "browserslist", "caniuse", "core_js", "polyfill", "ponyfill",
    "intersection_observer", "mutation_observer", "resize_observer",
    "performance_observer", "web_worker", "service_worker", "shared_worker",
    "worklet", "paint_api", "layout_api", "animation_api", "storage_api",
    "indexeddb", "websql", "localstorage", "sessionstorage", "cookie",
    "cache_api", "fetch", "xhr", "websocket", "sse", "beacon",
    "navigator", "geolocation", "permissions", "media_devices",
    "getusermedia", "getdisplaymedia", "rtcpeerconnection", "datachannel",
    "screen_capture", "picture_in_picture", "remote_playback",
    "media_session", "web_audio", "web_midi", "web_gl", "web_gpu",
    "web_assembly", "web_crypto", "web_authn", "web_otp", "web_nfc",
    "web_bluetooth", "web_usb", "web_serial", "webhid", "web_share",
    "contact_picker", "file_system", "native_file_system", "drag_drop",
    "clipboard", "selection", "fullscreen", "pointer_lock", "keyboard_lock",
    "wake_lock", "screen_orientation", "device_orientation", "motion",
    "ambient_light", "proximity", "battery", "network_information",
    "connection", "online", "offline", "sync", "periodic_sync",
    "background_fetch", "content_index", "badging", "app_badge",
    "notification_triggers", "push", "push_manager", "notification",
    "vibration", "speech_recognition", "speech_synthesis", "tts",
    "web_speech", "web_animations", "css_animations", "transitions",
    "transforms", "filters", "masks", "clip_path", "blend_modes",
    "variables", "custom_properties", "container_queries", "layers",
    "scope", "nesting", "has", "is", "where", "not", "host",
    "slotted", "part", "theme", "color_scheme", "prefers_color_scheme",
    "prefers_reduced_motion", "prefers_contrast", "prefers_reduced_transparency",
    "forced_colors", "inverted_colors", "scripting", "hover", "pointer",
    "any_hover", "any_pointer", "display_mode", "orientation", "width",
    "height", "aspect_ratio", "resolution", "color", "monochrome",
    "grid", "update", "overflow_block", "overflow_inline", "color_gamut",
    "dynamic_range", "video_color_gamut", "video_dynamic_range",
    "transform_3d", "transform_2d", "math", "srcset", "sizes", "picture",
    "source", "img", "video", "audio", "track", "canvas", "svg",
    "mathml", "iframe", "embed", "object", "param", "map", "area",
    "figure", "figcaption", "details", "summary", "dialog", "popover",
    "menu", "menuitem", "slot", "template", "shadow", "custom_element",
    "declarative_shadow_dom", "constructable_stylesheets", "adoptedstyle",
    "observable", "signal", "effect", "computed", "memo", "batch",
    "untrack", "onmount", "oncleanup", "onerror", "onsuspend",
    "onresume", "ontimeupdate", "onvolumechange", "onratechange",
    "ondurationchange", "onloadedmetadata", "onloadeddata",
    "oncanplay", "oncanplaythrough", "onplay", "onpause", "onwaiting",
    "onseeking", "onseeked", "onended", "onstalled", "onemptied",
    "onabort", "onerror", "onloadstart", "onprogress", "onload",
    "onloadend", "onbeforeunload", "onunload", "onpagehide",
    "onpageshow", "onpopstate", "onhashchange", "onresize",
    "onscroll", "onorientationchange", "onvisibilitychange",
    "ononline", "onoffline", "onmessage", "onmessageerror",
    "onstorage", "onchange", "oninput", "oninvalid", "onsubmit",
    "onreset", "onformdata", "onselect", "onselectionchange",
    "oncopy", "oncut", "onpaste", "ondrag", "ondragstart",
    "ondragend", "ondragenter", "ondragleave", "ondragover",
    "ondrop", "onclick", "ondblclick", "onmousedown", "onmouseup",
    "onmouseenter", "onmouseleave", "onmousemove", "onmouseout",
    "onmouseover", "onwheel", "oncontextmenu", "onshow", "ontoggle",
    "onbeforeprint", "onafterprint", "onanimationstart", "onanimationend",
    "onanimationiteration", "ontransitionstart", "ontransitionend",
    "ontransitioncancel", "onpointerdown", "onpointerup", "onpointermove",
    "onpointerenter", "onpointerleave", "onpointerover", "onpointerout",
    "onpointercancel", "ongotpointercapture", "onlostpointercapture",
    "ontouchstart", "ontouchend", "ontouchmove", "ontouchcancel",
    "onkeypress", "onkeydown", "onkeyup", "onfocus", "onblur",
    "onfocusin", "onfocusout", "onchange", "oninput", "oninvalid",
}


def is_mixed(text_en, text_pt):
    """Detecta se text_pt tem texto misturado pt/en (não idêntico e não puro técnico)"""
    if text_en == text_pt:
        return False  # já coberto por 'identical'
    # tokeniza palavras do pt
    words_pt = re.findall(r"[a-zA-Z]+", text_pt)
    # conta palavras que parecem inglesas comuns (exceto termos técnicos)
    english_common = {
        "the", "and", "for", "are", "but", "not", "you", "all", "can", "had", "her", "was", "one", "our",
        "out", "day", "get", "has", "him", "his", "how", "its", "may", "new", "now", "old", "see", "two",
        "who", "boy", "did", "she", "use", "her", "way", "many", "oil", "sit", "set", "run", "eat",
        "far", "sea", "eye", "ago", "off", "too", "any", "say", "man", "try", "ask", "end", "why",
        "let", "put", "say", "she", "try", "way", "own", "say", "too", "old", "tell", "very", "when",
        "come", "here", "just", "like", "long", "make", "over", "such", "take", "than", "them", "well",
        "also", "back", "each", "find", "give", "good", "have", "into", "look", "most", "next", "only",
        "other", "right", "should", "some", "time", "under", "very", "what", "work", "years", "your",
        "about", "after", "again", "being", "could", "first", "from", "going", "great", "know", "last",
        "life", "little", "more", "much", "never", "once", "part", "people", "place", "same", "still",
        "their", "then", "there", "these", "think", "three", "through", "want", "water", "where",
        "which", "while", "will", "would", "year", "called", "before", "between", "both", "came",
        "down", "each", "even", "every", "found", "given", "going", "having", "made", "make", "many",
        "might", "must", "need", "never", "often", "once", "only", "other", "over", "said", "same",
        "should", "since", "some", "still", "such", "take", "than", "that", "them", "then", "there",
        "these", "they", "this", "those", "though", "through", "under", "very", "was", "well", "were",
        "what", "when", "where", "which", "while", "with", "within", "without", "work", "world",
        "would", "year", "years", "you", "your", "yours", "yourself", "yourselves",
        # mais palavras comuns em UI
        "enabled", "disabled", "enable", "disable", "enableddisabled",
        "true", "false", "yes", "no", "ok", "cancel", "close", "save", "delete",
        "edit", "add", "remove", "play", "pause", "stop", "next", "previous",
        "shuffle", "repeat", "volume", "mute", "power", "menu", "settings",
        "search", "filter", "sort", "view", "list", "grid", "thumb", "compact",
        "panel", "discovery", "flow", "crossfade", "gapless", "bit", "depth",
        "rate", "sample", "channel", "gain", "limiter", "preamp", "tone",
        "bass", "mid", "treble", "equalizer", "parametric", "peak", "shelf",
        "pass", "notch", "low", "high", "band", "q", "frequency", "hz",
        "khz", "db", "ms", "s", "min", "h", "d", "w", "mo", "y",
        "this", "action", "cannot", "be", "undone", "are", "sure", "want",
        "to", "you", "your", "item", "items", "track", "tracks", "album",
        "albums", "artist", "artists", "playlist", "playlists", "radio",
        "radios", "podcast", "podcasts", "audiobook", "audiobooks", "genre",
        "genres", "song", "songs", "music", "library", "queue", "player",
        "players", "provider", "providers", "server", "client", "account",
        "user", "users", "admin", "guest", "role", "permission", "token",
        "session", "password", "username", "login", "logout", "sign", "in",
        "out", "up", "back", "continue", "complete", "connect", "connected",
        "connecting", "connection", "failed", "error", "success", "successful",
        "loading", "load", "loaded", "refresh", "update", "updated", "updating",
        "create", "created", "creating", "delete", "deleted", "deleting",
        "remove", "removed", "removing", "add", "added", "adding", "edit",
        "edited", "editing", "change", "changed", "changing", "set", "setting",
        "configured", "configuration", "configure", "setup", "install",
        "installed", "installing", "uninstall", "uninstalled", "uninstalling",
        "download", "downloaded", "downloading", "upload", "uploaded",
        "uploading", "import", "imported", "importing", "export", "exported",
        "exporting", "sync", "synced", "syncing", "synchronize", "synchronized",
        "scan", "scanned", "scanning", "search", "searched", "searching",
        "find", "found", "finding", "select", "selected", "selecting",
        "deselect", "deselected", "deselecting", "choose", "chosen", "choosing",
        "pick", "picked", "picking", "clear", "cleared", "clearing",
        "reset", "resetting", "default", "defaults", "restore", "restored",
        "restoring", "copy", "copied", "copying", "paste", "pasted", "pasting",
        "cut", "undo", "redo", "move", "moved", "moving", "drag", "dragged",
        "dragging", "drop", "dropped", "dropping", "resize", "resized",
        "resizing", "rotate", "rotated", "rotating", "zoom", "zoomed",
        "zooming", "scroll", "scrolled", "scrolling", "swipe", "swiped",
        "swiping", "tap", "tapped", "tapping", "click", "clicked", "clicking",
        "press", "pressed", "pressing", "hold", "held", "holding", "release",
        "released", "releasing", "hover", "hovered", "hovering", "focus",
        "focused", "focusing", "blur", "blurred", "blurring", "activate",
        "activated", "activating", "deactivate", "deactivated", "deactivating",
        "show", "shown", "showing", "hide", "hidden", "hiding", "display",
        "displayed", "displaying", "visible", "visibility", "invisible",
        "opacity", "transparent", "translucent", "opaque", "color", "colors",
        "background", "foreground", "border", "borders", "margin", "margins",
        "padding", "paddings", "width", "height", "size", "sizes", "length",
        "position", "positions", "top", "bottom", "left", "right", "center",
        "middle", "upper", "lower", "inner", "outer", "front", "rear",
        "horizontal", "vertical", "diagonal", "radial", "linear", "circular",
        "rectangular", "square", "round", "rounded", "sharp", "blunt",
        "smooth", "rough", "flat", "curved", "straight", "thick", "thin",
        "bold", "light", "heavy", "soft", "hard", "solid", "dashed",
        "dotted", "double", "groove", "ridge", "inset", "outset", "none",
        "hidden", "visible", "collapse", "separate", "auto", "normal",
        "reverse", "alternate", "forwards", "backwards", "both", "infinite",
        "initial", "inherit", "unset", "revert", "all", "unset", "default",
        "initial", "inherit", "unset", "revert", "all", "none", "hidden",
    }
    count_eng = 0
    for w in words_pt:
        w_lower = w.lower()
        if w_lower in english_common and w_lower not in TECH_TERMS and len(w_lower) > 2:
            count_eng += 1
    # se há pelo menos 2 palavras inglesas comuns, consideramos misturado
    # exceto se o en for muito curto ou o pt for quase todo técnico
    if count_eng >= 2:
        return True
    # Outro critério: se há substring inglesa longa preservada do en
    en_words = re.findall(r"[a-zA-Z]{4,}", text_en)
    for ew in en_words:
        if ew.lower() not in TECH_TERMS and ew.lower() in text_pt.lower():
            # verifica se não é parte de uma palavra maior em pt
            # simples: se a palavra aparece isolada
            if re.search(r'\b' + re.escape(ew) + r'\b', text_pt, re.IGNORECASE):
                return True
    return False


# Mapeamento de categorias
CATEGORY_RULES = [
    ("login", lambda k: k.startswith("login.") or k.startswith("auth.") or k.startswith("remote.")),
    ("settings", lambda k: k.startswith("settings.")),
    ("player", lambda k: k.startswith("player_") or k.startswith("players") or k.startswith("player.") or k in {
        "all_players", "all_groups", "currently_playing_players", "no_player_playing",
        "no_player", "power_on_player", "power_off_player", "powered_off_players",
        "sync_player_with", "open_player_settings", "select_repeat_mode", "repeat_mode",
        "shuffle_disable", "shuffle_enable", "dont_stop_the_music_enable", "dont_stop_the_music_disable",
        "open_dsp_settings", "dsp_active", "volume_normalization", "play_now_replace",
        "streamdetails", "player_options", "select_sound_mode", "player_tip",
        "stop_playback", "volume_normalization_gain_correction",
    } or k.startswith("streamdetails.") or k.startswith("player_options.") or k.startswith("player_tip.")),
    ("queue", lambda k: k.startswith("queue") or k.startswith("queue_option.") or k in {
        "transfer_queue", "save_queue_as_playlist", "play_replace_next", "all_enqueue_options",
        "music_assistant_source", "music_assistant_library", "enqueue", "play_now_replace",
    }),
    ("library", lambda k: k in {
        "library", "add_library", "remove_library", "confirm_library_remove",
        "item_in_library", "check_item_in_library", "recently_played", "in_progress_items",
    } or k.startswith("recommendations.")),
    ("artists", lambda k: k.startswith("artist") and not k.startswith("artist_name")),
    ("albums", lambda k: k.startswith("album")),
    ("tracks", lambda k: k.startswith("track")),
    ("playlists", lambda k: k.startswith("playlist") or k in {
        "add_playlist", "remove_playlist", "create_playlist", "new_playlist_name",
        "open_playlist", "save_queue_as_playlist", "import_playlist", "import_playlist_title",
        "import_playlist_invalid_file", "import_playlist_search_providers", "export_playlist",
    }),
    ("radio", lambda k: k.startswith("radio") or k.startswith("radiobrowser_") or k in {
        "play_radio", "radios",
    }),
    ("podcasts", lambda k: k.startswith("podcast")),
    ("audiobooks", lambda k: k.startswith("audiobook") or k.startswith("chapter") or k in {
        "authors", "narrators", "series_plural", "series_singular", "collection", "collections",
    }),
    ("search", lambda k: k.startswith("search") or k in {
        "try_global_search", "type_to_search", "global_search", "topresult",
    }),
    ("notifications", lambda k: k.startswith("notification") or k in {
        "show_info",
    }),
    ("errors", lambda k: k.startswith("error") or k.endswith("_failed") or k.endswith("_error") or "invalid" in k or k in {
        "connection_failed", "login_failed", "login_error", "setup_failed", "setup_error",
        "uri_copy_failed", "search_failed", "add_alias_failed", "link_alias_failed",
        "promote_alias_failed", "remove_alias_failed", "merge_genres_failed",
        "genre_add_failed", "link_to_genre_failed", "playlist_create_provider_error",
        "playlist_create_no_type_selected", "no_log_output", "scanner_status_failed",
        "scan_trigger_failed", "restore_defaults_failed", "full_restore_failed",
        "error_loading_genres", "player_needs_setup", "provider_requires_attention",
        "provider_requires_attention_detail", "qr_failed", "qr_camera_error",
        "token_create_failed", "token_revoke_failed", "session_revoke_failed",
        "password_change_failed", "user_create_failed", "user_update_failed",
        "user_delete_failed", "user_disable_failed", "user_enable_failed",
        "token_copy_failed", "background_tasks.history_clear_failed",
        "background_task.toast.run_failed", "background_task.toast.schedule_enable_failed",
        "background_task.toast.schedule_disable_failed", "background_task.toast.schedule_update_failed",
        "background_task.toast.retry_failed", "background_task.toast.cancel_failed",
        "background_task.toast.remove_failed", "background_task.toast.log_load_failed",
        "background_task.toast.log_copy_failed", "remote_access_error_loading",
        "remote_access_error_toggle", "remote_access_error_copy",
        "no_player_access", "no_player_access_detail", "nothing_playing",
        "guest_access_disabled", "link_copy_fail", "add_to_queue_failed",
        "load_artist_tracks_failed", "boost_disabled", "skip_disabled",
        "skip_failed", "guest_access_toggle_failed", "qr_failed",
    }),
    ("actions", lambda k: k in {
        "actions", "add", "add_alias", "add_genre", "add_library", "add_playlist",
        "add_queue", "add_url_item", "cancel", "clear_selection", "close",
        "create", "delete", "delete_db", "delete_genre", "delete_genres",
        "edit", "edit_playlist", "edit_radio", "edit_track", "enable", "disable",
        "export_playlist", "import_playlist", "link", "link_alias", "link_to_genre",
        "map_provider_mapping", "mark_played", "mark_unplayed", "merge_genres",
        "move", "play", "play_album_from", "play_from_here", "play_next",
        "play_now", "play_now_replace", "play_playlist_from", "play_replace",
        "play_replace_next", "power_off_player", "power_on_player", "promote",
        "promote_alias", "refresh", "refresh_item", "remove", "remove_alias",
        "remove_genre_exclusion", "remove_library", "remove_playlist",
        "remove_provider_mapping", "save", "save_changes", "save_queue_as_playlist",
        "search", "search_all_providers", "select_all", "select_players",
        "select_providers", "select_repeat_mode", "select_sound_mode",
        "select_source", "select_target_genre", "sendspin_static_delay",
        "show_advanced_settings", "show_info", "show_select_boxes", "shuffle",
        "shuffle_disable", "shuffle_enable", "skip", "sort", "stop_playback",
        "sync_now", "transfer_queue", "try_global_search", "update_metadata",
        "update_password", "view", "view_players", "view_songs", "sync_player_with",
    } or k.startswith("action") or k.endswith("_action")),
    ("common", lambda k: True),  # catch-all
]


def get_category(key):
    for cat, rule in CATEGORY_RULES:
        if rule(key):
            return cat
    return "common"


def main():
    en = load_json(EN_PATH)
    pt = load_json(PT_PATH)

    flat_en = flatten(en)
    flat_pt = flatten(pt)

    keys_en = set(flat_en.keys())
    keys_pt = set(flat_pt.keys())

    missing_pt = keys_en - keys_pt
    extra_pt = keys_pt - keys_en

    identical = []
    mixed = []
    placeholder_issues = []

    for k in keys_en & keys_pt:
        v_en = flat_en[k]
        v_pt = flat_pt[k]
        if v_en == v_pt:
            identical.append(k)
        elif is_mixed(v_en, v_pt):
            mixed.append(k)
        ph_en = extract_placeholders(v_en)
        ph_pt = extract_placeholders(v_pt)
        if ph_en != ph_pt:
            placeholder_issues.append((k, ph_en, ph_pt))

    # Agrupar por categoria
    cat_stats = defaultdict(lambda: {
        "total_en": 0, "total_pt": 0,
        "missing": [], "extra": [],
        "identical": [], "mixed": [], "placeholder": [],
    })

    for k in keys_en:
        cat = get_category(k)
        cat_stats[cat]["total_en"] += 1
        if k in keys_pt:
            cat_stats[cat]["total_pt"] += 1
        else:
            cat_stats[cat]["missing"].append(k)

    for k in keys_pt:
        cat = get_category(k)
        if k not in keys_en:
            cat_stats[cat]["extra"].append(k)

    for k in identical:
        cat = get_category(k)
        cat_stats[cat]["identical"].append(k)

    for k in mixed:
        cat = get_category(k)
        cat_stats[cat]["mixed"].append(k)

    for k, ph_en, ph_pt in placeholder_issues:
        cat = get_category(k)
        cat_stats[cat]["placeholder"].append((k, ph_en, ph_pt))

    # Gerar relatório
    lines = []
    lines.append("# Relatório de Auditoria de Tradução – TSi MUSIC Frontend")
    lines.append("")
    lines.append("**Arquivos analisados:**")
    lines.append(f"- `en.json`: {len(keys_en)} chaves")
    lines.append(f"- `pt_BR.json`: {len(keys_pt)} chaves")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Resumo Global")
    lines.append("")
    lines.append("| Métrica | Valor |")
    lines.append("|---------|-------|")
    lines.append(f"| Total de chaves em `en.json` | {len(keys_en)} |")
    lines.append(f"| Total de chaves em `pt_BR.json` | {len(keys_pt)} |")
    lines.append(f"| Chaves faltantes em `pt_BR.json` | {len(missing_pt)} |")
    lines.append(f"| Chaves extras em `pt_BR.json` | {len(extra_pt)} |")
    lines.append(f"| Chaves idênticas (não traduzidas) | {len(identical)} |")
    lines.append(f"| Chaves com texto misturado pt/en | {len(mixed)} |")
    lines.append(f"| Chaves com placeholders mal formatados | {len(placeholder_issues)} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Seções
    sections_order = [
        "login", "settings", "player", "queue", "library",
        "artists", "albums", "tracks", "playlists", "radio",
        "podcasts", "audiobooks", "search", "notifications",
        "errors", "actions", "common",
    ]

    for sec in sections_order:
        stats = cat_stats.get(sec, {"total_en":0, "total_pt":0, "missing":[], "extra":[], "identical":[], "mixed":[], "placeholder":[]})
        total_en = stats["total_en"]
        total_pt = stats["total_pt"]
        missing = stats["missing"]
        extra = stats["extra"]
        ident = stats["identical"]
        mix = stats["mixed"]
        ph = stats["placeholder"]
        problems = len(missing) + len(extra) + len(ident) + len(mix) + len(ph)

        if total_en == 0 and total_pt == 0:
            status = "❌ ausente"
        elif len(missing) == 0 and len(ident) == 0 and len(mix) == 0 and len(ph) == 0 and len(extra) == 0:
            status = "✅ completo"
        elif len(missing) == 0 and problems <= 5:
            status = "⚠️ parcial"
        else:
            status = "⚠️ parcial"

        lines.append(f"## {sec.capitalize()}")
        lines.append("")
        lines.append(f"**Status:** {status}")
        lines.append("")
        lines.append("| Métrica | Valor |")
        lines.append("|---------|-------|")
        lines.append(f"| Chaves em en.json | {total_en} |")
        lines.append(f"| Chaves em pt_BR.json | {total_pt} |")
        lines.append(f"| Faltantes | {len(missing)} |")
        lines.append(f"| Extras | {len(extra)} |")
        lines.append(f"| Não traduzidas (idênticas) | {len(ident)} |")
        lines.append(f"| Texto misturado pt/en | {len(mix)} |")
        lines.append(f"| Placeholders mal formatados | {len(ph)} |")
        lines.append(f"| **Total de problemas** | **{problems}** |")
        lines.append("")

        if missing:
            lines.append("### Exemplos de chaves faltantes")
            for k in missing[:10]:
                lines.append(f"- `{k}` → `{flat_en[k]}`")
            if len(missing) > 10:
                lines.append(f"- ... e mais {len(missing)-10} chaves")
            lines.append("")

        if ident:
            lines.append("### Exemplos de não traduzidas (idênticas)")
            for k in ident[:10]:
                lines.append(f"- `{k}` → `{flat_en[k]}`")
            if len(ident) > 10:
                lines.append(f"- ... e mais {len(ident)-10} chaves")
            lines.append("")

        if mix:
            lines.append("### Exemplos de texto misturado pt/en")
            for k in mix[:10]:
                lines.append(f"- `{k}` → `pt_BR: {flat_pt[k]}` (en: `{flat_en[k]}`)")
            if len(mix) > 10:
                lines.append(f"- ... e mais {len(mix)-10} chaves")
            lines.append("")

        if ph:
            lines.append("### Exemplos de placeholders mal formatados")
            for k, ph_en, ph_pt in ph[:10]:
                lines.append(f"- `{k}` → en: `{ph_en}` | pt: `{ph_pt}`")
            if len(ph) > 10:
                lines.append(f"- ... e mais {len(ph)-10} chaves")
            lines.append("")

        if extra:
            lines.append("### Exemplos de chaves extras (não existem em en.json)")
            for k in extra[:10]:
                lines.append(f"- `{k}` → `{flat_pt[k]}`")
            if len(extra) > 10:
                lines.append(f"- ... e mais {len(extra)-10} chaves")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Detalhes completos em seções colapsáveis (opcional, mas útil)
    lines.append("## Detalhes Completos")
    lines.append("")

    if missing_pt:
        lines.append("### Todas as chaves faltantes em pt_BR.json")
        for k in sorted(missing_pt):
            lines.append(f"- `{k}`")
        lines.append("")

    if extra_pt:
        lines.append("### Todas as chaves extras em pt_BR.json")
        for k in sorted(extra_pt):
            lines.append(f"- `{k}`")
        lines.append("")

    if identical:
        lines.append("### Todas as chaves idênticas")
        for k in sorted(identical):
            lines.append(f"- `{k}` → `{flat_en[k]}`")
        lines.append("")

    if mixed:
        lines.append("### Todas as chaves com texto misturado")
        for k in sorted(mix):
            lines.append(f"- `{k}` → pt: `{flat_pt[k]}` | en: `{flat_en[k]}`")
        lines.append("")

    if placeholder_issues:
        lines.append("### Todas as chaves com placeholders mal formatados")
        for k, ph_en, ph_pt in sorted(placeholder_issues, key=lambda x: x[0]):
            lines.append(f"- `{k}` → en: `{ph_en}` | pt: `{ph_pt}`")
        lines.append("")

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Relatório salvo em {OUT_PATH}")
    print(f"Total en: {len(keys_en)}, pt: {len(keys_pt)}")
    print(f"Missing: {len(missing_pt)}, Extra: {len(extra_pt)}, Identical: {len(identical)}, Mixed: {len(mixed)}, Placeholder: {len(placeholder_issues)}")


if __name__ == "__main__":
    main()
