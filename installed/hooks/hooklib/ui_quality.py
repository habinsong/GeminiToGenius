from __future__ import annotations

import re
from pathlib import Path

from .config import (
    CATALOG_TRIGGER_RE,
    DARK_THEME_TRIGGER_RE,
    DESIGN_TRIGGER_RE,
    GTG_TRIGGER_RE,
    INTERACTION_TRIGGER_RE,
    STATIC_PAGE_RE,
    READ_ONLY_TRIGGER_RE,
    WRITE_INTENT_RE,
)
from .payloads import latest_user_prompt, tool_name, write_target_path, written_paths


UI_SUFFIXES = {
    ".css", ".scss", ".sass", ".less", ".html", ".htm", ".js", ".mjs", ".ts",
    ".jsx", ".tsx", ".vue", ".svelte",
}
SCRIPT_SUFFIXES = {".js", ".mjs", ".ts", ".jsx", ".tsx", ".vue", ".svelte"}
MARKUP_SUFFIXES = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte"}
DEFINITE_PATTERNS = (
    ("gradient", re.compile(r"(?:linear|radial|conic)-gradient\s*\(", re.IGNORECASE), "장식용 그라데이션을 단색·테두리·타이포그래피 위계로 바꾸세요."),
    ("default-font", re.compile(r"(?:(?:font-family|--[\w-]*font[\w-]*)\s*:[^;]*(?:\bInter\b|\bRoboto\b|\bArial\b)|fonts\.googleapis\.com[^\n]*(?:Inter|Roboto|Arial))", re.IGNORECASE), "Inter·Roboto·Arial 기본값을 쓰지 말고 제품·언어에 맞는 서체와 시스템 fallback을 고르세요."),
    ("pill-radius", re.compile(r"border-radius\s*:\s*(?:999(?:9)?px|9999rem|50rem|100%)", re.IGNORECASE), "pill은 상태 토글처럼 형태가 필요한 컨트롤에만 남기세요."),
    ("soft-radius", re.compile(r"border-radius\s*:\s*(?:1[2-9]|[2-9][0-9])(?:px|rem)", re.IGNORECASE), "반복 카드의 12px 이상 둥근 모서리를 제거하고 경계 의미를 다시 정하세요."),
    ("hover-motion", re.compile(r":hover[^{}]*\{[^{}]*(?:transform|animation)\s*:", re.IGNORECASE | re.DOTALL), "목적 없는 hover 이동·확대·회전 애니메이션을 제거하세요."),
    ("glow", re.compile(r"(?:glow|neon|shadow-(?:cyan|blue|purple)|0\s+0\s+(?:[1-9][0-9]|[1-9]\d{2,})px)", re.IGNORECASE), "글로우·네온 효과를 제거하세요."),
    ("neon-color", re.compile(r"(?:#30d158|#00ff[0-9a-f]{2}|#00ffff|#ff00ff|rgba?\s*\(\s*48\s*,\s*209\s*,\s*88)", re.IGNORECASE), "형광 초록·네온사인 발광 색상을 제거하고 최고 수준의 명도 대비를 갖는 정제된 색상을 사용하세요."),
    ("fake-window-chrome", re.compile(r"(?:traffic-light|apple-traffic-lights|traffic_lights|window-chrome|window_chrome|fake-window|fake_window)", re.IGNORECASE), "웹페이지에 억지스러운 트래픽 라이트 점이나 가짜 윈도우 창틀을 만들지 말고 웹 본연의 전폭 캔버스를 사용하세요."),
    ("abstract-icon", re.compile(r"(?:magic[-_ ]?wand|wand[-_ ]?magic|sparkles?|heroicons?/sparkles?|lucide-wand|fa-wand)", re.IGNORECASE), "요술봉·반짝이 같은 추상 아이콘을 실제 대상·동작 아이콘이나 텍스트로 바꾸세요."),
    ("generic-copy", re.compile(r"(?:build the future|unlock (?:the )?(?:power|future|potential)|revolutioni[sz]e|supercharge|next[- ]generation|cutting[- ]edge|seamless(?:ly)?|ai[- ]powered|intelligent platform|미래를 (?:구축|만드)|가능성을 열|혁신적인|차세대|완벽한 경험|AI 기반의? 혁신)", re.IGNORECASE), "기능을 설명하지 않는 마케팅 문구를 실제 동작·대상·결과로 바꾸세요."),
    ("fake-proof", re.compile(r"(?:trusted by|loved by|10x|99(?:\.\d+)?%|testimonial|customer stor(?:y|ies)|사용자 후기|고객 사례)", re.IGNORECASE), "출처 없는 지표·후기·사회적 증거를 제거하세요."),
)


def is_ui_task(payload: dict) -> bool:
    target = write_target_path(payload)
    return bool(DESIGN_TRIGGER_RE.search(latest_user_prompt(payload))) or bool(
        target and target.suffix.lower() in UI_SUFFIXES
    )


def is_strict_gtg(payload: dict) -> bool:
    return bool(GTG_TRIGGER_RE.search(latest_user_prompt(payload)))


def is_read_only_request(payload: dict) -> bool:
    prompt = latest_user_prompt(payload)
    if not prompt:
        return True
    if READ_ONLY_TRIGGER_RE.search(prompt):
        if re.search(r"(?:고쳐(?:줘|라|달라|야|서)|수정해(?:줘|라|달라|야|서)|추가해(?:줘|라|달라|야|서)|만들어(?:줘|라|달라|야|서)|구현해(?:줘|라|달라|야|서)|삭제해(?:줘|라|달라|야|서)|(?:please\s+)?(?:fix|add|implement|create|refactor|remove|delete)\s+this)", prompt, re.IGNORECASE):
            return False
        return True
    return False


def proposed_text(payload: dict) -> str:
    call = payload.get("toolCall")
    args = call.get("args") if isinstance(call, dict) else None
    if not isinstance(args, dict):
        return ""
    parts: list[str] = []
    for key in ("CodeContent", "codeContent", "ReplacementContent", "replacementContent"):
        value = args.get(key)
        if isinstance(value, str):
            parts.append(value)
    chunks = args.get("ReplacementChunks", args.get("replacementChunks"))
    if isinstance(chunks, list):
        for chunk in chunks:
            if not isinstance(chunk, dict):
                continue
            for key in ("ReplacementContent", "replacementContent"):
                value = chunk.get(key)
                if isinstance(value, str):
                    parts.append(value)
    return "\n".join(parts)


def quality_issues(
    text: str,
    path: Path | None = None,
    *,
    whole_file: bool = False,
    strict: bool = False,
    allow_dark_technical: bool = False,
    allow_catalog: bool = False,
    static_page: bool = False,
) -> list[str]:
    if path and path.suffix.lower() not in UI_SUFFIXES:
        return []
    issues = [f"{code}: {message}" for code, pattern, message in DEFINITE_PATTERNS if pattern.search(text)]
    lowered = text.lower()
    card_classes = re.findall(
        r"(?:class|className)\s*=\s*[\"'][^\"']*\b[\w-]*card[\w-]*\b",
        text,
        re.IGNORECASE,
    )
    if len(card_classes) >= 3:
        issues.append("card-grid: 동일한 카드 반복 대신 콘텐츠 우선순위에 맞춘 섹션·목록·비대칭 구조를 사용하세요.")
    if strict and path and path.suffix.lower() in {".css", ".scss", ".sass", ".less"}:
        radius_values = re.findall(r"border-radius\s*:\s*([^;}{]+)", text, re.IGNORECASE)
        repeated_radius = max((radius_values.count(value) for value in set(radius_values)), default=0)
        if repeated_radius >= 4:
            issues.append("mechanical-radius: 같은 모서리 반경을 모든 면에 반복하지 말고 경계의 역할을 구분하세요.")
        stretch_count = len(re.findall(r"(?:width\s*:\s*100%|flex-grow\s*:\s*1\b)", text, re.IGNORECASE))
        if stretch_count >= 3:
            issues.append("mechanical-stretch: 화면 채우기용 width:100%·flex-grow:1 반복을 줄이고 콘텐츠 관계에 맞춘 크기를 사용하세요.")
        blur_declarations = re.findall(
            r"([^{}]+)\{[^{}]*(?:backdrop-filter|filter)\s*:[^;]*blur\s*\([^;]*;?[^{}]*\}",
            text,
            re.IGNORECASE,
        )
        content_blur = [
            selector for selector in blur_declarations
            if re.search(r"(?:main|section|article|card|hero|content|panel|footer)", selector, re.IGNORECASE)
        ]
        if content_blur:
            issues.append("content-blur: 블러·유리 재료를 콘텐츠 면에 장식으로 깔지 말고 기능 계층에만 제한하세요.")
        elif len(blur_declarations) >= 3:
            issues.append("material-overuse: 블러·유리 재료를 반복하지 말고 탐색·제어 계층에만 제한하세요.")
        palette_hits = sum(color in lowered for color in ("#0d1117", "#161b22", "#30363d", "#58a6ff"))
        if palette_hits >= 3:
            issues.append("template-palette: 제품 근거 없이 GitHub 문서형 팔레트를 복제하지 마세요.")
        slate_hits = sum(
            color in lowered
            for color in ("#f8fafc", "#f1f5f9", "#e2e8f0", "#cbd5e1", "#0f172a", "#475569", "#2563eb", "#1d4ed8")
        )
        if slate_hits >= 5:
            issues.append("slate-template: 다크 테마를 Tailwind Slate 라이트 문서 템플릿으로 단순 반전하지 말고 제품에서 색·서체·면 구분 근거를 가져오세요.")
        bordered_blocks = len(
            re.findall(
                r"\{(?=[^{}]*\bborder(?:-[\w-]+)?\s*:)(?=[^{}]*\bpadding\s*:)(?=[^{}]*\bbackground(?:-color)?\s*:)[^{}]*\}",
                text,
                re.IGNORECASE,
            )
        )
        if static_page and bordered_blocks >= 3:
            issues.append("boxed-section-repeat: 정적 설명 페이지의 섹션을 같은 배경·테두리·패딩 상자로 반복하지 말고 여백·타이포그래피·콘텐츠 관계로 구분하세요.")
        centered_wrappers = len(
            re.findall(
                r"\{(?=[^{}]*\bmax-width\s*:)(?=[^{}]*\bmargin\s*:\s*0\s+auto)[^{}]*\}",
                text,
                re.IGNORECASE,
            )
        )
        if static_page and centered_wrappers >= 3:
            issues.append("centered-doc-shell: header·main·footer를 같은 중앙 max-width 틀에 복제하지 말고 페이지 목적에 맞는 고유한 위계와 비대칭 공간을 설계하세요.")
        colors = {value.lower() for value in re.findall(r"#[0-9a-fA-F]{6}\b", text)}
        rgb = [tuple(int(value[index:index + 2], 16) for index in (1, 3, 5)) for value in colors]
        near_black = [value for value in rgb if max(value) <= 56]
        bright_cool = [value for value in rgb if value[0] <= 90 and value[1] >= 140 and value[2] >= 180]
        technical_signals = bool(
            re.search(r"(?:ui-monospace|sfmono|menlo|consolas|technical|terminal|slate|cyan)", text, re.IGNORECASE)
        )
        if not allow_dark_technical and len(near_black) >= 2 and bright_cool and technical_signals:
            issues.append("dark-technical-template: 개발 도구라는 이유로 검은 배경·시안 포인트·모노스페이스 문서 테마를 자동 선택하지 마세요.")
        if re.search(r"scroll-behavior\s*:\s*smooth", text, re.IGNORECASE):
            issues.append("decorative-scroll: 요청하지 않은 smooth scroll을 제거하세요.")
    if strict and path and path.suffix.lower() in MARKUP_SUFFIXES:
        if not allow_catalog and len(re.findall(r"<tr\b", text, re.IGNORECASE)) >= 6:
            issues.append("catalog-table: 저장소 설명을 긴 명세표·규칙표로 덤프하지 말고 효과·설치·동작 증거·한계를 먼저 보여주세요.")
    if whole_file and path and path.suffix.lower() in MARKUP_SUFFIXES:
        if "<main" not in lowered and "role=\"main\"" not in lowered and "role='main'" not in lowered:
            issues.append("semantic-main: 주요 콘텐츠에 main 의미 구조가 없습니다.")
        if not re.search(r"<h1\b", text, re.IGNORECASE):
            issues.append("semantic-h1: 페이지 목적을 직접 설명하는 h1이 없습니다.")
        if path.suffix.lower() in {".html", ".htm"} and "name=\"viewport\"" not in lowered and "name='viewport'" not in lowered:
            issues.append("viewport: 반응형 viewport 선언이 없습니다.")
    return list(dict.fromkeys(issues))


def ui_write_decision(payload: dict) -> dict:
    if not is_ui_task(payload):
        return {"decision": "allow"}
    if tool_name(payload).lower() not in {"write_to_file", "replace_file_content", "multi_replace_file_content"}:
        return {"decision": "allow"}
    text = proposed_text(payload)
    path = write_target_path(payload)
    strict = is_strict_gtg(payload)
    prompt = latest_user_prompt(payload)
    issues = quality_issues(
        text,
        path,
        strict=strict,
        allow_dark_technical=bool(DARK_THEME_TRIGGER_RE.search(prompt)),
        allow_catalog=bool(CATALOG_TRIGGER_RE.search(prompt)),
        static_page=bool(STATIC_PAGE_RE.search(prompt)),
    )
    if (
        strict
        and path
        and path.suffix.lower() in SCRIPT_SUFFIXES
        and STATIC_PAGE_RE.search(prompt)
        and not INTERACTION_TRIGGER_RE.search(prompt)
        and re.search(r"(?:addEventListener|IntersectionObserver|requestAnimationFrame|setInterval|setTimeout)", text)
    ):
        issues.append("unrequested-interaction: 정적 설명 페이지에 요청하지 않은 JavaScript 상호작용을 추가하지 마세요.")
    if not issues:
        return {"decision": "allow"}
    return {"decision": "deny", "reason": "AI Slop 쓰기를 차단했습니다. " + " ".join(issues[:5])}


def workspace_ui_issues(payload: dict) -> list[str]:
    if not is_ui_task(payload):
        return []
    issues: list[str] = []
    prompt = latest_user_prompt(payload)
    for path in sorted(written_paths(payload)):
        if path.suffix.lower() not in UI_SUFFIXES or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        issues.extend(
            f"{path.name}: {issue}"
            for issue in quality_issues(
                text,
                path,
                whole_file=True,
                strict=is_strict_gtg(payload),
                allow_dark_technical=bool(DARK_THEME_TRIGGER_RE.search(prompt)),
                allow_catalog=bool(CATALOG_TRIGGER_RE.search(prompt)),
                static_page=bool(STATIC_PAGE_RE.search(prompt)),
            )
        )
    return list(dict.fromkeys(issues))
