# 🚀 TSi MUSIC — CI/CD Pipeline de Deploy

> Documentação do pipeline de deploy contínuo para o MidiaServer-SaudeClinica.
> **Versão:** v2.9.5 | **Data:** 2026-04-19

---

## 📋 Sumário

- [Visão Geral](#visão-geral)
- [Arquitetura do Pipeline](#arquitetura-do-pipeline)
- [GitHub Actions (Deploy Automático)](#github-actions-deploy-automático)
- [Script de Deploy Local](#script-de-deploy-local)
- [Pré-requisitos do Servidor](#pré-requisitos-do-servidor)
- [Configuração de Secrets](#configuração-de-secrets)
- [Idempotência e Segurança](#idempotência-e-segurança)
- [Webhooks e Self-Hosted Runners](#webhooks-e-self-hosted-runners)
- [Troubleshooting](#troubleshooting)

---

## Visão Geral

O pipeline CI/CD do TSi MUSIC foi projetado para ser **leve, eficiente e seguro**, automatizando o processo de entrega do frontend estático para o servidor de produção `MidiaServer-SaudeClinica`.

### Objetivos

1. **Automatização total:** todo push na branch `main` dispara build, testes e deploy
2. **Zero credenciais em código:** todas as credenciais são injetadas via GitHub Secrets
3. **Idempotência:** múltiplas execuções seguidas produzem o mesmo resultado
4. **Validação pós-deploy:** health check automático garante que o serviço está saudável
5. **Fallback manual:** script local `scripts/deploy.sh` permite deploy manual quando necessário

---

## Arquitetura do Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TSi MUSIC — CI/CD Pipeline v2.9.5                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │   Push to   │───►│  GitHub     │───►│   Build &   │───►│   Deploy    │   │
│  │   main      │    │  Actions    │    │   Test      │    │   (rsync)   │   │
│  └─────────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘   │
│                                                                   │          │
│                              ┌────────────────────────────────────┘          │
│                              ▼                                               │
│                    ┌─────────────────┐                                       │
│                    │  MidiaServer    │                                       │
│                    │  100.86.64.1    │                                       │
│                    │  (Tailscale)    │                                       │
│                    └────────┬────────┘                                       │
│                             │                                                │
│                    ┌────────▼────────┐                                       │
│                    │  Docker Compose │                                       │
│                    │    ma-wiki      │                                       │
│                    │   (nginx:alp)   │                                       │
│                    └─────────────────┘                                       │
│                                                                              │
│  Saída:                                                                      │
│  ├── https://100.86.64.1:8443  (HTTPS)                                      │
│  └── https://100.86.64.1:8080  (HTTP → redirect HTTPS)                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Fluxo de Execução

| Etapa | Ferramenta | Duração estimada |
|-------|-----------|------------------|
| Checkout | `actions/checkout@v4` | ~2s |
| Setup Node.js | `actions/setup-node@v4` | ~5s |
| Install deps | `yarn install` | ~30s (com cache) |
| Test + Lint | `yarn test:run`, `yarn lint` | ~20s |
| Build | `yarn build` | ~45s |
| Deploy (rsync) | `rsync -avz --delete` | ~10s |
| Reload nginx | `docker exec ma-wiki nginx -s reload` | ~2s |
| Health check | `curl /info` | ~5s |
| **Total** | | **~2 minutos** |

---

## GitHub Actions (Deploy Automático)

### Arquivo

`.github/workflows/deploy.yml`

### Trigger

- **Push na branch `main`** — deploy automático
- **Manual (`workflow_dispatch`)** — permite deploy sob demanda com opções:
  - `skip_tests`: pula testes e lint para deploy de emergência

### Jobs

#### Job 1: `validate`

Executa em `ubuntu-latest`:
1. Checkout do repositório
2. Setup Node.js 22.x com cache Yarn
3. Instala dependências (`yarn install --frozen-lockfile`)
4. Executa testes (`yarn test:run`)
5. Executa lint (`yarn lint`)
6. Build de produção (`yarn build`)
7. Upload do artefato `production-build`

#### Job 2: `deploy`

Depende do job `validate`. Executa apenas se `validate` passar:
1. Download do artefato de build
2. Setup do SSH agent com a chave privada do servidor
3. **Rsync** dos arquivos para o servidor (exclui `nginx.conf`, `certs/`, `docker-compose.yml`, `.env`)
4. **Reload graceful** do nginx no container `ma-wiki`
5. **Health check** via `/info` — espera HTTP 200 por até 60 segundos

### Secrets Necessários

Configure em **Settings > Secrets and variables > Actions**:

| Secret | Descrição | Obrigatório | Exemplo |
|--------|-----------|-------------|---------|
| `DEPLOY_HOST` | IP ou hostname do servidor via Tailscale | Sim | `100.86.64.1` |
| `DEPLOY_USER` | Usuário SSH no servidor | Sim | `tsi` |
| `DEPLOY_SSH_KEY` | Conteúdo da chave privada SSH (`id_ed25519_midiaserver`) | Sim | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `DEPLOY_PATH` | Path remoto de deploy | Não | `/home/tsi/docker/ma-wiki` |
| `DEPLOY_DOCKER_COMPOSE` | Path do docker-compose.yml remoto | Não | `/home/tsi/docker/ma-wiki/docker-compose.yml` |

> **⚠️ Atenção:** O secret `DEPLOY_SSH_KEY` deve conter o **conteúdo completo** da chave privada (`cat ~/.ssh/id_ed25519_midiaserver`), não o path do arquivo.

---

## Script de Deploy Local

### Arquivo

`scripts/deploy.sh`

### Uso

```bash
# Deploy completo (build + test + deploy + health check)
./scripts/deploy.sh

# Deploy rápido (pula build se já existir)
./scripts/deploy.sh --skip-build

# Deploy de emergência (pula testes)
./scripts/deploy.sh --skip-tests

# Simulação (não altera nada no servidor)
./scripts/deploy.sh --dry-run

# Força recriação do container
./scripts/deploy.sh --restart

# Apenas health check
./scripts/deploy.sh --health-only

# Ajuda
./scripts/deploy.sh --help
```

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DEPLOY_HOST` | IP/hostname do servidor | `100.86.64.1` |
| `DEPLOY_USER` | Usuário SSH | `tsi` |
| `DEPLOY_PATH` | Path remoto | `/home/tsi/docker/ma-wiki` |
| `SSH_KEY` | Path da chave SSH local | `~/.ssh/id_ed25519_midiaserver` |
| `BUILD_DIR` | Diretório de build local | `music_assistant_frontend` |

### Exemplo com variáveis customizadas

```bash
DEPLOY_HOST=100.86.64.1 \
DEPLOY_USER=tsi \
SSH_KEY=~/.ssh/id_ed25519_midiaserver \
  ./scripts/deploy.sh
```

---

## Pré-requisitos do Servidor

### Sistema Operacional

- Linux (Ubuntu/Debian recomendado)
- Docker e Docker Compose instalados
- Tailscale ativo e configurado
- Usuário com acesso SSH via chave pública

### Estrutura de Diretórios

```
/home/tsi/docker/ma-wiki/
├── docker-compose.yml      # Configuração do container nginx
├── nginx.conf              # Configuração customizada do nginx
├── certs/
│   ├── tailscale.crt       # Certificado SSL Tailscale
│   └── tailscale.key       # Chave privada SSL
├── index.html              # (deployado via CI/CD)
├── manifest.webmanifest    # (deployado via CI/CD)
├── assets/                 # (deployado via CI/CD)
└── ...                     # demais arquivos do build
```

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

### Permissões SSH

O usuário de deploy precisa de:
1. Chave pública adicionada em `~/.ssh/authorized_keys`
2. Permissão para executar `docker` sem sudo (usuário no grupo `docker`) **OU**
3. Sudoers configurado para `docker` e `docker compose` sem senha

### Firewall

As portas devem estar acessíveis:
- `8443/tcp` — HTTPS (Tailscale serve/proxy)
- `8080/tcp` — HTTP (redirect)
- `22/tcp` — SSH (para deploy)

Regras nftables/ufw necessárias para comunicação Docker→Host:

```bash
sudo nft add rule ip filter ufw-user-input ip saddr 172.18.0.0/16 tcp dport 8095 accept
sudo nft add rule ip filter ufw-user-input ip saddr 172.18.0.0/16 tcp dport 8097 accept
sudo nft add rule ip filter ufw-user-input ip saddr 172.18.0.0/16 tcp dport 8927 accept
```

---

## Idempotência e Segurança

### Idempotência

O pipeline é **idempotente** por design:

1. **Rsync com `--delete`:** garante que o diretório remoto é espelhado exatamente como o build local
2. **Reload graceful:** se o `nginx.conf` não mudou, apenas um `nginx -s reload` é executado (sem downtime)
3. **Recreate condicional:** o container só é recriado se o `nginx.conf` foi alterado (comparando checksums SHA-256)
4. **Health check:** valida que o deploy funcionou antes de considerar a execução bem-sucedida

### Segurança

| Medida | Implementação |
|--------|--------------|
| Credenciais | GitHub Secrets (`DEPLOY_SSH_KEY`, `DEPLOY_HOST`, `DEPLOY_USER`) |
| Chaves SSH | Nunca commitadas; injetadas em runtime pelo `webfactory/ssh-agent` |
| Rsync | Exclui arquivos sensíveis (`nginx.conf`, `certs/`, `docker-compose.yml`, `.env`) |
| StrictHostKeyChecking | `no` para Tailscale (rede confiável), mas com `known_hosts` populado no CI |
| Container | Roda como read-only (`:ro`) para volumes do nginx |
| SSL | Certificados Tailscale permanecem no servidor, nunca trafegam pelo CI |

---

## Webhooks e Self-Hosted Runners

### Webhooks vs GitHub Actions

| Opção | Vantagem | Desvantagem | Recomendado |
|-------|----------|-------------|-------------|
| **GitHub Actions + rsync** | Simples, não requer infra extra, grátis | Depende de conectividade Tailscale do runner | ✅ **Sim** |
| **Webhook para servidor** | Deploy instantâneo, controle total do servidor | Requer serviço listener no servidor, exposição de endpoint | ⚠️ Complexo |
| **Self-hosted runner** | Acesso direto à rede Tailscale, maior controle | Requer manutenção do runner, atualizações de segurança | ✅ Alternativa |

### Self-Hosted Runner (Alternativa)

Se o runner GitHub não conseguir alcançar o Tailscale, instale um runner self-hosted no próprio servidor ou em uma VM na mesma rede:

```bash
# No servidor MidiaServer ou VM próxima
mkdir -p ~/actions-runner && cd ~/actions-runner
curl -o actions-runner-linux-x64-2.320.0.tar.gz \
  -L https://github.com/actions/runner/releases/download/v2.320.0/actions-runner-linux-x64-2.320.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.320.0.tar.gz
./config.sh --url https://github.com/B0yZ4kr14/TSiMUSIC --token <TOKEN>
./run.sh
```

Depois, altere `runs-on: ubuntu-latest` para `runs-on: self-hosted` no workflow.

### Webhook Manual (Avançado)

Para deploy via webhook sem GitHub Actions:

```bash
# No servidor, um serviço simples com webhookd ou similar
# que executa: cd /home/tsi/docker/ma-wiki && git pull && docker exec ma-wiki nginx -s reload
```

> **Nota:** Webhooks exigem exposição de um endpoint HTTP/HTTPS, o que aumenta a superfície de ataque. Não recomendado para este cenário.

---

## Troubleshooting

### "Permission denied (publickey)" no CI

```bash
# Verifique se a chave pública está no authorized_keys do servidor
ssh -i ~/.ssh/id_ed25519_midiaserver tsi@100.86.64.1 "cat ~/.ssh/authorized_keys"

# Verifique permissões
ssh tsi@100.86.64.1 "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
```

### "Health check falhou"

```bash
# No servidor, verifique logs do container
ssh tsi@100.86.64.1 "docker logs ma-wiki --tail 50"

# Verifique se o nginx está rodando
ssh tsi@100.86.64.1 "docker exec ma-wiki ps aux | grep nginx"

# Teste localmente no servidor
curl -Ik https://localhost:8443/info
```

### "Rsync falhou com código 23"

Código 23 = erro parcial de transferência. Geralmente permissões no diretório remoto:

```bash
ssh tsi@100.86.64.1 "sudo chown -R tsi:tsi /home/tsi/docker/ma-wiki"
```

### Container não reinicia após mudança no nginx.conf

```bash
# Reinicie manualmente
ssh tsi@100.86.64.1 "cd /home/tsi/docker/ma-wiki && docker compose restart"
```

### Dry-run para diagnóstico

```bash
# Local
./scripts/deploy.sh --dry-run

# Ver o que seria alterado sem aplicar
```

---

## 🏷️ Tags

`#TSiMUSIC` `#CI/CD` `#GitHub-Actions` `#deploy` `#nginx` `#docker` `#MidiaServer-SaudeClinica`
