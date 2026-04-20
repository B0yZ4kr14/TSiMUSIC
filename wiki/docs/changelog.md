# Changelog

## v2.9.5 — 2026-04-19

### Segurança
- Certificados SSL duplos: Let's Encrypt (hostname) + autoassinado (IP)
- Headers de segurança completos: CSP, HSTS, X-Frame-Options, etc.
- Cookie `Secure; SameSite=Strict` no sidebar
- Meta tags OG/Twitter dinâmicas via JavaScript

### Infraestrutura
- Nginx triple server block: HTTP/80 + HTTPS/443 LE + HTTPS/443 self-signed
- Tailscale Serve configurado como proxy HTTPS
- Docker Compose com healthcheck
- Firewall nftables configurado para Docker bridge

### Monitoramento
- Healthcheck systemd timer a cada 5 minutos
- Dashboard HTML na porta 8765
- Logrotate configurado

### CI/CD
- GitHub Actions workflow `deploy.yml`
- Script `deploy.sh` com flags (`--dry-run`, `--skip-tests`, etc.)
- Documentação `docs/DEPLOY.md`

---

## v2.9.4 — 2026-04-18

### Frontend
- Rebranding completo: TSi MUSIC
- Tema premium com glassmorphism e gradientes
- PWA com service worker e precache
- Tradução completa pt-BR (1532 keys)

---

## v2.9.3 — 2026-04-17

### Correções
- Fix de proxy WebSocket para Music Assistant
- Configuração de audio stack (PipeWire + Snapcast)

---

## v2.9.2 — 2026-04-16

### Deploy Inicial
- Setup do servidor `saudeclinica`
- Docker container `ma-wiki` (nginx:alpine)
- Integração com Music Assistant Server v2.8.5
