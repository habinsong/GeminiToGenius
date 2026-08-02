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


def write_complete_plan(workspace: Path, *, routes: int = 2) -> None:
    plan_dir = workspace / "docs" / "plans"
    plan_dir.mkdir(parents=True, exist_ok=True)
    route_names = ["index.html", "details.html", "verification.html"]
    route_lines = "\n".join(f"Route: /{route_names[index - 1]}" for index in range(1, routes + 1))
    (plan_dir / "design-plan.md").write_text(
        """# Design plan\n\nGoal: help the user inspect the product.\nUser: repository maintainer.\nTask: read the evidence and choose a next action.\nContent hierarchy: purpose, primary action, details.\n"""
        + route_lines
        + """\nStates: loading, empty, error, success, disabled, selected, focus.\nResponsive: mobile first at 320 CSS px and wider layouts.\nAdaptive strategy: reflow, reveal, or presentation change at the full-screen to compact transition.\nKeyboard pattern: tabs use the WAI-ARIA tabs pattern and visible focus.\nVisual direction: restrained mode with editorial hierarchy and product-specific emphasis.\nRationale: typography and spacing expose the real content order.\nAlternative: compare an expressive navigation shell and record the tradeoff before choosing.\nRejected alternative: discard the expressive shell because it adds no task value.\nDecision: choose restrained hierarchy.\nEvidence finding: adaptive panes reduce navigation cost.\nImplementation impact: route layout and focus order change at the compact threshold.\nVerification gate: browser and keyboard checks at every route.\nMotion: explain a state change; trigger is route feedback, purpose is feedback, duration is 180ms, easing is ease-out, budget is 200ms.\nReduced motion: prefers-reduced-motion removes non-essential motion.\nAccessibility: keyboard order, visible focus, labels, target size.\nEvidence matrix: source files, tests, official design references, and https://developer.apple.com/design/human-interface-guidelines/layout, https://www.w3.org/TR/WCAG22/, https://developer.chrome.com/docs/web-platform/long-animation-frames, and https://research.google/pubs/guide-a-benchmark-for-user-context-understanding-and-assistance-in-gui-workflow-videos/.\n""",
        encoding="utf-8",
    )
    (plan_dir / "implementation-plan.md").write_text(
        """# Implementation plan\n\nFiles: index.html, details.html, style.css, app.js, tests/page.test.js.\nResponsibilities: view markup, visual rules, interaction state, and test assertions stay separate; no God Object.\nState and data flow: route state enters the view and actions return explicit state.\nIntent and source of truth: route intent is owned by the URL and rendered data stays in the existing source.\nRoute contract: each page has title, main, h1, and real links.\nDependencies: use existing platform APIs and preserve the current interface contract.\nSteps: inspect, implement, render, test.\nRisk and rollback: preserve the existing route and revert only changed files.\n""",
        encoding="utf-8",
    )
    (plan_dir / "verification-plan.md").write_text(
        """# Verification plan\n\nCommand: python3 scripts/verify_plan.py . --require-multi-page --require-ui-evidence\nRoute matrix: verify Home and Details routes with real links.\nFlow trace: open index.html, activate the Details link, return Home, and confirm the selected state.\nPlan-implementation audit: compare every planned route and changed file with the implementation.\nBrowser observation: open screenshots and inspect the actual rendered hierarchy at every route.\nIndependent oracle: WAI-ARIA and WCAG criteria are checked separately from the model report.\n320 mobile: no horizontal overflow and readable order.\n768 medium: navigation, type scale, and content grouping remain usable.\n1280 desktop: hierarchy and route navigation remain clear.\nKeyboard focus: tab order and visible focus ring.\nReduced motion: prefers-reduced-motion removes non-essential transitions.\nState transition: test loading, empty, error, success, disabled, selected, and focus transitions.\nOverflow: verify scrollWidth and element bounds.\nPerformance: measure INP and CLS when the environment allows it.\nAccessibility: inspect aria names, screen reader landmarks, and 24 CSS px target controls.\nEvidence: open mobile, medium, and desktop screenshots for every route.\nPass/fail: pass only when all route, state, accessibility, and render checks pass.\n""",
        encoding="utf-8",
    )


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


def test_shell_documentation_read_is_code_first(runner) -> None:
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        workspace = directory / "workspace"
        source = workspace / "src" / "main.py"
        readme = workspace / "README.md"
        source.parent.mkdir(parents=True)
        source.write_text("print('source')\n", encoding="utf-8")
        readme.write_text("# README\n", encoding="utf-8")
        payload = write_transcript(
            directory,
            [{"type": "USER_INPUT", "content": "/GTG 기능을 고쳐줘"}],
            "shell-documentation-conversation",
        )
        payload["workspacePaths"] = [str(workspace)]
        payload["toolCall"] = {
            "name": "run_command",
            "args": {"CommandLine": "sed -n '1,80p' README.md"},
        }
        denied = runner.decision_for("scope-read-gate", payload)
        assert denied["decision"] == "deny"
        assert "shell 명령" in denied["reason"]


def test_ide_native_documentation_analysis_is_code_first(runner) -> None:
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        workspace = directory / "workspace"
        source = workspace / "src" / "main.py"
        readme = workspace / "README.md"
        source.parent.mkdir(parents=True)
        source.write_text("print('source')\n", encoding="utf-8")
        readme.write_text("# README\n", encoding="utf-8")
        payload = write_transcript(
            directory,
            [{"type": "USER_INPUT", "content": "/GTG 기능을 고쳐줘"}],
            "native-analysis-conversation",
        )
        payload["workspacePaths"] = [str(workspace)]
        payload["toolCall"] = {
            "name": "analyze",
            "args": {"paths": [str(readme)]},
        }
        denied = runner.decision_for("scope-read-gate", payload)
        assert denied["decision"] == "deny"
        assert "IDE의 문서 분석 우회" in denied["reason"]

        payload["toolCall"] = {
            "name": "analyze",
            "args": {"paths": [str(source)]},
        }
        denied = runner.decision_for("scope-read-gate", payload)
        assert denied["decision"] == "deny"
        assert "등록된 전체 파일 읽기" in denied["reason"]

        payload["toolCall"] = {
            "name": "list_directory",
            "args": {"path": str(workspace / "docs")},
        }
        denied = runner.decision_for("scope-read-gate", payload)
        assert denied["decision"] == "deny"
        assert "IDE의 문서 분석 우회" in denied["reason"]

        payload["toolCall"] = {
            "name": "list_dir",
            "args": {"path": str(workspace)},
        }
        denied = runner.decision_for("scope-read-gate", payload)
        assert denied["decision"] == "deny"
        assert "workspace·폴더·파일 트리" in denied["reason"]

        payload["toolCall"] = {
            "name": "explore_workspace",
            "args": {"path": str(workspace)},
        }
        denied = runner.decision_for("scope-read-gate", payload)
        assert denied["decision"] == "deny"
        assert any(
            marker in denied["reason"]
            for marker in ("workspace·폴더·파일 트리", "IDE의 문서 분석 우회")
        )

        for command in (
            "find . -maxdepth 3 -not -path '*/.*'",
            "rg --files .",
            "git ls-files",
        ):
            payload["toolCall"] = {
                "name": "run_command",
                "args": {"CommandLine": command},
            }
            denied = runner.decision_for("scope-read-gate", payload)
            assert denied["decision"] == "deny"
            assert "workspace·폴더·파일 트리" in denied["reason"]


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


def test_strict_ui_research_requires_diverse_official_sources(runner) -> None:
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        records = [
            {"type": "USER_INPUT", "content": "/GTG 반응형 웹페이지를 만들어줘"},
            {"tool_calls": [{"name": "search_web", "args": {"q": "adaptive layout motion accessibility"}}]},
            {"type": "SEARCH_WEB", "status": "DONE", "content": "results"},
            {"tool_calls": [{"name": "read_url_content", "args": {"Url": "https://developer.apple.com/design/human-interface-guidelines/layout"}}]},
            {"type": "READ_URL_CONTENT", "status": "DONE", "content": "Apple layout"},
            {"tool_calls": [{"name": "read_url_content", "args": {"Url": "https://developer.chrome.com/docs/web-platform/long-animation-frames"}}]},
            {"type": "READ_URL_CONTENT", "status": "DONE", "content": "Chrome LoAF"},
            {"tool_calls": [{"name": "read_url_content", "args": {"Url": "https://www.w3.org/TR/WCAG22/"}}]},
            {"type": "READ_URL_CONTENT", "status": "DONE", "content": "WCAG"},
            {"tool_calls": [{"name": "read_url_content", "args": {"Url": "https://research.google/pubs/guide-a-benchmark-for-user-context-understanding-and-assistance-in-gui-workflow-videos/"}}]},
            {"type": "READ_URL_CONTENT", "status": "DONE", "content": "GUIDE"},
            {"source": "MODEL", "content": "https://developer.apple.com/design/human-interface-guidelines/layout https://developer.chrome.com/docs/web-platform/long-animation-frames https://www.w3.org/TR/WCAG22/ https://research.google/pubs/guide-a-benchmark-for-user-context-understanding-and-assistance-in-gui-workflow-videos/"},
        ]
        payload = write_transcript(directory, records, "strict-ui-research-conversation")
        assert runner.research_gate_required(payload)
        assert runner.research_evidence_present(payload)

        records = records[:5] + records[-1:]
        payload = write_transcript(directory, records, "strict-ui-research-conversation")
        assert not runner.research_evidence_present(payload)


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
        path.write_text("\n".join(f"{path.name} line {index}" for index in range(1, 5)) + "\n", encoding="utf-8")
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

    records.append(view_call(files[1], StartLine=2, EndLine=4))
    payload = write_transcript(directory, records, "scope-conversation")
    payload["workspacePaths"] = [str(workspace)]
    payload["toolCall"] = {"name": "replace_file_content", "args": {"TargetFile": str(files[1])}}
    assert runner.decision_for("scope-read-gate", payload)["decision"] == "allow"

    records[3] = view_call(files[3], StartLine=1, EndLine=1)
    records[4] = view_call(files[4], StartLine=1, EndLine=1)
    payload = write_transcript(directory, records, "scope-conversation")
    payload["workspacePaths"] = [str(workspace)]
    payload["toolCall"] = {"name": "run_command", "args": {"CommandLine": "apply_patch < fix.patch"}}
    assert runner.decision_for("scope-read-gate", payload)["decision"] == "deny"
    return temporary, directory, payload


def test_chunked_full_file_coverage(runner) -> None:
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        source = directory / "style.css"
        source.write_text("\n".join(f"line {index}" for index in range(1, 1002)) + "\n", encoding="utf-8")
        records = [
            {"type": "USER_INPUT", "content": "웹페이지를 수정해줘"},
            view_call(source, StartLine=1, EndLine=800),
            view_call(source, StartLine=801, EndLine=1001),
        ]
        payload = write_transcript(directory, records, "coverage-conversation")
        assert source.resolve() in runner.fully_viewed_paths(payload)
        assert runner.path_coverage(payload, source) == (1001, 1001, True)

        records[-1] = view_call(source, StartLine=802, EndLine=1001)
        payload = write_transcript(directory, records, "coverage-conversation")
        assert source.resolve() not in runner.fully_viewed_paths(payload)
        assert runner.path_coverage(payload, source) == (800, 1001, False)


def test_ui_slop_gate(runner) -> None:
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        css = directory / "style.css"
        bad_payload = write_transcript(
            directory,
            [{"type": "USER_INPUT", "content": "제품 웹페이지를 만들어줘"}],
            "ui-conversation",
        )
        bad_payload["toolCall"] = {
            "name": "write_to_file",
            "args": {
                "TargetFile": str(css),
                "CodeContent": "body{font-family:Inter;background:linear-gradient(red,blue)}.card{border-radius:16px}",
            },
        }
        denied = runner.decision_for("scope-read-gate", bad_payload)
        assert denied["decision"] == "deny"
        assert "gradient" in denied["reason"]
        assert "default-font" in denied["reason"]

        good_payload = write_transcript(
            directory,
            [{"type": "USER_INPUT", "content": "제품 웹페이지를 만들어줘"}],
            "ui-conversation",
        )
        good_payload["toolCall"] = {
            "name": "write_to_file",
            "args": {
                "TargetFile": str(css),
                "CodeContent": "body{font-family:Charter,serif;color:#111}.command{inline-size:fit-content;border:1px solid}",
            },
        }
        assert runner.decision_for("scope-read-gate", good_payload)["decision"] == "allow"


def test_strict_gtg_ui_gate(runner) -> None:
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        css = directory / "style.css"
        css_payload = write_transcript(
            directory,
            [{"type": "USER_INPUT", "content": "/GTG 제품 웹페이지를 만들어줘"}],
            "strict-ui-conversation",
        )
        css_payload["toolCall"] = {
            "name": "write_to_file",
            "args": {
                "TargetFile": str(css),
                "CodeContent": """
:root{--font-sans:Roboto,Arial,sans-serif;--radius:6px}
body{background:#0d1117;color:#58a6ff;scroll-behavior:smooth}
.a{border-radius:var(--radius);background:#161b22;border-color:#30363d}
.b{border-radius:var(--radius)}.c{border-radius:var(--radius)}.d{border-radius:var(--radius)}
""",
            },
        }
        denied = runner.decision_for("scope-read-gate", css_payload)
        assert denied["decision"] == "deny"
        assert "default-font" in denied["reason"]
        assert "template-palette" in denied["reason"]
        assert "mechanical-radius" in denied["reason"]

        script = directory / "app.js"
        script_payload = write_transcript(
            directory,
            [{"type": "USER_INPUT", "content": "/GTG 제품 웹페이지를 만들어줘"}],
            "strict-script-conversation",
        )
        script_payload["toolCall"] = {
            "name": "write_to_file",
            "args": {
                "TargetFile": str(script),
                "CodeContent": "document.addEventListener('scroll', () => setTimeout(() => {}, 10));",
            },
        }
        denied = runner.decision_for("scope-read-gate", script_payload)
        assert denied["decision"] == "deny"
        assert "unrequested-interaction" in denied["reason"]

        technical_payload = write_transcript(
            directory,
            [{"type": "USER_INPUT", "content": "/GTG 저장소 설명 웹페이지를 만들어줘"}],
            "technical-ui-conversation",
        )
        technical_payload["toolCall"] = {
            "name": "write_to_file",
            "args": {
                "TargetFile": str(css),
                "CodeContent": """
:root{--bg:#0a0e17;--panel:#121824;--accent:#00e5ff;--font:ui-monospace,Menlo,monospace}
body{background:var(--bg);color:var(--accent);font-family:var(--font)}
""",
            },
        }
        denied = runner.decision_for("scope-read-gate", technical_payload)
        assert denied["decision"] == "deny"
        assert "dark-technical-template" in denied["reason"]

        slate_payload = write_transcript(
            directory,
            [{"type": "USER_INPUT", "content": "/GTG 저장소 설명 웹페이지를 만들어줘"}],
            "slate-ui-conversation",
        )
        slate_payload["toolCall"] = {
            "name": "write_to_file",
            "args": {
                "TargetFile": str(css),
                "CodeContent": """
:root{--bg:#f8fafc;--surface:#f1f5f9;--line:#e2e8f0;--strong:#cbd5e1;--ink:#0f172a;--muted:#475569}
.header{max-width:820px;margin:0 auto;background:var(--surface);border:1px solid var(--line);padding:1rem}
.main{max-width:820px;margin:0 auto;background:var(--bg);border:1px solid var(--line);padding:1rem}
.footer{max-width:820px;margin:0 auto;background:white;border:1px solid var(--line);padding:1rem}
""",
            },
        }
        denied = runner.decision_for("scope-read-gate", slate_payload)
        assert denied["decision"] == "deny"
        assert "slate-template" in denied["reason"]
        assert "boxed-section-repeat" in denied["reason"]
        assert "centered-doc-shell" in denied["reason"]

        markup = directory / "index.html"
        catalog_payload = write_transcript(
            directory,
            [{"type": "USER_INPUT", "content": "/GTG 저장소 설명 웹페이지를 만들어줘"}],
            "catalog-ui-conversation",
        )
        catalog_payload["toolCall"] = {
            "name": "write_to_file",
            "args": {
                "TargetFile": str(markup),
                "CodeContent": "<main><h1>제품</h1><table>" + "<tr><td>규칙</td></tr>" * 6 + "</table></main>",
            },
        }
        denied = runner.decision_for("scope-read-gate", catalog_payload)
        assert denied["decision"] == "deny"
        assert "catalog-table" in denied["reason"]


def test_interface_planning_gate(runner) -> None:
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        workspace = directory / "site"
        source_paths = [workspace / "index.html", workspace / "style.css", workspace / "app.js"]
        test_path = workspace / "tests" / "page.test.js"
        for path in source_paths + [test_path]:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"{path.name} source\n", encoding="utf-8")
        records = [
            {"type": "USER_INPUT", "content": "/GTG multi-page website를 만들어줘"},
            *(view_call(path) for path in source_paths + [test_path]),
        ]
        payload = write_transcript(directory, records, "planning-conversation")
        payload["workspacePaths"] = [str(workspace)]
        payload["toolCall"] = {
            "name": "write_to_file",
            "args": {"TargetFile": str(source_paths[0]), "CodeContent": "<main><h1>Home</h1></main>"},
        }
        denied = runner.decision_for("scope-read-gate", payload)
        assert denied["decision"] == "deny"
        assert "docs/plans" in denied["reason"]

        runner_module = runner
        write_complete_plan(workspace, routes=1)
        denied = runner_module.decision_for("scope-read-gate", payload)
        assert denied["decision"] == "deny"
        assert "at-least-two-routes" in denied["reason"]

        write_complete_plan(workspace, routes=2)
        assert runner_module.decision_for("scope-read-gate", payload)["decision"] == "allow"

        design_path = workspace / "docs" / "plans" / "design-plan.md"
        design_path.write_text(
            design_path.read_text(encoding="utf-8").replace(
                "https://www.w3.org/TR/WCAG22/",
                "https://github.com/duration/easing/README.md",
            ),
            encoding="utf-8",
        )
        denied = runner_module.decision_for("scope-read-gate", payload)
        assert denied["decision"] == "deny"
        assert "real-evidence-url" in denied["reason"]


def test_plan_cli_contract(runner) -> None:
    with tempfile.TemporaryDirectory() as temp:
        workspace = Path(temp) / "site"
        write_complete_plan(workspace, routes=2)
        script_path = ROOT / "scripts" / "verify_plan.py"
        spec = importlib.util.spec_from_file_location("verify_plan", script_path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.check(workspace, True, True)
        assert result["ok"]
        assert result["routes"] == 2


def test_fabricated_evidence_command_gate(runner) -> None:
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        payload = write_transcript(
            directory,
            [{"type": "USER_INPUT", "content": "최신 공식 UI 자료를 검색해서 검증해줘"}],
            "evidence-command-conversation",
        )
        payload["toolCall"] = {
            "name": "run_command",
            "args": {
                "CommandLine": 'python3 -c "print(\'https://github.com/duration/easing/README.md\')"',
            },
        }
        denied = runner.decision_for("scope-read-gate", payload)
        assert denied["decision"] == "deny"
        assert "출처·검증 증거" in denied["reason"]


def test_multi_page_static_contract(runner) -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        for name, label, link in (("index.html", "Home", "details.html"), ("details.html", "Details", "index.html")):
            (root / name).write_text(
                f'<html lang="en"><head><meta charset="utf-8"><title>{label}</title><meta name="viewport" content="width=device-width"></head>'
                f'<body><main><h1>{label}</h1><a href="{link}">Go</a></main></body></html>',
                encoding="utf-8",
            )
        (root / "style.css").write_text(
            ":focus-visible{outline:2px solid #111}@media(prefers-reduced-motion:reduce){*{animation:none}}\n",
            encoding="utf-8",
        )
        script_path = ROOT / "scripts" / "verify_multi_page.py"
        spec = importlib.util.spec_from_file_location("verify_multi_page", script_path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        found = module.routes(root)
        failures, contracts = module.static_checks(root, found)
        assert len(found) == 2
        assert not failures
        assert contracts["reducedMotion"] and contracts["visibleFocus"]
        render_spec = importlib.util.spec_from_file_location(
            "verify_ui_render", ROOT / "scripts" / "verify_ui_render.py"
        )
        assert render_spec and render_spec.loader
        render_module = importlib.util.module_from_spec(render_spec)
        render_spec.loader.exec_module(render_module)
        assert {label for _, _, label in render_module.VIEWPORTS} == {"mobile", "medium", "desktop"}


def test_post_write_verification(runner) -> None:
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        source = directory / "main.py"
        source.write_text("print('done')\n", encoding="utf-8")
        records = [
            {"type": "USER_INPUT", "content": "/GTG 코드를 고쳐줘"},
            {
                "tool_calls": [
                    {
                        "name": "write_to_file",
                        "args": {"TargetFile": str(source), "CodeContent": "print('done')\n"},
                    }
                ]
            },
        ]
        payload = write_transcript(directory, records, "post-write-conversation")
        assert runner.post_write_unverified_paths(payload) == [source.resolve()]
        assert not runner.verification_after_last_write(payload)

        records.append(view_call(source))
        payload = write_transcript(directory, records, "post-write-conversation")
        assert runner.post_write_unverified_paths(payload) == []
        assert not runner.verification_after_last_write(payload)

        records.append(
            {
                "tool_calls": [
                    {"name": "run_command", "args": {"CommandLine": "python3 -m pytest -q"}}
                ]
            }
        )
        records.append(
            {
                "type": "RUN_COMMAND",
                "status": "DONE",
                "content": "pytest passed",
            }
        )
        payload = write_transcript(directory, records, "post-write-conversation")
        assert runner.verification_after_last_write(payload)

        records[-2] = {
            "tool_calls": [
                {"name": "run_command", "args": {"CommandLine": "echo test"}}
            ]
        }
        records[-1] = {"type": "RUN_COMMAND", "status": "DONE", "content": "test"}
        payload = write_transcript(directory, records, "post-write-conversation")
        assert not runner.verification_after_last_write(payload)


def test_visual_verification_gate(runner) -> None:
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        page = directory / "index.html"
        page.write_text("<main><h1>GTG</h1></main>\n", encoding="utf-8")
        narrow = directory / "narrow.png"
        records = [
            {"type": "USER_INPUT", "content": "/GTG 설명 웹페이지를 만들어줘"},
            {
                "tool_calls": [
                    {
                        "name": "write_to_file",
                        "args": {"TargetFile": str(page), "CodeContent": page.read_text(encoding="utf-8")},
                    }
                ]
            },
            view_call(page),
            {
                "tool_calls": [
                    {
                        "name": "run_command",
                        "args": {"CommandLine": "python3 -m http.server 8000 && curl localhost:8000"},
                    }
                ]
            },
        ]
        payload = write_transcript(directory, records, "visual-conversation")
        assert not runner.visual_verification_status(payload)[0]

        records.extend(
            [
                {
                    "tool_calls": [
                        {
                            "name": "run_command",
                            "args": {
                                "CommandLine": "python3 ~/.gemini/config/agy-focus/current/scripts/verify_ui_render.py index.html --output-dir ."
                            },
                        }
                    ]
                },
                {
                    "type": "SYSTEM_MESSAGE",
                    "status": "DONE",
                    "content": 'Task verify_ui_render.py completed successfully. Output: {"ok": true, "viewports": [{"width": 320}, {"width": 1280}]}',
                },
                view_call(narrow),
            ]
        )
        payload = write_transcript(directory, records, "visual-conversation")
        assert runner.visual_verification_status(payload) == (True, "")


def test_code_first_document_gate(runner) -> None:
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        workspace = directory / "workspace"
        paths = [
            workspace / "index.html",
            workspace / "style.css",
            workspace / "app.js",
            workspace / "tests" / "page.test.js",
            workspace / "README.md",
        ]
        for path in paths:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"{path.name}\n", encoding="utf-8")
        records = [{"type": "USER_INPUT", "content": "/GTG 웹페이지를 수정해줘"}]
        payload = write_transcript(directory, records, "code-first-conversation")
        payload["workspacePaths"] = [str(workspace)]
        payload["toolCall"] = {"name": "view_file", "args": {"AbsolutePath": str(paths[-1])}}
        denied = runner.decision_for("scope-read-gate", payload)
        assert denied["decision"] == "deny"
        assert "README·docs 선행" in denied["reason"]

        payload["toolCall"] = {
            "name": "read_url_content",
            "args": {"Url": "https://raw.githubusercontent.com/example/project/main/README.md"},
        }
        denied = runner.decision_for("scope-read-gate", payload)
        assert denied["decision"] == "deny"
        assert "원격 README 선행" in denied["reason"]

        skill = workspace / "skills" / "gtg" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("# GTG\n", encoding="utf-8")
        payload["toolCall"] = {"name": "view_file", "args": {"AbsolutePath": str(skill)}}
        assert runner.decision_for("scope-read-gate", payload)["decision"] == "allow"

        reference = ROOT / "skills" / "gtg" / "references" / "ui-quality.md"
        payload["toolCall"] = {"name": "view_file", "args": {"AbsolutePath": str(reference)}}
        assert runner.decision_for("scope-read-gate", payload)["decision"] == "allow"

        records.extend(view_call(path) for path in paths[:2])
        payload = write_transcript(directory, records, "code-first-conversation")
        payload["workspacePaths"] = [str(workspace)]
        payload["toolCall"] = {
            "name": "read_url_content",
            "args": {"Url": "https://raw.githubusercontent.com/example/project/main/README.md"},
        }
        assert runner.decision_for("scope-read-gate", payload)["decision"] == "deny"

        records.extend(view_call(path) for path in paths[2:4])
        payload = write_transcript(directory, records, "code-first-conversation")
        payload["workspacePaths"] = [str(workspace)]
        payload["toolCall"] = {"name": "view_file", "args": {"AbsolutePath": str(paths[-1])}}
        assert runner.decision_for("scope-read-gate", payload)["decision"] == "allow"
        payload["toolCall"] = {
            "name": "read_url_content",
            "args": {"Url": "https://raw.githubusercontent.com/example/project/main/README.md"},
        }
        assert runner.decision_for("scope-read-gate", payload)["decision"] == "allow"


def test_external_repository_evidence_gate(runner) -> None:
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        workspace = directory / "site"
        files = [workspace / "index.html", workspace / "style.css", workspace / "app.js"]
        for path in files:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"{path.name}\n", encoding="utf-8")
        write_complete_plan(workspace, routes=2)
        records = [
            {"type": "USER_INPUT", "content": '/GTG "habinsong/GeminiToGenius" 를 설명하는 웹페이지 만들어줘'},
            *(view_call(path) for path in files),
        ]
        payload = write_transcript(directory, records, "repository-evidence-conversation")
        payload["workspacePaths"] = [str(workspace)]
        payload["toolCall"] = {
            "name": "write_to_file",
            "args": {"TargetFile": str(files[0]), "CodeContent": "<main><h1>GTG</h1></main>"},
        }
        denied = runner.decision_for("scope-read-gate", payload)
        assert denied["decision"] == "deny"
        assert "1차 근거" in denied["reason"]
        assert runner.referenced_github_slug(payload) == "habinsong/GeminiToGenius"

        records.extend(
            [
                {
                    "tool_calls": [
                        {
                            "name": "read_url_content",
                            "args": {"Url": "https://github.com/habinsong/GeminiToGenius"},
                        }
                    ]
                },
                {"type": "READ_URL_CONTENT", "status": "DONE", "content": "GeminiToGenius README"},
            ]
        )
        payload = write_transcript(directory, records, "repository-evidence-conversation")
        payload["workspacePaths"] = [str(workspace)]
        payload["toolCall"] = {
            "name": "write_to_file",
            "args": {"TargetFile": str(files[0]), "CodeContent": "<main><h1>GTG</h1></main>"},
        }
        assert not runner.repository_reference_evidence_present(payload)
        assert runner.decision_for("scope-read-gate", payload)["decision"] == "deny"

        records.extend(
            [
                {
                    "tool_calls": [
                        {
                            "name": "read_url_content",
                            "args": {
                                "Url": "https://raw.githubusercontent.com/habinsong/GeminiToGenius/main/scripts/install.sh"
                            },
                        }
                    ]
                },
                {"type": "READ_URL_CONTENT", "status": "DONE", "content": "#!/usr/bin/env bash"},
            ]
        )
        payload = write_transcript(directory, records, "repository-evidence-conversation")
        payload["workspacePaths"] = [str(workspace)]
        payload["toolCall"] = {
            "name": "write_to_file",
            "args": {"TargetFile": str(files[0]), "CodeContent": "<main><h1>GTG</h1></main>"},
        }
        assert runner.repository_reference_evidence_present(payload)
        assert runner.decision_for("scope-read-gate", payload)["decision"] == "allow"

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
        check=False,
        env=environment,
    )
    if result.returncode:
        raise AssertionError(f"hook failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def test_stop_snapshot_requires_code_first_intake() -> None:
    with tempfile.TemporaryDirectory() as temp:
        directory = Path(temp)
        workspace = directory / "workspace"
        files = [workspace / "index.html", workspace / "style.css", workspace / "app.js"]
        for path in files:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"{path.name}\n", encoding="utf-8")
        readme = workspace / "README.md"
        readme.write_text("# Notes\n", encoding="utf-8")
        payload = write_transcript(
            directory,
            [
                {"type": "USER_INPUT", "content": "/GTG UI를 검토해줘"},
                view_call(readme),
            ],
            "stop-code-first-conversation",
        )
        payload["workspacePaths"] = [str(workspace)]
        payload["fullyIdle"] = True
        environment = os.environ.copy()
        environment["HOME"] = str(directory / "home")
        response = invoke_hook_cli("stop-snapshot", payload, environment)
        assert response["decision"] == "continue", response
        assert "코드 우선 인테이크" in response["reason"]


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
    test_strict_ui_research_requires_diverse_official_sources(runner)
    test_chunked_full_file_coverage(runner)
    test_ui_slop_gate(runner)
    test_strict_gtg_ui_gate(runner)
    test_interface_planning_gate(runner)
    test_plan_cli_contract(runner)
    test_fabricated_evidence_command_gate(runner)
    test_ide_native_documentation_analysis_is_code_first(runner)
    test_multi_page_static_contract(runner)
    test_post_write_verification(runner)
    test_visual_verification_gate(runner)
    test_code_first_document_gate(runner)
    test_external_repository_evidence_gate(runner)
    test_document_target_does_not_require_unrelated_code(runner)
    temporary, directory, payload = test_scope_read_gate(runner)
    try:
        test_hook_cli(directory, payload)
    finally:
        temporary.cleanup()
    test_stop_snapshot_requires_code_first_intake()
    print("hook runner tests passed")


if __name__ == "__main__":
    main()
