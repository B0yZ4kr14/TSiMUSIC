#!/usr/bin/env python3
# cspell:disable
# =============================================================================
# TSi-MUSIC — Backup Automatizado
# Versão: v2.9.5
#
# Realiza backup automatizado dos dados do Music Assistant, configurações
# nginx e certificados no MidiaServer-SaudeClinica.
#
# Uso:
#   python3 tsimusic-backup.py
#   python3 tsimusic-backup.py --ma-only
#   python3 tsimusic-backup.py --config-only
#   python3 tsimusic-backup.py --list
#   python3 tsimusic-backup.py --restore /path/to/backup.tar.gz
#
# Variáveis de ambiente:
#   BACKUP_HOST   — IP/hostname do servidor (default: 100.86.64.1)
#   BACKUP_USER   — Usuário SSH (default: tsi)
#   BACKUP_PATH   — Diretório local de backups (default: ~/.tsimusic/backups)
#   SSH_KEY       — Path da chave SSH local
# =============================================================================

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
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
DEFAULT_HOST = os.getenv("BACKUP_HOST", "100.86.64.1")
DEFAULT_USER = os.getenv("BACKUP_USER", "tsi")
DEFAULT_BACKUP_PATH = os.getenv("BACKUP_PATH", str(Path.home() / ".tsimusic" / "backups"))
DEFAULT_SSH_KEY = os.getenv("SSH_KEY", str(Path.home() / ".ssh" / "id_ed25519_midiaserver"))
DEFAULT_REMOTE_PATH = "/home/tsi/docker/ma-wiki"
DEFAULT_MA_DATA_PATH = "/home/tsi/.musicassistant"

VERSION = "2.9.5"
SCRIPT_NAME = "tsimusic-backup"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
def log_info(msg: str) -> None:
    print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL}  {msg}")


def log_ok(msg: str) -> None:
    print(f"{Fore.GREEN}[OK]{Style.RESET_ALL}    {msg}")


def log_warn(msg: str) -> None:
    print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL}  {msg}")


def log_error(msg: str) -> None:
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")


def log_step(msg: str) -> None:
    bar = f"{Fore.CYAN}{'━' * 60}{Style.RESET_ALL}"
    print(f"\n{bar}\n{Fore.CYAN}[STEP]{Style.RESET_ALL}  {msg}\n{bar}")


# ---------------------------------------------------------------------------
# Backup engine
# ---------------------------------------------------------------------------
class BackupEngine:
    def __init__(
        self,
        host: str,
        user: str,
        ssh_key: str,
        backup_dir: str,
        remote_path: str,
        ma_data_path: str,
    ) -> None:
        self.host = host
        self.user = user
        self.ssh_key = Path(ssh_key).expanduser()
        self.backup_dir = Path(backup_dir).expanduser()
        self.remote_path = remote_path
        self.ma_data_path = ma_data_path

    def _ssh(self, cmd: str, timeout: int = 60) -> tuple[int, str, str]:
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

    def _verify_ssh(self) -> bool:
        code, _, _ = self._ssh("echo OK", timeout=10)
        return code == 0

    def _generate_timestamp(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    def _build_tar_cmd(self, mode: str, timestamp: str) -> str | None:
        """Constrói o comando tar remoto baseado no modo de backup."""
        remote_backup = f"/tmp/tsimusic_backup_{timestamp}.tar.gz"

        if mode == "full":
            # Verifica se o diretório MA existe remotamente
            code, _, _ = self._ssh(f"test -d {self.ma_data_path}")
            ma_exists = code == 0

            includes: list[str] = []
            if ma_exists:
                includes.append(self.ma_data_path)
            else:
                log_warn(f"Diretório MA não encontrado em {self.ma_data_path}; pulando MA data")

            includes.append(f"-C {self.remote_path} nginx.conf docker-compose.yml .env certs")

            sources = " ".join(includes)
            return f"tar -czf {remote_backup} {sources} 2>&1"

        if mode == "ma-only":
            code, _, _ = self._ssh(f"test -d {self.ma_data_path}")
            if code != 0:
                log_error(f"Diretório MA não encontrado: {self.ma_data_path}")
                return None
            return f"tar -czf {remote_backup} -C {self.ma_data_path} . 2>&1"

        if mode == "config-only":
            return (
                f"tar -czf {remote_backup} "
                f"-C {self.remote_path} nginx.conf docker-compose.yml .env certs 2>&1"
            )

        return None

    def create(self, mode: str) -> Path | None:
        log_step(f"Criando backup ({mode})")

        if not self._verify_ssh():
            log_error(f"Falha na conexão SSH para {self.user}@{self.host}")
            return None

        self.backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = self._generate_timestamp()
        tar_cmd = self._build_tar_cmd(mode, timestamp)
        if tar_cmd is None:
            log_error("Modo de backup inválido")
            return None

        # Executa tar no host remoto
        code, out, err = self._ssh(tar_cmd, timeout=120)
        if code != 0:
            log_error(f"Falha ao criar tarball remoto: {err.strip() or out.strip()}")
            return None

        remote_backup = f"/tmp/tsimusic_backup_{timestamp}.tar.gz"
        local_backup = self.backup_dir / f"tsimusic_{mode}_{timestamp}.tar.gz"

        # Download
        scp_cmd = [
            "scp",
            "-i", str(self.ssh_key),
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            f"{self.user}@{self.host}:{remote_backup}",
            str(local_backup),
        ]
        result = subprocess.run(scp_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            log_error(f"Falha ao baixar backup: {result.stderr.strip()}")
            self._ssh(f"rm -f {remote_backup}")
            return None

        # Limpa tmp remoto
        self._ssh(f"rm -f {remote_backup}")

        # Metadados
        meta = {
            "timestamp": timestamp,
            "mode": mode,
            "host": self.host,
            "file": str(local_backup.name),
            "size_bytes": local_backup.stat().st_size,
        }
        meta_path = local_backup.with_suffix(".tar.gz.json")
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

        size_mb = meta["size_bytes"] / (1024 * 1024)
        log_ok(f"Backup criado: {local_backup.name} ({size_mb:.2f} MB)")
        return local_backup

    def list_backups(self) -> list[dict[str, Any]]:
        log_step("Listando backups")
        if not self.backup_dir.exists():
            log_warn(f"Diretório de backups não existe: {self.backup_dir}")
            return []

        backups: list[dict[str, Any]] = []
        for path in sorted(self.backup_dir.glob("*.tar.gz")):
            meta_path = path.with_suffix(".tar.gz.json")
            meta: dict[str, Any] = {}
            if meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text(encoding="utf-8"))
                except Exception:
                    pass

            stat = path.stat()
            backups.append({
                "file": str(path.name),
                "path": str(path),
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                "mode": meta.get("mode", "unknown"),
                "host": meta.get("host", "unknown"),
            })

        return backups

    def restore(self, backup_path: str) -> bool:
        log_step(f"Restaurando backup: {backup_path}")
        src = Path(backup_path).expanduser()
        if not src.exists():
            log_error(f"Arquivo não encontrado: {src}")
            return False

        if not self._verify_ssh():
            log_error(f"Falha na conexão SSH para {self.user}@{self.host}")
            return False

        remote_backup = f"/tmp/{src.name}"

        # Upload
        scp_cmd = [
            "scp",
            "-i", str(self.ssh_key),
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            str(src),
            f"{self.user}@{self.host}:{remote_backup}",
        ]
        result = subprocess.run(scp_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            log_error(f"Falha ao enviar backup: {result.stderr.strip()}")
            return False

        # Detecta modo a partir do nome ou metadados
        mode = "full"
        meta_path = src.with_suffix(".tar.gz.json")
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                mode = meta.get("mode", "full")
            except Exception:
                pass
        elif "ma-only" in src.name:
            mode = "ma-only"
        elif "config-only" in src.name:
            mode = "config-only"

        if mode == "ma-only":
            extract_cmd = f"tar -xzf {remote_backup} -C {self.ma_data_path} && rm -f {remote_backup}"
        elif mode == "config-only":
            extract_cmd = f"tar -xzf {remote_backup} -C {self.remote_path} && rm -f {remote_backup}"
        else:
            # Full: extrai na raiz e depois move se necessário
            # O tarball full contém paths absolutos ou relativos
            extract_cmd = f"tar -xzf {remote_backup} -C / && rm -f {remote_backup}"

        code, out, err = self._ssh(extract_cmd, timeout=120)
        if code != 0:
            log_error(f"Falha ao extrair backup: {err.strip() or out.strip()}")
            return False

        log_ok("Backup restaurado com sucesso")
        log_info("Reinicie os containers para aplicar as alterações:")
        log_info(f"  ssh {self.user}@{self.host} 'cd {self.remote_path} && docker compose restart'")
        return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        description="Backup automatizado do TSi-MUSIC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s                    # Backup completo
  %(prog)s --ma-only          # Apenas dados do Music Assistant
  %(prog)s --config-only      # Apenas configs (nginx, docker-compose, certs)
  %(prog)s --list             # Listar backups existentes
  %(prog)s --restore ~/backups/tsimusic_full_20250101_120000.tar.gz
        """,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--ma-only", action="store_true", help="Backup apenas dos dados do MA")
    group.add_argument("--config-only", action="store_true", help="Backup apenas das configs")
    group.add_argument("--list", action="store_true", help="Listar backups existentes")
    group.add_argument("--restore", metavar="PATH", help="Restaurar backup a partir do path")

    parser.add_argument("--host", default=DEFAULT_HOST, help="Host do servidor")
    parser.add_argument("--user", default=DEFAULT_USER, help="Usuário SSH")
    parser.add_argument("--ssh-key", default=DEFAULT_SSH_KEY, help="Path da chave SSH")
    parser.add_argument("--backup-dir", default=DEFAULT_BACKUP_PATH, help="Diretório local de backups")
    parser.add_argument("--remote-path", default=DEFAULT_REMOTE_PATH, help="Path remoto do deploy")
    parser.add_argument("--ma-data-path", default=DEFAULT_MA_DATA_PATH, help="Path remoto dos dados do MA")
    parser.add_argument("--json", action="store_true", help="Saída em JSON (apenas para --list)")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    engine = BackupEngine(
        host=args.host,
        user=args.user,
        ssh_key=args.ssh_key,
        backup_dir=args.backup_dir,
        remote_path=args.remote_path,
        ma_data_path=args.ma_data_path,
    )

    if args.list:
        backups = engine.list_backups()
        if args.json:
            print(json.dumps(backups, indent=2, default=str))
            return 0

        if not backups:
            log_warn("Nenhum backup encontrado.")
            return 0

        print(f"\n{Fore.CYAN}{'━' * 80}{Style.RESET_ALL}")
        print(f"  {'ARQUIVO':<45} {'MODO':<12} {'TAMANHO':<10} {'DATA'}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'━' * 80}{Style.RESET_ALL}")
        for b in backups:
            print(f"  {b['file']:<45} {b['mode']:<12} {b['size_mb']:<10.2f} {b['created'][:19]}")
        print(f"{Fore.CYAN}{'━' * 80}{Style.RESET_ALL}")
        log_info(f"Total: {len(backups)} backup(s)")
        return 0

    if args.restore:
        ok = engine.restore(args.restore)
        return 0 if ok else 1

    mode = "full"
    if args.ma_only:
        mode = "ma-only"
    elif args.config_only:
        mode = "config-only"

    result = engine.create(mode)
    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
