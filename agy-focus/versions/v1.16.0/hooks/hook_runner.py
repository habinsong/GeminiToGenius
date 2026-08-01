#!/usr/bin/env python3
"""Small, fail-open Antigravity lifecycle hooks for the agy-focus profile."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


CONFIG_ROOT = Path.home() / ".gemini" / "config" / "agy-focus"
STATE_ROOT = CONFIG_ROOT / "state"
STATE_FILE = STATE_ROOT / "last_state.json"
VERSION_FILE = CONFIG_ROOT / "current" / "VERSION"
RESEARCH_TRIGGER_RE = re.compile(
    r"(최신|latest|공식|official|검색|search|출처|source|검증|verify)"
    r".*(문서|docs?|찾|확인|research|검색|source|출처|검증|verify)"
    r"|(문서|docs?|찾|확인|research|검색|source|출처|검증|verify)"
    r".*(최신|latest|공식|official|검색|search|출처|source|검증|verify)",
    re.IGNORECASE,
)
CHANGE_TRIGGER_RE = re.compile(
    r"(?:\b(?:fix|add|build|make|create|implement|update|change|edit|refactor|"
    r"remove|write)\b|고쳐|수정|추가|만들어|구현|변경|작성|리팩터|삭제)",
    re.IGNORECASE,
)
DESIGN_TRIGGER_RE = re.compile(
    r"(?:\b(?:ui|ux|css|html|react|tailwind|frontend|landing|dashboard|"
    r"component|responsive|layout)\b|디자인|화면|페이지|버튼|레이아웃|반응형|"
    r"랜딩|대시보드|컴포넌트)",
    re.IGNORECASE,
)
COPY_TRIGGER_RE = re.compile(
    r"(?:\b(?:copywriting|microcopy|headline|button label|empty state|"
    r"error message|ui copy)\b|카피|문구|헤드라인|버튼 텍스트|오류 문구|빈 상태|"
    r"설명문)",
    re.IGNORECASE,
)
URL_RE = re.compile(r"https?://[^\s)\]}>]+", re.IGNORECASE)
ANTIGRAVITY_DOC_URL_RE = re.compile(
    r"https?://(?:www\.)?antigravity\.google/docs(?:/|[?#])", re.IGNORECASE
)
GEMINI_DOC_URL_RE = re.compile(
    r"https?://ai\.google\.dev/(?:gemini-api/)?docs(?:/|[?#])", re.IGNORECASE
)
MAX_RESEARCH_GATE_RETRIES = 3
ONE_TIME_STATE_KEYS = (
    "uiEvidenceConversationId",
    "designContextConversationId",
    "copyContextConversationId",
    "scopeIntakeConversationId",
)
SENSITIVE_NAME_RE = re.compile(
    r"(?:^|/)(?:\.env(?:\..*)?|[^/]+\.(?:pem|key)|id_rsa|id_ed25519|"
    r"[^/]*(?:secret|token|credential|password)[^/]*)$",
    re.IGNORECASE,
)
SKIPPED_SCOPE_PARTS = {".git", "__pycache__", "node_modules", ".venv", "venv", "build", "dist"}
COMMAND_WRITE_RE = re.compile(
    r"(?:^|[;&|]\s*)(?:apply_patch|sed\s+-[^\n]*i|perl\s+-[^\n]*pi|"
    r"tee\b|touch\b|mkdir\b|cp\b|mv\b|rm\b|truncate\b|install\b|ln\b|"
    r"git\s+(?:apply|mv|rm)\b)|(?<!\d)>(?![>&])",
    re.IGNORECASE,
)
UNSUPPORTED_OFFICIAL_CLAIM_RE = re.compile(
    r"(?:\binspect\s+hooks\b|\bdecide\s+hooks\b|\btransform\s+hooks\b|"
    r"\bpython\s+sdk\b|google\.antigravity\.hooks(?:\.policy)?|"
    r"\bprogrammatic(?:\s+logic|\s+policy)\b|"
    r"after[_\s]+model[_\s]+responses?\b|"
    r"before[_\s]+tool[_\s]+call\b|after[_\s]+model[_\s]+call\b|"
    r"\bask_user\b|\bcontinue_on_error\b|`?event`?\s*[:：]|"
    r"antigravity\s+plugin\s+directory|plugin\s+directory|"
    r"mcp\s+server\s+definitions|alongside\s+skills\s*,?\s*rules)",
    re.IGNORECASE,
)


def read_payload() -> dict:
    try:
        value = json.load(sys.stdin)
        return value if isinstance(value, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def tool_name(payload: dict) -> str:
    call = payload.get("toolCall")
    return str(call.get("name", "")) if isinstance(call, dict) else ""


def command_line(payload: dict) -> str:
    call = payload.get("toolCall")
    args = call.get("args") if isinstance(call, dict) else None
    if not isinstance(args, dict):
        return ""
    for key in ("CommandLine", "commandLine", "command_line", "command", "cmd"):
        value = args.get(key)
        if isinstance(value, str):
            return value
    return ""


def previous_failed() -> bool:
    state = read_state()
    return bool(state.get("failed"))


def read_state() -> dict:
    try:
        value = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def profile_version() -> str:
    try:
        return VERSION_FILE.read_text(encoding="utf-8").strip() or "unknown"
    except OSError:
        return "unknown"


def is_target_model(model_name: str) -> bool:
    normalized = model_name.lower()
    return (
        "gemini" in normalized
        and ("3.6" in normalized or "3-6" in normalized)
        and "flash" in normalized
        and "high" in normalized
    )


def save_state(
    event: str,
    payload: dict,
    *,
    failed: bool = False,
    extra: dict | None = None,
) -> None:
    """Store lifecycle metadata only; never copy transcript or tool arguments."""
    try:
        STATE_ROOT.mkdir(parents=True, exist_ok=True)
        state = {
            "event": event,
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "profileVersion": profile_version(),
            "modelName": payload.get("modelName", ""),
            "workspacePaths": payload.get("workspacePaths", []),
            "stepIdx": payload.get("stepIdx"),
            "invocationNum": payload.get("invocationNum"),
            "failed": failed,
        }
        previous = read_state()
        conversation_id = str(payload.get("conversationId", ""))
        if (
            conversation_id
            and previous.get("researchGateConversationId") == conversation_id
        ):
            state["researchGateConversationId"] = conversation_id
            state["researchGateAttempts"] = previous.get("researchGateAttempts", 0)
        for key in ONE_TIME_STATE_KEYS:
            if conversation_id and previous.get(key) == conversation_id:
                state[key] = conversation_id
        fd, temp_name = tempfile.mkstemp(prefix="last_state.", dir=STATE_ROOT)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            if extra:
                state.update(extra)
            json.dump(state, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temp_name, STATE_FILE)
    except OSError:
        pass


def emit(value: dict) -> None:
    json.dump(value, sys.stdout, ensure_ascii=False, separators=(",", ":"))
    sys.stdout.write("\n")


def transcript_records(payload: dict) -> list[dict]:
    transcript_path = payload.get("transcriptPath")
    if not isinstance(transcript_path, str) or not transcript_path:
        return []
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    records: list[dict] = []
    for line in lines:
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            records.append(value)
    return records


def latest_request_records(payload: dict) -> list[dict]:
    records = transcript_records(payload)
    for index in range(len(records) - 1, -1, -1):
        if records[index].get("type") == "USER_INPUT":
            return records[index:]
    return records


def latest_user_prompt(payload: dict) -> str:
    records = latest_request_records(payload)
    for record in reversed(records):
        content = record.get("content")
        if record.get("type") == "USER_INPUT" and isinstance(content, str):
            return content
    return ""


def research_gate_required(payload: dict) -> bool:
    return bool(RESEARCH_TRIGGER_RE.search(latest_user_prompt(payload)))


def prompt_matches(payload: dict, pattern: re.Pattern[str]) -> bool:
    return bool(pattern.search(latest_user_prompt(payload)))


def one_time_anchor_needed(
    payload: dict,
    state_key: str,
    pattern: re.Pattern[str],
) -> bool:
    conversation_id = str(payload.get("conversationId", ""))
    if not conversation_id or not prompt_matches(payload, pattern):
        return False
    return read_state().get(state_key) != conversation_id


def one_time_anchor_response(
    payload: dict,
    state_key: str,
    pattern: re.Pattern[str],
    message: str,
) -> tuple[dict, dict | None]:
    if not one_time_anchor_needed(payload, state_key, pattern):
        return {}, None
    return (
        {
            "injectSteps": [
                {
                    "ephemeralMessage": message
                }
            ]
        },
        {state_key: str(payload.get("conversationId", ""))},
    )


def scope_intake_response(payload: dict) -> tuple[dict, dict | None]:
    return one_time_anchor_response(
        payload,
        "scopeIntakeConversationId",
        CHANGE_TRIGGER_RE,
        "변경 작업: 검색 결과 조각만 보고 수정하지 마세요. 먼저 활성 workspace의 안전한 텍스트 파일 목록을 경로순으로 만들고, 현재 작업에 영향을 줄 수 있는 파일을 `view_file`로 처음부터 끝까지 하나씩 읽으세요. git 저장소면 `git ls-files -co --exclude-standard`를 기준으로 하고, 바이너리·캐시·의존성·비밀 파일만 제외 사유를 남기세요. 목록 조회나 rg 결과는 파일을 읽은 증거가 아닙니다.",
    )


def design_context_response(payload: dict) -> tuple[dict, dict | None]:
    return one_time_anchor_response(
        payload,
        "designContextConversationId",
        DESIGN_TRIGGER_RE,
        "UI 작업: 구현 전에 실제 사용자·핵심 작업·상태·기존 화면과 디자인 시스템을 확인하세요. 화면을 다르게 보이게 하려는 이유로 카드·그라데이션·가짜 지표·AI 배지·추상 아이콘·장식 애니메이션을 넣지 마세요. 모바일 읽기 순서와 키보드 조작을 먼저 정하고, 실제 화면을 확인하기 전에는 시각 품질을 통과로 쓰지 마세요.",
    )


def copy_context_response(payload: dict) -> tuple[dict, dict | None]:
    return one_time_anchor_response(
        payload,
        "copyContextConversationId",
        COPY_TRIGGER_RE,
        "카피 작업: 제목은 화면의 일을, 버튼은 사용자의 동작을, 오류는 문제와 복구 방법을 직접 말하세요. 한 문장에는 한 가지 정보만 두고 중요한 말을 앞에 두세요. 추상 슬로건·AI 자기소개·과장된 환영 문구·사용자 탓·농담을 넣지 마세요.",
    )


def visual_evidence_response(payload: dict) -> tuple[dict, dict | None]:
    quality_pattern = re.compile(
        f"(?:{DESIGN_TRIGGER_RE.pattern}|{COPY_TRIGGER_RE.pattern})", re.IGNORECASE
    )
    return one_time_anchor_response(
        payload,
        "uiEvidenceConversationId",
        quality_pattern,
        "UI·카피 결과: 모델이 만든 첫 화면·문구를 정답으로 승인하지 마세요. 실제 대상·사용자 행동·기존 시스템과 화면을 확인하세요. 보라·파랑 그라데이션, 가짜 지표, 범용 AI 대시보드, 장식 애니메이션, 추상 아이콘으로 빈 공간을 채우지 마세요.",
    )


def expected_official_url_re(prompt: str) -> re.Pattern[str]:
    if re.search(r"antigravity", prompt, re.IGNORECASE):
        return ANTIGRAVITY_DOC_URL_RE
    if re.search(r"gemini", prompt, re.IGNORECASE):
        return GEMINI_DOC_URL_RE
    return URL_RE


def research_evidence_present(payload: dict) -> bool:
    records = latest_request_records(payload)
    prompt = "\n".join(
        record.get("content", "")
        for record in records
        if record.get("type") == "USER_INPUT" and isinstance(record.get("content"), str)
    )
    tool_result_types = {
        record.get("type")
        for record in records
        if record.get("status") == "DONE"
    }
    read_urls: list[str] = []
    assistant_text: list[str] = []
    for record in records:
        content = record.get("content")
        if record.get("source") == "MODEL" and isinstance(content, str):
            assistant_text.append(content)
        calls = record.get("tool_calls")
        if isinstance(calls, list):
            for call in calls:
                if not isinstance(call, dict) or call.get("name", "").lower() != "read_url_content":
                    continue
                args = call.get("args")
                if isinstance(args, dict) and isinstance(args.get("Url"), str):
                    read_urls.append(args["Url"])
    expected_url = expected_official_url_re(prompt)
    has_successful_tools = {
        "SEARCH_WEB",
        "READ_URL_CONTENT",
    }.issubset(tool_result_types)
    read_official_page = any(expected_url.search(url) for url in read_urls)
    reported_source = bool(expected_url.search("\n".join(assistant_text)))
    has_unsupported_claim = bool(
        UNSUPPORTED_OFFICIAL_CLAIM_RE.search("\n".join(assistant_text))
    )
    return (
        has_successful_tools
        and read_official_page
        and reported_source
        and not has_unsupported_claim
    )


def workspace_roots(payload: dict) -> list[Path]:
    values = payload.get("workspacePaths")
    if not isinstance(values, list):
        return []
    roots: list[Path] = []
    for value in values:
        if not isinstance(value, str):
            continue
        path = Path(value).expanduser()
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved.is_dir():
            roots.append(resolved)
    return sorted(set(roots))


def tracked_or_untracked_paths(root: Path) -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-co", "--exclude-standard"],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )
        return [root / line for line in result.stdout.splitlines() if line]
    except (OSError, subprocess.SubprocessError):
        return sorted(path for path in root.rglob("*") if path.is_file())


def safe_text_path(root: Path, path: Path) -> bool:
    try:
        resolved = path.resolve()
        resolved.relative_to(root)
    except (OSError, ValueError):
        return False
    relative = resolved.relative_to(root)
    if any(part in SKIPPED_SCOPE_PARTS for part in relative.parts):
        return False
    if SENSITIVE_NAME_RE.search(relative.as_posix()):
        return False
    try:
        with resolved.open("rb") as stream:
            return b"\0" not in stream.read(8192)
    except OSError:
        return False


def scope_text_paths(payload: dict) -> list[Path]:
    paths: set[Path] = set()
    for root in workspace_roots(payload):
        for candidate in tracked_or_untracked_paths(root):
            if safe_text_path(root, candidate):
                paths.add(candidate.resolve())
    return sorted(paths)


def transcript_tool_calls(payload: dict) -> list[dict]:
    calls: list[dict] = []
    for record in latest_request_records(payload):
        for key in ("tool_calls", "toolCalls"):
            value = record.get(key)
            if isinstance(value, list):
                calls.extend(call for call in value if isinstance(call, dict))
        value = record.get("toolCall")
        if isinstance(value, dict):
            calls.append(value)
    return calls


def fully_viewed_paths(payload: dict) -> set[Path]:
    result: set[Path] = set()
    for call in transcript_tool_calls(payload):
        if str(call.get("name", "")).lower() != "view_file":
            continue
        args = call.get("args")
        if not isinstance(args, dict):
            continue
        if any(key in args for key in ("StartLine", "EndLine", "startLine", "endLine")):
            continue
        value = args.get("AbsolutePath", args.get("absolutePath"))
        if not isinstance(value, str):
            continue
        try:
            result.add(Path(value).expanduser().resolve())
        except OSError:
            continue
    return result


def scope_read_gate(payload: dict) -> dict:
    name = tool_name(payload).lower()
    if name == "run_command" and not COMMAND_WRITE_RE.search(command_line(payload)):
        return {"decision": "allow"}
    required = scope_text_paths(payload)
    if not required:
        return {"decision": "allow"}
    missing = [path for path in required if path not in fully_viewed_paths(payload)]
    if not missing:
        return {"decision": "allow"}
    preview = ", ".join(path.name for path in missing[:3])
    return {
        "decision": "deny",
        "reason": f"변경 전 파일 인테이크가 끝나지 않았습니다. 전체 읽기 {len(required) - len(missing)}/{len(required)}; 다음 파일부터 경로순으로 끝까지 읽으세요: {preview}",
    }


def decision_for(event: str, payload: dict) -> dict:
    name = tool_name(payload).lower()
    command = command_line(payload)

    if event == "mcp-purpose-gate" or re.search(r"(?:^|[._-])(mcp|plugin)(?:[._-]|$)", name):
        return {
            "decision": "force_ask",
            "reason": "현재 작업 목적에 필요한 MCP 또는 플러그인 연결인지 확인한 뒤 실행하세요.",
        }

    if event == "destructive-command-gate":
        pattern = r"\b(rm\s+(-[A-Za-z]*r[A-Za-z]*|--recursive|--no-preserve-root)|git\s+(reset\s+--hard|clean\b)|git\s+push\s+[^\n]*--force|find\s+[^\n]*\s-delete\b|sudo\b|mkfs\b|diskutil\s+erase\w*|chmod\s+-R)\b"
        if re.search(pattern, command, re.IGNORECASE):
            return {
                "decision": "force_ask",
                "reason": "삭제·강제 변경·권한 변경 가능성이 있는 명령입니다. 정확한 범위를 확인하세요.",
            }

    if event == "external-input-gate":
        pattern = r"\b(curl|wget|git\s+(clone|fetch|pull|push|submodule\s+(add|update))|npm\s+(install|i|exec)|pnpm\s+(add|install|dlx)|yarn\s+(add|install|dlx)|bunx|pip3?\s+install|python3?\s+-m\s+pip\s+install|pipx\s+install|brew\s+install|uv\s+(add|pip\s+install|tool\s+install)|cargo\s+(add|install)|go\s+install|docker\s+pull|npx\b|gh\s+(pr|issue|release)\s+(create|comment|close|merge|edit))\b"
        if re.search(pattern, command, re.IGNORECASE):
            return {
                "decision": "force_ask",
                "reason": "외부 네트워크·설치·확장 입력입니다. 현재 작업에 직접 필요한지 확인하세요.",
            }

    if event == "scope-read-gate":
        return scope_read_gate(payload)

    return {"decision": "allow"}


def main() -> None:
    event = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    payload = read_payload()

    if event in {
        "mcp-purpose-gate",
        "destructive-command-gate",
        "external-input-gate",
        "scope-read-gate",
    }:
        emit(decision_for(event, payload))
        save_state(event, payload)
        return

    if event == "focus-anchor":
        failed = previous_failed()
        save_state(event, payload)
        try:
            active_version = profile_version()
        except OSError:
            active_version = "unknown"
        model_name = str(payload.get("modelName", "")).strip()
        model_note = f" 현재 모델: {model_name}." if model_name else ""
        steps = [
            {
                "ephemeralMessage": f"집중 앵커({active_version}): @멘션·/액션 선택을 기다리지 말고 현재 자연어 지시를 답변·조회·변경·검색·UI·진단 중 하나로 자동 라우팅하세요. 현재 사용자 지시와 활성 작업창 상태만 추적하고, 관련 없는 정리·플러그인·MCP 연결은 시작하지 마세요. 최신·공식·문서·검색 요청이면 기억이나 내장 가이드로 대체하지 말고 실제 search_web와 read_url_content 결과 및 공식 URL을 확보한 뒤에만 답하세요. 변경 전 확인과 변경 후 검증을 끝낸 뒤에만 완료라고 판단하세요.{model_note}"
            }
        ]
        if model_name and not is_target_model(model_name):
            steps.append(
                {
                    "ephemeralMessage": f"현재 모델({model_name})은 Gemini 3.6 Flash (High)와 일치하지 않습니다. High 전용 동작이라고 가정하지 말고 모델 불일치를 짧게 보고하세요."
                }
            )
        if failed:
            steps.append(
                {
                    "ephemeralMessage": "직전 도구 호출이 실패했습니다. 같은 호출을 반복하지 말고 오류의 핵심을 확인한 뒤 원인 가설 하나와 최소 재검증을 선택하세요."
                }
            )
        emit({"injectSteps": steps})
        return

    if event == "scope-intake-anchor":
        response, extra = scope_intake_response(payload)
        save_state(event, payload, failed=bool(payload.get("error")), extra=extra)
        emit(response)
        return

    if event == "design-context-anchor":
        response, extra = design_context_response(payload)
        save_state(event, payload, failed=bool(payload.get("error")), extra=extra)
        emit(response)
        return

    if event == "copy-context-anchor":
        response, extra = copy_context_response(payload)
        save_state(event, payload, failed=bool(payload.get("error")), extra=extra)
        emit(response)
        return

    if event == "visual-evidence-anchor":
        response, extra = visual_evidence_response(payload)
        save_state(event, payload, failed=bool(payload.get("error")), extra=extra)
        emit(response)
        return

    if event == "stop-snapshot":
        if payload.get("fullyIdle") is False:
            save_state(event, payload, failed=bool(payload.get("error")))
            emit({"decision": "continue", "reason": "백그라운드 작업이 아직 실행 중입니다. 작업 상태를 확인한 뒤 종료하세요."})
            return
        conversation_id = str(payload.get("conversationId", ""))
        previous = read_state()
        attempts = 0
        if previous.get("researchGateConversationId") == conversation_id:
            try:
                attempts = int(previous.get("researchGateAttempts", 0))
            except (TypeError, ValueError):
                attempts = 0
        if (
            conversation_id
            and research_gate_required(payload)
            and not research_evidence_present(payload)
            and attempts < MAX_RESEARCH_GATE_RETRIES
        ):
            save_state(
                event,
                payload,
                failed=bool(payload.get("error")),
                extra={
                    "researchGateConversationId": conversation_id,
                    "researchGateAttempts": attempts + 1,
                },
            )
            emit(
                {
                    "decision": "continue",
                    "reason": "최신·공식 요청은 실제 search_web 호출, 공식 페이지 read_url_content 확인, URL 출처 보고가 있어야 완료됩니다. canonical Hooks 페이지에 직접 없는 Inspect/Decide/Transform 분류, Python SDK, ask_user, before_tool_call, after_model_call, continue_on_error, event: 필드를 보고하지 마세요. 페이지에 실제로 적힌 hooks.json, enabled, PreToolUse, PostToolUse, PreInvocation, PostInvocation, Stop, type, command, timeout만 기준으로 다시 작성하세요.",
                }
            )
            return
        save_state(event, payload, failed=bool(payload.get("error")))
        emit({"decision": "allow"})
        return

    save_state(event, payload, failed=bool(payload.get("error")))
    emit({})


if __name__ == "__main__":
    main()
