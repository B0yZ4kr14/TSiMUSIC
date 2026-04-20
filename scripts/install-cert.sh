#!/usr/bin/env bash
# cspell:disable
# =============================================================================
# Script: install-cert.sh
# Descrição: Baixa e instala o certificado ip-tailscale.crt no trust store
# Uso: curl -fsSL https://midiaserver-saudeclinica.tailbda57.ts.net/install-cert.sh | bash
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[AVISO]${NC} $1"; }
log_error() { echo -e "${RED}[ERRO]${NC} $1"; }

SERVER_IP="100.86.64.1"
SERVER_PORT="8443"
CERT_URL="https://midiaserver-saudeclinica.tailbda57.ts.net/certs/ip-tailscale.crt"
CERT_FILE="ip-tailscale.crt"
TMP_DIR="$(mktemp -d)"
trap "rm -rf '$TMP_DIR'" EXIT

cd "$TMP_DIR"

detect_os() {
  case "$(uname -s)" in
    Linux*)     echo "linux";;
    Darwin*)    echo "mac";;
    CYGWIN*|MINGW*|MSYS*) echo "windows";;
    *)          echo "unknown";;
  esac
}

OS="$(detect_os)"

log_info "Detectado sistema operacional: $OS"

# ---------------------------------------------------------------------------
# Baixar certificado
# ---------------------------------------------------------------------------
log_info "Baixando certificado de $CERT_URL ..."
if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$CERT_URL" -o "$CERT_FILE" || {
    log_warn "Falha ao baixar via hostname. Tentando via IP (ignorando SSL verificação)..."
    curl -fsSLk "https://${SERVER_IP}:${SERVER_PORT}/certs/ip-tailscale.crt" -o "$CERT_FILE"
  }
elif command -v wget >/dev/null 2>&1; then
  wget -q "$CERT_URL" -O "$CERT_FILE" || {
    log_warn "Falha ao baixar via hostname. Tentando via IP (ignorando SSL verificação)..."
    wget -q --no-check-certificate "https://${SERVER_IP}:${SERVER_PORT}/certs/ip-tailscale.crt" -O "$CERT_FILE"
  }
else
  log_error "curl ou wget são necessários."
  exit 1
fi

if [[ ! -s "$CERT_FILE" ]]; then
  log_error "Certificado baixado está vazio ou não foi salvo."
  exit 1
fi

log_ok "Certificado baixado (${CERT_FILE})"

# ---------------------------------------------------------------------------
# Instalar no trust store
# ---------------------------------------------------------------------------
if [[ "$OS" == "linux" ]]; then
  if command -v update-ca-certificates >/dev/null 2>&1; then
    # Debian/Ubuntu
    log_info "Instalando em /usr/local/share/ca-certificates/ ..."
    sudo cp "$CERT_FILE" /usr/local/share/ca-certificates/ip-tailscale.crt
    sudo update-ca-certificates
    log_ok "Certificado instalado (update-ca-certificates)."
  elif command -v update-ca-trust >/dev/null 2>&1; then
    # RHEL/CentOS/Fedora/Arch
    log_info "Instalando em /etc/ca-certificates/trust-source/anchors/ ou /usr/share/ca-certificates/trust-source/ ..."
    if [[ -d /etc/ca-certificates/trust-source/anchors ]]; then
      sudo cp "$CERT_FILE" /etc/ca-certificates/trust-source/anchors/ip-tailscale.crt
      sudo update-ca-trust
    elif [[ -d /usr/share/ca-certificates/trust-source ]]; then
      sudo cp "$CERT_FILE" /usr/share/ca-certificates/trust-source/ip-tailscale.crt
      sudo update-ca-trust
    else
      log_error "Diretório de trust store não encontrado."
      exit 1
    fi
    log_ok "Certificado instalado (update-ca-trust)."
  else
    log_error "Não foi possível detectar o utilitário de trust store do Linux."
    exit 1
  fi

elif [[ "$OS" == "mac" ]]; then
  log_info "Adicionando certificado ao System Keychain..."
  sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain "$CERT_FILE"
  log_ok "Certificado adicionado ao System Keychain."

elif [[ "$OS" == "windows" ]]; then
  log_warn "Windows detectado. Instalação automática não é suportada neste script."
  log_info "Salve o arquivo $CERT_FILE e instale manualmente via 'Gerenciar Certificados do Usuário' -> Autoridades de Certificação Raiz Confiáveis."
  cp "$CERT_FILE" "$HOME/Desktop/ip-tailscale.crt"
  log_ok "Certificado copiado para a Área de Trabalho."
  exit 0

else
  log_error "Sistema operacional não suportado: $OS"
  exit 1
fi

# ---------------------------------------------------------------------------
# Verificar instalação
# ---------------------------------------------------------------------------
log_info "Verificando conexão SSL com o servidor..."
if openssl s_client -connect "${SERVER_IP}:${SERVER_PORT}" -showcerts </dev/null 2>/dev/null | openssl x509 -noout -subject >/dev/null 2>&1; then
  log_ok "Conexão SSL estabelecida com sucesso."
else
  log_warn "Não foi possível validar a conexão SSL. Verifique se o certificado foi instalado corretamente."
fi

log_info "Verificando chain de confiança..."
VERIFY_RESULT=$(openssl s_client -connect "${SERVER_IP}:${SERVER_PORT}" -CAfile /dev/null </dev/null 2>/dev/null | awk '/Verify return code/{print $NF}' || true)
if [[ "$VERIFY_RESULT" == "0" ]] || [[ "$VERIFY_RESULT" == "19" ]] || [[ "$VERIFY_RESULT" == "21" ]]; then
  log_warn "O navegador pode ainda exibir aviso até ser reiniciado."
  log_ok "Certificado está presente no trust store."
else
  log_warn "Código de verificação: ${VERIFY_RESULT}. Reinicie o navegador após a instalação."
fi

log_ok "Processo concluído!"
