#!/usr/bin/env python3
"""Deterministic checks for agy-focus hook routing, intake, and gates."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "hooks/hook_runner.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("agy_focus_hook_runner", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_transcript(directory: Path, records: list[dict], conversation_id: str = "test-conversation") -> dict:
    path = directory / "transcript.jsonl"
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )
    return {"conversationId": conversation_id, "transcriptPath": str(path)}


def view_call(path: Path, **extra: object) -> dict:
    args: dict[str, object] = {"AbsolutePath": str(path)}
    args.update(extra)
    return {"tool_calls": [{"name": "view_file", "args": args}]}


def test_tool_decisions(runner) -> None:
    assert runner.decision_for("mcp-purpose-gate", {"toolCall": {"name": "mcp.search"}})["decision"] == "force_ask"
    assert runner.decision_for(
        "destructive-command-gate",
        {"toolCall": {"args": {"CommandLine": "rm -rf ./build"}}},
    )["decision"] == "force_ask"
    assert runner.decision_for(
        "external-input-gate",
        {"toolCall": {"args": {"CommandLine": "git pull --ff-only"}}},
    )["decision"] == "force_ask"
    assert runner.decision_for(
        "external-input-gate",
        {"toolCall": {"args": {"CommandLine": "pytest -q"}}},
    )["decision"] == "allow"
    assert runner.decision_for(
        "scope-read-gate",
        {"toolCall": {"name": "run_command", "args": {"CommandLine": "pytest -q"}}},
    )["decision"] == "allow"


def test_context_anchors(runner) -> None:
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        ui_payload = write_transcript(
            directory,
            [{"type": "USER_INPUT", "content": "반응형 UI 화면과 버튼 문구를 고쳐줘"}],
        )
        original_read_state = runner.read_state
        runner.read_state = lambda: {}
        try:
            design, design_extra = runner.design_context_response(ui_payload)
            copy, copy_extra = runner.copy_context_response(ui_payload)
            visual, visual_extra = runner.visual_evidence_response(ui_payload)
            intake, intake_extra = runner.scope_intake_response(ui_payload)
            assert design.get("injectSteps") and design_extra == {"designContextConversationId": "test-conversation"}
            assert copy.get("injectSteps") and copy_extra == {"copyContextConversationId": "test-conversation"}
            assert visual.get("injectSteps") and visual_extra == {"uiEvidenceConversationId": "test-conversation"}
            assert intake.get("injectSteps") and intake_extra == {"scopeIntakeConversationId": "test-conversation"}
            assert not runner.research_gate_required(ui_payload)
        finally:
            runner.read_state = original_read_state

        research_payload = write_transcript(
            directory,
            [{"type": "USER_INPUT", "content": "Gemini 최신 공식 문서를 찾아줘"}],
            "research-conversation",
        )
        assert runner.research_gate_required(research_payload)
        assert not runner.prompt_matches(research_payload, runner.DESIGN_TRIGGER_RE)
        assert not runner.prompt_matches(research_payload, runner.COPY_TRIGGER_RE)

        architecture_payload = write_transcript(
            directory,
            [{"type": "USER_INPUT", "content": "백엔드 기능과 컴포넌트를 리팩터링해줘"}],
            "architecture-conversation",
        )
        runner.read_state = lambda: {}
        try:
            architecture, architecture_extra = runner.architecture_context_response(architecture_payload)
            assert architecture.get("injectSteps")
            assert architecture_extra == {"architectureContextConversationId": "architecture-conversation"}
        finally:
            runner.read_state = original_read_state


def test_scope_read_gate(runner) -> tuple[tempfile.TemporaryDirectory, Path, dict]:
    temporary = tempfile.TemporaryDirectory()
    directory = Path(temporary.name)
    workspace = directory / "workspace"
    workspace.mkdir()
    files = [
        workspace / "README.md",
        workspace / "src" / "main.py",
        workspace / "src" / "helper.py",
        workspace / "src" / "tokenizer.py",
        workspace / "tests" / "test_main.py",
    ]
    for path in files:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {path.name}\n", encoding="utf-8")
    sensitive = workspace / ".env"
    sensitive.write_text("TOKEN=do-not-read\n", encoding="utf-8")

    records = [{"type": "USER_INPUT", "content": "이 기능을 고쳐줘"}]
    payload = write_transcript(directory, records, "scope-conversation")
    payload["workspacePaths"] = [str(workspace)]
    payload["toolCall"] = {"name": "replace_file_content", "args": {"TargetFile": str(files[1])}}
    ordered = runner.scope_text_paths(payload)
    assert files[3].resolve() in ordered
    assert ordered.index(files[1].resolve()) < ordered.index(files[4].resolve())
    assert ordered.index(files[2].resolve()) < ordered.index(files[4].resolve())
    assert ordered.index(files[3].resolve()) < ordered.index(files[4].resolve())
    assert ordered.index(files[4].resolve()) < ordered.index(files[0].resolve())
    denied = runner.decision_for("scope-read-gate", payload)
    assert denied["decision"] == "deny"
    assert "0/3" in denied["reason"]

    records.append(view_call(files[0]))
    payload = write_transcript(directory, records, "scope-conversation")
    payload["workspacePaths"] = [str(workspace)]
    payload["toolCall"] = {"name": "replace_file_content", "args": {"TargetFile": str(files[1])}}
    denied = runner.decision_for("scope-read-gate", payload)
    assert denied["decision"] == "deny"
    assert "README" in denied["reason"]

    records.extend(view_call(path) for path in files[2:])
    payload = write_transcript(directory, records, "scope-conversation")
    payload["workspacePaths"] = [str(workspace)]
    payload["toolCall"] = {"name": "replace_file_content", "args": {"TargetFile": str(files[1])}}
    denied = runner.decision_for("scope-read-gate", payload)
    assert denied["decision"] == "deny"
    assert "수정 대상 파일" in denied["reason"]

    records.append(view_call(files[1]))
    payload = write_transcript(directory, records, "scope-conversation")
    payload["workspacePaths"] = [str(workspace)]
    payload["toolCall"] = {"name": "replace_file_content", "args": {"TargetFile": str(files[1])}}
    assert runner.decision_for("scope-read-gate", payload)["decision"] == "allow"

    records[-1] = view_call(files[1], StartLine=1, EndLine=1)
    payload = write_transcript(directory, records, "scope-conversation")
    payload["workspacePaths"] = [str(workspace)]
    payload["toolCall"] = {"name": "replace_file_content", "args": {"TargetFile": str(files[1])}}
    assert runner.decision_for("scope-read-gate", payload)["decision"] == "deny"

    records[-2] = view_call(files[4], StartLine=1, EndLine=1)
    payload = write_transcript(directory, records, "scope-conversation")
    payload["workspacePaths"] = [str(workspace)]
    payload["toolCall"] = {"name": "run_command", "args": {"CommandLine": "apply_patch < fix.patch"}}
    assert runner.decision_for("scope-read-gate", payload)["decision"] == "deny"
    return temporary, directory, payload


def test_document_target_does_not_require_unrelated_code(runner) -> None:
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        workspace = directory / "workspace"
        workspace.mkdir()
        readme = workspace / "README.md"
        source = workspace / "src" / "main.py"
        source.parent.mkdir()
        readme.write_text("# Read me\n", encoding="utf-8")
        source.write_text("print('code')\n", encoding="utf-8")
        records = [{"type": "USER_INPUT", "content": "README 문구를 수정해줘"}]
        payload = write_transcript(directory, records, "document-conversation")
        payload["workspacePaths"] = [str(workspace)]
        payload["toolCall"] = {
            "name": "replace_file_content",
            "args": {"TargetFile": str(readme)},
        }
        assert runner.decision_for("scope-read-gate", payload)["decision"] == "deny"
        records.append(view_call(readme))
        payload = write_transcript(directory, records, "document-conversation")
        payload["workspacePaths"] = [str(workspace)]
        payload["toolCall"] = {
            "name": "replace_file_content",
            "args": {"TargetFile": str(readme)},
        }
        assert runner.decision_for("scope-read-gate", payload)["decision"] == "allow"


def invoke_hook_cli(event: str, payload: dict, environment: dict[str, str]) -> dict:
    result = subprocess.run(
        [sys.executable, str(RUNNER_PATH), event],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
        env=environment,
    )
    return json.loads(result.stdout)


def test_hook_cli(scope_directory: Path, payload: dict) -> None:
    home = scope_directory / "home"
    home.mkdir()
    environment = os.environ.copy()
    environment["HOME"] = str(home)
    intake = invoke_hook_cli("scope-intake-anchor", payload, environment)
    assert intake.get("injectSteps")
    assert invoke_hook_cli("scope-intake-anchor", payload, environment) == {}
    response = invoke_hook_cli("scope-read-gate", payload, environment)
    assert response["decision"] == "deny"


def main() -> None:
    runner = load_runner()
    test_tool_decisions(runner)
    test_context_anchors(runner)
    test_document_target_does_not_require_unrelated_code(runner)
    temporary, directory, payload = test_scope_read_gate(runner)
    try:
        test_hook_cli(directory, payload)
    finally:
        temporary.cleanup()
    print("hook runner tests passed")


if __name__ == "__main__":
    main()
