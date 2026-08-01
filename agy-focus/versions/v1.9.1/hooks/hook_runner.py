#!/usr/bin/env python3
"""Small, fail-open Antigravity lifecycle hooks for the agy-focus profile."""

from __future__ import annotations

import json
import os
import re
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
URL_RE = re.compile(r"https?://[^\s)\]}>]+", re.IGNORECASE)
ANTIGRAVITY_DOC_URL_RE = re.compile(
    r"https?://(?:www\.)?antigravity\.google/docs(?:/|[?#])", re.IGNORECASE
)
GEMINI_DOC_URL_RE = re.compile(
    r"https?://ai\.google\.dev/(?:gemini-api/)?docs(?:/|[?#])", re.IGNORECASE
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


def research_gate_required(payload: dict) -> bool:
    records = latest_request_records(payload)
    user_inputs = [
        record.get("content", "")
        for record in records
        if record.get("type") == "USER_INPUT" and isinstance(record.get("content"), str)
    ]
    return bool(user_inputs and RESEARCH_TRIGGER_RE.search(user_inputs[-1]))


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
    return has_successful_tools and read_official_page and reported_source


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

    return {"decision": "allow"}


def main() -> None:
    event = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    payload = read_payload()

    if event in {"mcp-purpose-gate", "destructive-command-gate", "external-input-gate"}:
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
            and attempts < 1
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
                    "reason": "최신·공식 요청은 실제 search_web 호출, 공식 페이지 read_url_content 확인, URL 출처 보고가 있어야 완료됩니다. 한 번 더 검색→공식 페이지 읽기→출처 링크 보고 순서로 진행하세요.",
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
