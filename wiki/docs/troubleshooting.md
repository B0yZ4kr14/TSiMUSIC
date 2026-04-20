# Troubleshooting

> Problemas comuns e soluções para o TSi MUSIC em produção.

---

## Diagnóstico Rápido

Antes de qualquer troubleshooting, execute os comandos básicos de diagnóstico:

```bash
# Verificar containers
docker ps --filter name=ma-wiki --filter name=music-assistant

# Verificar logs do MA
docker logs music-assistant-server --tail 50

# Verificar status do snapserver
curl -s http://172.18.0.1:1780/jsonrpc \
  -X POST -d '{"jsonrpc":"2.0","method":"Server.GetStatus","id":1}'

# Verificar pipewire
pactl info
pw-cli ls Node | grep -E "state|node.name"
```

---

## ❌ "Não consigo fazer login / frontend não conecta"

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

**Solução:**
1. Verifique se o `nginx.conf` possui as configurações de proxy para `/ws`, `/sendspin`, `/imageproxy`
2. Verifique se o container foi reiniciado após mudanças no nginx
3. Verifique as regras de firewall (nftables) para a rede Docker

---

## 🔇 "Player selecionado mas não ouço áudio"

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
3. Verifique o volume do ALSA:
   ```bash
   pactl list sinks | grep Volume
   ```

---

## 🚫 "Mixed content blocked"

**Sintoma:** Console do navegador mostra erro de mixed content ao tentar conectar a `ws://...`

**Causa:** Frontend HTTPS tentando conectar a WebSocket não seguro.

**Solução:** O nginx proxy já resolve isso. O frontend deve se conectar a `wss://100.86.64.1:8443/ws` (detectado automaticamente via `/info`).

---

## 🔐 "Permission denied (publickey)" no CI

```bash
# Verifique se a chave pública está no authorized_keys do servidor
ssh -i ~/.ssh/id_ed25519_midiaserver tsi@100.86.64.1 "cat ~/.ssh/authorized_keys"

# Verifique permissões
ssh tsi@100.86.64.1 "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
```

---

## ❌ "Health check falhou"

```bash
# No servidor, verifique logs do container
ssh tsi@100.86.64.1 "docker logs ma-wiki --tail 50"

# Verifique se o nginx está rodando
ssh tsi@100.86.64.1 "docker exec ma-wiki ps aux | grep nginx"

# Teste localmente no servidor
curl -Ik https://localhost:8443/info
```

---

## 📦 "Rsync falhou com código 23"

Código 23 = erro parcial de transferência. Geralmente permissões no diretório remoto:

```bash
ssh tsi@100.86.64.1 "sudo chown -R tsi:tsi /home/tsi/docker/ma-wiki"
```

---

## 🐳 Container não reinicia após mudança no nginx.conf

```bash
# Reinicie manualmente
ssh tsi@100.86.64.1 "cd /home/tsi/docker/ma-wiki && docker compose restart"
```

---

## 🔥 Firewall bloqueando conexões Docker

**Sintoma:** Containers Docker não conseguem acessar portas do host.

**Verificação:**
```bash
sudo nft list chain ip filter ufw-user-input | grep 172.18
```

**Solução:**
```bash
sudo nft add rule ip filter ufw-user-input ip saddr 172.18.0.0/16 tcp dport 8095 accept
sudo nft add rule ip filter ufw-user-input ip saddr 172.18.0.0/16 tcp dport 8097 accept
sudo nft add rule ip filter ufw-user-input ip saddr 172.18.0.0/16 tcp dport 8927 accept
```

---

## 🧪 Dry-run para Diagnóstico

```bash
# Local
./scripts/deploy.sh --dry-run

# Ver o que seria alterado sem aplicar
```

---

## 📊 Verificar Biblioteca MA

```bash
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

### v2.9.5 — Correções de Infraestrutura

**Problema:** Frontend não conseguia se conectar ao MA Server devido a mixed content.

**Causa raiz:**
1. nginx não proxyava endpoints do MA (`/ws`, `/sendspin`, `/imageproxy`)
2. Firewall nftables bloqueava conexões da rede Docker `172.18.0.0/16`

**Correções aplicadas:**
1. ✅ nginx.conf atualizado com 5 location blocks de proxy
2. ✅ Regras nftables adicionadas para rede docker
3. ✅ Container nginx reiniciado
4. ✅ Testes de validação: `/info`, `/ws`, `/sendspin`, `/imageproxy` — todos funcionando

---

> 🏷️ `#TSiMUSIC` `#Troubleshooting` `#MidiaServer-SaudeClinica`
