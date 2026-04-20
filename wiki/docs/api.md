# Referência de API

> Endpoints e protocolos de comunicação do TSi MUSIC com o Music Assistant Server.

---

## Endpoints HTTP

### `GET /info`

Retorna informações do servidor para auto-detecção pelo frontend.

**Resposta:**
```json
{
  "server_version": "2.8.5",
  "status": "running",
  "server_id": "..."
}
```

**Uso:**
```bash
curl -Ik https://100.86.64.1:8443/info
```

---

### `GET /imageproxy`

Proxy para imagens e capas de álbuns do Stream Server.

**Parâmetros:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `path` | string | Caminho do recurso |
| `provider` | string | ID do provider (ex: `filesystem_local`) |
| `size` | int | Tamanho da imagem em pixels |

**Exemplo:**
```bash
curl -Ik "https://100.86.64.1:8443/imageproxy?path=test_sound.mp3&provider=filesystem_local&size=128"
```

---

### `GET /preview`

Proxy para pré-visualizações de áudio do Stream Server.

**Exemplo:**
```bash
curl -Ik https://100.86.64.1:8443/preview?path=...
```

---

## WebSocket API

### Conexão

```
wss://100.86.64.1:8443/ws
```

O frontend se conecta ao MA Server via WebSocket através do proxy nginx. A conexão é segura (WSS) e resolve o problema de mixed content.

### Teste de Conexão

```python
import asyncio, websockets, ssl, json

async def test():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    async with websockets.connect('wss://100.86.64.1:8443/ws', ssl=ctx) as ws:
        msg = await asyncio.wait_for(ws.recv(), timeout=5)
        data = json.loads(msg)
        print(f"Server: {data.get('server_version')}, Status: {data.get('status')}")

asyncio.run(test())
```

---

## Sendspin Streaming

### Conexão

```
wss://100.86.64.1:8443/sendspin
```

Protocolo WebSocket para streaming de áudio no navegador (web player).

---

## Tabela de Endpoints

| Endpoint | Método | Destino | Descrição |
|----------|--------|---------|-----------|
| `/info` | GET | `172.18.0.1:8095/info` | Auto-detecção do servidor |
| `/ws` | WebSocket | `172.18.0.1:8095/ws` | API principal do MA |
| `/sendspin` | WebSocket | `172.18.0.1:8095/sendspin` | Streaming de áudio no navegador |
| `/imageproxy` | GET | `172.18.0.1:8097` | Imagens e capas |
| `/preview` | GET | `172.18.0.1:8097` | Pré-visualizações de áudio |

---

## Snapcast API (JSON-RPC)

### Status do Servidor

```bash
curl -s http://172.18.0.1:1780/jsonrpc \
  -X POST -d '{"jsonrpc":"2.0","method":"Server.GetStatus","id":1}'
```

### Verificar Nodes PipeWire

```bash
pw-cli ls Node | grep -E "Snapcast|alsa_output"
```

### Verificar Links de Áudio

```bash
pw-link -l | grep -E "Snapcast|alsa_output"
```

---

## Providers de Músia

| Provider | ID | Tipo |
|----------|-----|------|
| Músicas Locais | `filesystem_local` | Sistema de arquivos |
| Spotify | `spotify` | Streaming |
| Spotify Connect | `spotify_connect` | Streaming |
| AirPlay | `airplay` | Streaming |
| Snapcast | `snapcast` | Multi-room audio |
| Radio Browser | `radiobrowser` | Rádio online |

---

## Comandos WebSocket Comuns

O Music Assistant expõe uma API rica via WebSocket. Os comandos mais utilizados pelo frontend incluem:

| Comando | Descrição |
|---------|-----------|
| `players/all` | Lista todos os players |
| `player_queues/all` | Lista todas as filas |
| `music/tracks` | Lista tracks da biblioteca |
| `music/albums` | Lista álbuns |
| `music/artists` | Lista artistas |
| `player/play` | Inicia playback |
| `player/pause` | Pausa playback |
| `player/next` | Próxima faixa |
| `player/previous` | Faixa anterior |
| `player/volume_set` | Define volume |

Para a documentação completa da API do Music Assistant, consulte o [repositório oficial](https://github.com/music-assistant/server).

---

> 🏷️ `#TSiMUSIC` `#API` `#WebSocket` `#Music-Assistant`
