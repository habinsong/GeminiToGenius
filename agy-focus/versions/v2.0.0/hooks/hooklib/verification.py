from __future__ import annotations

import json
import re
from pathlib import Path

from .config import VERIFICATION_COMMAND_RE, VISUAL_RENDER_COMMAND_RE
from .coverage import path_coverage
from .payloads import (
    call_target_path,
    command_line,
    last_write_indexes,
    latest_request_records,
    transcript_tool_calls,
)


UI_RENDER_HELPER_RE = re.compile(r"verify_ui_render\.py", re.IGNORECASE)


def successful_ui_measurement(payload: dict) -> bool:
    pending: str | None = None
    for record in latest_request_records(payload):
        content = str(record.get("content", ""))
        if (
            record.get("type") == "SYSTEM_MESSAGE"
            and UI_RENDER_HELPER_RE.search(content)
            and "completed successfully" in content.lower()
            and re.search(r'["\']ok["\']\s*:\s*true', content, re.IGNORECASE)
        ):
            return True
        for call in record.get("tool_calls", record.get("toolCalls", [])):
            if not isinstance(call, dict) or str(call.get("name", "")).lower() != "run_command":
                continue
            pending = command_line({"toolCall": call})
        if record.get("type") != "RUN_COMMAND" or not pending:
            continue
        command = pending
        pending = None
        if (
            UI_RENDER_HELPER_RE.search(command)
            and record.get("status") == "DONE"
            and re.search(r'["\']ok["\']\s*:\s*true', content, re.IGNORECASE)
        ):
            return True
    return False


def post_write_unverified_paths(payload: dict) -> list[Path]:
    calls = transcript_tool_calls(payload)
    missing: list[Path] = []
    for path, write_index in last_write_indexes(payload).items():
        if not path.is_file():
            continue
        later_calls = calls[write_index + 1 :]
        if not path_coverage(later_calls, path)[2]:
            missing.append(path)
    return sorted(missing)


def verification_after_last_write(payload: dict) -> bool:
    writes = last_write_indexes(payload)
    if not writes:
        return True
    last_write = max(writes.values())
    for call in transcript_tool_calls(payload)[last_write + 1 :]:
        if str(call.get("name", "")).lower() != "run_command":
            continue
        command = command_line({"toolCall": call})
        if VERIFICATION_COMMAND_RE.search(command) or VISUAL_RENDER_COMMAND_RE.search(command):
            return True
    return False


def visual_verification_status(payload: dict) -> tuple[bool, str]:
    writes = last_write_indexes(payload)
    if not writes:
        return True, ""
    calls = transcript_tool_calls(payload)
    later_calls = calls[max(writes.values()) + 1 :]
    if not successful_ui_measurement(payload):
        return (
            False,
            "`python3 ~/.gemini/config/agy-focus/current/scripts/verify_ui_render.py <HTML> --output-dir <DIR>`로 "
            "320px·1280px 렌더와 수평 overflow 계측을 통과한 기록이 없습니다.",
        )
    render_indexes: list[int] = []
    evidence_text: list[str] = []
    for index, call in enumerate(later_calls):
        name = str(call.get("name", "")).lower()
        serialized = json.dumps(call.get("args", {}), ensure_ascii=False)
        if name == "run_command" and VISUAL_RENDER_COMMAND_RE.search(command_line({"toolCall": call})):
            render_indexes.append(index)
            evidence_text.append(serialized)
        elif re.search(r"(?:browser|screenshot|preview|render)", name):
            render_indexes.append(index)
            evidence_text.append(serialized)
    if not render_indexes:
        return False, "HTTP 200·파서·curl은 화면 검증이 아닙니다. 실제 브라우저 스크린샷을 생성하세요."
    evidence = "\n".join(evidence_text)
    helper_invoked = bool(UI_RENDER_HELPER_RE.search(evidence))
    has_narrow = helper_invoked or bool(
        re.search(r"(?:width|window[-_ ]?size|viewport)[^\d]{0,12}320\b|320\s*[,x×]\s*\d+", evidence, re.IGNORECASE)
    )
    has_wide = helper_invoked or bool(
        re.search(
            r"(?:width|window[-_ ]?size|viewport)[^\d]{0,12}(?:768|1024|1200|1280|1440)\b|"
            r"(?:768|1024|1200|1280|1440)\s*[,x×]\s*\d+",
            evidence,
            re.IGNORECASE,
        )
    )
    if not has_narrow or not has_wide:
        return False, "320px 좁은 화면과 768px 이상 넓은 화면을 각각 렌더링한 증거가 없습니다."
    first_render = min(render_indexes)
    for call in later_calls[first_render + 1 :]:
        if str(call.get("name", "")).lower() != "view_file":
            continue
        path = call_target_path(call)
        if path and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            return True, ""
    return False, "스크린샷 파일을 생성했지만 실제 이미지를 열어 확인한 기록이 없습니다."
