#!/usr/bin/env python3
"""Antigravity lifecycle entrypoint for the agy-focus profile."""

from __future__ import annotations

import json
import sys
from pathlib import Path


HOOKS_ROOT = Path(__file__).resolve().parent
if str(HOOKS_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOKS_ROOT))

from hooklib.anchors import (  # noqa: E402
    architecture_context_response,
    copy_context_response,
    design_context_response,
    scope_intake_response,
    visual_evidence_response,
)
from hooklib.config import (  # noqa: E402
    ARCHITECTURE_TRIGGER_RE,
    CHANGE_TRIGGER_RE,
    COPY_TRIGGER_RE,
    DESIGN_TRIGGER_RE,
    WRITE_INTENT_RE,
)
from hooklib.gates import (  # noqa: E402
    decision_for,
    research_evidence_present,
    research_gate_required,
    scope_read_complete,
    scope_read_reason,
)
from hooklib.repository_evidence import (  # noqa: E402
    referenced_github_slug,
    repository_reference_evidence_present,
)
from hooklib.payloads import (  # noqa: E402
    fully_viewed_paths,
    path_coverage,
    prompt_matches,
    read_payload,
    scope_text_paths,
    written_paths,
)
from hooklib.state import is_target_model, profile_version, read_state, save_state  # noqa: E402
from hooklib.ui_quality import is_read_only_request, is_strict_gtg, is_ui_task, workspace_ui_issues  # noqa: E402
from hooklib.verification import (  # noqa: E402
    post_write_unverified_paths,
    planning_verification_status,
    verification_after_last_write,
    visual_verification_status,
)


def emit(value: dict) -> None:
    json.dump(value, sys.stdout, ensure_ascii=False, separators=(",", ":"))
    sys.stdout.write("\n")


def previous_failed() -> bool:
    return bool(read_state().get("failed"))


def stored_attempts(previous: dict, conversation_id: str, prefix: str) -> int:
    if previous.get(f"{prefix}ConversationId") != conversation_id:
        return 0
    try:
        return int(previous.get(f"{prefix}Attempts", 0))
    except (TypeError, ValueError):
        return 0


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
        model_name = str(payload.get("modelName", "")).strip()
        model_note = f" 현재 모델: {model_name}." if model_name else ""
        steps = [
            {
                "ephemeralMessage": f"집중 앵커({profile_version()}): @멘션·/액션 선택을 기다리지 말고 현재 자연어 지시를 자동 라우팅하세요. 빨리 끝내기 위해 완료 조건을 줄이거나 README·계획서·검색 조각으로 실제 코드를 대체하지 마세요. 변경이면 전체 파일 지도를 만든 뒤 영향 범위의 실제 소스·호출 경계·테스트를 파일별로 끝까지 읽고 문서는 마지막에 대조하세요. 관련 없는 저장소 전체를 무조건 주입하지 마세요. 최신·공식 요청이면 실제 search_web와 read_url_content 결과 및 공식 URL을 확보하세요. 변경 후 직접 검증을 끝낸 뒤에만 완료로 판단하세요.{model_note}"
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

    anchor_handlers = {
        "scope-intake-anchor": scope_intake_response,
        "architecture-boundary-anchor": architecture_context_response,
        "design-context-anchor": design_context_response,
        "copy-context-anchor": copy_context_response,
        "visual-evidence-anchor": visual_evidence_response,
    }
    if event in anchor_handlers:
        response, extra = anchor_handlers[event](payload)
        save_state(event, payload, failed=bool(payload.get("error")), extra=extra)
        emit(response)
        return

    if event == "stop-snapshot":
        if payload.get("fullyIdle") is False:
            save_state(event, payload, failed=bool(payload.get("error")))
            emit({"decision": "continue", "reason": "백그라운드 작업이 아직 실행 중입니다. 작업 상태를 확인한 뒤 종료하세요."})
            return

        unverified_paths = post_write_unverified_paths(payload)
        if unverified_paths:
            save_state(event, payload, failed=bool(payload.get("error")))
            names = ", ".join(str(path) for path in unverified_paths[:4])
            emit(
                {
                    "decision": "continue",
                    "reason": "방금 쓴 파일을 현재 내용 기준으로 끝까지 다시 읽지 않았습니다. "
                    + names
                    + " 파일을 첫 줄부터 마지막 줄까지 구간 누락 없이 확인하세요.",
                }
            )
            return

        if not verification_after_last_write(payload):
            save_state(event, payload, failed=bool(payload.get("error")))
            emit(
                {
                    "decision": "continue",
                    "reason": "마지막 변경 뒤 직접 검증이 없습니다. 프로젝트에 맞는 test·build·lint·typecheck·실행 또는 웹 렌더 검증을 실제로 실행하고 결과를 확인하세요.",
                }
            )
            return

        ui_issues = workspace_ui_issues(payload)
        if ui_issues:
            save_state(event, payload, failed=bool(payload.get("error")))
            emit(
                {
                    "decision": "continue",
                    "reason": "UI 결과가 GTG 품질 게이트를 통과하지 못했습니다. "
                    + " ".join(ui_issues[:6])
                    + " 실제 화면을 다시 렌더링한 뒤 같은 항목을 재검증하세요.",
                }
            )
            return

        plan_ok, plan_reason = planning_verification_status(payload)
        if not plan_ok:
            save_state(event, payload, failed=bool(payload.get("error")))
            emit({"decision": "continue", "reason": plan_reason})
            return

        if is_strict_gtg(payload) and is_ui_task(payload):
            visual_ok, visual_reason = visual_verification_status(payload)
            if not visual_ok:
                save_state(event, payload, failed=bool(payload.get("error")))
                emit(
                    {
                        "decision": "continue",
                        "reason": "GTG UI 작업의 실제 화면 증거가 부족합니다. "
                        + visual_reason
                        + " 좁은 화면과 넓은 화면 이미지를 직접 열어 위계·잘림·가로 스크롤을 확인하세요.",
                    }
                )
                return

        conversation_id = str(payload.get("conversationId", ""))
        previous = read_state()
        scope_attempts = stored_attempts(previous, conversation_id, "scopeGate")
        has_written = bool(written_paths(payload))
        write_requested = (prompt_matches(payload, WRITE_INTENT_RE) or prompt_matches(payload, CHANGE_TRIGGER_RE)) and not is_read_only_request(payload)
        scope_required = is_strict_gtg(payload) or has_written or write_requested
        if scope_required and not scope_read_complete(payload):
            save_state(
                event,
                payload,
                failed=bool(payload.get("error")),
                extra={
                    "scopeGateConversationId": conversation_id,
                    "scopeGateAttempts": scope_attempts + 1,
                },
            )
            emit(
                {
                    "decision": "continue",
                    "reason": scope_read_reason(payload)
                    + " 이 게이트는 재시도 횟수로 우회하지 않습니다.",
                }
            )
            return

        research_attempts = stored_attempts(previous, conversation_id, "researchGate")
        if research_gate_required(payload) and not research_evidence_present(payload):
            save_state(
                event,
                payload,
                failed=bool(payload.get("error")),
                extra={
                    "researchGateConversationId": conversation_id,
                    "researchGateAttempts": research_attempts + 1,
                },
            )
            emit(
                {
                    "decision": "continue",
                    "reason": "최신·공식 요청은 실제 search_web 호출, 공식 페이지 read_url_content 확인, URL 출처 보고가 있어야 완료됩니다. /GTG UI 작업은 공식 URL 4개 이상·서로 다른 호스트 3개 이상·플랫폼/접근성/성능/HCI/디자인 시스템 분야 4개 이상을 읽고 모든 URL을 보고해야 합니다. 계획의 결정·근거 발견·구현 영향·검증 게이트도 남기세요. 이 게이트는 재시도 횟수로 우회하지 않습니다. canonical Hooks 페이지에 직접 없는 Inspect/Decide/Transform 분류, Python SDK, ask_user, before_tool_call, after_model_call, continue_on_error, event: 필드를 보고하지 마세요.",
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
