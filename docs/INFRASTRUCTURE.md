# 🏗️ TSi MUSIC — Infraestrutura de Produção

> Documentação técnica completa da infraestrutura do TSi MUSIC em produção no `MidiaServer-SaudeClinica`.
> **Data:** 2026-04-19 | **Versão:** v2.9.5

---

## 📋 Sumário

- [Arquitetura de Rede](#arquitetura-de-rede)
- [Container Docker — `ma-wiki`](#container-docker--ma-wiki)
- [Music Assistant Server](#music-assistant-server)
- [Nginx Proxy Configuration](#nginx-proxy-configuration)
- [Firewall (nftables/ufw)](#firewall-nftablesufw)
- [Audio Pipeline](#audio-pipeline)
- [Diagnóstico e Troubleshooting](#diagnóstico-e-troubleshooting)
- [Histórico de Correções](#histórico-de-correções)

---

## 🌐 Arquitetura de Rede

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

### Endereços e Portas

| Serviço | Host | Porta | Protocolo | Descrição |
|---------|------|-------|-----------|-----------|
| TSi MUSIC Frontend | `100.86.64.1` | `8443` | HTTPS | Nginx + build estático |
| TSi MUSIC Frontend | `100.86.64.1` | `8080` | HTTP | Redirect → HTTPS |
| MA WebSocket API | `172.18.0.1` | `8095` | WS/WSS | API principal (via proxy) |
| MA Stream Server | `172.18.0.1` | `8097` | HTTP | Imagens e streams (via proxy) |
| MA Sendspin | `172.18.0.1` | `8927` | WS | WebRTC gateway interno |
| Snapserver TCP | `127.0.0.1` | `1705` | TCP | Controle Snapcast |
| Snapserver HTTP | `127.0.0.1` | `1780` | HTTP | API JSON-RPC Snapcast |

---

## 🐳 Container Docker — `ma-wiki`

### Docker Compose

```yaml
services:
  ma-wiki:
    image: nginx:alpine
    container_name: ma-wiki
    restart: unless-stopped
    ports:
      - "8080:80"
      - "8443:443"
    volumes:
      - /home/tsi/docker/ma-wiki:/usr/share/nginx/html:ro
      - /home/tsi/docker/ma-wiki/nginx.conf:/etc/nginx/nginx.conf:ro
```

### Volumes Montados

| Host | Container | Modo | Conteúdo |
|------|-----------|------|----------|
| `/home/tsi/docker/ma-wiki` | `/usr/share/nginx/html` | ro | Build do frontend + certs + nginx.conf |
| `/home/tsi/docker/ma-wiki/nginx.conf` | `/etc/nginx/nginx.conf` | ro | Configuração nginx customizada |

### Certificados SSL

- **Local:** `/home/tsi/docker/ma-wiki/certs/`
- `tailscale.crt` — Certificado Tailscale HTTPS
- `tailscale.key` — Chave privada Tailscale

---

## 🎵 Music Assistant Server

### Container

```bash
docker run -d \
  --name music-assistant-server \
  --privileged \
  -v /home/tsi/docker/music-assistant/data:/data \
  -v /home/tsi/Music/local:/music:ro \
  -v /run/user/1000/pulse:/run/user/1000/pulse \
  -v /dev/snd:/dev/snd \
  -p 8095:8095 \
  -p 8097:8097 \
  -p 8927:8927 \
  music-assistant-server
```

### Providers Configurados

| Provider | Domínio | Status | Configuração |
|----------|---------|--------|--------------|
| Músicas Locais | `filesystem_local` | ✅ | Path: `/music` |
| Spotify | `spotify` | ✅ | Logado como "saúde clínica odontologia" |
| Spotify Connect | `spotify_connect` | ✅ | — |
| AirPlay | `airplay` | ✅ | — |
| Snapcast | `snapcast` | ✅ | — |
| Radio Browser | `radiobrowser` | ✅ | — |

### Players Registrados

| ID | Nome | Provider | Estado |
|----|------|----------|--------|
| `up007d4d298faf` | Music Assistant | `universal_player` | idle |
| `ma_t5ttov45na` | Web (Chrome on Linux) | `sendspin` | idle |
| `ma_50e549722626` | MidiaServer-SaudeClinica | `snapcast` | idle |

---

## ⚙️ Nginx Proxy Configuration

O nginx atua como **reverse proxy** para o Music Assistant Server, resolvendo o problema de **mixed content** (frontend HTTPS tentando conectar a WS não seguro).

### Arquivo: `deploy/nginx.conf`

```nginx
worker_processes auto;
events { worker_connections 1024; }
http {
    include /etc/nginx/mime.types;
    server_tokens off;
    sendfile on;
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript image/svg+xml;

    server {
        listen 80;
        return 301 https://$host:8443$request_uri;
    }

    server {
        listen 443 ssl;
        ssl_certificate /usr/share/nginx/html/certs/tailscale.crt;
        ssl_certificate_key /usr/share/nginx/html/certs/tailscale.key;
        ssl_protocols TLSv1.2 TLSv1.3;

        root /usr/share/nginx/html;
        index index.html;

        # Proxy WebSocket API — CRÍTICO para funcionamento
        location /ws {
            proxy_pass http://172.18.0.1:8095/ws;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 86400;
        }

        # Proxy Sendspin streaming — CRÍTICO para web player
        location /sendspin {
            proxy_pass http://172.18.0.1:8095/sendspin;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 86400;
        }

        # Proxy stream server (images, previews)
        location /imageproxy {
            proxy_pass http://172.18.0.1:8097;
            proxy_set_header Host $host;
        }

        location /preview {
            proxy_pass http://172.18.0.1:8097;
            proxy_set_header Host $host;
        }

        # Proxy info endpoint — para auto-detecção do frontend
        location /info {
            proxy_pass http://172.18.0.1:8095/info;
            proxy_set_header Host $host;
        }

        # Security Headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

        location ~* \.html$ {
            expires 1d;
            add_header Cache-Control "public, must-revalidate" always;
        }

        location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 7d;
            add_header Cache-Control "public, immutable" always;
        }

        location ~* \.(json|webmanifest)$ {
            expires 1d;
            add_header Cache-Control "public, must-revalidate" always;
        }
    }
}
```

> **⚠️ NOTA:** O IP `172.18.0.1` é o gateway da bridge Docker `ma-wiki_default`. Se a rede Docker for recriada, este IP pode mudar. Nesse caso, atualize o `proxy_pass` no nginx.conf.

---

## 🔥 Firewall (nftables/ufw)

### Regras necessárias para comunicação Docker → Host

O firewall UFW/nftables do host bloqueia por padrão conexões da rede Docker para portas específicas. As seguintes regras foram adicionadas:

```bash
# Permitir acesso da rede docker 172.18.0.0/16 às portas do MA
sudo nft add rule ip filter ufw-user-input ip saddr 172.18.0.0/16 tcp dport 8095 accept
sudo nft add rule ip filter ufw-user-input ip saddr 172.18.0.0/16 tcp dport 8097 accept
sudo nft add rule ip filter ufw-user-input ip saddr 172.18.0.0/16 tcp dport 8927 accept
```

### Verificar regras ativas

```bash
sudo nft list chain ip filter ufw-user-input | grep 172.18
```

---

## 🎧 Audio Pipeline

### Diagrama

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

### Snapserver Config

| Parâmetro | Valor |
|-----------|-------|
| Stream codec | FLAC |
| Sample format | 48000:16:2 |
| Chunk ms | 26 |
| Buffer | 1000 |
| Stream default | `pipe:///tmp/snapfifo` |

### Snapclient

```bash
/usr/bin/snapclient --host 127.0.0.1 --player pipewire
```

### PipeWire Status

```bash
# Verificar nodes
pw-cli ls Node | grep -E "Snapcast|alsa_output"

# Verificar links
pw-link -l | grep -E "Snapcast|alsa_output"

# Verificar volume
pactl list sinks | grep -A 5 "Name: alsa_output"
```

---

## 🔍 Diagnóstico e Troubleshooting

### Problema: "Não consigo fazer login / frontend não conecta"

**Causa provável:** Mixed content ou nginx não proxyando o WebSocket.

**Verificação:**
```bash
# Testar se /info está acessível via nginx
curl -Ik https://100.86.64.1:8443/info
# Esperado: HTTP/2 200

# Testar WebSocket via nginx
python3 -c "
import asyncio, websockets, ssl, json
async def test():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    async with websockets.connect('wss://100.86.64.1:8443/ws', ssl=ctx) as ws:
        msg = await asyncio.wait_for(ws.recv(), timeout=5)
        print(json.loads(msg))
asyncio.run(test())
"
```

**Solução:** Verificar se o nginx.conf possui as configurações de proxy e se o container foi reiniciado.

---

### Problema: "Player selecionado mas não ouço áudio"

**Causa provável:** Queue vazia ou player errado selecionado.

**Verificação via WebSocket:**
```bash
# Conectar ao MA Server e verificar estado
# Command: player_queues/all
# Verificar: items, state, current_item
```

**Players disponíveis:**
- **Web (Chrome on Linux)** → Áudio no navegador (usa Sendspin)
- **MidiaServer-SaudeClinica** → Áudio na saída física (Snapcast → PipeWire → ALSA)

**Solução:**
1. Selecione o player correto no menu de players (ícone 🔊)
2. Adicione música à fila (Biblioteca → Play)
3. Verifique o volume do ALSA: `pactl list sinks | grep Volume`

---

### Problema: "Mixed content blocked"

**Sintoma:** Console do navegador mostra erro de mixed content ao tentar conectar a `ws://...`

**Causa:** Frontend HTTPS tentando conectar a WebSocket não seguro.

**Solução:** O nginx proxy já resolve isso. O frontend deve se conectar a `wss://100.86.64.1:8443/ws` (detectado automaticamente).

---

### Comandos de Diagnóstico Rápido

```bash
# Verificar containers
docker ps --filter name=ma-wiki --filter name=music-assistant

# Verificar logs do MA
docker logs music-assistant-server --tail 50

# Verificar status do snapserver
curl -s http://127.0.0.1:1780/jsonrpc \
  -X POST -d '{"jsonrpc":"2.0","method":"Server.GetStatus","id":1}'

# Verificar pipewire
pactl info
pw-cli ls Node | grep -E "state|node.name"

# Verificar biblioteca MA
ssh saudeclinica 'docker exec music-assistant-server python3 -c "
import sqlite3
conn = sqlite3.connect(\"/data/library.db\")
cur = conn.cursor()
cur.execute(\"SELECT COUNT(*) FROM tracks\")
print(f\"Tracks: {cur.fetchone()[0]}\")
conn.close()
"'
```

---

## 📝 Histórico de Correções

### v2.9.5 — Correções de Infraestrutura (2026-04-19)

**Problema:** Frontend não conseguia se conectar ao MA Server devido a mixed content (HTTPS → WS não seguro).

**Causa raiz:**
1. nginx não proxyava endpoints do MA (`/ws`, `/sendspin`, `/imageproxy`)
2. Firewall nftables bloqueava conexões da rede Docker `172.18.0.0/16` para portas 8095/8097/8927

**Correções aplicadas:**
1. ✅ nginx.conf atualizado com 5 location blocks de proxy
2. ✅ Regras nftables adicionadas para rede docker
3. ✅ Container nginx reiniciado
4. ✅ Testes de validação: `/info`, `/ws`, `/sendspin`, `/imageproxy` — todos funcionando

**Impacto:**
- Auto-detecção do servidor pelo frontend funciona automaticamente
- Web player (Sendspin) funciona sem mixed content
- Imagens/capas carregam corretamente via proxy
- Conexão WebSocket estável via WSS

---

## 🏷️ Tags

`#TSiMUSIC` `#MidiaServer-SaudeClinica` `#infraestrutura` `#nginx` `#docker`
