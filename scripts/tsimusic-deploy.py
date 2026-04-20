#!/usr/bin/env python3
# cspell:disable
# =============================================================================
# TSi-MUSIC — Deploy Automatizado
# Versão: v2.9.6
#
# Deploy automatizado do frontend TSi-MUSIC para o MidiaServer-SaudeClinica.
# Suporta: dry-run, backup, rollback, health check pós-deploy.
#
# Uso:
#   python3 tsimusic-deploy.py
#   python3 tsimusic-deploy.py --dry-run
#   python3 tsimusic-deploy.py --rollback
#   python3 tsimusic-deploy.py --backup-only
#
# Variáveis de ambiente:
#   DEPLOY_HOST       — IP ou hostname (padrão: 100.86.64.1)
#   DEPLOY_USER       — Usuário SSH (padrão: tsi)
#   DEPLOY_PATH       — Path remoto (padrão: /home/tsi/docker/ma-wiki)
#   SSH_KEY           — Path da chave SSH (padrão: ~/.ssh/id_ed25519_b0yz4kr14)
# =============================================================================

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Configuração
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_HOST = os.getenv("DEPLOY_HOST", "100.86.64.1")
DEFAULT_USER = os.getenv("DEPLOY_USER", "tsi")
DEFAULT_PATH = os.getenv("DEPLOY_PATH", "/home/tsi/docker/ma-wiki")
DEFAULT_SSH_KEY = os.getenv("SSH_KEY", os.path.expanduser("~/.ssh/id_ed25519_b0yz4kr14"))
DEFAULT_BUILD_DIR = os.getenv("BUILD_DIR", "music_assistant_frontend")
BACKUP_DIR = Path.home() / ".tsimusic" / "backups"


# ─────────────────────────────────────────────────────────────────────────────
# Cores ANSI
# ─────────────────────────────────────────────────────────────────────────────

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def log(msg: str, level: str = "info") -> None:
    prefix = {
        "info": f"{BLUE}[INFO]{RESET}",
        "ok": f"{GREEN}[OK]{RESET}",
        "warn": f"{YELLOW}[AVISO]{RESET}",
        "err": f"{RED}[ERRO]{RESET}",
    }.get(level, "[?]")
    print(f"{prefix} {msg}")


# ─────────────────────────────────────────────────────────────────────────────
# SSH Helpers
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SSHConfig:
    host: str
    user: str
    key: str

    def cmd(self, remote_cmd: str) -> list[str]:
        return [
            "ssh",
            "-i", self.key,
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=10",
            f"{self.user}@{self.host}",
            remote_cmd,
        ]

    def run(self, remote_cmd: str, check: bool = True) -> subprocess.CompletedProcess:
        cmd = self.cmd(remote_cmd)
        return subprocess.run(cmd, capture_output=True, text=True, check=check)


def ssh_rsync(
    ssh: SSHConfig,
    src: str,
    dst: str,
    dry_run: bool = False,
    exclude: list[str] | None = None,
) -> bool:
    """Rsync local → remoto. Retorna True em sucesso."""
    args = [
        "rsync", "-avz", "--delete",
        "-e", f"ssh -i {ssh.key} -o StrictHostKeyChecking=no -o ConnectTimeout=10",
    ]
    if dry_run:
        args.append("--dry-run")
    for pattern in (exclude or []):
        args.extend(["--exclude", pattern])
    args.extend([src, f"{ssh.user}@{ssh.host}:{dst}"])

    log(f"{'[DRY-RUN] ' if dry_run else ''}rsync {src} → {ssh.host}:{dst}")
    result = subprocess.run(args)
    return result.returncode == 0


# ─────────────────────────────────────────────────────────────────────────────
# Operações
# ─────────────────────────────────────────────────────────────────────────────

def check_prerequisites(ssh: SSHConfig) -> bool:
    """Verifica conectividade SSH e ferramentas."""
    log("Verificando pré-requisitos...")

    if not Path(DEFAULT_SSH_KEY).exists():
        log(f"Chave SSH não encontrada: {DEFAULT_SSH_KEY}", "err")
        return False

    try:
        result = ssh.run("echo 'ping'", check=False)
        if result.returncode != 0 or "ping" not in result.stdout:
            log("Falha na conectividade SSH", "err")
            return False
    except Exception as e:
        log(f"Erro SSH: {e}", "err")
        return False

    log("Conectividade SSH OK", "ok")
    return True


def build_frontend() -> bool:
    """Executa build do frontend com Vite."""
    log("Build do frontend com Vite...")
    result = subprocess.run(["yarn", "build"], capture_output=True, text=True)
    if result.returncode != 0:
        log(f"Build falhou:\n{result.stderr}", "err")
        return False
    log("Build concluído", "ok")
    return True


def backup_remote(ssh: SSHConfig, deploy_path: str) -> str | None:
    """Cria backup no servidor remoto. Retorna path do backup ou None."""
    ts = time.strftime("%Y%m%d_%H%M%S")
    backup_path = f"/home/{ssh.user}/.tsimusic/backups/{ts}"
    log(f"Criando backup remoto em {backup_path}...")

    ssh.run(f"mkdir -p {backup_path}")
    result = ssh.run(f"cp -a {deploy_path}/* {backup_path}/", check=False)
    if result.returncode != 0:
        log("Falha ao criar backup remoto", "warn")
        return None

    log(f"Backup remoto criado: {backup_path}", "ok")
    return backup_path


def rollback(ssh: SSHConfig, deploy_path: str, backup_path: str) -> bool:
    """Restaura backup remoto."""
    log(f"Rollback para {backup_path}...")
    ssh.run(f"rm -rf {deploy_path}/*")
    result = ssh.run(f"cp -a {backup_path}/* {deploy_path}/", check=False)
    if result.returncode != 0:
        log("Rollback falhou", "err")
        return False
    ssh.run(f"docker exec ma-wiki nginx -s reload")
    log("Rollback concluído", "ok")
    return True


def health_check(ssh: SSHConfig) -> bool:
    """Health check rápido pós-deploy."""
    log("Health check pós-deploy...")
    try:
        result = ssh.run("curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/", check=False)
        if result.stdout.strip() == "200":
            log("Health check passou (HTTP 200)", "ok")
            return True
        log(f"Health check falhou (HTTP {result.stdout.strip()})", "err")
        return False
    except Exception as e:
        log(f"Erro no health check: {e}", "err")
        return False


def deploy(
    ssh: SSHConfig,
    deploy_path: str,
    build_dir: str,
    dry_run: bool = False,
    backup: bool = True,
) -> bool:
    """Executa deploy completo."""
    backup_path = None
    if backup and not dry_run:
        backup_path = backup_remote(ssh, deploy_path)

    # Rsync com exclusão de arquivos sensíveis
    exclude = [
        "nginx.conf",
        "certs/",
        "docker-compose.yml",
        ".env",
    ]
    src = f"{build_dir}/"
    if not src.endswith("/"):
        src += "/"

    ok = ssh_rsync(ssh, src, deploy_path, dry_run=dry_run, exclude=exclude)
    if not ok:
        log("Rsync falhou", "err")
        return False

    if dry_run:
        log("Dry-run concluído — nenhuma alteração feita", "ok")
        return True

    # Reload nginx no container
    log("Reload nginx...")
    ssh.run("docker exec ma-wiki nginx -s reload")
    log("Nginx reload concluído", "ok")

    # Health check
    if not health_check(ssh):
        if backup_path:
            log("Tentando rollback automático...", "warn")
            rollback(ssh, deploy_path, backup_path)
        return False

    log("Deploy concluído com sucesso!", "ok")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deploy automatizado do TSi-MUSIC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true", help="Simulação (não altera servidor)")
    parser.add_argument("--skip-build", action="store_true", help="Usa build existente")
    parser.add_argument("--skip-backup", action="store_true", help="Não cria backup")
    parser.add_argument("--rollback", metavar="BACKUP_PATH", help="Rollback para backup específico")
    parser.add_argument("--backup-only", action="store_true", help="Apenas cria backup")
    parser.add_argument("--health-only", action="store_true", help="Apenas health check")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host de deploy")
    parser.add_argument("--user", default=DEFAULT_USER, help="Usuário SSH")
    parser.add_argument("--path", default=DEFAULT_PATH, help="Path remoto")
    parser.add_argument("--build-dir", default=DEFAULT_BUILD_DIR, help="Diretório de build")

    args = parser.parse_args()

    ssh = SSHConfig(host=args.host, user=args.user, key=DEFAULT_SSH_KEY)

    if not check_prerequisites(ssh):
        return 1

    if args.health_only:
        return 0 if health_check(ssh) else 1

    if args.backup_only:
        backup_remote(ssh, args.path)
        return 0

    if args.rollback:
        return 0 if rollback(ssh, args.path, args.rollback) else 1

    if not args.skip_build and not args.dry_run:
        if not build_frontend():
            return 1

    ok = deploy(
        ssh,
        args.path,
        args.build_dir,
        dry_run=args.dry_run,
        backup=not args.skip_backup,
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
