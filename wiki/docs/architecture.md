# Arquitetura do Sistema

> Visão técnica completa da arquitetura do TSi MUSIC em produção no `MidiaServer-SaudeClinica`.

---

## Diagrama de Rede

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TSi MUSIC — Arquitetura de Rede                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   [Cliente]                    [Tailscale]              [MidiaServer]        │
│   Navegador/Chrome ──────────► 100.86.64.1:8443 ─────► nginx:443 (ma-wiki)  │
│                                                                              │
│   nginx proxy:                                                               │
│   ├── /ws        ──proxy──► MA Server :8095/ws      (WebSocket API)         │
│   ├── /sendspin  ──proxy──► MA Server :8095/sendspin (Sendspin streaming)   │
│   ├── /imageproxy──proxy──► Stream Server :8097     (imagens/capas)        │
│   ├── /preview   ──proxy──► Stream Server :8097     (pré-visualizações)    │
│   └── /info      ──proxy──► MA Server :8095/info    (auto-detecção)        │
│                                                                              │
│   MA Server (docker: music-assistant-server)                                 │
│   ├── Porta 8095: WebSocket API + HTTP                                       │
│   ├── Porta 8097: Stream Server (imagens, áudio)                             │
│   ├── Porta 8927: Sendspin (WebRTC/streaming interno)                        │
│   └── /music:     Volume bind para /home/tsi/Music/local                     │
│                                                                              │
│   Audio Pipeline:                                                            │
│   MA Server ──► Snapserver (:1705) ──► /tmp/snapfifo ──► Snapclient         │
│   Snapclient (pipewire output) ──► PipeWire ──► ALSA ──► Caixas de som      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Endereços e Portas

| Serviço | Host | Porta | Protocolo | Descrição |
|---------|------|-------|-----------|-----------|
| TSi MUSIC Frontend | `100.86.64.1` | `8443` | HTTPS | Nginx + build estático |
| TSi MUSIC Frontend | `100.86.64.1` | `8080` | HTTP | Redirect → HTTPS |
| MA WebSocket API | `172.18.0.1` | `8095` | WS/WSS | API principal (via proxy) |
| MA Stream Server | `172.18.0.1` | `8097` | HTTP | Imagens e streams (via proxy) |
| MA Sendspin | `172.18.0.1` | `8927` | WS | WebRTC gateway interno |
| Snapserver TCP | `172.18.0.1` | `1705` | TCP | Controle Snapcast |
| Snapserver HTTP | `172.18.0.1` | `1780` | HTTP | API JSON-RPC Snapcast |

---

## Componentes

### 1. Frontend (TSi MUSIC)

- **Tecnologia:** Vue 3 + TypeScript + Vite
- **Build:** Saída estática em `music_assistant_frontend/`
- **Deploy:** Sincronizado via rsync para o servidor
- **PWA:** Suporte completo com service worker, manifest e ícones customizados

### 2. Nginx Reverse Proxy (`ma-wiki`)

- **Imagem:** `nginx:alpine`
- **Função:** Servir o frontend estático + proxyar endpoints do MA Server
- **SSL:** Certificados duplos (Tailscale LE + self-signed para IP)
- **Portas:** `8080` (HTTP) e `8443` (HTTPS)

### 3. Music Assistant Server

- **Container:** `music-assistant-server`
- **Modo:** Privilegiado (acesso a `/dev/snd` e PipeWire)
- **Volumes:**
  - `/data` — dados do MA
  - `/music` — biblioteca local (read-only)
  - `/run/user/1000/pulse` — PipeWire/PulseAudio
  - `/dev/snd` — dispositivos de áudio

### 4. Audio Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  MA Server  │───►│  Snapserver │───►│   Snapfifo  │───►│  Snapclient │───►│  PipeWire   │
│  (docker)   │    │  (port 1705)│    │  (/tmp/...) │    │  (pipewire) │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘
                                                                                    │
                                                                                    ▼
                                                                             ┌─────────────┐
                                                                             │    ALSA     │
                                                                             │  (HDA Intel)│
                                                                             └──────┬──────┘
                                                                                    │
                                                                                    ▼
                                                                             ┌─────────────┐
                                                                             │ Caixas Som  │
                                                                             └─────────────┘
```

| Parâmetro | Valor |
|-----------|-------|
| Stream codec | FLAC |
| Sample format | 48000:16:2 |
| Chunk ms | 26 |
| Buffer | 1000 |
| Stream default | `pipe:///tmp/snapfifo` |

### 5. Tailscale

- **Função:** VPN mesh para acesso seguro ao servidor
- **IP do servidor:** `100.86.64.1`
- **Hostname:** `midiaserver-saudeclinica.tailbda57.ts.net`

---

## Fluxo de Dados

1. **Cliente** acessa `https://100.86.64.1:8443/` via Tailscale
2. **Nginx** serve o frontend estático (Vue app)
3. **Frontend** detecta o MA Server via `/info`
4. **WebSocket** `/ws` conecta frontend ao MA Server via proxy nginx
5. **Streaming** `/sendspin` entrega áudio ao navegador
6. **Imagens** `/imageproxy` carrega capas e artes
7. **Áudio físico** MA Server → Snapserver → Snapclient → PipeWire → ALSA → caixas

---

## Providers de Música

| Provider | Domínio | Status | Configuração |
|----------|---------|--------|--------------|
| Músicas Locais | `filesystem_local` | ✅ | Path: `/music` |
| Spotify | `spotify` | ✅ | Logado |
| Spotify Connect | `spotify_connect` | ✅ | — |
| AirPlay | `airplay` | ✅ | — |
| Snapcast | `snapcast` | ✅ | — |
| Radio Browser | `radiobrowser` | ✅ | — |

---

## Players Registrados

| ID | Nome | Provider | Estado |
|----|------|----------|--------|
| `up007d4d298faf` | Music Assistant | `universal_player` | idle |
| `ma_t5ttov45na` | Web (Chrome on Linux) | `sendspin` | idle |
| `ma_50e549722626` | MidiaServer-SaudeClinica | `snapcast` | idle |
