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
    try:
        value = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return bool(value.get("failed")) if isinstance(value, dict) else False
    except (OSError, json.JSONDecodeError):
        return False


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


def save_state(event: str, payload: dict, *, failed: bool = False) -> None:
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
        fd, temp_name = tempfile.mkstemp(prefix="last_state.", dir=STATE_ROOT)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(state, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temp_name, STATE_FILE)
    except OSError:
        pass


def emit(value: dict) -> None:
    json.dump(value, sys.stdout, ensure_ascii=False, separators=(",", ":"))
    sys.stdout.write("\n")


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
                "ephemeralMessage": f"집중 앵커({active_version}): @멘션·/액션 선택을 기다리지 말고 현재 자연어 지시를 답변·조회·변경·검색·UI·진단 중 하나로 자동 라우팅하세요. 현재 사용자 지시와 활성 작업창 상태만 추적하고, 관련 없는 정리·플러그인·MCP 연결은 시작하지 마세요. 변경 전 확인과 변경 후 검증을 끝낸 뒤에만 완료라고 판단하세요.{model_note}"
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
        save_state(event, payload, failed=bool(payload.get("error")))
        if payload.get("fullyIdle") is False:
            emit({"decision": "continue", "reason": "백그라운드 작업이 아직 실행 중입니다. 작업 상태를 확인한 뒤 종료하세요."})
        else:
            emit({"decision": "allow"})
        return

    save_state(event, payload, failed=bool(payload.get("error")))
    emit({})


if __name__ == "__main__":
    main()
