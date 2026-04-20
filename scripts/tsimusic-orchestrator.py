#!/usr/bin/env python3
# cspell:disable
# =============================================================================
# TSi-MUSIC — OpenSquad Orchestrator CLI
# Versão: v2.9.5
#
# Orquestra squads do OpenSquad para automação do TSi-MUSIC.
#
# Uso:
#   python3 tsimusic-orchestrator.py --list
#   python3 tsimusic-orchestrator.py --run <squad-name>
#   python3 tsimusic-orchestrator.py --status
#   python3 tsimusic-orchestrator.py --health
#
# Configuração:
#   tsimusic.toml  (diretório atual ou ~/.config/tsimusic/)
#   Variáveis de ambiente: TSIMUSIC_OPENSQUAD_PATH, TSIMUSIC_SQUADS_DIR
# =============================================================================

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# Colorama para saída colorida multiplataforma
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    # Fallback se colorama não estiver instalado
    class _DummyColor:
        def __getattr__(self, name: str) -> str:
            return ""
    Fore = Style = _DummyColor()  # type: ignore[misc]

# TOML parser (tomli para <3.11, builtin para >=3.11)
try:
    import tomllib  # type: ignore[import]
except ImportError:
    import tomli as tomllib  # type: ignore[import]

# ---------------------------------------------------------------------------
# Constantes e defaults
# ---------------------------------------------------------------------------
SCRIPT_NAME = "tsimusic-orchestrator"
VERSION = "2.9.5"
DEFAULT_OPENSQUAD_PATH = Path.home() / "opensquad"
CONFIG_FILENAMES = ["tsimusic.toml", ".tsimusic.toml"]

# ---------------------------------------------------------------------------
# Logging colorizado
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
# Configuração
# ---------------------------------------------------------------------------
class Config:
    """Carrega configuração de tsimusic.toml + variáveis de ambiente."""

    opensquad_path: Path
    squads_dir: Path
    default_squad: str | None

    def __init__(self, overrides: dict[str, Any] | None = None) -> None:
        overrides = overrides or {}
        raw = self._load_toml()

        self.opensquad_path = Path(
            overrides.get("opensquad_path")
            or os.getenv("TSIMUSIC_OPENSQUAD_PATH")
            or raw.get("opensquad", {}).get("path", str(DEFAULT_OPENSQUAD_PATH))
        ).expanduser().resolve()

        self.squads_dir = Path(
            overrides.get("squads_dir")
            or os.getenv("TSIMUSIC_SQUADS_DIR")
            or raw.get("opensquad", {}).get("squads_dir", str(self.opensquad_path / "squads"))
        ).expanduser().resolve()

        self.default_squad = (
            overrides.get("default_squad")
            or os.getenv("TSIMUSIC_DEFAULT_SQUAD")
            or raw.get("opensquad", {}).get("default_squad")
        )

    @staticmethod
    def _find_config_file() -> Path | None:
        for name in CONFIG_FILENAMES:
            local = Path.cwd() / name
            if local.exists():
                return local
            home_cfg = Path.home() / ".config" / "tsimusic" / name
            if home_cfg.exists():
                return home_cfg
        return None

    @classmethod
    def _load_toml(cls) -> dict[str, Any]:
        cfg_path = cls._find_config_file()
        if not cfg_path:
            return {}
        try:
            with cfg_path.open("rb") as fh:
                return tomllib.load(fh)  # type: ignore[return-value]
        except Exception as exc:
            log_warn(f"Erro lendo {cfg_path}: {exc}")
            return {}

# ---------------------------------------------------------------------------
# OpenSquad helpers
# ---------------------------------------------------------------------------
class OpenSquadManager:
    def __init__(self, config: Config) -> None:
        self.cfg = config

    def _run_npx(self, *args: str, capture: bool = True) -> subprocess.CompletedProcess[str]:
        cmd = ["npx", "opensquad", *args]
        return subprocess.run(
            cmd,
            cwd=str(self.cfg.opensquad_path),
            capture_output=capture,
            text=True,
            check=False,
        )

    def list_squads(self) -> list[dict[str, Any]]:
        """Lista squads disponíveis lendo o diretório de squads."""
        squads: list[dict[str, Any]] = []
        if not self.cfg.squads_dir.exists():
            log_warn(f"Diretório de squads não encontrado: {self.cfg.squads_dir}")
            return squads

        for entry in sorted(self.cfg.squads_dir.iterdir()):
            if entry.is_dir() and not entry.name.startswith((".", "_")):
                squad_info = self._read_squad_metadata(entry)
                squads.append(squad_info)
        return squads

    def _read_squad_metadata(self, path: Path) -> dict[str, Any]:
        meta = {
            "name": path.name,
            "path": str(path),
            "description": "",
            "status": "unknown",
        }
        # Tenta ler um arquivo squad.toml ou squad.json dentro do diretório
        for meta_file in ("squad.toml", "squad.json", "config.toml", "config.json"):
            fp = path / meta_file
            if fp.exists():
                try:
                    if meta_file.endswith(".toml"):
                        with fp.open("rb") as fh:
                            data = tomllib.load(fh)  # type: ignore[assignment]
                    else:
                        data = json.loads(fp.read_text(encoding="utf-8"))
                    meta["description"] = data.get("description", data.get("name", ""))
                    meta["status"] = data.get("status", "configured")
                except Exception:
                    pass
                break

        # Verifica histórico de execuções (pasta output/)
        output_dir = path / "output"
        if output_dir.exists():
            runs = sorted(
                (p for p in output_dir.iterdir() if p.is_file()),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if runs:
                meta["last_run"] = runs[0].name
                meta["last_run_time"] = runs[0].stat().st_mtime
        return meta

    def run_squad(self, name: str) -> int:
        """Executa um squad via npx opensquad run <name>."""
        log_step(f"Executando squad: {name}")
        log_info("Isso pode levar alguns minutos...")

        # Primeiro verifica se o squad existe
        squad_path = self.cfg.squads_dir / name
        if not squad_path.exists():
            log_error(f"Squad não encontrado: {name}")
            log_info(f"Diretório esperado: {squad_path}")
            return 1

        result = self._run_npx("run", name, capture=False)
        return result.returncode

    def status(self) -> dict[str, Any]:
        """Retorna status geral do ecossistema OpenSquad."""
        status: dict[str, Any] = {
            "opensquad_path": str(self.cfg.opensquad_path),
            "squads_dir": str(self.cfg.squads_dir),
            "squads_count": 0,
            "squads": [],
            "npx_available": False,
            "version": VERSION,
        }

        # Verifica npx
        npx_check = subprocess.run(["which", "npx"], capture_output=True, text=True)
        status["npx_available"] = npx_check.returncode == 0

        # Lista squads
        squads = self.list_squads()
        status["squads_count"] = len(squads)
        status["squads"] = squads
        return status

# ---------------------------------------------------------------------------
# Health check rápido (orquestrator)
# ---------------------------------------------------------------------------
def quick_health(config: Config) -> int:
    """Health check rápido do ambiente local OpenSquad."""
    log_step("Health check rápido — OpenSquad")
    healthy = True

    checks = [
        ("Diretório OpenSquad", config.opensquad_path.exists()),
        ("Diretório squads", config.squads_dir.exists()),
        ("npx disponível", subprocess.run(["which", "npx"], capture_output=True).returncode == 0),
        ("Node.js disponível", subprocess.run(["which", "node"], capture_output=True).returncode == 0),
    ]

    for label, ok in checks:
        if ok:
            log_ok(f"{label}: OK")
        else:
            log_error(f"{label}: FALHA")
            healthy = False

    # Verifica se existem squads
    mgr = OpenSquadManager(config)
    squads = mgr.list_squads()
    if squads:
        log_ok(f"Squads encontrados: {len(squads)}")
    else:
        log_warn("Nenhum squad encontrado")

    return 0 if healthy else 1

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        description="Orquestra squads do OpenSquad para automação do TSi-MUSIC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s --list
  %(prog)s --run tsimusic-eta-scripts
  %(prog)s --status
  %(prog)s --health
        """,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", "-l", action="store_true", help="Lista squads disponíveis")
    group.add_argument("--run", "-r", metavar="SQUAD", help="Executa um squad")
    group.add_argument("--status", "-s", action="store_true", help="Status de todos os squads")
    group.add_argument("--health", "-H", action="store_true", help="Health check rápido")

    parser.add_argument(
        "--opensquad-path",
        metavar="PATH",
        help="Path do OpenSquad (sobrescreve config/env)",
    )
    parser.add_argument(
        "--squads-dir",
        metavar="PATH",
        help="Diretório de squads (sobrescreve config/env)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Saída em JSON (apenas para --list e --status)",
    )
    return parser


def cmd_list(mgr: OpenSquadManager, json_mode: bool) -> int:
    squads = mgr.list_squads()
    if json_mode:
        print(json.dumps(squads, indent=2, default=str))
        return 0

    if not squads:
        log_warn("Nenhum squad encontrado.")
        log_info(f"Diretório pesquisado: {mgr.cfg.squads_dir}")
        return 0

    print(f"\n{Fore.CYAN}{'━' * 70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'SQUAD':<30}{'STATUS':<12}{'DESCRIÇÃO':<30}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'━' * 70}{Style.RESET_ALL}")
    for s in squads:
        name = s["name"][:28]
        status = s.get("status", "unknown")[:10]
        desc = s.get("description", "")[:28]
        status_color = Fore.GREEN if status == "active" else Fore.YELLOW if status == "configured" else Fore.WHITE
        print(f"{name:<30}{status_color}{status:<12}{Style.RESET_ALL}{desc:<30}")
    print(f"{Fore.CYAN}{'━' * 70}{Style.RESET_ALL}\n")
    log_info(f"Total: {len(squads)} squad(s)")
    return 0


def cmd_run(mgr: OpenSquadManager, squad_name: str) -> int:
    code = mgr.run_squad(squad_name)
    if code == 0:
        log_ok(f"Squad '{squad_name}' executado com sucesso.")
    else:
        log_error(f"Squad '{squad_name}' falhou com código {code}.")
    return code


def cmd_status(mgr: OpenSquadManager, json_mode: bool) -> int:
    status = mgr.status()
    if json_mode:
        print(json.dumps(status, indent=2, default=str))
        return 0

    log_step("Status do OpenSquad")
    print(f"  OpenSquad path : {status['opensquad_path']}")
    print(f"  Squads dir     : {status['squads_dir']}")
    print(f"  npx disponível : {'Sim' if status['npx_available'] else 'Não'}")
    print(f"  Squads         : {status['squads_count']}")

    for s in status["squads"]:
        last = s.get("last_run", "nunca")
        print(f"    • {s['name']:<25} [{s.get('status', '?'):<10}] last: {last}")
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    overrides = {}
    if args.opensquad_path:
        overrides["opensquad_path"] = args.opensquad_path
    if args.squads_dir:
        overrides["squads_dir"] = args.squads_dir

    config = Config(overrides)
    mgr = OpenSquadManager(config)

    if args.list:
        return cmd_list(mgr, args.json)
    if args.run:
        return cmd_run(mgr, args.run)
    if args.status:
        return cmd_status(mgr, args.json)
    if args.health:
        return quick_health(config)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
