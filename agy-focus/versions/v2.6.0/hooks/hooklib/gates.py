from __future__ import annotations

import re

from .config import (
    ARCHITECTURE_TRIGGER_RE,
    COMMAND_WRITE_RE,
    DESIGN_TRIGGER_RE,
    DOCUMENT_TASK_RE,
    DOC_SUFFIXES,
    GEMINI_DOC_URL_RE,
    INSTRUCTION_NAMES,
    SOURCE_SUFFIXES,
)
from .payloads import (
    command_line,
    fully_viewed_paths,
    intake_priority,
    latest_user_prompt,
    path_coverage,
    scope_text_paths,
    tool_name,
    write_target_path,
)
from .planning import is_plan_path, planning_gate
from .repository_evidence import repository_reference_gate
from .ui_quality import is_strict_gtg, is_ui_task, ui_write_decision
from .evidence import is_fabricated_evidence_command
from .read_order import (
    documentation_read_denied,
    tool_documentation_read_denied,
    workspace_exploration_denied,
)
from .research import research_evidence_present, research_gate_required
WRITE_TOOLS = {"write_to_file", "replace_file_content", "multi_replace_file_content"}
def scope_read_status(payload: dict) -> dict:
    candidates = scope_text_paths(payload)
    viewed = fully_viewed_paths(payload)
    implementation = [path for path in candidates if 1 <= intake_priority(path)[0] <= 4]
    sources = [path for path in candidates if intake_priority(path)[0] == 2]
    tests = [path for path in candidates if intake_priority(path)[0] == 3]
    prompt = latest_user_prompt(payload)
    target = write_target_path(payload)
    strict_intake = is_strict_gtg(payload)
    code_task = bool(ARCHITECTURE_TRIGGER_RE.search(prompt) or DESIGN_TRIGGER_RE.search(prompt)) or bool(
        target and target.suffix.lower() in SOURCE_SUFFIXES
    )
    document_only = bool(DOCUMENT_TASK_RE.search(prompt)) and not code_task
    if strict_intake and not document_only:
        code_task = True
    minimum = 0 if document_only else len(implementation) if code_task and strict_intake else 3 if code_task else 1
    minimum = min(minimum, len(implementation))
    source_minimum = len(sources) if code_task and strict_intake else min(3, len(sources)) if code_task else 0
    implementation_viewed = [path for path in implementation if path in viewed]
    sources_viewed = [path for path in sources if path in viewed]
    tests_viewed = [path for path in tests if path in viewed]
    target_requires_read = bool(target and target.exists() and target.is_file())
    target_read = not target_requires_read or target in viewed
    return {
        "implementation": implementation,
        "implementationViewed": implementation_viewed,
        "sources": sources,
        "sourcesViewed": sources_viewed,
        "sourceMinimum": source_minimum,
        "tests": tests,
        "testsViewed": tests_viewed,
        "testRequired": code_task and bool(tests),
        "minimum": minimum,
        "codeTask": code_task,
        "target": target,
        "targetRequiresRead": target_requires_read,
        "targetRead": target_read,
    }
def scope_read_complete(payload: dict) -> bool:
    status = scope_read_status(payload)
    return (
        len(status["implementationViewed"]) >= status["minimum"]
        and len(status["sourcesViewed"]) >= status["sourceMinimum"]
        and status["targetRead"]
        and (not status["testRequired"] or len(status["testsViewed"]) >= len(status["tests"]))
    )
def scope_read_reason(payload: dict) -> str:
    status = scope_read_status(payload)
    viewed = set(status["implementationViewed"])
    missing = [path for path in status["implementation"] if path not in viewed]
    parts = [
        "변경 전 코드 우선 인테이크가 부족합니다.",
        f"구현·설정·테스트 전체 읽기 {len(viewed)}/{status['minimum']} 근거.",
    ]
    if len(status["sourcesViewed"]) < status["sourceMinimum"]:
        source_viewed = set(status["sourcesViewed"])
        missing_sources = [path for path in status["sources"] if path not in source_viewed]
        preview = ", ".join(str(path) for path in missing_sources[:3])
        parts.append(
            f"실제 소스 전체 읽기 {len(source_viewed)}/{status['sourceMinimum']} 근거. 후보: {preview}."
        )
    if status["targetRequiresRead"] and not status["targetRead"]:
        covered, total, _ = path_coverage(payload, status["target"])
        detail = f" 현재 연속 구간 {covered}/{total}줄." if total is not None else ""
        parts.append(f"수정 대상 파일을 구간 누락 없이 끝까지 읽으세요: {status['target']}.{detail}")
    if len(viewed) < status["minimum"] and missing:
        preview = ", ".join(str(path) for path in missing[:3])
        parts.append(f"영향 범위를 따라 관련 구현 파일을 끝까지 읽으세요. 후보: {preview}.")
    if status["testRequired"] and not status["testsViewed"]:
        preview = ", ".join(str(path) for path in status["tests"][:3])
        parts.append(f"기존 관련 테스트를 모두 끝까지 읽고 기대 동작을 확인하세요. 후보: {preview}.")
    parts.append("README·계획·검색 결과는 구현 근거 수에 포함되지 않습니다.")
    return " ".join(parts)
def documentation_read_gate(payload: dict) -> dict:
    target = write_target_path(payload)
    if not target:
        return {"decision": "allow"}
    name = target.name.lower()
    if name in INSTRUCTION_NAMES:
        return {"decision": "allow"}
    if any((parent / "SKILL.md").is_file() for parent in list(target.parents)[:3]):
        return {"decision": "allow"}
    if target.suffix.lower() not in DOC_SUFFIXES and name not in {"readme", "changelog"}:
        return {"decision": "allow"}
    status = scope_read_status(payload)
    if not status["codeTask"] or not status["sources"]:
        return {"decision": "allow"}
    sources_ready = len(status["sourcesViewed"]) >= status["sourceMinimum"]
    tests_ready = not status["testRequired"] or len(status["testsViewed"]) >= len(status["tests"])
    if sources_ready and tests_ready:
        return {"decision": "allow"}
    return {
        "decision": "deny",
        "reason": "README·docs 선행 읽기를 차단했습니다. 저장소 지침과 manifest는 먼저 볼 수 있지만, "
        "현재 동작 판단은 실제 소스 전체와 기존 관련 테스트 전체를 "
        "첫 줄부터 마지막 줄까지 읽은 뒤 문서와 대조하세요.",
    }


def external_reference_gate(payload: dict) -> dict:
    status = scope_read_status(payload)
    if not status["codeTask"] or not status["sources"]:
        return {"decision": "allow"}
    sources_ready = len(status["sourcesViewed"]) >= status["sourceMinimum"]
    tests_ready = not status["testRequired"] or len(status["testsViewed"]) >= len(status["tests"])
    if sources_ready and tests_ready:
        return {"decision": "allow"}
    return {
        "decision": "deny",
        "reason": "웹 검색·원격 README 선행 판단을 차단했습니다. 먼저 현재 workspace의 실제 소스 전체"
        "와 기존 관련 테스트 전체를 끝까지 읽고, 그 뒤 외부 문서와 대조하세요.",
    }


def scope_read_gate(payload: dict) -> dict:
    name = tool_name(payload).lower()
    target = write_target_path(payload)
    if target and is_plan_path(target):
        if is_strict_gtg(payload) and is_ui_task(payload) and not scope_read_complete(payload):
            return {
                "decision": "deny",
                "reason": "docs/plans 쓰기를 소스 선독보다 앞세울 수 없습니다. 실제 HTML/CSS/JavaScript·호출 경로·상태·관련 테스트를 먼저 끝까지 읽고 그 뒤 계획을 작성하세요.",
            }
        return {"decision": "allow"}
    if name == "run_command" and is_fabricated_evidence_command(command_line(payload)):
        return {
            "decision": "deny",
            "reason": "출력만 만드는 명령을 출처·검증 증거로 꾸미는 우회를 차단했습니다. "
            "실제 공식 URL을 열고 읽은 결과나 실제 검증 명령의 완료 출력을 사용하세요.",
        }
    if name == "run_command" and documentation_read_denied(command_line(payload), scope_read_status(payload)):
        return {
            "decision": "deny",
            "reason": "README·docs를 shell 명령으로 먼저 훑는 우회를 차단했습니다. "
            "먼저 실제 소스·호출·상태·테스트를 `view_file`로 첫 줄부터 마지막 줄까지 빠짐없이 확인하세요. "
            "문서·README·검색 결과는 구현 근거가 아니며 소스 인테이크가 끝난 뒤에만 대조할 수 있습니다.",
        }
    if tool_documentation_read_denied(payload, scope_read_status(payload)):
        return {
            "decision": "deny",
            "reason": "IDE의 문서 분석 우회를 차단했습니다. 먼저 실제 소스·호출·상태·테스트를 "
            "view_file로 첫 줄부터 마지막 줄까지 읽고, 그 뒤 README·docs를 대조하세요.",
        }
    if workspace_exploration_denied(payload, scope_read_status(payload)):
        return {
            "decision": "deny",
            "reason": "workspace·폴더·파일 트리 선행 탐색을 차단했습니다. 먼저 실제 구현 소스와 관련 테스트를 "
            "파일별로 첫 줄부터 마지막 줄까지 읽으세요. 디렉터리 요약·탐색 결과는 소스 인테이크 근거가 아닙니다.",
        }
    allowed_names = {"run_command", "view_file", "read_url_content", "search_web", *WRITE_TOOLS}
    if name not in allowed_names:
        status = scope_read_status(payload)
        if status["codeTask"] and status["sources"] and not scope_read_complete(payload):
            return {
                "decision": "deny",
                "reason": "소스 인테이크 전에는 등록된 전체 파일 읽기·검증 경로만 허용합니다. "
                "IDE의 요약·분석·workspace 탐색 결과로 실제 소스 전체 읽기를 대체하지 마세요.",
            }
        return {"decision": "allow"}
    if name == "view_file":
        return documentation_read_gate(payload)
    if name in {"read_url_content", "search_web"}:
        return external_reference_gate(payload)
    if name == "run_command" and not COMMAND_WRITE_RE.search(command_line(payload)):
        return {"decision": "allow"}
    if name in WRITE_TOOLS or (name == "run_command" and COMMAND_WRITE_RE.search(command_line(payload))):
        plan_decision = planning_gate(payload)
        if plan_decision["decision"] != "allow":
            return plan_decision
    if not scope_read_complete(payload):
        return {"decision": "deny", "reason": scope_read_reason(payload)}
    if name in WRITE_TOOLS or (name == "run_command" and COMMAND_WRITE_RE.search(command_line(payload))):
        return repository_reference_gate(payload)
    return {"decision": "allow"}
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
        ui_decision = ui_write_decision(payload)
        if ui_decision["decision"] != "allow":
            return ui_decision
        return scope_read_gate(payload)

    return {"decision": "allow"}
