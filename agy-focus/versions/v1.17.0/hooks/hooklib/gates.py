from __future__ import annotations

import re

from .config import (
    ANTIGRAVITY_DOC_URL_RE,
    ARCHITECTURE_TRIGGER_RE,
    COMMAND_WRITE_RE,
    DOCUMENT_TASK_RE,
    GEMINI_DOC_URL_RE,
    RESEARCH_TRIGGER_RE,
    SOURCE_SUFFIXES,
    UNSUPPORTED_OFFICIAL_CLAIM_RE,
    URL_RE,
)
from .payloads import (
    command_line,
    fully_viewed_paths,
    intake_priority,
    latest_request_records,
    latest_user_prompt,
    scope_text_paths,
    tool_name,
    write_target_path,
)


def research_gate_required(payload: dict) -> bool:
    return bool(RESEARCH_TRIGGER_RE.search(latest_user_prompt(payload)))


def expected_official_url_re(prompt: str):
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
        record.get("type") for record in records if record.get("status") == "DONE"
    }
    read_urls: list[str] = []
    assistant_text: list[str] = []
    for record in records:
        content = record.get("content")
        if record.get("source") == "MODEL" and isinstance(content, str):
            assistant_text.append(content)
        calls = record.get("tool_calls")
        if not isinstance(calls, list):
            continue
        for call in calls:
            if not isinstance(call, dict) or str(call.get("name", "")).lower() != "read_url_content":
                continue
            args = call.get("args")
            if isinstance(args, dict) and isinstance(args.get("Url"), str):
                read_urls.append(args["Url"])
    expected_url = expected_official_url_re(prompt)
    return (
        {"SEARCH_WEB", "READ_URL_CONTENT"}.issubset(tool_result_types)
        and any(expected_url.search(url) for url in read_urls)
        and bool(expected_url.search("\n".join(assistant_text)))
        and not UNSUPPORTED_OFFICIAL_CLAIM_RE.search("\n".join(assistant_text))
    )


def scope_read_status(payload: dict) -> dict:
    candidates = scope_text_paths(payload)
    viewed = fully_viewed_paths(payload)
    implementation = [path for path in candidates if 1 <= intake_priority(path)[0] <= 4]
    prompt = latest_user_prompt(payload)
    target = write_target_path(payload)
    code_task = bool(ARCHITECTURE_TRIGGER_RE.search(prompt)) or bool(
        target and target.suffix.lower() in SOURCE_SUFFIXES
    )
    document_only = bool(DOCUMENT_TASK_RE.search(prompt)) and not code_task
    minimum = 0 if document_only else 3 if code_task else 1
    minimum = min(minimum, len(implementation))
    implementation_viewed = [path for path in implementation if path in viewed]
    target_requires_read = bool(target and target.exists() and target.is_file())
    target_read = not target_requires_read or target in viewed
    return {
        "implementation": implementation,
        "implementationViewed": implementation_viewed,
        "minimum": minimum,
        "target": target,
        "targetRequiresRead": target_requires_read,
        "targetRead": target_read,
    }


def scope_read_complete(payload: dict) -> bool:
    status = scope_read_status(payload)
    return (
        len(status["implementationViewed"]) >= status["minimum"]
        and status["targetRead"]
    )


def scope_read_reason(payload: dict) -> str:
    status = scope_read_status(payload)
    viewed = set(status["implementationViewed"])
    missing = [path for path in status["implementation"] if path not in viewed]
    parts = [
        "변경 전 코드 우선 인테이크가 부족합니다.",
        f"구현·설정·테스트 전체 읽기 {len(viewed)}/{status['minimum']} 최소 근거.",
    ]
    if status["targetRequiresRead"] and not status["targetRead"]:
        parts.append(f"수정 대상 파일을 먼저 끝까지 읽으세요: {status['target']}.")
    if len(viewed) < status["minimum"] and missing:
        preview = ", ".join(str(path) for path in missing[:3])
        parts.append(f"영향 범위를 따라 관련 구현 파일을 끝까지 읽으세요. 후보: {preview}.")
    parts.append("README·계획·검색 결과는 구현 근거 수에 포함되지 않습니다.")
    return " ".join(parts)


def scope_read_gate(payload: dict) -> dict:
    name = tool_name(payload).lower()
    if name == "run_command" and not COMMAND_WRITE_RE.search(command_line(payload)):
        return {"decision": "allow"}
    if scope_read_complete(payload):
        return {"decision": "allow"}
    return {"decision": "deny", "reason": scope_read_reason(payload)}


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
