#!/usr/bin/env python3
"""
TSi MUSIC Premium Patch Engine
==============================
Idempotent patch system for rebranding Music Assistant frontend to TSi MUSIC.
Supports: apply, rollback, validate, dry-run.

Usage:
    python patch-engine.py --apply [--dry-run]
    python patch-engine.py --rollback
    python patch-engine.py --validate
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ── Paths ──
PATCH_DIR = Path(__file__).parent.resolve()
CONFIG_PATH = PATCH_DIR / "patch-config.json"
BACKUP_DIR = PATCH_DIR / "backup"
TARGET_REPO = None  # set from CLI

# ── Colors for terminal output ──
R = "\033[0;31m"
G = "\033[0;32m"
Y = "\033[1;33m"
B = "\033[0;34m"
C = "\033[0;36m"
NC = "\033[0m"


def log_info(msg: str):
    print(f"{B}[INFO]{NC} {msg}")


def log_ok(msg: str):
    print(f"{G}[OK]{NC} {msg}")


def log_warn(msg: str):
    print(f"{Y}[WARN]{NC} {msg}")


def log_err(msg: str):
    print(f"{R}[ERR]{NC} {msg}")


# ── Helpers ──
def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def backup_path(rel_path: str) -> Path:
    return BACKUP_DIR / rel_path.replace("/", "--")


def save_backup(rel_path: str, src: Path):
    """Copy file to backup dir preserving relative structure as flat filenames."""
    if not src.exists():
        return
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    dst = backup_path(rel_path)
    shutil.copy2(src, dst)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str):
    path.write_text(content, encoding="utf-8")


def count_occurrences(text: str, pattern: str) -> int:
    return text.count(pattern)


# ── Phase implementations ──
class PatchEngine:
    def __init__(self, target: Path, config: dict, dry_run: bool = False):
        self.target = target
        self.config = config
        self.dry_run = dry_run
        self.skipped: list[str] = []
        self.applied: list[str] = []
        self.errors: list[str] = []

    def _resolve(self, rel: str) -> Path:
        return self.target / rel

    def _is_protected(self, rel_path: str) -> bool:
        for pat in self.config.get("protected_patterns", []):
            if pat in rel_path:
                return True
        return False

    # ── Phase 1: Assets ──
    def apply_assets(self):
        log_info("Phase: Assets")
        for item in self.config.get("assets", {}).get("copy", []):
            src = PATCH_DIR / item["src"]
            dst_rel = item["dst"]
            dst = self._resolve(dst_rel)

            if not src.exists():
                log_warn(f"Asset not found: {src}")
                self.skipped.append(dst_rel)
                continue

            if not self.dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                save_backup(dst_rel, dst)
                shutil.copy2(src, dst)

            self.applied.append(f"asset: {dst_rel}")
            log_ok(f"Asset -> {dst_rel}")

    # ── Phase 2: Color tokens ──
    def apply_color_tokens(self):
        log_info("Phase: Color Tokens")
        for rel_path, replacements in self.config.get("color_tokens", {}).items():
            path = self._resolve(rel_path)
            if not path.exists():
                log_warn(f"File not found: {rel_path}")
                self.skipped.append(rel_path)
                continue

            content = read_text(path)
            modified = False

            for rep in replacements:
                old, new = rep["old"], rep["new"]
                limit = rep.get("limit", 0)
                occ = count_occurrences(content, old)

                if occ == 0:
                    # Maybe already patched
                    if count_occurrences(content, new) > 0:
                        continue
                    else:
                        log_warn(f"Pattern not found in {rel_path}: {old[:40]}...")
                        continue

                if limit > 0 and occ != limit:
                    log_warn(f"Expected {limit} occurrences, found {occ} in {rel_path}")
                    self.skipped.append(f"{rel_path}: {old[:40]}")
                    continue

                content = content.replace(old, new)
                modified = True
                self.applied.append(f"color: {rel_path} -> {old[:30]}...")

            if modified and not self.dry_run:
                save_backup(rel_path, path)
                write_text(path, content)

            if modified:
                log_ok(f"Color tokens -> {rel_path}")

    # ── Phase 3: Text replacements ──
    def apply_text_replacements(self):
        log_info("Phase: Text Replacements")
        for rel_path, replacements in self.config.get("text_replacements", {}).items():
            if self._is_protected(rel_path):
                log_warn(f"Skipping protected file: {rel_path}")
                continue

            path = self._resolve(rel_path)
            if not path.exists():
                log_warn(f"File not found: {rel_path}")
                self.skipped.append(rel_path)
                continue

            content = read_text(path)
            modified = False

            for rep in replacements:
                old, new = rep["old"], rep["new"]
                skip_if = rep.get("skip_if_contains", [])

                # Skip if any protected substring is present
                if any(s in content for s in skip_if):
                    continue

                occ = count_occurrences(content, old)
                if occ == 0:
                    if count_occurrences(content, new) > 0:
                        continue  # Already patched
                    log_warn(f"Pattern not found in {rel_path}: {old[:50]}...")
                    continue

                content = content.replace(old, new)
                modified = True
                self.applied.append(f"text: {rel_path} -> {old[:40]}...")

            if modified and not self.dry_run:
                save_backup(rel_path, path)
                write_text(path, content)

            if modified:
                log_ok(f"Text -> {rel_path}")

    # ── Phase 4: i18n replacements ──
    def apply_i18n(self):
        log_info("Phase: i18n Replacements")
        i18n = self.config.get("i18n_replacements", {})
        pattern = i18n.get("pattern", "Music Assistant")
        replacement = i18n.get("replacement", "TSi MUSIC")
        files = i18n.get("files", [])

        for rel_path in files:
            path = self._resolve(rel_path)
            if not path.exists():
                log_warn(f"Translation file not found: {rel_path}")
                self.skipped.append(rel_path)
                continue

            content = read_text(path)
            occ = count_occurrences(content, pattern)

            if occ == 0:
                if count_occurrences(content, replacement) > 0:
                    continue
                log_warn(f"No occurrences in {rel_path}")
                continue

            # Only replace inside quoted string values, not keys
            # Simple approach: replace all occurrences in values only
            lines = content.splitlines()
            new_lines = []
            for line in lines:
                if pattern in line and "\"" in line:
                    # Heuristic: only replace after the first colon in JSON
                    if ":" in line:
                        parts = line.split(":", 1)
                        key_part = parts[0]
                        val_part = parts[1]
                        val_part = val_part.replace(pattern, replacement)
                        line = key_part + ":" + val_part
                new_lines.append(line)

            new_content = "\n".join(new_lines) + "\n"
            if new_content != content:
                if not self.dry_run:
                    save_backup(rel_path, path)
                    write_text(path, new_content)
                self.applied.append(f"i18n: {rel_path} ({occ} occurrences)")
                log_ok(f"i18n -> {rel_path} ({occ} replacements)")

    # ── Phase 5: Hardcoded colors ──
    def apply_hardcoded_colors(self):
        log_info("Phase: Hardcoded Colors")
        for rel_path, replacements in self.config.get("hardcoded_colors", {}).items():
            path = self._resolve(rel_path)
            if not path.exists():
                log_warn(f"File not found: {rel_path}")
                self.skipped.append(rel_path)
                continue

            content = read_text(path)
            modified = False

            for rep in replacements:
                old, new = rep["old"], rep["new"]
                limit = rep.get("limit", 0)
                context = rep.get("context", "")

                occ = count_occurrences(content, old)
                if occ == 0:
                    if count_occurrences(content, new) > 0:
                        continue
                    log_warn(f"Color pattern not found in {rel_path}: {old}")
                    continue

                if limit > 0 and occ != limit:
                    log_warn(f"Expected {limit} color occurrences, found {occ} in {rel_path}")
                    continue

                # If context specified, only replace lines containing context
                if context:
                    lines = content.splitlines()
                    new_lines = []
                    replaced_in_file = 0
                    for line in lines:
                        if context in line and old in line and (limit == 0 or replaced_in_file < limit):
                            line = line.replace(old, new)
                            replaced_in_file += 1
                        new_lines.append(line)
                    content = "\n".join(new_lines) + "\n"
                else:
                    content = content.replace(old, new)

                modified = True
                self.applied.append(f"color-fix: {rel_path} -> {old}")

            if modified and not self.dry_run:
                save_backup(rel_path, path)
                write_text(path, content)

            if modified:
                log_ok(f"Color fix -> {rel_path}")

    # ── Phase 6: CSS inject ──
    def apply_css_inject(self):
        log_info("Phase: CSS Premium Inject")
        css_cfg = self.config.get("css_inject", {})
        src = PATCH_DIR / css_cfg["file"]
        dst_rel = css_cfg["target"]
        dst = self._resolve(dst_rel)
        import_stmt = css_cfg["import_statement"]
        import_target_rel = css_cfg["import_target"]
        import_target = self._resolve(import_target_rel)

        # Copy CSS file
        if src.exists():
            if not self.dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                save_backup(dst_rel, dst)
                shutil.copy2(src, dst)
            self.applied.append(f"css: {dst_rel}")
            log_ok(f"CSS -> {dst_rel}")
        else:
            log_warn(f"CSS source not found: {src}")
            self.skipped.append(str(src))

        # Add import to main.ts
        if import_target.exists():
            content = read_text(import_target)
            if import_stmt in content:
                log_info("CSS import already present")
            else:
                if not self.dry_run:
                    save_backup(import_target_rel, import_target)
                    # Add import after the last existing import
                    lines = content.splitlines()
                    last_import_idx = -1
                    for i, line in enumerate(lines):
                        if line.strip().startswith("import "):
                            last_import_idx = i
                    if last_import_idx >= 0:
                        lines.insert(last_import_idx + 1, import_stmt)
                    else:
                        lines.insert(0, import_stmt)
                    write_text(import_target, "\n".join(lines) + "\n")
                self.applied.append(f"import: {import_target_rel}")
                log_ok(f"Import added -> {import_target_rel}")

    # ── Phase 7: Meta tags ──
    def apply_meta_tags(self):
        log_info("Phase: Meta Tags")
        meta_cfg = self.config.get("meta_tags", {})
        target_rel = meta_cfg["target"]
        target = self._resolve(target_rel)

        if not target.exists():
            log_warn(f"Meta target not found: {target_rel}")
            self.skipped.append(target_rel)
            return

        content = read_text(target)
        insert_after = meta_cfg["insert_after"]
        tags = meta_cfg["tags"]

        modified = False
        for tag in tags:
            # Extract tag name for idempotency check
            tag_key = tag.split(" ")[1].split("=")[0] if "=" in tag else tag
            if tag_key in content:
                continue  # Already present

            if insert_after in content:
                content = content.replace(insert_after, insert_after + "\n    " + tag, 1)
                modified = True
                self.applied.append(f"meta: {tag_key}")
            else:
                log_warn(f"Insert anchor not found in {target_rel}")
                self.skipped.append(f"meta: {tag_key}")

        if modified and not self.dry_run:
            save_backup(target_rel, target)
            write_text(target, content)

        if modified:
            log_ok(f"Meta tags -> {target_rel}")

    # ── Phase 8: Manifest enhancements ──
    def apply_manifest(self):
        log_info("Phase: Manifest Enhancements")
        manifest_cfg = self.config.get("manifest_enhancements", {})
        target_rel = manifest_cfg["target"]
        target = self._resolve(target_rel)

        if not target.exists():
            log_warn(f"Manifest target not found: {target_rel}")
            self.skipped.append(target_rel)
            return

        content = read_text(target)
        modified = False

        for addition in manifest_cfg.get("additions", []):
            after = addition["after"]
            line = addition["line"]
            if line in content:
                continue  # Already present
            if after in content:
                content = content.replace(after, after + "\n" + line, 1)
                modified = True
                self.applied.append(f"manifest: {line.strip()}")
            else:
                log_warn(f"Manifest anchor not found: {after}")
                self.skipped.append(f"manifest: {line.strip()}")

        if modified and not self.dry_run:
            save_backup(target_rel, target)
            write_text(target, content)

        if modified:
            log_ok(f"Manifest -> {target_rel}")

    # ── Rollback ──
    def rollback(self):
        log_info("Rolling back patch...")
        if not BACKUP_DIR.exists():
            log_warn("No backup directory found")
            return

        restored = 0
        for backup_file in BACKUP_DIR.iterdir():
            # Convert flat backup name back to relative path
            rel_path = backup_file.name.replace("--", "/")
            target = self._resolve(rel_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_file, target)
            restored += 1
            log_ok(f"Restored: {rel_path}")

        # Remove CSS import from main.ts
        import_target = self._resolve("src/main.ts")
        if import_target.exists():
            content = read_text(import_target)
            css_cfg = self.config.get("css_inject", {})
            import_stmt = css_cfg.get("import_statement", "")
            if import_stmt and import_stmt in content:
                content = content.replace(import_stmt + "\n", "")
                content = content.replace("\n" + import_stmt, "")
                write_text(import_target, content)
                log_ok("Removed CSS import from main.ts")

        log_info(f"Rollback complete. {restored} files restored.")

    # ── Validate ──
    def validate(self):
        log_info("Validating patch...")
        issues = []

        # Check for remaining visible "Music Assistant" occurrences
        result = subprocess.run(
            ["grep", "-rn", "Music Assistant", "src/", "index.html", "vite.config.ts"],
            cwd=self.target,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            # Filter out comments and protected files
            for line in lines:
                if any(p in line for p in self.config.get("protected_patterns", [])):
                    continue
                if "//" in line or "/*" in line:
                    continue
                issues.append(line)

        if issues:
            log_warn(f"Found {len(issues)} potential remaining occurrences:")
            for issue in issues[:10]:
                print(f"  {Y}->{NC} {issue}")
        else:
            log_ok("No visible 'Music Assistant' occurrences found")

        # Check build
        log_info("Running build...")
        build = subprocess.run(
            ["npm", "run", "build"],
            cwd=self.target,
            capture_output=True,
            text=True,
        )
        if build.returncode == 0:
            log_ok("Build successful")
        else:
            log_err("Build failed!")
            print(build.stderr[:500])
            issues.append("build failed")

        return len(issues) == 0

    # ── Run all phases ──
    def run_apply(self):
        log_info(f"Target: {self.target}")
        log_info(f"Dry-run: {self.dry_run}")

        self.apply_assets()
        self.apply_color_tokens()
        self.apply_text_replacements()
        self.apply_i18n()
        self.apply_hardcoded_colors()
        self.apply_css_inject()
        self.apply_meta_tags()
        self.apply_manifest()

        print()
        log_ok(f"Applied: {len(self.applied)} changes")
        if self.skipped:
            log_warn(f"Skipped: {len(self.skipped)} items")
            for s in self.skipped:
                print(f"  {Y}->{NC} {s}")
        if self.errors:
            log_err(f"Errors: {len(self.errors)}")

        # Save report
        report = {
            "timestamp": datetime.now().isoformat(),
            "target": str(self.target),
            "dry_run": self.dry_run,
            "applied": self.applied,
            "skipped": self.skipped,
            "errors": self.errors,
        }
        report_path = PATCH_DIR / f"report-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        log_info(f"Report saved: {report_path}")


def main():
    parser = argparse.ArgumentParser(description="TSi MUSIC Premium Patch Engine")
    parser.add_argument("--apply", action="store_true", help="Apply the patch")
    parser.add_argument("--rollback", action="store_true", help="Rollback to pre-patch state")
    parser.add_argument("--validate", action="store_true", help="Validate current state")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without applying")
    parser.add_argument("--target", type=str, default="~/Projects/music-assistant/frontend",
                        help="Path to the Music Assistant frontend repo")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    if not target.exists():
        log_err(f"Target directory not found: {target}")
        sys.exit(1)

    config = load_config()
    engine = PatchEngine(target, config, dry_run=args.dry_run)

    if args.rollback:
        engine.rollback()
    elif args.validate:
        ok = engine.validate()
        sys.exit(0 if ok else 1)
    elif args.apply or args.dry_run:
        engine.run_apply()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
