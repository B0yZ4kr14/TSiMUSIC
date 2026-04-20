#!/usr/bin/env python3
# cspell:disable
# =============================================================================
# TSi-MUSIC — Gerenciamento de Certificados SSL
# Versão: v2.9.5
#
# Verifica, renova e gera certificados SSL para o TSi-MUSIC no
# MidiaServer-SaudeClinica. Suporta certificados Let's Encrypt via
# Tailscale e autoassinados para IP.
#
# Uso:
#   python3 tsimusic-cert-manager.py --check
#   python3 tsimusic-cert-manager.py --renew
#   python3 tsimusic-cert-manager.py --generate-ip
#   python3 tsimusic-cert-manager.py --info
#
# Variáveis de ambiente:
#   CERT_HOST     — IP/hostname do servidor (default: 100.86.64.1)
#   CERT_USER     — Usuário SSH (default: tsi)
#   SSH_KEY       — Path da chave SSH local
#   CERT_DIR      — Diretório remoto dos certs (default: /home/tsi/docker/ma-wiki/certs)
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
DEFAULT_HOST = os.getenv("CERT_HOST", "100.86.64.1")
DEFAULT_USER = os.getenv("CERT_USER", "tsi")
DEFAULT_SSH_KEY = os.getenv("SSH_KEY", str(Path.home() / ".ssh" / "id_ed25519_midiaserver"))
DEFAULT_CERT_DIR = os.getenv("CERT_DIR", "/home/tsi/docker/ma-wiki/certs")
DEFAULT_REMOTE_PATH = "/home/tsi/docker/ma-wiki"

VERSION = "2.9.5"
SCRIPT_NAME = "tsimusic-cert-manager"
WARNING_DAYS = 30

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
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class CertInfo:
    subject: dict[str, str] = field(default_factory=dict)
    issuer: dict[str, str] = field(default_factory=dict)
    not_before: str = ""
    not_after: str = ""
    days_left: int = 0
    serial: str = ""
    san: list[str] = field(default_factory=list)
    is_self_signed: bool = False
    error: str = ""


# ---------------------------------------------------------------------------
# Certificate manager
# ---------------------------------------------------------------------------
class CertManager:
    def __init__(
        self,
        host: str,
        user: str,
        ssh_key: str,
        cert_dir: str,
        remote_path: str,
    ) -> None:
        self.host = host
        self.user = user
        self.ssh_key = Path(ssh_key).expanduser()
        self.cert_dir = cert_dir
        self.remote_path = remote_path

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

    def _get_remote_cert_info(self) -> CertInfo:
        """Obtém informações do certificado no host remoto via OpenSSL."""
        # Tenta ler o certificado diretamente no servidor
        cert_path = f"{self.cert_dir}/cert.pem"
        code, out, err = self._ssh(
            f"openssl x509 -in {cert_path} -noout -text -dates 2>&1 || echo 'CERT_NOT_FOUND'"
        )
        if code != 0 or "CERT_NOT_FOUND" in out or "No such file" in out:
            # Fallback: tenta via tailscale cert info
            code2, out2, _ = self._ssh("tailscale cert 2>&1 | head -n 20 || true")
            if code2 == 0 and out2.strip():
                return CertInfo(error=f"Cert não encontrado em {cert_path}. Tailscale: {out2.strip()[:200]}")
            return CertInfo(error=f"Certificado não encontrado em {cert_path}")

        return self._parse_openssl_text(out)

    @staticmethod
    def _parse_openssl_text(text: str) -> CertInfo:
        info = CertInfo()

        # Subject
        m = re.search(r"Subject:\s*(.+)", text)
        if m:
            info.subject = dict(re.findall(r"(\w+)\s*=\s*([^,]+)", m.group(1)))

        # Issuer
        m = re.search(r"Issuer:\s*(.+)", text)
        if m:
            info.issuer = dict(re.findall(r"(\w+)\s*=\s*([^,]+)", m.group(1)))

        # Dates
        m = re.search(r"notBefore=(.+)", text)
        if m:
            info.not_before = m.group(1).strip()
        m = re.search(r"notAfter=(.+)", text)
        if m:
            info.not_after = m.group(1).strip()

        # Serial
        m = re.search(r"Serial Number:\s*([\da-fA-F:]+)", text)
        if m:
            info.serial = m.group(1).strip()

        # SAN
        san_match = re.search(r"X509v3 Subject Alternative Name:\s*\n\s*(.+)", text)
        if san_match:
            info.san = [s.strip() for s in san_match.group(1).split(",")]

        # Self-signed check
        if info.subject == info.issuer and info.subject:
            info.is_self_signed = True

        # Compute days left
        if info.not_after:
            try:
                expire = ssl.cert_time_to_seconds(info.not_after)
                now = datetime.now(timezone.utc).timestamp()
                info.days_left = int((expire - now) / 86400)
            except Exception:
                pass

        return info

    def _get_cert_via_socket(self, port: int = 8443) -> CertInfo:
        """Obtém certificado conectando via socket SSL."""
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with socket.create_connection((self.host, port), timeout=10) as sock:
                with ctx.wrap_socket(sock, server_hostname=self.host) as ssock:
                    cert = ssock.getpeercert(binary_form=True)
                    if not cert:
                        return CertInfo(error="Nenhum certificado retornado pelo socket")

                    # Parse via OpenSSL localmente
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix=".pem", delete=False) as tmp:
                        tmp.write(cert)
                        tmp_path = tmp.name

                    result = subprocess.run(
                        ["openssl", "x509", "-in", tmp_path, "-noout", "-text", "-dates"],
                        capture_output=True,
                        text=True,
                    )
                    Path(tmp_path).unlink(missing_ok=True)
                    if result.returncode != 0:
                        return CertInfo(error=f"Falha ao parsear cert: {result.stderr.strip()}")
                    return self._parse_openssl_text(result.stdout)
        except Exception as exc:
            return CertInfo(error=str(exc))

    def check(self, remote: bool = True) -> CertInfo:
        log_step("Verificando certificado SSL")

        if remote and self._verify_ssh():
            info = self._get_remote_cert_info()
        else:
            info = self._get_cert_via_socket()

        if info.error:
            log_error(info.error)
            return info

        status = "OK"
        if info.days_left < 0:
            status = "EXPIRADO"
        elif info.days_left < WARNING_DAYS:
            status = "AVISO"

        color = Fore.GREEN if status == "OK" else Fore.YELLOW if status == "AVISO" else Fore.RED
        print(f"\n  Subject : {info.subject}")
        print(f"  Issuer  : {info.issuer}")
        print(f"  SAN     : {', '.join(info.san) or 'N/A'}")
        print(f"  Válido de: {info.not_before}")
        print(f"  Válido até: {info.not_after}")
        print(f"  Dias restantes: {color}{info.days_left}{Style.RESET_ALL}")
        print(f"  Autoassinado: {'Sim' if info.is_self_signed else 'Não'}")
        print(f"  Status  : {color}{status}{Style.RESET_ALL}\n")

        if status == "AVISO":
            log_warn(f"Certificado expira em {info.days_left} dia(s). Considere renovar.")
        elif status == "EXPIRADO":
            log_error("Certificado EXPIRADO! Ação imediata necessária.")
        else:
            log_ok("Certificado válido.")

        return info

    def info(self, remote: bool = True) -> CertInfo:
        log_step("Informações detalhadas do certificado")

        if remote and self._verify_ssh():
            info = self._get_remote_cert_info()
            # Se conseguir, mostra o certificado raw também
            cert_path = f"{self.cert_dir}/cert.pem"
            code, out, _ = self._ssh(f"openssl x509 -in {cert_path} -noout -subject -issuer -dates -serial -ext subjectAltName 2>&1")
            if code == 0:
                print(f"\n{Fore.CYAN}--- OpenSSL output ---{Style.RESET_ALL}")
                print(out)
        else:
            info = self._get_cert_via_socket()
            print(f"\n{Fore.CYAN}--- Socket SSL info ---{Style.RESET_ALL}")
            print(f"  Host: {self.host}")
            print(f"  Port: 8443")

        if info.error:
            log_error(info.error)
            return info

        print(f"\n{Fore.CYAN}--- Parsed ---{Style.RESET_ALL}")
        print(f"  Subject      : {info.subject}")
        print(f"  Issuer       : {info.issuer}")
        print(f"  Serial       : {info.serial}")
        print(f"  SAN          : {info.san}")
        print(f"  Not Before   : {info.not_before}")
        print(f"  Not After    : {info.not_after}")
        print(f"  Days Left    : {info.days_left}")
        print(f"  Self-signed  : {info.is_self_signed}")
        return info

    def renew(self) -> bool:
        log_step("Renovando certificado via Tailscale")

        if not self._verify_ssh():
            log_error(f"Falha na conexão SSH para {self.user}@{self.host}")
            return False

        # Detecta o hostname tailscale
        code, out, _ = self._ssh("tailscale status --json 2>/dev/null | grep -oP '(?<=\"DNSName\":\")[^\"]+' | head -1")
        ts_hostname = out.strip().rstrip(".") if code == 0 else ""

        if not ts_hostname:
            log_warn("Não foi possível detectar hostname Tailscale; tentando gerar para FQDN padrão")
            # Fallback: usa hostname do servidor
            code, out, _ = self._ssh("hostname -f 2>/dev/null || hostname")
            ts_hostname = out.strip()

        log_info(f"Hostname detectado: {ts_hostname}")

        # Executa tailscale cert
        cert_cmd = f"tailscale cert --cert-file {self.cert_dir}/cert.pem --key-file {self.cert_dir}/key.pem {ts_hostname}"
        code, out, err = self._ssh(cert_cmd, timeout=60)
        if code != 0:
            log_error(f"Falha ao renovar certificado: {err.strip() or out.strip()}")
            return False

        log_ok("Certificado renovado com sucesso")
        log_info("Reinicie o container nginx para aplicar:")
        log_info(f"  ssh {self.user}@{self.host} 'cd {self.remote_path} && docker compose restart'")
        return True

    def generate_ip_cert(self) -> bool:
        log_step("Gerando certificado autoassinado para IP")

        if not self._verify_ssh():
            log_error(f"Falha na conexão SSH para {self.user}@{self.host}")
            return False

        # Gera cert autoassinado válido por 365 dias
        key_path = f"{self.cert_dir}/key.pem"
        cert_path = f"{self.cert_dir}/cert.pem"

        gen_cmd = (
            f"openssl req -x509 -nodes -days 365 -newkey rsa:2048 "
            f"-keyout {key_path} -out {cert_path} "
            f"-subj '/CN={self.host}' "
            f"-addext 'subjectAltName=IP:{self.host}' 2>&1"
        )
        code, out, err = self._ssh(gen_cmd, timeout=30)
        if code != 0:
            log_error(f"Falha ao gerar certificado: {err.strip() or out.strip()}")
            return False

        log_ok(f"Certificado autoassinado gerado para IP {self.host}")
        log_info("Reinicie o container nginx para aplicar")
        return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=SCRIPT_NAME,
        description="Gerenciamento de certificados SSL do TSi-MUSIC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s --check
  %(prog)s --check --host 100.86.64.1
  %(prog)s --renew
  %(prog)s --generate-ip
  %(prog)s --info
        """,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Verificar validade do certificado")
    group.add_argument("--renew", action="store_true", help="Renovar certificado via Tailscale")
    group.add_argument("--generate-ip", action="store_true", help="Gerar cert autoassinado para IP")
    group.add_argument("--info", action="store_true", help="Mostrar informações detalhadas")

    parser.add_argument("--host", default=DEFAULT_HOST, help="Host alvo (default: 100.86.64.1)")
    parser.add_argument("--user", default=DEFAULT_USER, help="Usuário SSH")
    parser.add_argument("--ssh-key", default=DEFAULT_SSH_KEY, help="Path da chave SSH")
    parser.add_argument("--cert-dir", default=DEFAULT_CERT_DIR, help="Diretório remoto dos certs")
    parser.add_argument("--remote-path", default=DEFAULT_REMOTE_PATH, help="Path remoto do deploy")
    parser.add_argument("--json", action="store_true", help="Saída em JSON (apenas --check/--info)")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    manager = CertManager(
        host=args.host,
        user=args.user,
        ssh_key=args.ssh_key,
        cert_dir=args.cert_dir,
        remote_path=args.remote_path,
    )

    if args.check:
        info = manager.check()
        if args.json:
            print(json.dumps(asdict(info), indent=2, default=str))
        return 0 if not info.error else 1

    if args.info:
        info = manager.info()
        if args.json:
            print(json.dumps(asdict(info), indent=2, default=str))
        return 0 if not info.error else 1

    if args.renew:
        ok = manager.renew()
        return 0 if ok else 1

    if args.generate_ip:
        ok = manager.generate_ip_cert()
        return 0 if ok else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
