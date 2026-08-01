#!/usr/bin/env python3
"""Deterministic checks for agy-focus hook routing and gates."""

from __future__ import annotations

import importlib.util
import json
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


def write_transcript(records: list[dict]) -> tuple[tempfile.TemporaryDirectory, dict]:
    directory = tempfile.TemporaryDirectory()
    path = Path(directory.name) / "transcript.jsonl"
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )
    return directory, {"conversationId": "test-conversation", "transcriptPath": str(path)}


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


def test_prompt_detectors(runner) -> None:
    directory, ui_payload = write_transcript(
        [{"type": "USER_INPUT", "content": "반응형 UI 화면과 버튼 문구를 고쳐줘"}]
    )
    try:
        assert runner.ui_evidence_required(ui_payload)
        original_read_state = runner.read_state
        runner.read_state = lambda: {}
        try:
            assert runner.ui_evidence_anchor_needed(ui_payload)
            response, extra = runner.visual_evidence_response(ui_payload)
            assert response.get("injectSteps")
            assert extra == {"uiEvidenceConversationId": "test-conversation"}
        finally:
            runner.read_state = original_read_state
        assert not runner.research_gate_required(ui_payload)
    finally:
        directory.cleanup()

    directory, research_payload = write_transcript(
        [{"type": "USER_INPUT", "content": "Gemini 최신 공식 문서를 찾아줘"}]
    )
    try:
        assert runner.research_gate_required(research_payload)
        assert not runner.ui_evidence_required(research_payload)
    finally:
        directory.cleanup()


def main() -> None:
    runner = load_runner()
    test_tool_decisions(runner)
    test_prompt_detectors(runner)
    print("hook runner tests passed")


if __name__ == "__main__":
    main()
