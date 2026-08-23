from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlsplit

from .config import (
    DESIGN_TRIGGER_RE,
    MULTI_PAGE_TRIGGER_RE,
    OFFICIAL_UI_SOURCE_RE,
    PLACEHOLDER_EVIDENCE_RE,
    STATIC_PAGE_RE,
)
from .payloads import command_line, latest_user_prompt, tool_name, workspace_roots, write_target_path
from .design_contract import decision_ledger_status
from .research_contract import plan_evidence_status
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
    if re.search(r"\b(?:single[- ]?screen|one[- ]?screen)\s+app\b|단일\s*화면\s*앱", prompt, re.IGNORECASE):
        return False
    return bool(MULTI_PAGE_TRIGGER_RE.search(prompt) or STATIC_PAGE_RE.search(prompt))


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
        (r"user outcome|success signal|사용자 결과|성공 기준|완료 조건",),
        (r"content hierarchy|정보 위계|콘텐츠 위계|information architecture|구조",),
        (r"route|page|경로|페이지",),
        (r"loading|empty|error|success|disabled|selected|상태",),
        (r"responsive|mobile|320|반응형|모바일",),
        (r"visual direction|시각 방향|visual language|시각 언어",),
        (r"restrained|expressive|절제|표현적|모드|mode",),
        (r"rationale|근거|이유|판단",),
        (r"alternative|대안|tradeoff|절충",),
        (r"motion|animation|애니메이션|움직임",),
        (r"trigger|트리거|when|조건",),
        (r"purpose|목적|이유",),
        (r"duration|easing|ms|시간|속도",),
        (r"budget|예산|50ms|200ms|350ms|상한",),
        (r"reduced motion|prefers-reduced-motion|감속",),
        (r"accessib|접근성|focus|키보드",),
        (r"adaptive|reflow|reveal|presentation|적응형|재배치|노출|전환",),
        (r"full[- ]?screen|compact|전체 화면|좁은 화면",),
        (r"keyboard pattern|tabs|grid|dialog|키보드 패턴|탭 패턴",),
        (r"decision|판단|결정",),
        (r"evidence finding|근거 발견|finding",),
        (r"implementation impact|구현 영향",),
        (r"verification gate|검증 게이트",),
        (r"rejected alternative|버린 대안",),
        (r"evidence|근거|source|출처|https?://",),
        (r"recovery|undo|retry|복구|되돌리|재시도",),
    ),
    "implementation-plan.md": (
        (r"file|파일|변경 범위|scope",),
        (r"responsib|책임|boundary|경계|god object",),
        (r"state|data flow|상태|데이터 흐름",),
        (r"intent|의도|source of truth|단일 진실",),
        (r"route|page|경로|페이지",),
        (r"dependency|의존|interface|계약",),
        (r"step|순서|단계|command|명령",),
        (r"rollback|복구|risk|위험",),
    ),
    "verification-plan.md": (
        (r"command|명령|검증 절차|check",),
        (r"route|page|경로|페이지|matrix|매트릭스",),
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
        (r"flow trace|interaction trace|사용자 흐름|동선",),
        (r"computer\s*use|vision|visual observation|컴퓨터\s*유즈|비전|시각 관찰",),
        (r"web comparison|external reference|외부 근거|웹 대조|웹 비교",),
        (r"plan[- ]?implementation|계획[- ]?구현|계획과 구현",),
        (r"vision|browser observation|화면 관찰|브라우저 관찰",),
        (r"independent oracle|독립 기준|독립 검증",),
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
    evidence = plan_evidence_status(design_text)
    if not evidence["ok"]:
        missing_sections.extend(f"design-plan.md:{failure}" for failure in evidence["failures"])
    ledger = decision_ledger_status(design_text)
    if not ledger["ok"]:
        missing_sections.extend(f"design-plan.md:{failure}" for failure in ledger["failures"])
    route_count = len(re.findall(r"^\s*(?:[-*]\s*)?(?:route|page|경로|페이지)\s*[:：]", design_text, re.IGNORECASE | re.MULTILINE))
    if route_count == 0:
        route_count = len(re.findall(r"(?:route|page|경로|페이지)\s*[:：]", design_text, re.IGNORECASE))
    multi_ok = not multi_page_required(prompt) or route_count >= 2
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
        "officialUiSourceCount": len(evidence["officialUrls"]),
        "officialUiSourceHosts": evidence["hosts"],
        "officialUiSourceCategories": evidence["categories"],
        "decisionCount": ledger["decisionCount"],
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
