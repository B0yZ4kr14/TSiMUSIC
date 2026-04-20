#!/usr/bin/env bash
# cspell:disable
# =============================================================================
# TSi MUSIC — Script de Deploy Local para MidiaServer-SaudeClinica
# Versão: v2.9.5
#
# Uso:
#   ./scripts/deploy.sh [opções]
#
# Opções:
#   --skip-build      Pula o build (usa o diretório de build existente)
#   --skip-tests      Pula testes e lint
#   --dry-run         Executa rsync em modo simulação (--dry-run)
#   --restart         Força restart do container (mesmo sem mudanças no nginx.conf)
#   --health-only     Apenas executa health check, sem deploy
#   -h, --help        Mostra esta ajuda
#
# Variáveis de ambiente (sobrescrevem defaults):
#   DEPLOY_HOST       — Host do servidor (default: 100.86.64.1)
#   DEPLOY_USER       — Usuário SSH (default: tsi)
#   DEPLOY_PATH       — Path remoto (default: /home/tsi/docker/ma-wiki)
#   SSH_KEY           — Path da chave SSH (default: ~/.ssh/id_ed25519_midiaserver)
#   BUILD_DIR         — Diretório de build (default: music_assistant_frontend)
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Cores e logging
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC}  $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}   $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step()  { echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; echo -e "${CYAN}[STEP]${NC} $1"; echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; }

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEPLOY_HOST="${DEPLOY_HOST:-100.86.64.1}"
DEPLOY_USER="${DEPLOY_USER:-tsi}"
DEPLOY_PATH="${DEPLOY_PATH:-/home/tsi/docker/ma-wiki}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_ed25519_midiaserver}"
BUILD_DIR="${BUILD_DIR:-music_assistant_frontend}"
COMPOSE_FILE="${DEPLOY_PATH}/docker-compose.yml"
HEALTH_URL="https://${DEPLOY_HOST}:8443/info"
HEALTH_TIMEOUT=60

# Flags
SKIP_BUILD=false
SKIP_TESTS=false
DRY_RUN=false
FORCE_RESTART=false
HEALTH_ONLY=false

# ---------------------------------------------------------------------------
# Parse args
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-build)  SKIP_BUILD=true; shift ;;
    --skip-tests)  SKIP_TESTS=true; shift ;;
    --dry-run)     DRY_RUN=true; shift ;;
    --restart)     FORCE_RESTART=true; shift ;;
    --health-only) HEALTH_ONLY=true; shift ;;
    -h|--help)
      sed -n '2,22p' "$0"
      exit 0
      ;;
    *)
      log_error "Opção desconhecida: $1"
      echo "Use --help para ver as opções disponíveis."
      exit 1
      ;;
  esac
done

# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
print_banner() {
  echo ""
  echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${CYAN}║${NC}           ${GREEN}TSi MUSIC — Deploy Pipeline v2.9.5${NC}                ${CYAN}║${NC}"
  echo -e "${CYAN}║${NC}      Target: ${YELLOW}${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}${NC}              ${CYAN}║${NC}"
  echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
  echo ""
}

verify_prerequisites() {
  log_step "Verificando pré-requisitos"

  local missing=()

  if ! command -v rsync &>/dev/null; then missing+=("rsync"); fi
  if ! command -v ssh &>/dev/null; then missing+=("ssh"); fi
  if ! command -v curl &>/dev/null; then missing+=("curl"); fi
  if ! command -v yarn &>/dev/null; then missing+=("yarn"); fi
  if ! command -v docker &>/dev/null && [ "$SKIP_BUILD" = false ]; then
    log_warn "Docker não encontrado localmente — build pode falhar se depende de containers"
  fi

  if [ ${#missing[@]} -gt 0 ]; then
    log_error "Ferramentas ausentes: ${missing[*]}"
    exit 1
  fi

  if [ ! -f "$SSH_KEY" ]; then
    log_error "Chave SSH não encontrada: $SSH_KEY"
    exit 1
  fi

  # Testa conectividade SSH
  log_info "Testando conexão SSH..."
  if ! ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o BatchMode=yes \
      "${DEPLOY_USER}@${DEPLOY_HOST}" "echo OK" &>/dev/null; then
    log_error "Não foi possível conectar via SSH para ${DEPLOY_USER}@${DEPLOY_HOST}"
    log_info "Verifique: (1) Tailscale ativo, (2) chave SSH correta, (3) servidor online"
    exit 1
  fi

  log_ok "Pré-requisitos verificados"
}

run_tests() {
  if [ "$SKIP_TESTS" = true ]; then
    log_warn "Pulando testes e lint (--skip-tests)"
    return 0
  fi

  log_step "Executando testes e lint"

  yarn test:run
  log_ok "Testes passaram"

  yarn lint
  log_ok "Lint passou"
}

run_build() {
  if [ "$SKIP_BUILD" = true ]; then
    if [ ! -d "$BUILD_DIR" ]; then
      log_error "Diretório de build não encontrado: $BUILD_DIR"
      log_info "Execute sem --skip-build ou rode 'yarn build' manualmente."
      exit 1
    fi
    log_warn "Pulando build (--skip-build) — usando diretório existente: $BUILD_DIR"
    return 0
  fi

  log_step "Build de produção"
  yarn build
  log_ok "Build concluído em: $BUILD_DIR"
}

sync_files() {
  if [ "$HEALTH_ONLY" = true ]; then
    log_warn "Modo health-only — pulando sincronização"
    return 0
  fi

  log_step "Sincronizando arquivos via rsync"

  local rsync_flags="-avz"
  if [ "$DRY_RUN" = true ]; then
    rsync_flags="${rsync_flags} --dry-run"
    log_warn "MODO SIMULAÇÃO — nenhuma alteração será feita no servidor"
  else
    rsync_flags="${rsync_flags} --delete"
  fi

  log_info "Origem:  $(pwd)/${BUILD_DIR}/"
  log_info "Destino: ${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}/"

  rsync $rsync_flags \
    --exclude="nginx.conf" \
    --exclude="certs/" \
    --exclude="docker-compose.yml" \
    --exclude=".env" \
    --exclude="*.md" \
    -e "ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" \
    "${BUILD_DIR}/" \
    "${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}/"

  if [ "$DRY_RUN" = true ]; then
    log_warn "Dry-run concluído — revise as alterações acima antes de executar sem --dry-run"
  else
    log_ok "Sincronização concluída"
  fi
}

restart_container() {
  if [ "$HEALTH_ONLY" = true ]; then
    return 0
  fi

  if [ "$DRY_RUN" = true ]; then
    log_warn "Dry-run — pulando reinicialização do container"
    return 0
  fi

  log_step "Reinicializando container nginx"

  local restart_cmd
  restart_cmd=$(cat <<'EOF'
set -e
COMPOSE_DIR="$(dirname __COMPOSE_FILE__)"
cd "$COMPOSE_DIR"

if docker ps --format "{{.Names}}" | grep -q "^ma-wiki$"; then
  echo "Container ma-wiki encontrado"

  # Verifica se nginx.conf mudou comparando checksums
  LOCAL_NGINX_SHA=$(sha256sum nginx.conf 2>/dev/null | awk '{print $1}' || echo "")
  CONTAINER_NGINX_SHA=$(docker exec ma-wiki sha256sum /etc/nginx/nginx.conf 2>/dev/null | awk '{print $1}' || echo "")

  if [ "$LOCAL_NGINX_SHA" != "$CONTAINER_NGINX_SHA" ] || [ "__FORCE_RESTART__" = "true" ]; then
    echo "Configuração nginx alterada ou restart forçado — recriando container..."
    docker compose down
    docker compose up -d
  else
    echo "Configuração inalterada — executando reload graceful do nginx..."
    docker exec ma-wiki nginx -s reload
  fi
else
  echo "Container ma-wiki não encontrado — subindo via docker compose..."
  docker compose up -d
fi

echo "Status do container:"
docker ps --filter "name=ma-wiki" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
EOF
)

  restart_cmd="${restart_cmd//__COMPOSE_FILE__/${COMPOSE_FILE}}"
  restart_cmd="${restart_cmd//__FORCE_RESTART__/${FORCE_RESTART}}"

  ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    "${DEPLOY_USER}@${DEPLOY_HOST}" "bash -c '$restart_cmd'"

  log_ok "Container nginx atualizado"
}

health_check() {
  log_step "Health check pós-deploy"

  local elapsed=0
  local interval=5
  local http_code

  while [ $elapsed -lt $HEALTH_TIMEOUT ]; do
    http_code=$(curl -s -o /dev/null -w "%{http_code}" \
      --connect-timeout 5 --max-time 10 \
      --insecure \
      "$HEALTH_URL" 2>/dev/null || echo "000")

    if [ "$http_code" = "200" ]; then
      log_ok "Health check passou — HTTP 200 em /info"
      log_info "URL: https://${DEPLOY_HOST}:8443"
      return 0
    fi

    log_warn "Aguardando... (${elapsed}/${HEALTH_TIMEOUT}s) — último código: $http_code"
    sleep $interval
    elapsed=$((elapsed + interval))
  done

  log_error "Health check falhou — servidor não respondeu com HTTP 200 em ${HEALTH_TIMEOUT}s"
  log_info "Verifique: ssh ${DEPLOY_USER}@${DEPLOY_HOST} 'docker logs ma-wiki --tail 50'"
  return 1
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
  print_banner
  verify_prerequisites

  if [ "$HEALTH_ONLY" = false ]; then
    run_tests
    run_build
    sync_files
    restart_container
  fi

  health_check

  echo ""
  log_ok "Deploy concluído com sucesso! 🎵"
  log_info "Acesse: https://${DEPLOY_HOST}:8443"
  echo ""
}

main "$@"
