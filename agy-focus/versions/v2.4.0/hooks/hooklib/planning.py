from __future__ import annotations

import re
from pathlib import Path

from .config import DESIGN_TRIGGER_RE, MULTI_PAGE_TRIGGER_RE, PLACEHOLDER_EVIDENCE_RE, STATIC_PAGE_RE
from .payloads import command_line, latest_user_prompt, tool_name, workspace_roots, write_target_path
from .ui_quality import UI_SUFFIXES, is_strict_gtg, is_ui_task


PLAN_RELATIVE_PATHS = (
    Path("docs/plans/design-plan.md"),
    Path("docs/plans/implementation-plan.md"),
    Path("docs/plans/verification-plan.md"),
)
MIN_PLAN_CHARACTERS = 360


def is_plan_path(path: Path | None) -> bool:
    if not path or path.suffix.lower() != ".md":
        return False
    parts = [part.lower() for part in path.parts]
    return "plans" in parts and "docs" in parts and parts.index("plans") > parts.index("docs")


def multi_page_required(prompt: str) -> bool:
    if MULTI_PAGE_TRIGGER_RE.search(prompt):
        return True
    return bool(STATIC_PAGE_RE.search(prompt) and not re.search(r"\b(?:landing\s*page|single\s*page)\b|단일\s*페이지", prompt, re.IGNORECASE))


def ui_source_write(payload: dict) -> bool:
    target = write_target_path(payload)
    if target:
        return target.suffix.lower() in UI_SUFFIXES
    if tool_name(payload).lower() == "run_command":
        line = command_line(payload)
        return not bool(re.search(r"docs/plans/[^\s'\"]+\.md", line, re.IGNORECASE))
    return False


def planning_required(payload: dict) -> bool:
    prompt = latest_user_prompt(payload)
    return bool(
        workspace_roots(payload)
        and is_strict_gtg(payload)
        and (is_ui_task(payload) or DESIGN_TRIGGER_RE.search(prompt))
        and ui_source_write(payload)
    )


def workspace_plan_root(payload: dict) -> Path | None:
    target = write_target_path(payload)
    roots = workspace_roots(payload)
    if target:
        for root in roots:
            try:
                target.relative_to(root)
            except ValueError:
                continue
            return root
    for root in roots:
        if (root / "docs" / "plans").is_dir():
            return root
    return roots[0] if roots else None


def plan_paths(root: Path) -> tuple[Path, ...]:
    return tuple(root / relative for relative in PLAN_RELATIVE_PATHS)


def _contains(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE | re.MULTILINE) for pattern in patterns)


PLAN_SECTION_PATTERNS: dict[str, tuple[tuple[str, ...], ...]] = {
    "design-plan.md": (
        (r"goal|목표", r"user|사용자", r"task|행동|작업"),
        (r"content hierarchy|정보 위계|콘텐츠 위계|information architecture|구조",),
        (r"route|page|경로|페이지",),
        (r"loading|empty|error|success|disabled|selected|상태",),
        (r"responsive|mobile|320|반응형|모바일",),
        (r"visual direction|시각 방향|visual language|시각 언어",),
        (r"rationale|근거|이유|판단",),
        (r"alternative|대안|tradeoff|절충",),
        (r"motion|animation|애니메이션|움직임",),
        (r"purpose|목적|이유",),
        (r"duration|easing|ms|시간|속도",),
        (r"reduced motion|prefers-reduced-motion|감속",),
        (r"accessib|접근성|focus|키보드",),
        (r"evidence|근거|source|출처|https?://",),
    ),
    "implementation-plan.md": (
        (r"file|파일|변경 범위|scope",),
        (r"responsib|책임|boundary|경계|god object",),
        (r"state|data flow|상태|데이터 흐름",),
        (r"route|page|경로|페이지",),
        (r"dependency|의존|interface|계약",),
        (r"step|순서|단계|command|명령",),
        (r"rollback|복구|risk|위험",),
    ),
    "verification-plan.md": (
        (r"command|명령|검증 절차|check",),
        (r"320|mobile|좁은|모바일",),
        (r"768|medium|tablet|중간",),
        (r"1280|desktop|wide|넓은|데스크톱",),
        (r"keyboard|focus|키보드|포커스",),
        (r"reduced motion|prefers-reduced-motion|감속",),
        (r"overflow|잘림|스크롤",),
        (r"state transition|상태 전환|상태 변화",),
        (r"performance|inp|cls|성능",),
        (r"measure|측정|계측",),
        (r"accessib|aria|screen reader|접근성",),
        (r"target|24|조작",),
        (r"evidence|screenshot|스크린샷|증거",),
        (r"pass|fail|통과|실패|expected|기대",),
    ),
}


def plan_status(root: Path | None, prompt: str = "") -> dict:
    if not root:
        return {"ok": False, "root": None, "missingFiles": [str(path) for path in PLAN_RELATIVE_PATHS], "missingSections": [], "routeCount": 0}
    missing_files: list[str] = []
    missing_sections: list[str] = []
    texts: dict[str, str] = {}
    for relative in PLAN_RELATIVE_PATHS:
        path = root / relative
        if not path.is_file():
            missing_files.append(relative.as_posix())
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            missing_files.append(relative.as_posix())
            continue
        texts[path.name] = text
        if not text.strip():
            missing_sections.append(f"{path.name}:non-empty")
            continue
        if len(text.strip()) < MIN_PLAN_CHARACTERS:
            missing_sections.append(f"{path.name}:minimum-{MIN_PLAN_CHARACTERS}-characters")
        for index, patterns in enumerate(PLAN_SECTION_PATTERNS[path.name], start=1):
            if not _contains(text, patterns):
                missing_sections.append(f"{path.name}:section-{index}")
    design_text = texts.get("design-plan.md", "")
    if PLACEHOLDER_EVIDENCE_RE.search(design_text):
        missing_sections.append("design-plan.md:real-evidence-url")
    route_count = len(re.findall(r"^\s*(?:[-*]\s*)?(?:route|page|경로|페이지)\s*[:：]", design_text, re.IGNORECASE | re.MULTILINE))
    if route_count == 0:
        route_count = len(re.findall(r"(?:route|page|경로|페이지)\s*[:：]", design_text, re.IGNORECASE))
    multi_ok = not multi_page_required(prompt) or route_count >= 2 or bool(re.search(r"multi[- ]?page|다중\s*페이지", design_text, re.IGNORECASE))
    if multi_page_required(prompt) and not multi_ok:
        missing_sections.append("design-plan.md:at-least-two-routes")
    return {
        "ok": not missing_files and not missing_sections,
        "root": str(root),
        "missingFiles": missing_files,
        "missingSections": missing_sections,
        "routeCount": route_count,
        "multiPageRequired": multi_page_required(prompt),
        "multiPageReady": multi_ok,
    }


def planning_gate(payload: dict) -> dict:
    if not planning_required(payload):
        return {"decision": "allow"}
    status = plan_status(workspace_plan_root(payload), latest_user_prompt(payload))
    if status["ok"]:
        return {"decision": "allow"}
    missing = ", ".join(status["missingFiles"][:3]) or ", ".join(status["missingSections"][:4])
    return {
        "decision": "deny",
        "reason": "UI 소스 쓰기 전에 docs/plans/design-plan.md, implementation-plan.md, verification-plan.md를 먼저 작성하고 "
        "실제 사용자·화면 경로·상태·반응형·감속 모션·책임 경계·검증 명령을 채우세요. "
        + (f"현재 부족한 항목: {missing}." if missing else "계획을 다시 확인하세요."),
    }
