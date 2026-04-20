# Certificados e SSL

> Configuração de certificados SSL duplos no TSi MUSIC: Let's Encrypt via Tailscale + self-signed para acesso por IP.

---

## Visão Geral

O nginx do TSi MUSIC utiliza uma configuração de **certificados duplos** para cobrir todos os cenários de acesso:

1. **Tailscale Let's Encrypt** — certificado válido para o hostname Tailscale
2. **Self-signed** — certificado para acesso direto por IP (`100.86.64.1`)

---

## Arquitetura SSL

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SSL Dual-Cert Architecture                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Acesso por hostname (SNI):                                                  │
│  https://midiaserver-saudeclinica.tailbda57.ts.net:8443                     │
│         │                                                                    │
│         └──► nginx:443 (SNI match)                                           │
│              ├── tailscale.crt  (Let's Encrypt válido)                       │
│              └── tailscale.key                                               │
│                                                                              │
│  Acesso por IP (default_server):                                             │
│  https://100.86.64.1:8443                                                   │
│         │                                                                    │
│         └──► nginx:443 default_server                                        │
│              ├── ip-tailscale.crt  (self-signed)                             │
│              └── ip-tailscale.key                                            │
│                                                                              │
│  Acesso HTTP (redirect implícito):                                           │
│  http://100.86.64.1:8080  ──►  serve conteúdo direto (Tailscale serve)       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Certificado Tailscale (Let's Encrypt)

### O que é

O Tailscale oferece **certificados Let's Encrypt gratuitos e automáticos** para qualquer node na sua tailnet. O certificado é válido para o hostname máquina da tailnet.

### Hostname

```
midiaserver-saudeclinica.tailbda57.ts.net
```

### Arquivos

| Arquivo | Path no servidor | Path no container |
|---------|------------------|-------------------|
| Certificado | `/home/tsi/docker/ma-wiki/certs/tailscale.crt` | `/usr/share/nginx/html/certs/tailscale.crt` |
| Chave privada | `/home/tsi/docker/ma-wiki/certs/tailscale.key` | `/usr/share/nginx/html/certs/tailscale.key` |

### Obtenção do Certificado

```bash
# No servidor MidiaServer, como root ou com sudo
tailscale cert midiaserver-saudeclinica.tailbda57.ts.net

# Isso gera automaticamente:
# /var/lib/tailscale/certs/midiaserver-saudeclinica.tailbda57.ts.net.crt
# /var/lib/tailscale/certs/midiaserver-saudeclinica.tailbda57.ts.net.key

# Copie para o diretório do nginx
cp /var/lib/tailscale/certs/midiaserver-saudeclinica.tailbda57.ts.net.crt \
   /home/tsi/docker/ma-wiki/certs/tailscale.crt
cp /var/lib/tailscale/certs/midiaserver-saudeclinica.tailbda57.ts.net.key \
   /home/tsi/docker/ma-wiki/certs/tailscale.key
chown tsi:tsi /home/tsi/docker/ma-wiki/certs/*
chmod 600 /home/tsi/docker/ma-wiki/certs/*
```

### Renovação Automática

O Tailscale renova o certificado automaticamente. Após a renovação, copie os novos arquivos e reinicie o container:

```bash
# Script de renovação (pode ser adicionado ao cron)
tailscale cert --cert-file /home/tsi/docker/ma-wiki/certs/tailscale.crt \
               --key-file /home/tsi/docker/ma-wiki/certs/tailscale.key \
               midiaserver-saudeclinica.tailbda57.ts.net
docker exec ma-wiki nginx -s reload
```

---

## Certificado Self-Signed (IP)

### O que é

Um certificado **self-signed** para permitir acesso HTTPS direto pelo IP Tailscale (`100.86.64.1`). Navegadores mostrarão um aviso de segurança, mas a conexão será criptografada.

### Arquivos

| Arquivo | Path no servidor | Path no container |
|---------|------------------|-------------------|
| Certificado | `/home/tsi/docker/ma-wiki/certs/ip-tailscale.crt` | `/usr/share/nginx/html/certs/ip-tailscale.crt` |
| Chave privada | `/home/tsi/docker/ma-wiki/certs/ip-tailscale.key` | `/usr/share/nginx/html/certs/ip-tailscale.key` |

### Geração do Certificado

```bash
# Gerar chave privada e certificado self-signed para o IP
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /home/tsi/docker/ma-wiki/certs/ip-tailscale.key \
  -out /home/tsi/docker/ma-wiki/certs/ip-tailscale.crt \
  -subj "/CN=100.86.64.1" \
  -addext "subjectAltName=IP:100.86.64.1"

# Ajustar permissões
chown tsi:tsi /home/tsi/docker/ma-wiki/certs/ip-tailscale.*
chmod 600 /home/tsi/docker/ma-wiki/certs/ip-tailscale.*
```

---

## Configuração Nginx

### Server Blocks

O nginx possui **3 server blocks**:

| Porta | Server Name | Certificado | Propósito |
|-------|-------------|-------------|-----------|
| `80` | `_` | Nenhum | Serve conteúdo HTTP direto (Tailscale serve proxy) |
| `443` | `midiaserver-saudeclinica.tailbda57.ts.net` | `tailscale.crt` | HTTPS com cert válido |
| `443` | `default_server` | `ip-tailscale.crt` | HTTPS para acesso por IP |

### Exemplo de Configuração

```nginx
# Server block 1: HTTP (80)
server {
    listen 80;
    # ... serve conteúdo direto
}

# Server block 2a: HTTPS (443) — Tailscale LE cert for hostname (SNI)
server {
    listen 443 ssl;
    server_name midiaserver-saudeclinica.tailbda57.ts.net;

    ssl_certificate /usr/share/nginx/html/certs/tailscale.crt;
    ssl_certificate_key /usr/share/nginx/html/certs/tailscale.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    # ...
}

# Server block 2b: HTTPS (443) — Self-signed cert for IP access (default SNI fallback)
server {
    listen 443 ssl default_server;

    ssl_certificate /usr/share/nginx/html/certs/ip-tailscale.crt;
    ssl_certificate_key /usr/share/nginx/html/certs/ip-tailscale.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    # ...
}
```

---

## Security Headers

O nginx aplica os seguintes headers de segurança em todas as respostas:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

---

## Cache de Assets

```nginx
# Long-term cache para assets versionados (Vite hashed filenames)
location ~* \.(?:js|css|woff2|png|jpg|jpeg|gif|svg|ico|webmanifest)$ {
    add_header Cache-Control "public, immutable, max-age=31536000" always;
    expires 1y;
    access_log off;
}
```

---

## Validação

```bash
# Testar certificado Tailscale
curl -vI https://midiaserver-saudeclinica.tailbda57.ts.net:8443/info 2>&1 | grep "subject:"

# Testar certificado IP (self-signed)
curl -Ik --insecure https://100.86.64.1:8443/info

# Verificar data de expiração do certificado
openssl x509 -in /home/tsi/docker/ma-wiki/certs/tailscale.crt -noout -dates
openssl x509 -in /home/tsi/docker/ma-wiki/certs/ip-tailscale.crt -noout -dates
```

---

> 🏷️ `#TSiMUSIC` `#SSL` `#Tailscale` `#Let's-Encrypt` `#nginx`
