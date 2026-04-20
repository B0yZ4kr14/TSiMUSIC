#!/usr/bin/env python3
# cspell:disable
# =============================================================================
# TSi-MUSIC — Análise de Logs
# Versão: v2.9.5
#
# Analisa logs do nginx e Music Assistant no MidiaServer-SaudeClinica.
# Suporta filtragem por tempo, status codes, IPs e erros.
#
# Uso:
#   python3 tsimusic-log-analyzer.py --nginx
#   python3 tsimusic-log-analyzer.py --nginx --errors
#   python3 tsimusic-log-analyzer.py --nginx --top-ips
#   python3 tsimusic-log-analyzer.py --nginx --status-codes
#   python3 tsimusic-log-analyzer.py --nginx --since 1h
#   python3 tsimusic-log-analyzer.py --ma --errors
#
# Variáveis de ambiente:
#   LOG_HOST      — IP/hostname do servidor (default: 100.86.64.1)
#   LOG_USER      — Usuário SSH (default: tsi)
#   SSH_KEY       — Path da chave SSH local
# =============================================================================

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
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
DEFAULT_HOST = os.getenv("LOG_HOST", "100.86.64.1")
DEFAULT_USER = os.getenv("LOG_USER", "tsi")
DEFAULT_SSH_KEY = os.getenv("SSH_KEY", str(Path.home() / ".ssh" / "id_ed25519_midiaserver"))

VERSION = "2.9.5"
SCRIPT_NAME = "tsimusic-log-analyzer"

# Nginx log format: $remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "..." "..."
NGINX_LOG_RE = re.compile(
    r'^(?P<ip>[\d.]+)\s+-\s+(?P<user>\S+)\s+\[(?P<time>[^\]]+)\]\s+'
    r'"(?P<method>\S+)\s+(?P<path>\S+)\s+(?P<proto>[^"]*)"\s+'
    r'(?P<status>\d+)\s+(?P<bytes>\d+)\s+"(?P<referer>[^"]*)"\s+"(?P<ua>[^"]*)"'
)

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
# Log entry
# ---------------------------------------------------------------------------
class LogEntry:
    def __init__(self, raw: str) -> None:
        self.raw = raw
        self.ip = ""
        self.user = ""
        self.time_str = ""
        self.time: datetime | None = None
        self.method = ""
        self.path = ""
        self.proto = ""
        self.status = 0
        self.bytes = 0
        self.referer = ""
        self.ua = ""
        self._parse()

    def _parse(self) -> None:
        m = NGINX_LOG_RE.match(self.raw)
        if not m:
            return
        self.ip = m.group("ip")
        self.user = m.group("user")
        self.time_str = m.group("time")
        self.method = m.group("method")
        self.path = m.group("path")
        self.proto = m.group("proto")
        self.status = int(m.group("status"))
        self.bytes = int(m.group("bytes"))
        self.referer = m.group("referer")
        self.ua = m.group("ua")
        try:
            # Format: 18/Apr/2026:18:50:26 +0000
            self.time = datetime.strptime(self.time_str, "%d/%b/%Y:%H:%M:%S %z")
        except ValueError:
            pass

    def is_error(self) -> bool:
        return self.status >= 400

    def to_dict(self) -> dict[str, Any]:
        return {
            "ip": self.ip,
            "time": self.time_str,
            "method": self.method,
            "path": self.path,
            "status": self.status,
            "bytes": self.bytes,
            "referer": self.referer,
            "ua": self.ua,
        }


# ---------------------------------------------------------------------------
# Log analyzer engine
# ---------------------------------------------------------------------------
class LogAnalyzer:
    def __init__(
        self,
        host: str,
        user: str,
        ssh_key: str,
    ) -> None:
        self.host = host
        self.user = user
        self.ssh_key = Path(ssh_key).expanduser()

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

    def _verify_ssh(self) -> bool:
        code, _, _ = self._ssh("echo OK", timeout=10)
        return code == 0

    def _fetch_nginx_logs(self, since: timedelta | None = None) -> list[str]:
        """Busca logs do nginx dentro do container ma-wiki."""
        log_cmd = "docker exec ma-wiki cat /var/log/nginx/access.log 2>/dev/null || true"
        if since:
            # Filtra localmente após buscar; nginx access log não tem journalctl
            pass
        code, out, err = self._ssh(log_cmd, timeout=30)
        if code != 0:
            log_warn(f"Erro ao buscar logs nginx: {err.strip()}")
        lines = out.strip().splitlines()
        return lines

    def _fetch_ma_logs(self, since: timedelta | None = None) -> list[str]:
        """Busca logs do Music Assistant (docker logs)."""
        # Tenta container ma-wiki se tiver MA embedado, ou container music-assistant
        for container in ["music-assistant", "ma-server", "ma-wiki"]:
            code, out, _ = self._ssh(f"docker ps --format '{{{{.Names}}}}' | grep -q '^{container}$'")
            if code == 0:
                since_flag = f" --since {since.total_seconds()}s" if since else ""
                log_cmd = f"docker logs{since_flag} {container} 2>&1 | tail -n 1000"
                code2, out2, err2 = self._ssh(log_cmd, timeout=30)
                if code2 == 0:
                    return out2.strip().splitlines()
                else:
                    log_warn(f"Erro ao buscar logs de {container}: {err2.strip()}")
                    return []
        log_warn("Nenhum container do Music Assistant encontrado")
        return []

    def _filter_since(self, entries: list[LogEntry], since: timedelta) -> list[LogEntry]:
        cutoff = datetime.now(timezone.utc) - since
        return [e for e in entries if e.time and e.time >= cutoff]

    def analyze_nginx(
        self,
        since: timedelta | None = None,
        errors_only: bool = False,
        top_ips: bool = False,
        status_codes: bool = False,
        json_mode: bool = False,
    ) -> dict[str, Any]:
        log_step("Analisando logs do nginx")
        lines = self._fetch_nginx_logs(since)
        if not lines:
            log_warn("Nenhuma linha de log encontrada")
            return {"entries": [], "summary": {}}

        entries = [LogEntry(line) for line in lines if line.strip()]
        if since:
            entries = self._filter_since(entries, since)
        if errors_only:
            entries = [e for e in entries if e.is_error()]

        total = len(entries)
        result: dict[str, Any] = {
            "total_lines": total,
            "since": str(since) if since else None,
            "errors_only": errors_only,
        }

        if json_mode:
            result["entries"] = [e.to_dict() for e in entries]

        if status_codes:
            counter = Counter(e.status for e in entries if e.status)
            result["status_codes"] = dict(counter.most_common())
            if not json_mode:
                print(f"\n{Fore.CYAN}--- Distribuição de Status Codes ---{Style.RESET_ALL}")
                print(f"  {'Status':<10} {'Quantidade':<12} {'%':>6}")
                print(f"  {'-'*10} {'-'*12} {'-'*6}")
                for code, count in counter.most_common():
                    pct = (count / total * 100) if total else 0
                    color = Fore.GREEN if code < 400 else Fore.YELLOW if code < 500 else Fore.RED
                    print(f"  {color}{code:<10}{Style.RESET_ALL} {count:<12} {pct:>6.1f}")
                print("")

        if top_ips:
            counter = Counter(e.ip for e in entries if e.ip)
            result["top_ips"] = dict(counter.most_common(20))
            if not json_mode:
                print(f"\n{Fore.CYAN}--- Top IPs ---{Style.RESET_ALL}")
                print(f"  {'IP':<20} {'Requisições':<12}")
                print(f"  {'-'*20} {'-'*12}")
                for ip, count in counter.most_common(20):
                    print(f"  {ip:<20} {count:<12}")
                print("")

        if errors_only and not json_mode and not status_codes and not top_ips:
            print(f"\n{Fore.CYAN}--- Erros (status >= 400) ---{Style.RESET_ALL}")
            for e in entries:
                color = Fore.YELLOW if e.status < 500 else Fore.RED
                print(f"  {color}{e.status}{Style.RESET_ALL} {e.method} {e.path} — {e.ip} @ {e.time_str}")
            print(f"\n  Total de erros: {len(entries)}\n")
            result["error_count"] = len(entries)

        if not json_mode and not status_codes and not top_ips and not errors_only:
            # Resumo geral
            errors = [e for e in entries if e.is_error()]
            print(f"\n{Fore.CYAN}--- Resumo ---{Style.RESET_ALL}")
            print(f"  Total de requisições: {total}")
            print(f"  Erros (>=400): {len(errors)}")
            if entries:
                unique_ips = len(set(e.ip for e in entries if e.ip))
                print(f"  IPs únicos: {unique_ips}")
                statuses = Counter(e.status for e in entries if e.status)
                print(f"  Status mais comum: {statuses.most_common(1)[0][0]} ({statuses.most_common(1)[0][1]}x)")
            print("")

        return result

    def analyze_ma(
        self,
        since: timedelta | None = None,
        errors_only: bool = False,
        json_mode: bool = False,
    ) -> dict[str, Any]:
        log_step("Analisando logs do Music Assistant")
        lines = self._fetch_ma_logs(since)
        if not lines:
            log_warn("Nenhuma linha de log do MA encontrada")
            return {"entries": [], "summary": {}}

        if errors_only:
            # Filtra linhas com ERROR, CRITICAL, Exception
            error_keywords = ("ERROR", "CRITICAL", "EXCEPTION", "Traceback")
            lines = [line for line in lines if any(kw in line.upper() for kw in error_keywords)]

        total = len(lines)
        result: dict[str, Any] = {
            "total_lines": total,
            "since": str(since) if since else None,
            "errors_only": errors_only,
        }

        if json_mode:
            result["entries"] = lines

        if not json_mode:
            print(f"\n{Fore.CYAN}--- Logs do Music Assistant ---{Style.RESET_ALL}")
            if errors_only:
                print(f"  Mostrando {total} linha(s) de erro:\n")
            for line in lines:
                if "ERROR" in line or "CRITICAL" in line:
                    print(f"  {Fore.RED}{line}{Style.RESET_ALL}")
                elif "WARN" in line:
                    print(f"  {Fore.YELLOW}{line}{Style.RESET_ALL}")
                else:
                    print(f"  {line}")
            print("")

        return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def parse_since(value: str) -> timedelta:
    """Converte strings como '1h', '30m', '1d' para timedelta."""
    m = re.match(r"^(\d+)([smhd])$", value.lower())
    if not m:
        raise argparse.ArgumentTypeError(
            f"Formato inválido: '{value}'. Use: <número><s|m|h|d> (ex: 1h, 30m, 1d)"
        )
    num, unit = int(m.group(1)), m.group(2)
    mapping = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days"}
    return timedelta(**{mapping[unit]: num})


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        description="Análise de logs do TSi-MUSIC (nginx e Music Assistant)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s --nginx
  %(prog)s --nginx --errors --since 1h
  %(prog)s --nginx --top-ips --since 1d
  %(prog)s --nginx --status-codes
  %(prog)s --ma --errors
        """,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--nginx", action="store_true", help="Analisar logs do nginx")
    group.add_argument("--ma", action="store_true", help="Analisar logs do Music Assistant")

    parser.add_argument("--errors", action="store_true", help="Mostrar apenas erros")
    parser.add_argument("--top-ips", action="store_true", help="IPs com mais requisições (apenas nginx)")
    parser.add_argument("--status-codes", action="store_true", help="Distribuição de status codes (apenas nginx)")
    parser.add_argument("--since", type=parse_since, metavar="INTERVAL", help="Filtrar desde (ex: 1h, 30m, 1d)")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host do servidor")
    parser.add_argument("--user", default=DEFAULT_USER, help="Usuário SSH")
    parser.add_argument("--ssh-key", default=DEFAULT_SSH_KEY, help="Path da chave SSH")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    analyzer = LogAnalyzer(
        host=args.host,
        user=args.user,
        ssh_key=args.ssh_key,
    )

    if not analyzer._verify_ssh():
        log_error(f"Falha na conexão SSH para {args.user}@{args.host}")
        return 1

    if args.nginx:
        result = analyzer.analyze_nginx(
            since=args.since,
            errors_only=args.errors,
            top_ips=args.top_ips,
            status_codes=args.status_codes,
            json_mode=args.json,
        )
    else:
        if args.top_ips or args.status_codes:
            log_warn("--top-ips e --status-codes são suportados apenas com --nginx")
        result = analyzer.analyze_ma(
            since=args.since,
            errors_only=args.errors,
            json_mode=args.json,
        )

    if args.json:
        print(json.dumps(result, indent=2, default=str))

    return 0


if __name__ == "__main__":
    sys.exit(main())
