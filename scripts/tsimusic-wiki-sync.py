#!/usr/bin/env python3
# cspell:disable
# =============================================================================
# TSi-MUSIC — Wiki Sync (Obsidian ↔ Repo)
# Versão: v2.9.5
#
# Sincroniza a wiki do TSi-MUSIC entre o Obsidian Vault e o repositório.
# Converte links Obsidian [[Note]] para links MkDocs [Note](Note.md).
#
# Uso:
#   python3 tsimusic-wiki-sync.py --obsidian-to-repo
#   python3 tsimusic-wiki-sync.py --repo-to-obsidian
#   python3 tsimusic-wiki-sync.py --obsidian-to-repo --apply
#
# Por padrão opera em modo dry-run. Use --apply para executar.
# =============================================================================

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

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
DEFAULT_OBSIDIAN_VAULT = Path.home() / "ObsidianAI-Orchestrator" / "vault" / "TSi-MUSIC"
DEFAULT_REPO_WIKI = Path(__file__).parent.parent / "wiki" / "docs"

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
# Link converter
# ---------------------------------------------------------------------------
class LinkConverter:
    """Converte links Obsidian para MkDocs e vice-versa."""

    # [[Note]] ou [[Note|Texto]]
    OBSIDIAN_LINK_RE = re.compile(r"\[\[(?P<target>[^|\]]+)(?:\|(?P<text>[^\]]+))?\]\]")
    # [Texto](Note.md)
    MKDOCS_LINK_RE = re.compile(r"\[(?P<text>[^\]]+)\]\((?P<target>[^)]+\.md)\)")

    @classmethod
    def obsidian_to_mkdocs(cls, content: str) -> str:
        def repl(match: re.Match[str]) -> str:
            target = match.group("target").strip()
            text = match.group("text")
            if text:
                return f"[{text}]({target}.md)"
            return f"[{target}]({target}.md)"
        return cls.OBSIDIAN_LINK_RE.sub(repl, content)

    @classmethod
    def mkdocs_to_obsidian(cls, content: str) -> str:
        def repl(match: re.Match[str]) -> str:
            text = match.group("text").strip()
            target = match.group("target").strip()
            # Remove .md do target
            target_clean = re.sub(r"\.md$", "", target)
            if text == target_clean:
                return f"[[{target_clean}]]"
            return f"[[{target_clean}|{text}]]"
        return cls.MKDOCS_LINK_RE.sub(repl, content)


# ---------------------------------------------------------------------------
# Sync engine
# ---------------------------------------------------------------------------
@dataclass
class SyncPlan:
    copy_ops: list[tuple[Path, Path]] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class WikiSyncEngine:
    def __init__(
        self,
        obsidian_dir: Path,
        repo_dir: Path,
        apply: bool = False,
    ) -> None:
        self.obsidian_dir = obsidian_dir
        self.repo_dir = repo_dir
        self.apply = apply
        self.converter = LinkConverter()

    def _collect_markdown_files(self, directory: Path) -> Iterable[Path]:
        if not directory.exists():
            return []
        return sorted(directory.rglob("*.md"))

    def _relative_path(self, file: Path, base: Path) -> Path:
        return file.relative_to(base)

    def _process_content(
        self,
        content: str,
        direction: str,  # "obsidian_to_mkdocs" | "repo_to_obsidian"
    ) -> str:
        if direction == "obsidian_to_mkdocs":
            return self.converter.obsidian_to_mkdocs(content)
        return self.converter.mkdocs_to_obsidian(content)

    def _copy_file(self, src: Path, dst: Path, direction: str) -> None:
        dst.parent.mkdir(parents=True, exist_ok=True)
        content = src.read_text(encoding="utf-8")
        processed = self._process_content(content, direction)
        dst.write_text(processed, encoding="utf-8")

    def sync_obsidian_to_repo(self) -> SyncPlan:
        log_step("Obsidian Vault → Repositório")
        plan = SyncPlan()

        if not self.obsidian_dir.exists():
            log_error(f"Obsidian Vault não encontrado: {self.obsidian_dir}")
            plan.errors.append(f"Missing: {self.obsidian_dir}")
            return plan

        files = list(self._collect_markdown_files(self.obsidian_dir))
        log_info(f"Arquivos encontrados no Obsidian: {len(files)}")

        for src in files:
            rel = self._relative_path(src, self.obsidian_dir)
            dst = self.repo_dir / rel
            plan.copy_ops.append((src, dst))
            if self.apply:
                try:
                    self._copy_file(src, dst, "obsidian_to_mkdocs")
                except Exception as exc:
                    log_error(f"Falha copiando {rel}: {exc}")
                    plan.errors.append(str(rel))
                else:
                    log_ok(f"Copiado: {rel}")
            else:
                log_info(f"[DRY-RUN] Copiar: {rel} → {dst}")

        return plan

    def sync_repo_to_obsidian(self) -> SyncPlan:
        log_step("Repositório → Obsidian Vault")
        plan = SyncPlan()

        if not self.repo_dir.exists():
            log_error(f"Diretório wiki/docs não encontrado: {self.repo_dir}")
            plan.errors.append(f"Missing: {self.repo_dir}")
            return plan

        files = list(self._collect_markdown_files(self.repo_dir))
        log_info(f"Arquivos encontrados no repo: {len(files)}")

        for src in files:
            rel = self._relative_path(src, self.repo_dir)
            dst = self.obsidian_dir / rel
            plan.copy_ops.append((src, dst))
            if self.apply:
                try:
                    self._copy_file(src, dst, "repo_to_obsidian")
                except Exception as exc:
                    log_error(f"Falha copiando {rel}: {exc}")
                    plan.errors.append(str(rel))
                else:
                    log_ok(f"Copiado: {rel}")
            else:
                log_info(f"[DRY-RUN] Copiar: {rel} → {dst}")

        return plan

    def summary(self, plan: SyncPlan) -> None:
        print(f"\n{Fore.CYAN}{'━' * 60}{Style.RESET_ALL}")
        print(f"  Operações planejadas: {len(plan.copy_ops)}")
        print(f"  Erros: {len(plan.errors)}")
        if not self.apply:
            print(f"\n  {Fore.YELLOW}Modo dry-run — nenhuma alteração foi feita.{Style.RESET_ALL}")
            print(f"  Adicione --apply para executar.")
        print(f"{Fore.CYAN}{'━' * 60}{Style.RESET_ALL}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tsimusic-wiki-sync",
        description="Sincroniza wiki TSi-MUSIC entre Obsidian Vault e repositório",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s --obsidian-to-repo           # Dry-run: Obsidian → repo
  %(prog)s --obsidian-to-repo --apply   # Executa: Obsidian → repo
  %(prog)s --repo-to-obsidian --apply   # Executa: repo → Obsidian
        """,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--obsidian-to-repo",
        action="store_true",
        help="Copia Obsidian Vault → repo/wiki/docs",
    )
    group.add_argument(
        "--repo-to-obsidian",
        action="store_true",
        help="Copia repo/wiki/docs → Obsidian Vault",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica as alterações (padrão: dry-run)",
    )
    parser.add_argument(
        "--obsidian-dir",
        default=str(DEFAULT_OBSIDIAN_VAULT),
        help="Path do Obsidian Vault TSi-MUSIC",
    )
    parser.add_argument(
        "--repo-dir",
        default=str(DEFAULT_REPO_WIKI),
        help="Path do diretório wiki/docs no repo",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    engine = WikiSyncEngine(
        obsidian_dir=Path(args.obsidian_dir).expanduser(),
        repo_dir=Path(args.repo_dir).expanduser(),
        apply=args.apply,
    )

    if args.obsidian_to_repo:
        plan = engine.sync_obsidian_to_repo()
    else:
        plan = engine.sync_repo_to_obsidian()

    engine.summary(plan)
    return 0 if not plan.errors else 1


if __name__ == "__main__":
    sys.exit(main())
