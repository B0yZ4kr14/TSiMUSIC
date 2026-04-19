# TSi MUSIC v2.9.5 — Correções de Infraestrutura

**Data:** 2026-04-19
**Status:** ✅ Deployed
**Acesso:** https://100.86.64.1:8443/

---

## 🎯 Destaques

- **Infraestrutura:** Nginx reverse proxy para endpoints do Music Assistant Server
- **Firewall:** Regras nftables para comunicação Docker ↔ Host
- **Diagnóstico:** Identificação e resolução do problema de "erros de reprodução"

---

## 🔍 Problema Diagnosticado

### Sintoma
Usuário reportava "erros de reprodução" ao tentar usar o TSi MUSIC.

### Causa Raiz
O **nginx (frontend)** não estava proxyando os endpoints do **Music Assistant Server**, causando:

1. **Mixed Content:** Frontend HTTPS (`https://100.86.64.1:8443/`) tentava conectar ao WebSocket não seguro (`ws://100.86.64.1:8095/ws`) — bloqueado pelos navegadores modernos
2. **Falha na auto-detecção:** O frontend não detectava automaticamente o servidor MA ao acessar a URL
3. **Imagens quebradas:** O endpoint `/imageproxy` não funcionava
4. **Web player inoperante:** O Sendspin (streaming de áudio no navegador) não conseguia conectar

### Diagnóstico Completo

| Componente | Status | Detalhes |
|------------|--------|----------|
| MA Server 2.8.5 | ✅ Healthy | Rodando em `music-assistant-server:8095` |
| Snapcast pipeline | ✅ Funcionando | Server → Client → PipeWire → ALSA |
| Biblioteca | ✅ 1 track | "Enthusiast" de Tours (test_sound.mp3) |
| Web player | ✅ Funcional | Sendspin streaming operacional |
| Nginx proxy | ❌ **Faltando** | Não proxyava `/ws`, `/sendspin`, `/imageproxy` |
| Firewall | ❌ **Bloqueando** | Rede Docker `172.18.0.0/16` sem acesso às portas MA |

---

## ✅ Correções Aplicadas

### 1. Nginx Reverse Proxy

**Arquivo atualizado:** `/home/tsi/docker/ma-wiki/nginx.conf`

Adicionados 5 location blocks de proxy:

| Location | Destino | Propósito |
|----------|---------|-----------|
| `/ws` | `172.18.0.1:8095/ws` | WebSocket API do MA |
| `/sendspin` | `172.18.0.1:8095/sendspin` | Streaming de áudio (web player) |
| `/imageproxy` | `172.18.0.1:8097` | Imagens e capas de álbuns |
| `/preview` | `172.18.0.1:8097` | Pré-visualizações |
| `/info` | `172.18.0.1:8095/info` | Auto-detecção do servidor |

Configuração versionada em: [`deploy/nginx.conf`](./deploy/nginx.conf)

### 2. Regras de Firewall

**Sistema:** nftables (ufw backend)

```bash
sudo nft add rule ip filter ufw-user-input ip saddr 172.18.0.0/16 tcp dport 8095 accept
sudo nft add rule ip filter ufw-user-input ip saddr 172.18.0.0/16 tcp dport 8097 accept
sudo nft add rule ip filter ufw-user-input ip saddr 172.18.0.0/16 tcp dport 8927 accept
```

**Por que necessário:** O container nginx roda na rede Docker `172.18.0.0/16` e precisa acessar o MA Server nas portas 8095/8097/8927. O firewall UFW bloqueava esse tráfego por padrão.

### 3. Documentação Técnica

Criado [`docs/INFRASTRUCTURE.md`](./docs/INFRASTRUCTURE.md) com:
- Diagrama de arquitetura de rede completo
- Configuração do container Docker
- Configuração do Music Assistant Server
- Nginx proxy configuration (completo e comentado)
- Regras de firewall
- Audio pipeline (Snapcast → PipeWire → ALSA)
- Guia de troubleshooting com comandos de diagnóstico

---

## 🧪 Validação

### Testes Executados

| Teste | Comando | Resultado |
|-------|---------|-----------|
| `/info` via proxy | `curl -Ik https://100.86.64.1:8443/info` | ✅ HTTP 200 |
| WebSocket via proxy | `wss://100.86.64.1:8443/ws` | ✅ Conecta, server_version=2.8.5 |
| Sendspin via proxy | `wss://100.86.64.1:8443/sendspin` | ✅ Conecta |
| Imageproxy via proxy | `curl -Ik https://100.86.64.1:8443/imageproxy?...` | ✅ HTTP 200, 8.3KB |
| Auto-detecção | Frontend fetch `/info` | ✅ Detecta como MA server |

### Fluxo de Áudio Validado

1. ✅ Track "Enthusiast" adicionada à queue do Snapcast
2. ✅ Stream ativo no snapserver (`Music Assistant - ma50e549722626`, status: `playing`)
3. ✅ Snapclient conectado e recebendo stream
4. ✅ PipeWire node "Snapcast" em estado `running`
5. ✅ ALSA output em estado `running` com volume 40%
6. ✅ Links de áudio ativos: `Snapcast:output_FL/FR → alsa_output:playback_FL/FR`

---

## 📁 Arquivos Modificados

| Arquivo | Ação | Descrição |
|---------|------|-----------|
| `deploy/nginx.conf` | ➕ Criado | Configuração nginx de produção com proxy MA |
| `docs/INFRASTRUCTURE.md` | ➕ Criado | Documentação técnica completa da infraestrutura |
| `README.md` | ✏️ Atualizado | Seção de deploy com proxy e validação |
| `RELEASE-v2.9.5.md` | ➕ Criado | Este documento |

---

## 📊 Estatísticas Finais

| Métrica | Valor |
|---------|-------|
| Versão | v2.9.5 |
| Features UX acumuladas | 15 |
| Security fixes | 10 HIGH → 0 |
| Infraestrutura | Nginx proxy + Firewall rules |
| Testes | 127/127 ✅ |
| Vulnerabilidades | 0 ✅ |
| Deploy | ✅ Ativo |

---

## 🏷️ Tags

`#TSiMUSIC` `#MidiaServer-SaudeClinica` `#infraestrutura` `#nginx` `#proxy` `#firewall`
