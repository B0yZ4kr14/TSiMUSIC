#!/usr/bin/env python3
# cspell:disable
# =============================================================================
# TSi-MUSIC — Health Check Avançado
# Versão: v2.9.5
#
# Verifica integridade completa do TSi-MUSIC no MidiaServer-SaudeClinica.
#
# Uso:
#   python3 tsimusic-healthcheck.py
#   python3 tsimusic-healthcheck.py --json
#   python3 tsimusic-healthcheck.py --host 100.86.64.1
#
# Exit codes:
#   0 — Todos os checks passaram
#   1 — Um ou mais checks falharam
# =============================================================================

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import ssl
import subprocess
import sys
import urllib.request
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

try:
    import websocket
    HAS_WEBSOCKET = True
except ImportError:
    HAS_WEBSOCKET = False

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_HOST = os.getenv("TSIMUSIC_HOST", "100.86.64.1")
DEFAULT_SSH_USER = os.getenv("DEPLOY_USER", "tsi")
DEFAULT_SSH_KEY = os.getenv("SSH_KEY", str(Path.home() / ".ssh" / "id_ed25519_midiaserver"))
HEALTH_PORT = 8443
HTTP_PORT = 8080
MA_WS_PORT = 8095
MA_STREAM_PORT = 8097

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class CheckResult:
    name: str
    status: str  # "pass", "warn", "fail"
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0


@dataclass
class HealthReport:
    timestamp: str
    host: str
    overall: str  # "healthy", "degraded", "unhealthy"
    checks: list[CheckResult]
    summary: dict[str, int] = field(default_factory=dict)

    def compute_summary(self) -> None:
        self.summary = {"pass": 0, "warn": 0, "fail": 0}
        for c in self.checks:
            self.summary[c.status] = self.summary.get(c.status, 0) + 1
        if self.summary["fail"] > 0:
            self.overall = "unhealthy"
        elif self.summary["warn"] > 0:
            self.overall = "degraded"
        else:
            self.overall = "healthy"


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
def _colored(label: str, color: str, msg: str) -> None:
    print(f"{color}[{label}]{Style.RESET_ALL} {msg}")


def log_pass(msg: str) -> None:
    _colored("PASS", Fore.GREEN, msg)


def log_warn(msg: str) -> None:
    _colored("WARN", Fore.YELLOW, msg)


def log_fail(msg: str) -> None:
    _colored("FAIL", Fore.RED, msg)


def log_info(msg: str) -> None:
    _colored("INFO", Fore.BLUE, msg)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
class HealthChecker:
    def __init__(self, host: str, ssh_user: str, ssh_key: str) -> None:
        self.host = host
        self.ssh_user = ssh_user
        self.ssh_key = Path(ssh_key).expanduser()
        self.results: list[CheckResult] = []
        self._ssh_prefix = [
            "ssh",
            "-i", str(self.ssh_key),
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=5",
            "-o", "BatchMode=yes",
            f"{self.ssh_user}@{self.host}",
        ]

    def _ssh(self, cmd: str) -> tuple[int, str, str]:
        """Executa comando via SSH. Retorna (returncode, stdout, stderr)."""
        result = subprocess.run(
            [*self._ssh_prefix, cmd],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.returncode, result.stdout, result.stderr

    def _check_container(self) -> CheckResult:
        name = "Container ma-wiki"
        code, out, err = self._ssh("docker ps --format '{{.Names}}' --filter 'name=ma-wiki'")
        if code != 0:
            return CheckResult(name, "fail", f"SSH/erro: {err.strip()}")
        if "ma-wiki" in out:
            return CheckResult(name, "pass", "Container ma-wiki está running", {"containers": out.strip().splitlines()})
        return CheckResult(name, "fail", "Container ma-wiki NÃO está running")

    def _check_ports(self) -> CheckResult:
        name = "Portas em escuta"
        ports = [HEALTH_PORT, HTTP_PORT, MA_WS_PORT, MA_STREAM_PORT]
        details: dict[str, Any] = {"ports": {}}
        all_listening = True

        for port in ports:
            # Verifica se a porta está aberta no host remoto via ss ou netstat
            code, out, _ = self._ssh(f"ss -tlnp '( sport = :{port} )' 2>/dev/null || netstat -tlnp 2>/dev/null | grep ':{port} '")
            listening = code == 0 and str(port) in out
            details["ports"][port] = "listening" if listening else "closed"
            if not listening:
                all_listening = False

        status = "pass" if all_listening else "fail"
        msg = "Todas as portas estão em escuta" if all_listening else "Algumas portas não estão em escuta"
        return CheckResult(name, status, msg, details)

    def _check_nginx_root(self) -> CheckResult:
        name = "Nginx responde 200 em /"
        url = f"https://{self.host}:{HEALTH_PORT}/"
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                ok = resp.status == 200
                return CheckResult(
                    name,
                    "pass" if ok else "fail",
                    f"HTTP {resp.status}" if ok else f"HTTP {resp.status} (esperado 200)",
                    {"status": resp.status},
                )
        except Exception as exc:
            return CheckResult(name, "fail", str(exc))

    def _check_ma_info(self) -> CheckResult:
        name = "MA Server /info JSON"
        url = f"https://{self.host}:{HEALTH_PORT}/info"
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
                body = resp.read().decode("utf-8")
                data = json.loads(body)
                return CheckResult(
                    name,
                    "pass",
                    f"server={data.get('server_name', 'unknown')} version={data.get('server_version', 'unknown')}",
                    {"json": data},
                )
        except json.JSONDecodeError as exc:
            return CheckResult(name, "fail", f"JSON inválido: {exc}")
        except Exception as exc:
            return CheckResult(name, "fail", str(exc))

    def _check_websocket(self) -> CheckResult:
        name = "WebSocket handshake /ws"
        if not HAS_WEBSOCKET:
            return CheckResult(name, "warn", "websocket-client não instalado (pip install websocket-client)")

        ws_url = f"wss://{self.host}:{HEALTH_PORT}/ws"
        try:
            ws = websocket.create_connection(
                ws_url,
                sslopt={"cert_reqs": ssl.CERT_NONE, "check_hostname": False},
                timeout=10,
            )
            # MA Server envia mensagem JSON imediatamente
            msg = ws.recv_timeout(5) if hasattr(ws, "recv_timeout") else ws.recv()
            ws.close()
            try:
                data = json.loads(msg)
                return CheckResult(name, "pass", f"Handshake OK: {data.get('event', 'connected')}", {"message": data})
            except json.JSONDecodeError:
                return CheckResult(name, "pass", "Handshake OK (mensagem não-JSON)", {"raw": msg[:200]})
        except Exception as exc:
            return CheckResult(name, "fail", str(exc))

    def _check_tailscale(self) -> CheckResult:
        name = "Tailscale Serve ativo"
        # Verifica se tailscale está ativo no host remoto
        code, out, err = self._ssh("tailscale status --json 2>/dev/null | head -c 2000")
        if code != 0:
            return CheckResult(name, "warn", f"Tailscale não disponível ou erro: {err.strip()}")
        try:
            data = json.loads(out)
            backend_state = data.get("BackendState", "Unknown")
            online = backend_state == "Running"
            return CheckResult(
                name,
                "pass" if online else "fail",
                f"Tailscale state={backend_state}",
                {"state": backend_state},
            )
        except json.JSONDecodeError:
            # Fallback simples
            return CheckResult(name, "pass" if "Running" in out else "warn", "Tailscale status obtido")

    def _check_ssl_cert(self) -> CheckResult:
        name = "SSL Cert validity"
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with socket.create_connection((self.host, HEALTH_PORT), timeout=10) as sock:
                with ctx.wrap_socket(sock, server_hostname=self.host) as ssock:
                    cert = ssock.getpeercert()
                    if not cert:
                        return CheckResult(name, "warn", "Certificado não fornecido (possivelmente self-signed local)")
                    not_after = cert.get("notAfter")
                    if not_after:
                        expire = ssl.cert_time_to_seconds(not_after)
                        now = datetime.now(timezone.utc).timestamp()
                        days_left = int((expire - now) / 86400)
                        status = "pass" if days_left > 7 else "warn" if days_left > 0 else "fail"
                        return CheckResult(name, status, f"{days_left} dia(s) até expirar", {"days_left": days_left, "not_after": not_after})
            return CheckResult(name, "warn", "Não foi possível obter certificado")
        except Exception as exc:
            return CheckResult(name, "warn", str(exc))

    def _check_disk_space(self) -> CheckResult:
        name = "Espaço em disco"
        code, out, _ = self._ssh("df -h / | tail -1")
        if code != 0:
            return CheckResult(name, "warn", "Não foi possível obter uso de disco")
        parts = out.strip().split()
        if len(parts) >= 5:
            usage_pct = parts[4].replace("%", "")
            try:
                pct = int(usage_pct)
                status = "pass" if pct < 80 else "warn" if pct < 95 else "fail"
                return CheckResult(name, status, f"Uso do disco: {pct}%", {"usage_percent": pct, "details": out.strip()})
            except ValueError:
                pass
        return CheckResult(name, "warn", f"Saída inesperada: {out.strip()}")

    def _check_memory(self) -> CheckResult:
        name = "Memória"
        code, out, _ = self._ssh("free -m | grep '^Mem:'")
        if code != 0:
            # Tenta /proc/meminfo
            code2, out2, _ = self._ssh("cat /proc/meminfo | grep -E 'MemTotal|MemAvailable'")
            if code2 == 0:
                lines = out2.strip().splitlines()
                vals = {}
                for line in lines:
                    m = re.match(r"(\w+):\s+(\d+)", line)
                    if m:
                        vals[m.group(1)] = int(m.group(2))
                total = vals.get("MemTotal", 1)
                avail = vals.get("MemAvailable", total)
                used_pct = int((1 - avail / total) * 100)
                status = "pass" if used_pct < 85 else "warn" if used_pct < 95 else "fail"
                return CheckResult(name, status, f"Uso de memória: {used_pct}%", {"usage_percent": used_pct})
            return CheckResult(name, "warn", "Não foi possível obter uso de memória")

        parts = out.strip().split()
        if len(parts) >= 3:
            total = int(parts[1])
            used = int(parts[2])
            used_pct = int((used / total) * 100) if total else 0
            status = "pass" if used_pct < 85 else "warn" if used_pct < 95 else "fail"
            return CheckResult(name, status, f"Uso de memória: {used_pct}%", {"usage_percent": used_pct, "total_mb": total, "used_mb": used})
        return CheckResult(name, "warn", f"Saída inesperada: {out.strip()}")

    def run_all(self) -> HealthReport:
        import time
        checks_methods = [
            self._check_container,
            self._check_ports,
            self._check_nginx_root,
            self._check_ma_info,
            self._check_websocket,
            self._check_tailscale,
            self._check_ssl_cert,
            self._check_disk_space,
            self._check_memory,
        ]
        results: list[CheckResult] = []
        for method in checks_methods:
            t0 = time.perf_counter()
            try:
                res = method()
            except Exception as exc:
                res = CheckResult(method.__name__.replace("_check_", ""), "fail", f"Exceção: {exc}")
            res.duration_ms = round((time.perf_counter() - t0) * 1000, 2)
            results.append(res)

        report = HealthReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            host=self.host,
            overall="unknown",
            checks=results,
        )
        report.compute_summary()
        return report


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------
def print_table(report: HealthReport) -> None:
    print(f"\n{Fore.CYAN}{'━' * 80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  TSi-MUSIC Health Check  v2.9.5  |  Host: {report.host}  |  {report.timestamp}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'━' * 80}{Style.RESET_ALL}\n")

    overall_color = Fore.GREEN if report.overall == "healthy" else Fore.YELLOW if report.overall == "degraded" else Fore.RED
    print(f"  Overall: {overall_color}{report.overall.upper()}{Style.RESET_ALL}")
    print(f"  Checks : {Fore.GREEN}{report.summary.get('pass', 0)} pass{Style.RESET_ALL} | "
          f"{Fore.YELLOW}{report.summary.get('warn', 0)} warn{Style.RESET_ALL} | "
          f"{Fore.RED}{report.summary.get('fail', 0)} fail{Style.RESET_ALL}\n")

    print(f"  {'CHECK':<28} {'STATUS':<8} {'MESSAGE':<40} {'MS':>6}")
    print(f"  {'-'*28} {'-'*8} {'-'*40} {'-'*6}")
    for c in report.checks:
        color = Fore.GREEN if c.status == "pass" else Fore.YELLOW if c.status == "warn" else Fore.RED
        print(f"  {c.name:<28} {color}{c.status.upper():<8}{Style.RESET_ALL} {c.message:<40} {c.duration_ms:>6.1f}")
    print("")


def print_json(report: HealthReport) -> None:
    # Converte dataclasses para dict recursivamente
    def serialize(obj: Any) -> Any:
        if isinstance(obj, list):
            return [serialize(i) for i in obj]
        if isinstance(obj, dict):
            return {k: serialize(v) for k, v in obj.items()}
        if hasattr(obj, "__dataclass_fields__"):
            return {k: serialize(v) for k, v in asdict(obj).items()}  # type: ignore[arg-type]
        return obj

    print(json.dumps(serialize(report), indent=2, default=str))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tsimusic-healthcheck",
        description="Health check avançado do TSi-MUSIC no MidiaServer-SaudeClinica",
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host alvo (default: 100.86.64.1)")
    parser.add_argument("--user", default=DEFAULT_SSH_USER, help="Usuário SSH (default: tsi)")
    parser.add_argument("--ssh-key", default=DEFAULT_SSH_KEY, help="Path da chave SSH")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    checker = HealthChecker(args.host, args.user, args.ssh_key)
    report = checker.run_all()

    if args.json:
        print_json(report)
    else:
        print_table(report)

    return 0 if report.overall == "healthy" else 1


if __name__ == "__main__":
    sys.exit(main())
