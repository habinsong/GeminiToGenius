from __future__ import annotations

import json
import re
from pathlib import Path

from .config import VERIFICATION_COMMAND_RE, VISUAL_RENDER_COMMAND_RE
from .coverage import path_coverage
from .evidence import is_fabricated_evidence_command
from .payloads import (
    call_target_path,
    command_line,
    last_write_indexes,
    latest_request_records,
    record_tool_calls,
    transcript_tool_calls,
)
from .planning import multi_page_required, plan_status, workspace_plan_root
from .plan_alignment import plan_alignment_status
from .payloads import latest_user_prompt, written_paths
from .ui_quality import is_strict_gtg, is_ui_task, UI_SUFFIXES
from .visual_contract import is_vision_observation, post_visual_web_research


UI_RENDER_HELPER_RE = re.compile(r"(?:verify_ui_render|verify_multi_page)\.py", re.IGNORECASE)
PLAN_HELPER_RE = re.compile(r"verify_plan\.py", re.IGNORECASE)
MULTI_PAGE_HELPER_RE = re.compile(r"verify_multi_page\.py", re.IGNORECASE)


def successful_ui_measurement(payload: dict) -> bool:
    pending: str | None = None
    for record in latest_request_records(payload):
        content = str(record.get("content", ""))
        if (
            record.get("type") in {"SYSTEM_MESSAGE", "GENERIC", "RUN_COMMAND"}
            and UI_RENDER_HELPER_RE.search(content)
            and ("completed successfully" in content.lower() or "성공적으로 완료" in content)
            and re.search(r'["\']ok["\']\s*:\s*true', content, re.IGNORECASE)
        ):
            return True
        for call in record_tool_calls(record):
            if not isinstance(call, dict) or str(call.get("name", "")).lower() != "run_command":
                continue
            pending = command_line({"toolCall": call})
        if record.get("type") not in {"RUN_COMMAND", "GENERIC", "SYSTEM_MESSAGE"} or not pending:
            continue
        command = pending
        pending = None
        if (
            UI_RENDER_HELPER_RE.search(command)
            and str(record.get("status", "")).upper() in {"DONE", "SUCCESS", "COMPLETED"}
            and re.search(r'["\']ok["\']\s*:\s*true', content, re.IGNORECASE)
        ):
            return True
    return False


def successful_helper(payload: dict, pattern: re.Pattern[str]) -> bool:
    pending: str | None = None
    for record in latest_request_records(payload):
        content = str(record.get("content", ""))
        for call in record_tool_calls(record):
            if not isinstance(call, dict) or str(call.get("name", "")).lower() != "run_command":
                continue
            pending = command_line({"toolCall": call})
        if record.get("type") not in {"RUN_COMMAND", "GENERIC", "SYSTEM_MESSAGE"} or not pending:
            continue
        command = pending
        pending = None
        if (
            pattern.search(command)
            and str(record.get("status", "")).upper() in {"DONE", "SUCCESS", "COMPLETED"}
            and re.search(r'["\']ok["\']\s*:\s*true', content, re.IGNORECASE)
        ):
            return True
    return False


def ui_source_was_written(payload: dict) -> bool:
    return any(path.suffix.lower() in UI_SUFFIXES for path in written_paths(payload))


def planning_verification_status(payload: dict) -> tuple[bool, str]:
    if not is_strict_gtg(payload) or not is_ui_task(payload) or not ui_source_was_written(payload):
        return True, ""
    status = plan_status(workspace_plan_root(payload), latest_user_prompt(payload))
    if not status["ok"]:
        return False, "계획 파일이 없거나 필수 항목이 비어 있습니다. `docs/plans/`의 세 계획을 먼저 완성하세요."
    aligned, alignment_reason = plan_alignment_status(payload)
    if not aligned:
        return False, alignment_reason
    if not successful_helper(payload, PLAN_HELPER_RE):
        return False, "마지막 구현 뒤 `verify_plan.py`가 `ok: true`를 반환한 기록이 없습니다."
    if multi_page_required(latest_user_prompt(payload)) and not successful_helper(payload, MULTI_PAGE_HELPER_RE):
        return False, "다중 페이지 작업인데 `verify_multi_page.py`의 `ok: true` 기록이 없습니다. 모든 경로를 렌더링하세요."
    return True, ""


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
    pending: list[str] = []
    call_index = -1
    for record in latest_request_records(payload):
        for call in record_tool_calls(record):
            call_index += 1
            if call_index <= last_write or str(call.get("name", "")).lower() != "run_command":
                continue
            command = command_line({"toolCall": call})
            if (
                (VERIFICATION_COMMAND_RE.search(command) or VISUAL_RENDER_COMMAND_RE.search(command))
                and not is_fabricated_evidence_command(command)
            ):
                pending.append(command)
        if not pending:
            continue
        if str(record.get("status", "")).upper() in {"DONE", "SUCCESS", "COMPLETED"} and record.get("type") in {"RUN_COMMAND", "GENERIC", "SYSTEM_MESSAGE"}:
            return True
        if (
            record.get("type") == "SYSTEM_MESSAGE"
            and str(record.get("status", "")).upper() in {"DONE", "SUCCESS", "COMPLETED"}
            and re.search(
                r"completed successfully|성공적으로 완료|완료되었습니다",
                str(record.get("content", "")),
                re.IGNORECASE,
            )
        ):
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
    vision_indexes: list[int] = []
    evidence_text: list[str] = []
    for index, call in enumerate(later_calls):
        name = str(call.get("name", "")).lower()
        serialized = json.dumps(call.get("args", {}), ensure_ascii=False)
        if name == "run_command" and VISUAL_RENDER_COMMAND_RE.search(command_line({"toolCall": call})):
            render_indexes.append(index)
            evidence_text.append(serialized)
        if is_vision_observation(call):
            vision_indexes.append(index)
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
    observations_after_render = [index for index in vision_indexes if index > first_render]
    if not observations_after_render:
        return False, "렌더 뒤 Computer Use·비전·실제 이미지 관찰 기록이 없습니다."
    required_screenshots = 2 if MULTI_PAGE_HELPER_RE.search(evidence) else 1
    opened_screenshots = 0
    for call in later_calls[first_render + 1 :]:
        if str(call.get("name", "")).lower() != "view_file":
            continue
        path = call_target_path(call)
        if path and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            opened_screenshots += 1
    visual_count = max(opened_screenshots, len(observations_after_render))
    if visual_count < required_screenshots:
        return False, f"스크린샷을 생성했지만 실제 비전 관찰이 {required_screenshots}개 미만입니다."
    research_ok, research_reason = post_visual_web_research(later_calls, max(observations_after_render))
    if not research_ok:
        return False, research_reason
    if visual_count >= required_screenshots:
        return True, ""
    return False, f"스크린샷 파일을 생성했지만 실제 이미지를 {required_screenshots}개 이상 열어 확인한 기록이 없습니다."
