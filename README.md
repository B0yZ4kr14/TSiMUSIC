# 🎵 TSi MUSIC

> Fork premium do [Music Assistant](https://github.com/music-assistant/frontend) — rebranding, tema glassmorphism, traduções pt_BR e 15+ funcionalidades de UX para o ecossistema **SaúdeClínica**.

[![Deploy Status](https://img.shields.io/badge/deploy-active-success)](https://100.86.64.1:8443/)
[![Vulnerabilities](https://img.shields.io/badge/vulnerabilities-0-success)](./RELEASE-v2.9.4.md)
[![Tests](https://img.shields.io/badge/tests-127%2F127-success)]()
[![pt_BR](https://img.shields.io/badge/tradu%C3%A7%C3%A3o-pt__BR%2096%25-blue)]()

---

## 🚨 AVISO DE SEGURANÇA — LEIA ANTES DE QUALQUER ATUALIZAÇÃO

### ⚠️ NUNCA faça `git merge` ou `git pull` diretamente do repositório upstream `music-assistant/frontend`

Este projeto é um **fork fortemente modificado**. Um merge direto do upstream irá **destruir**:

- Rebranding completo (logo, cores, identidade TSi MUSIC)
- Tema premium CSS (glassmorphism, gradiente roxo `#7c3aed`)
- Traduções pt_BR (1471 chaves, 96% de cobertura)
- 15+ features customizadas (mini player, atalhos, visualizer, PWA, etc.)
- Componentes novos (`AudioVisualizer.vue`, `KeyboardShortcutsHelp.vue`, etc.)
- Service Worker e manifest customizados
- Overrides de segurança no `package.json`

### ✅ Processo seguro de atualização

1. Criar branch de backup
2. `git fetch upstream --no-tags` (nunca merge)
3. `git cherry-pick` seletivo de commits relevantes
4. Resolver conflitos priorizando modificações TSi MUSIC
5. Executar lint, testes e build
6. Validar em staging antes de produção

Para detalhes completos, consulte a documentação de segurança no Obsidian Vault.

---

## ✨ Features

### Tema & Identidade
- 🎨 **Tema premium TSi MUSIC** — glassmorphism, gradiente roxo `#7c3aed`, tipografia Roboto
- 🌙 **Dark mode** nativo com ajustes de contraste premium
- 🖼️ **Rebranding completo** — logos, favicon, OG image, manifest PWA

### Player & Playback
- 🎛️ **Mini Player Mode** — toggle entre modo compacto e completo (tecla `M`)
- 🖥️ **Fullscreen player** com relógio, visualizador e controles estendidos (tecla `F`)
- 🎚️ **Indicador de volume** — overlay animado ao ajustar volume
- 📊 **Barras de equalizador animadas** — feedback visual do playback

### Navegação & UX
- ⌨️ **Atalhos de teclado globais** — espaço, setas, `F`, `M`, `Esc`, `/`, `?`
- ❓ **Ajuda de atalhos** — modal glassmorphism (tecla `?`)
- 🔝 **Scroll-to-top** — botão flutuante com gradiente roxo
- 📶 **Indicador offline** — banner automático ao perder conexão
- 📈 **Barra de progresso global** — durante navegação entre telas

### PWA & Notificações
- 📲 **PWA Install Prompt** — card elegante com cooldown de 7 dias
- 🔔 **Toast notifications** — glassmorphism com acento roxo
- 🏷️ **Título dinâmico da aba** — mostra faixa/artista em playback
- 🎭 **Animações de transição** — fade + slide entre telas

### Áudio & Visual
- 🌊 **Audio Visualizer Canvas** — 64 barras animadas no fullscreen (v2.9.4)
- 🔒 **Security audit** — 10 HIGH → **0 vulnerabilidades** (v2.9.4)

### Internacionalização
- 🇧🇷 **Traduções pt_BR** — 1471/1532 chaves (96%)

---

## 🛠️ Stack Tecnológica

| Tecnologia | Versão |
|------------|--------|
| Vue.js | 3.x (Composition API) |
| TypeScript | Strict mode |
| Vite | Build tool |
| Vuetify + shadcn-vue | UI frameworks |
| Tailwind CSS v4 | Estilização |
| Vue I18n | Internacionalização |
| Vitest | Testes |

---

## 🚀 Comandos de Build

```bash
# Instalar dependências
npm install

# Desenvolvimento
npm run dev          # http://localhost:3000

# Lint
npm run lint

# Testes
npm run test:run     # Todos os testes
npm run test:coverage # Com cobertura

# Build de produção
npm run build        # Saída: music_assistant_frontend/
```

---

## 🐳 Deploy

### Ambiente de Produção

| Configuração | Valor |
|--------------|-------|
| Servidor | `saudeclinica` (Tailscale) |
| URL | `https://100.86.64.1:8443/` |
| Container | `ma-wiki` (nginx:alpine) |
| Portas | `8080:80`, `8443:443` |
| Login | `Admin` / `saude@clinica` |

### Comandos Docker

```bash
# Verificar container
ssh saudeclinica "docker ps --filter name=ma-wiki"

# Build local + deploy
cd /tmp/ma-frontend-valid
npm run build
rsync -avz --delete music_assistant_frontend/ saudeclinica:/caminho/no/servidor/
ssh saudeclinica "docker exec ma-wiki nginx -s reload"

# Verificar status
ssh saudeclinica "docker logs ma-wiki --tail 20"
```

---

## 📝 Release Notes

- [v2.9.4 — Security Fixes + Audio Visualizer](./RELEASE-v2.9.4.md)
- [v2.9.3 — Mini Player + 13 Features UX](./RELEASE-v2.9.3.md)
- [v2.9.2 — Premium Theme + pt_BR](./RELEASE-v2.9.2.md)

---

## 🙏 Créditos

- **Music Assistant** — Projeto original e backend server ([github.com/music-assistant](https://github.com/music-assistant))
- **TSi MUSIC** — Rebranding, tema premium, traduções e features customizadas para SaúdeClínica

---

## 📄 Licença

Este projeto mantém a licença do Music Assistant original. As modificações TSi MUSIC são propriedade do ecossistema SaúdeClínica.

---

> 🏷️ `#TSiMUSIC` `#MidiaServer-SaudeClinica`
