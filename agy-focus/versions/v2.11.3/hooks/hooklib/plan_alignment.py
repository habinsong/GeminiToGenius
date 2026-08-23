from __future__ import annotations

import re
from pathlib import Path

from .payloads import latest_user_prompt, written_paths
from .planning import multi_page_required, workspace_plan_root
from .ui_quality import UI_SUFFIXES, is_strict_gtg, is_ui_task


ROUTE_RE = re.compile(r"^\s*(?:[-*]\s*)?(?:route|page|경로|페이지)\s*[:：]\s*(\S+)", re.IGNORECASE | re.MULTILINE)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _relative_mentions(text: str, root: Path, path: Path) -> bool:
    relative = path.resolve().relative_to(root.resolve()).as_posix()
    return relative in text or path.name in text


def plan_alignment_status(payload: dict) -> tuple[bool, str]:
    if not is_strict_gtg(payload) or not is_ui_task(payload):
        return True, ""
    root = workspace_plan_root(payload)
    if not root:
        return True, ""
    design = _read(root / "docs/plans/design-plan.md")
    implementation = _read(root / "docs/plans/implementation-plan.md")
    routes = [match.group(1).strip("`.,;:)") for match in ROUTE_RE.finditer(design)]
    changed_ui = sorted(
        path for path in written_paths(payload)
        if path.suffix.lower() in UI_SUFFIXES and "docs" not in path.parts[-3:]
    )
    missing_files = [path for path in changed_ui if not _relative_mentions(implementation, root, path)]
    if missing_files:
        names = ", ".join(str(path.relative_to(root)) for path in missing_files[:3])
        return False, f"구현 계획의 변경 파일 목록과 실제 UI 쓰기가 어긋납니다: {names}."
    if not multi_page_required(latest_user_prompt(payload)):
        return True, ""
    if len(routes) < 2:
        return False, "다중 페이지 계획에 Route가 두 개 이상 없습니다."
    source_text = "\n".join(_read(path) for path in changed_ui if path.is_file())
    missing_routes: list[str] = []
    for route in routes:
        route_path = route.split("?", 1)[0].split("#", 1)[0].lstrip("/") or "index.html"
        candidate = (root / route_path).resolve()
        if candidate.is_dir():
            candidate = candidate / "index.html"
        if not candidate.is_file() and route.casefold() not in source_text.casefold():
            missing_routes.append(route)
    if missing_routes:
        return False, "계획에만 있고 구현에서 확인되지 않는 Route가 있습니다: " + ", ".join(missing_routes[:3]) + "."
    return True, ""
