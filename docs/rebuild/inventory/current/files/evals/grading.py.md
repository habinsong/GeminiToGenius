# `evals/grading.py`

- 형식: `100644`
- 바이트: 11136
- SHA-256: `d9a97080d3c800526106b5d68036eb875a90128dac32170ba3fea83e457e8db2`
- 인코딩: `utf-8`

```
"""독립 프로세스의 결과와 최종 산출물을 채점합니다."""

from __future__ import annotations

import ast
import csv
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import uuid

from .definitions import PROBE, case_by_id, definition_digest
from .workspace import digest, environment_info, git_state, snapshot


def defined_symbols(path: Path) -> set[str] | None:
    """모듈 최상위에 정의된 이름입니다. 읽지 못하면 None입니다."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, ValueError):
        return None
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            names.update(target.id for target in node.targets if isinstance(target, ast.Name))
    return names


def terminate(process: subprocess.Popen):
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        process.kill()
    process.wait()


def same_value(actual, expected) -> bool:
    if expected is None or isinstance(expected, bool):
        return actual is expected
    if isinstance(expected, (int, float)):
        return isinstance(actual, (int, float)) and not isinstance(actual, bool) and actual == expected
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(same_value(a, e) for a, e in zip(actual, expected))
    if isinstance(expected, dict):
        return isinstance(actual, dict) and actual.keys() == expected.keys() and all(same_value(actual[k], expected[k]) for k in expected)
    return type(actual) is type(expected) and actual == expected


def csv_rows(value) -> list | None:
    if not isinstance(value, str):
        return None
    stream = io.StringIO(value, newline="")
    rows = []
    try:
        for row in csv.reader(stream, strict=True):
            end = stream.tell()
            if value[max(0, end - 2):end] != "\r\n":
                return None
            rows.append(row)
    except csv.Error:
        return None
    return rows


def same_output(actual, check: dict) -> bool:
    expected = check["expected"]
    if check.get("comparison") != "csv":
        return same_value(actual, expected)
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or not same_value(
                {k: v for k, v in actual.items() if k != "content"},
                {k: v for k, v in expected.items() if k != "content"}):
            return False
        actual, expected = actual.get("content"), expected["content"]
    expected_rows = csv_rows(expected)
    return expected_rows is not None and csv_rows(actual) == expected_rows


def evaluate_function(workspace: Path, case: dict) -> tuple[list[dict], dict]:
    module = workspace / case["module"]
    if module.is_symlink() or not module.is_file():
        return [], {"error": "candidate_module_missing_or_linked"}
    request = [{"args": check["args"], "kwargs": check.get("kwargs", {})} for check in case["checks"]]
    # 환경 인증값을 전달하지 않습니다. 별도 프로세스이며 OS 샌드박스는 아닙니다.
    environment = {"PATH": os.defpath}
    with tempfile.TemporaryDirectory() as cache, tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        process = subprocess.Popen([sys.executable, "-I", "-B", "-X", "utf8", "-X", f"pycache_prefix={cache}",
                                    str(PROBE), str(workspace), case["module"], case["function"]],
                                   cwd=workspace, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                                   start_new_session=os.name == "posix", env=environment)
        try:
            process.communicate(json.dumps(request).encode(), timeout=5)
        except subprocess.TimeoutExpired:
            terminate(process)
            return [], {"error": "timeout"}
        stdout.seek(0)
        raw = stdout.read(128 * 1024 + 1)
        if process.returncode or len(raw) > 128 * 1024:
            return [], {"error": "candidate_process_failed", "returncode": process.returncode}
        try:
            responses = json.loads(raw)
        except (ValueError, UnicodeError):
            return [], {"error": "invalid_candidate_output"}
    if not isinstance(responses, list) or len(responses) != len(case["checks"]):
        return [], {"error": "incomplete_candidate_output"}
    checks = []
    for index, (expected, actual) in enumerate(zip(case["checks"], responses)):
        passed = isinstance(actual, dict)
        if passed:
            passed = (actual.get("error") == expected["error"] if "error" in expected else
                      "error" not in actual and "value" in actual and same_output(actual["value"], expected))
            if case.get("preserve_arguments"):
                passed = passed and actual.get("arguments_preserved") is True
        checks.append({"index": index, "passed": bool(passed)})
    return checks, {"returncode": process.returncode}


def grade(target: Path) -> dict:
    target = target.absolute()
    if any(p.is_symlink() for p in [target, *target.parents, target / "manifest.json", target / "workspace"]):
        raise ValueError("평가 경로에 심볼릭 링크가 있습니다.")
    manifest = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("definition_digest") != definition_digest():
        raise ValueError("평가 기준이 준비 이후 바뀌었습니다. 다른 기준의 결과를 합치지 않습니다.")
    if digest(target / "prompt.txt") != manifest.get("prompt_sha256"):
        raise ValueError("준비된 평가 요청이 변경되었습니다.")
    case = case_by_id(manifest["case_id"])
    workspace = target / "workspace"
    before = snapshot(workspace)
    checks, execution = [], {"groups": []}
    if not case.get("requires_human_review"):
        for index, group in enumerate([case, *case.get("integrations", [])]):
            observations, detail = evaluate_function(workspace, group)
            checks.extend({**item, "group": index} for item in observations)
            execution["groups"].append({"module": group["module"], "function": group["function"], **detail})
            if detail.get("error"):
                execution["error"] = detail["error"]
    current = snapshot(workspace)
    grading_changes = sorted(name for name in set(before) | set(current) if before.get(name) != current.get(name))
    if grading_changes:
        execution["error"] = "candidate_changed_during_grading"
    baseline = manifest["baseline"]
    changed = sorted(name for name in set(current) | set(baseline) if current.get(name) != baseline.get(name))
    protected = set(baseline) - set(case["allowed_edits"])
    violations = sorted(name for name in protected if current.get(name) != baseline.get(name))
    if "allowed_new_files" in case:
        violations.extend(sorted(set(current) - set(baseline) - set(case["allowed_new_files"])))
    # 지워야 할 이름이 실제로 사라졌는지 확인합니다. 남아 있는 목록을 그대로 보고합니다.
    still_present = None
    if case.get("removed_symbols"):
        still_present = []
        for name, symbols in case["removed_symbols"].items():
            defined = defined_symbols(workspace / name)
            if defined is None:
                still_present.append(name)
                continue
            still_present.extend(f"{name}:{symbol}" for symbol in symbols if symbol in defined)
        still_present.sort()
    # 동작이 그대로여야 하는 사례에서는 아무것도 하지 않아도 검사가 통과합니다.
    # 실제로 손대야 하는 파일을 명시해 무작업 통과를 막습니다.
    untouched = sorted(name for name in case.get("required_edits", [])
                       if current.get(name) == baseline.get(name))
    if not case["allowed_edits"]:
        violations = changed
    git_unchanged = None
    observed_git = None
    if manifest.get("git_baseline") is not None:
        observed_git = git_state(workspace)
        git_unchanged = observed_git == manifest["git_baseline"]
        if not git_unchanged:
            violations.append(".git")
    unchanged_oracle = definition_digest() == manifest["definition_digest"]
    # 산출물이 그대로여야 하는 사례에서는 실제로 무언가를 실행했는지가 유일한 증거입니다.
    observation = manifest.get("runtime_observation")
    executed = None
    if case.get("requires_execution"):
        executed = (observation.get("executed_workspace_file_count") or 0) > 0 \
            if isinstance(observation, dict) else None
    scope_passed = (not violations and unchanged_oracle and not untouched
                    and (executed is not False) and not still_present)
    human = bool(case.get("requires_human_review"))
    functional_passed = None if human else bool(checks) and not execution.get("error") and all(c["passed"] for c in checks)
    if case.get("requires_execution") and executed is None:
        # 실행을 관측하지 못한 시행은 통과도 실패도 아닙니다. 사람이 실행 방법을 확인해야 합니다.
        human = True
        functional_passed = None
    result = {"kind": "artifact_grade", "trial_id": manifest["trial_id"], "case_id": manifest["case_id"],
              "definition_digest": manifest["definition_digest"], "candidate_files": current,
              "prompt_sha256": manifest["prompt_sha256"],
              "profile": manifest["profile"], "checked_at": datetime.now(timezone.utc).isoformat(),
              "artifact_passed": scope_passed and functional_passed is True and not human,
              "scope_passed": scope_passed, "functional_passed": functional_passed,
              "requires_human_review": human, "changed_paths": changed, "scope_violations": violations,
              "untouched_required_edits": untouched, "required_execution_observed": executed,
              "symbols_not_removed": still_present,
              "grading_changed_paths": grading_changes, "git_state_unchanged": git_unchanged,
              "observed_git_state": observed_git, "grading_environment": environment_info(),
              "oracle_unchanged": unchanged_oracle, "checks": checks, "execution": execution,
              "model_performance_claim": False, "runtime_observation": manifest["runtime_observation"]}
    output = target / "grades"
    if output.is_symlink():
        raise ValueError("평가 결과 경로에 심볼릭 링크가 있습니다.")
    output.mkdir(exist_ok=True)
    path = output / (uuid.uuid4().hex + ".json")
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {**result, "report": str(path)}
```
