#!/usr/bin/env python3
"""Synchronize version from the single source of truth (VERSION) across all components."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def sync_version() -> str:
    repo_root = Path(__file__).resolve().parents[1]
    version_file = repo_root / "VERSION"
    if not version_file.is_file():
        raise FileNotFoundError(f"Missing root VERSION file at {version_file}")

    version = version_file.read_text(encoding="utf-8").strip()
    if not version:
        raise ValueError("VERSION file cannot be empty")

    version_tag = f"v{version}"
    versions_dir = repo_root / "agy-focus" / "versions"
    target_version_dir = versions_dir / version_tag

    # If target version dir doesn't exist, duplicate the active current version
    current_link = repo_root / "agy-focus" / "current"
    if not target_version_dir.is_dir():
        if current_link.exists():
            active_src = current_link.resolve()
            shutil.copytree(active_src, target_version_dir)
        else:
            raise FileNotFoundError(f"Cannot initialize {target_version_dir}")

    # 1. Update VERSION file in target version directory
    (target_version_dir / "VERSION").write_text(version, encoding="utf-8")

    # 2. Update MANIFEST.json in target version directory
    manifest_path = target_version_dir / "MANIFEST.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["version"] = version
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # 3. Assemble GEMINI.md for the new version
    assemble_script = target_version_dir / "scripts" / "assemble_gemini.py"
    if assemble_script.is_file():
        subprocess.run([sys.executable, str(assemble_script)], check=True)

    # 4. Update agy-focus/current symlink
    if current_link.is_symlink() or current_link.exists():
        current_link.unlink()
    current_link.symlink_to(f"versions/{version_tag}")

    # 5. Prune all legacy version directories dynamically
    for item in versions_dir.iterdir():
        if item.is_dir() and item.name != version_tag:
            shutil.rmtree(item)

    print(f"Synchronized GeminiToGenius profile to single-source version: {version_tag}")
    return version


if __name__ == "__main__":
    sync_version()
