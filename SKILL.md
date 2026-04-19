# TSi MUSIC Frontend Skill

## Overview

Custom branded Music Assistant frontend for TSi MUSIC — a premium Vue 3 + Vuetify music streaming interface with Brazilian Portuguese (pt_BR) localization.

## Version

v2.9.2

## Key Features

- **Brand**: TSi MUSIC (replaced Open Home Foundation / Music Assistant)
- **Primary Color**: `#7c3aed` (violet)
- **UI Framework**: Vue 3 + Vuetify + reka-ui
- **Language**: pt-BR (complete i18n — 1532 keys)
- **Premium CSS**: Glassmorphism, gradient buttons, hover effects, layered shadows
- **PWA**: Service worker with precache (165 entries)
- **Build**: Vite 7.3.2, ~20s build time, 5.4MB output

## Premium CSS Effects

```css
/* Cards */
.v-card, [data-slot="card"] {
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 10px 20px rgba(0,0,0,0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.v-card:hover, [data-slot="card"]:hover {
  transform: translateY(-3px);
}

/* Buttons - Gradient */
.v-btn, [data-slot="button"] {
  background: linear-gradient(135deg, #7c3aed, #6d28d9, #5b21b6);
  border-radius: 8px;
}

/* Sidebar */
.v-navigation-drawer, [data-slot="sidebar"] {
  border-radius: 0 16px 16px 0;
  box-shadow: 4px 0 24px rgba(0,0,0,0.15);
}

/* Glassmorphism */
.v-dialog > .v-overlay__content > .v-card,
[data-slot="dialog-content"] {
  backdrop-filter: blur(12px);
  border-radius: 16px;
}

/* Tab indicator */
.v-tab--selected {
  box-shadow: inset 0 -2px 0 rgba(124, 58, 237, 0.60);
}
```

## Build & Deploy

```bash
cd /tmp/ma-frontend-valid
npm run build                    # Build to music_assistant_frontend/
sed -i 's/lang="en"/lang="pt-BR"/' music_assistant_frontend/index.html
tar czf ma-frontend.tar.gz music_assistant_frontend/

# Deploy to saudeclinica
scp ma-frontend.tar.gz saudeclinica:/tmp/
ssh saudeclinica 'cd /home/tsi/docker/ma-wiki && rm -rf assets/* *.html *.js && tar xzf /tmp/ma-frontend.tar.gz && cp -r music_assistant_frontend/* .'
```

## Environment

- **Server**: saudeclinica (100.86.64.1 via Tailscale)
- **Frontend**: https://100.86.64.1:8443/
- **Wiki**: https://100.86.64.1:8443/wiki/
- **Music Assistant Server**: music-assistant-server:8095

## Monitors

- `tsimusic-monitor-check.timer` — every 5 minutes
- `tsimusic-backup.timer` — daily at 04:00
- `tsimusic-pipeline.timer` — daily at 03:00

## Changelog

### [2.9.2] — 2026-04-18
- Complete pt_BR translation (1532 keys)
- Premium CSS with glassmorphism and gradients
- TSi MUSIC branding throughout
- Removed all Open Home Foundation references
- Fixed VitePWA manifest configuration
- Added OG meta tags and favicon.svg


## Release v2.9.2 — 2026-04-19

### Validação Premium Completa
- 4 squads orquestrados em paralelo
- Login MA realizado (Admin/saude@clinica)
- 10 screenshots capturados (dashboard, sidebar, configurações, about, player)

### Resultados da Validação
| Critério | Status |
|----------|--------|
| Logo TSi MUSIC | ✅ Todas as telas |
| Cor primária #7c3aed | ✅ Botões, tabs, indicators |
| Cards premium | ✅ border-radius 12px + hover lift |
| Sidebar pt-BR | ✅ Menu completo em português |
| Configurações pt-BR | ✅ 100% traduzido |
| CSS dashboard coverage | ✅ 100% componentes Vuetify |
| Glassmorphism | ✅ Dialogs, overlays, bottom-nav |

### Traduções
- 1532 chaves totais
- 1471 traduzidas (96%)
- 61 termos técnicos/gêneros mantidos em inglês

### Deploy
- Build: ~20s, 165 precache entries
- Deploy: saudeclinica (100.86.64.1:8443)
- Status: HTTP 200, container healthy
