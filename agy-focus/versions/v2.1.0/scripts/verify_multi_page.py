#!/usr/bin/env python3
"""Check same-origin HTML routes and render every route at narrow and wide widths."""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit


IGNORED_PARTS = {".git", "node_modules", "dist", "build", ".next", "coverage"}
HREF_RE = re.compile(r"\b(?:href|action)\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)


def routes(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.html") if not set(path.relative_to(root).parts) & IGNORED_PARTS)


def route_target(root: Path, source: Path, href: str) -> Path | None:
    value = html.unescape(href.strip())
    if not value or value.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        return None
    raw = parsed.path or source.name
    target = (source.parent / raw).resolve() if not raw.startswith("/") else (root / raw.lstrip("/")).resolve()
    if target.is_dir():
        target /= "index.html"
    if target.suffix == "" and (target.with_suffix(".html")).is_file():
        target = target.with_suffix(".html")
    return target


def static_checks(root: Path, html_paths: list[Path]) -> tuple[list[str], dict[str, bool]]:
    failures: list[str] = []
    aggregate = "\n".join(path.read_text(encoding="utf-8") for path in html_paths)
    css_paths = sorted(root.rglob("*.css"))
    aggregate += "\n" + "\n".join(path.read_text(encoding="utf-8") for path in css_paths if not set(path.relative_to(root).parts) & IGNORED_PARTS)
    for path in html_paths:
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for marker in ("<title", "<main", "<h1"):
            if marker not in lowered:
                failures.append(f"{path.relative_to(root)}:missing:{marker}")
        if not re.search(r"name\s*=\s*['\"]viewport['\"]", text, re.IGNORECASE):
            failures.append(f"{path.relative_to(root)}:missing:viewport")
    contracts = {
        "reducedMotion": bool(re.search(r"prefers-reduced-motion", aggregate, re.IGNORECASE)),
        "visibleFocus": bool(re.search(r":focus-visible|:focus\b|outline\s*:\s*[^n]|focus-ring", aggregate, re.IGNORECASE)),
        "viewTransition": bool(re.search(r"@view-transition|view-transition-name", aggregate, re.IGNORECASE)),
    }
    for name in ("reducedMotion", "visibleFocus"):
        if not contracts[name]:
            failures.append(f"contract:missing:{name}")
    return failures, contracts


def render(root: Path, route: Path, output: Path, chrome: str | None) -> dict:
    verifier = Path(__file__).with_name("verify_ui_render.py")
    route_output = output / route.relative_to(root).with_suffix("")
    command = [sys.executable, str(verifier), str(route), "--output-dir", str(route_output)]
    if chrome:
        command.extend(["--chrome", chrome])
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {"ok": False, "error": result.stderr.strip() or result.stdout.strip() or "invalid verifier output"}
    return {"route": str(route.relative_to(root)), "ok": result.returncode == 0 and payload.get("ok") is True, "result": payload}


def verify(root: Path, output: Path, chrome: str | None) -> dict:
    html_paths = routes(root)
    failures, contracts = static_checks(root, html_paths) if html_paths else (["routes:missing"], {})
    link_errors: list[str] = []
    known = set(html_paths)
    for source in html_paths:
        text = source.read_text(encoding="utf-8")
        for href in HREF_RE.findall(text):
            target = route_target(root, source, href)
            if target and target.suffix.lower() == ".html" and target not in known:
                link_errors.append(f"{source.relative_to(root)}->{href}")
    renders = [render(root, route, output, chrome) for route in html_paths] if not failures and not link_errors else []
    ok = len(html_paths) >= 2 and not failures and not link_errors and bool(renders) and all(item["ok"] for item in renders)
    return {"ok": ok, "routes": [str(path.relative_to(root)) for path in html_paths], "linkErrors": link_errors, "contracts": contracts, "renderResults": renders, "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--output-dir", default="ui-evidence")
    parser.add_argument("--chrome")
    args = parser.parse_args()
    try:
        result = verify(Path(args.root).expanduser().resolve(), Path(args.output_dir).expanduser().resolve(), args.chrome)
    except (OSError, UnicodeDecodeError, subprocess.SubprocessError) as error:
        result = {"ok": False, "error": str(error)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
