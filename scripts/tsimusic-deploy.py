#!/usr/bin/env python3
# cspell:disable
# =============================================================================
# TSi-MUSIC — Deploy Automatizado com Rollback
# Versão: v2.9.5
#
# Automatiza deploy do frontend estático para o MidiaServer-SaudeClinica
# com suporte a simulação, backup e rollback.
#
# Uso:
#   python3 tsimusic-deploy.py
#   python3 tsimusic-deploy.py --dry-run
#   python3 tsimusic-deploy.py --rollback
#   python3 tsimusic-deploy.py --backup
#
# Variáveis de ambiente:
#   DEPLOY_HOST     — IP/hostname do servidor (default: 100.86.64.1)
#   DEPLOY_USER     — Usuário SSH (default: tsi)
#   DEPLOY_PATH     — Path remoto de deploy (default: /home/tsi/docker/ma-wiki)
#   SSH_KEY         — Path da chave SSH local
#   BUILD_DIR       — Diretório de build local (default: music_assistant_frontend)
# =============================================================================

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class _DummyColor:
        def __getattr__(self, name: str) -> str:
            return ""
    Fore = Style = _DummyColor()  # type: ignore[misc]

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_HOST = os.getenv("DEPLOY_HOST", "100.86.64.1")
DEFAULT_USER = os.getenv("DEPLOY_USER", "tsi")
DEFAULT_PATH = os.getenv("DEPLOY_PATH", "/home/tsi/docker/ma-wiki")
DEFAULT_SSH_KEY = os.getenv("SSH_KEY", str(Path.home() / ".ssh" / "id_ed25519_midiaserver"))
DEFAULT_BUILD_DIR = os.getenv("BUILD_DIR", "music_assistant_frontend")
LOG_DIR = Path(__file__).parent / "logs"
BACKUP_DIR = Path(__file__).parent / "backups"
STATE_FILE = Path(__file__).parent / ".deploy_state.json"

# ---------------------------------------------------------------------------
# Logging estruturado
# ---------------------------------------------------------------------------
class StructuredLogger:
    def __init__(self, log_dir: Path) -> None:
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.log_dir / f"deploy_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.log"
        self.entries: list[dict[str, Any]] = []

    def _write(self, level: str, msg: str) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": msg,
        }
        self.entries.append(entry)
        with self.session_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, default=str) + "\n")

    def info(self, msg: str) -> None:
        print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL}  {msg}")
        self._write("info", msg)

    def ok(self, msg: str) -> None:
        print(f"{Fore.GREEN}[OK]{Style.RESET_ALL}    {msg}")
        self._write("ok", msg)

    def warn(self, msg: str) -> None:
        print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL}  {msg}")
        self._write("warn", msg)

    def error(self, msg: str) -> None:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")
        self._write("error", msg)

    def step(self, msg: str) -> None:
        bar = f"{Fore.CYAN}{'━' * 60}{Style.RESET_ALL}"
        print(f"\n{bar}\n{Fore.CYAN}[STEP]{Style.RESET_ALL}  {msg}\n{bar}")
        self._write("step", msg)


# ---------------------------------------------------------------------------
# Deploy state
# ---------------------------------------------------------------------------
@dataclass
class DeployState:
    last_deploy_time: str | None = None
    last_deploy_hash: str | None = None
    backups: list[dict[str, str]] = field(default_factory=list)

    def save(self, path: Path) -> None:
        with path.open("w", encoding="utf-8") as fh:
            json.dump(asdict(self), fh, indent=2, default=str)

    @classmethod
    def load(cls, path: Path) -> DeployState:
        if not path.exists():
            return cls()
        try:
            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            return cls(
                last_deploy_time=data.get("last_deploy_time"),
                last_deploy_hash=data.get("last_deploy_hash"),
                backups=data.get("backups", []),
            )
        except Exception:
            return cls()


# ---------------------------------------------------------------------------
# Deploy engine
# ---------------------------------------------------------------------------
class DeployEngine:
    def __init__(
        self,
        host: str,
        user: str,
        remote_path: str,
        ssh_key: str,
        build_dir: str,
        logger: StructuredLogger,
        dry_run: bool = False,
    ) -> None:
        self.host = host
        self.user = user
        self.remote_path = remote_path
        self.ssh_key = Path(ssh_key).expanduser()
        self.build_dir = Path(build_dir)
        self.log = logger
        self.dry_run = dry_run
        self.state = DeployState.load(STATE_FILE)

    def _ssh(self, cmd: str, timeout: int = 30) -> tuple[int, str, str]:
        ssh_cmd = [
            "ssh",
            "-i", str(self.ssh_key),
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "ConnectTimeout=5",
            "-o", "BatchMode=yes",
            f"{self.user}@{self.host}",
            cmd,
        ]
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr

    def _rsync(self, src: str, dst: str, extra_flags: list[str] | None = None) -> int:
        flags = ["-avz"]
        if self.dry_run:
            flags.append("--dry-run")
        else:
            flags.append("--delete")
        if extra_flags:
            flags.extend(extra_flags)

        excludes = [
            "--exclude=nginx.conf",
            "--exclude=certs/",
            "--exclude=docker-compose.yml",
            "--exclude=.env",
            "--exclude=*.md",
        ]

        rsync_cmd = [
            "rsync", *flags, *excludes,
            "-e", f"ssh -i {self.ssh_key} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null",
            src, dst,
        ]
        self.log.info(f"rsync: {src} → {dst}")
        if self.dry_run:
            self.log.warn("MODO SIMULAÇÃO — nenhuma alteração será feita")
        result = subprocess.run(rsync_cmd)
        return result.returncode

    def verify_prerequisites(self) -> bool:
        self.log.step("Verificando pré-requisitos")
        ok = True

        for tool in ("rsync", "ssh", "curl"):
            if shutil.which(tool) is None:
                self.log.error(f"Ferramenta ausente: {tool}")
                ok = False

        if not self.ssh_key.exists():
            self.log.error(f"Chave SSH não encontrada: {self.ssh_key}")
            ok = False

        if not self.build_dir.exists():
            self.log.error(f"Diretório de build não encontrado: {self.build_dir}")
            ok = False

        # Testa SSH
        code, _, _ = self._ssh("echo OK", timeout=10)
        if code != 0:
            self.log.error(f"Falha na conexão SSH para {self.user}@{self.host}")
            ok = False
        else:
            self.log.ok("Conexão SSH OK")

        return ok

    def compute_build_hash(self) -> str:
        """Computa hash SHA-256 recursivo do diretório de build."""
        sha = hashlib.sha256()
        for path in sorted(self.build_dir.rglob("*")):
            if path.is_file():
                sha.update(path.relative_to(self.build_dir).as_bytes())
                sha.update(path.read_bytes())
        return sha.hexdigest()[:16]

    def backup_remote(self) -> str | None:
        self.log.step("Backup da versão remota")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.tar.gz"
        local_backup = BACKUP_DIR / backup_name
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        # Faz backup remoto compactando e baixando
        remote_backup_cmd = f"tar -czf /tmp/{backup_name} -C {self.remote_path} ."
        code, _, err = self._ssh(remote_backup_cmd, timeout=60)
        if code != 0:
            self.log.error(f"Falha ao criar backup remoto: {err.strip()}")
            return None

        # Download do backup
        scp_cmd = [
            "scp",
            "-i", str(self.ssh_key),
            "-o", "StrictHostKeyChecking=no",
            f"{self.user}@{self.host}:/tmp/{backup_name}",
            str(local_backup),
        ]
        result = subprocess.run(scp_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            self.log.error(f"Falha ao baixar backup: {result.stderr.strip()}")
            return None

        # Limpa tmp remoto
        self._ssh(f"rm -f /tmp/{backup_name}")

        self.state.backups.append({
            "timestamp": timestamp,
            "file": str(local_backup),
            "hash": self.state.last_deploy_hash or "unknown",
        })
        # Mantém apenas os últimos 10 backups
        self.state.backups = self.state.backups[-10:]
        self.state.save(STATE_FILE)

        self.log.ok(f"Backup salvo: {local_backup}")
        return str(local_backup)

    def deploy(self) -> int:
        if not self.verify_prerequisites():
            return 1

        if not self.dry_run:
            self.backup_remote()

        self.log.step("Sincronizando arquivos")
        src = f"{self.build_dir}/"
        dst = f"{self.user}@{self.host}:{self.remote_path}/"
        code = self._rsync(src, dst)
        if code != 0:
            self.log.error(f"rsync falhou com código {code}")
            return code

        if self.dry_run:
            self.log.warn("Dry-run concluído — revise as alterações acima")
            return 0

        self.log.ok("Sincronização concluída")

        # Reinicialização do container
        self.log.step("Reinicializando container nginx")
        restart_script = f"""set -e
COMPOSE_DIR="$(dirname {self.remote_path}/docker-compose.yml)"
cd "$COMPOSE_DIR"

if docker ps --format '{{{{.Names}}}}' | grep -q '^ma-wiki$'; then
  LOCAL_SHA=$(sha256sum nginx.conf 2>/dev/null | awk '{{print $1}}' || echo "")
  CONTAINER_SHA=$(docker exec ma-wiki sha256sum /etc/nginx/nginx.conf 2>/dev/null | awk '{{print $1}}' || echo "")
  if [ "$LOCAL_SHA" != "$CONTAINER_SHA" ]; then
    echo "nginx.conf alterado — recriando container..."
    docker compose down
    docker compose up -d
  else
    echo "nginx.conf inalterado — reload graceful..."
    docker exec ma-wiki nginx -s reload
  fi
else
  echo "Container não encontrado — subindo via docker compose..."
  docker compose up -d
fi
docker ps --filter "name=ma-wiki" --format "table {{{{.Names}}}}\t{{{{.Status}}}}\t{{{{.Ports}}}}"
"""
        code, out, err = self._ssh(restart_script, timeout=60)
        if code != 0:
            self.log.error(f"Falha ao reiniciar container: {err.strip()}")
            return code
        print(out)
        self.log.ok("Container atualizado")

        # Health check
        self.log.step("Health check pós-deploy")
        health_url = f"https://{self.host}:8443/info"
        for attempt in range(1, 13):  # 60s total
            try:
                import urllib.request
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                req = urllib.request.Request(health_url)
                with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
                    if resp.status == 200:
                        self.log.ok("Health check passou — HTTP 200")
                        break
            except Exception:
                pass
            self.log.info(f"Aguardando... ({attempt * 5}/60s)")
            time.sleep(5)
        else:
            self.log.error("Health check falhou após 60s")
            return 1

        # Atualiza state
        self.state.last_deploy_time = datetime.now(timezone.utc).isoformat()
        self.state.last_deploy_hash = self.compute_build_hash()
        self.state.save(STATE_FILE)

        self.log.ok("Deploy concluído com sucesso! 🎵")
        self.log.info(f"Acesse: https://{self.host}:8443")
        return 0

    def rollback(self) -> int:
        self.log.step("Rollback para versão anterior")
        if not self.state.backups:
            self.log.error("Nenhum backup disponível para rollback")
            return 1

        last_backup = self.state.backups[-1]
        backup_file = Path(last_backup["file"])
        if not backup_file.exists():
            self.log.error(f"Arquivo de backup não encontrado: {backup_file}")
            return 1

        self.log.info(f"Restaurando backup: {backup_file.name}")

        # Envia backup para o servidor e extrai
        remote_backup = f"/tmp/{backup_file.name}"
        scp_cmd = [
            "scp",
            "-i", str(self.ssh_key),
            "-o", "StrictHostKeyChecking=no",
            str(backup_file),
            f"{self.user}@{self.host}:{remote_backup}",
        ]
        result = subprocess.run(scp_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            self.log.error(f"Falha ao enviar backup: {result.stderr.strip()}")
            return 1

        extract_cmd = f"tar -xzf {remote_backup} -C {self.remote_path} && rm -f {remote_backup}"
        code, _, err = self._ssh(extract_cmd, timeout=60)
        if code != 0:
            self.log.error(f"Falha ao extrair backup: {err.strip()}")
            return 1

        # Reinicia container
        self._ssh(f"cd {self.remote_path} && docker compose restart", timeout=60)
        self.log.ok("Rollback concluído")
        return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tsimusic-deploy",
        description="Deploy automatizado do TSi-MUSIC para MidiaServer-SaudeClinica",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s                       # Deploy padrão
  %(prog)s --dry-run             # Simulação
  %(prog)s --backup              # Apenas backup
  %(prog)s --rollback            # Rollback para versão anterior
        """,
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host do servidor")
    parser.add_argument("--user", default=DEFAULT_USER, help="Usuário SSH")
    parser.add_argument("--path", default=DEFAULT_PATH, help="Path remoto de deploy")
    parser.add_argument("--ssh-key", default=DEFAULT_SSH_KEY, help="Path da chave SSH")
    parser.add_argument("--build-dir", default=DEFAULT_BUILD_DIR, help="Diretório de build local")
    parser.add_argument("--dry-run", action="store_true", help="Simulação (não altera nada)")
    parser.add_argument("--rollback", action="store_true", help="Rollback para versão anterior")
    parser.add_argument("--backup", action="store_true", help="Apenas realiza backup remoto")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logger = StructuredLogger(LOG_DIR)
    engine = DeployEngine(
        host=args.host,
        user=args.user,
        remote_path=args.path,
        ssh_key=args.ssh_key,
        build_dir=args.build_dir,
        logger=logger,
        dry_run=args.dry_run,
    )

    if args.backup:
        path = engine.backup_remote()
        return 0 if path else 1

    if args.rollback:
        return engine.rollback()

    return engine.deploy()


if __name__ == "__main__":
    sys.exit(main())
