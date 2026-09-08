# `docs/rebuild/validation/2026-09-08-native/evaluator-source/harness.py`

- 형식: `100644`
- 바이트: 9124
- SHA-256: `c35a37c2f24e9e63bf04e48f112e534b351baae2009c447966f5f94a7ec27dee`
- 인코딩: `utf-8`

```
"""에이전트 작업 폴더 밖의 기준으로 결과와 변경 범위를 평가합니다."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid

from gtg.install import install
from gtg.runner import terminate
from gtg.spec import private


ROOT = Path(__file__).resolve().parents[1]
CASES = Path(__file__).with_name("cases.json")
PROBE = Path(__file__).with_name("probe.py")


def digest(path: Path) -> str:
    if path.is_symlink():
        return "link:" + os.readlink(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root: Path) -> dict:
    result = {}
    for folder, directories, files in os.walk(root, followlinks=False):
        directories[:] = [name for name in directories if not private(Path(name))]
        for name in [*directories, *files]:
            path = Path(folder) / name
            if private(path.relative_to(root)):
                continue
            if path.is_symlink() or path.is_file():
                result[path.relative_to(root).as_posix()] = digest(path)
    return result


def definition_digest() -> str:
    fixtures = json.dumps(snapshot(CASES.parent / "fixtures"), sort_keys=True)
    return hashlib.sha256((digest(CASES) + digest(PROBE) + digest(Path(__file__)) + fixtures).encode()).hexdigest()


def case_by_id(case_id: str) -> dict:
    cases = json.loads(CASES.read_text(encoding="utf-8"))["cases"]
    if case_id not in cases:
        raise ValueError("등록되지 않은 평가 사례입니다.")
    return cases[case_id]


def prepare(case_id: str, target: Path, profile: str = "baseline") -> dict:
    case = case_by_id(case_id)
    if profile not in {"baseline", "gtg"}:
        raise ValueError("평가 프로필은 baseline 또는 gtg여야 합니다.")
    target = target.absolute()
    if target.exists() or target.is_symlink() or any(p.is_symlink() for p in target.parents):
        raise ValueError("심볼릭 링크가 없는 새 평가 경로가 필요합니다.")
    target.mkdir(parents=True)
    workspace = target / "workspace"
    fixture = CASES.parent / "fixtures" / case["fixture"]
    shutil.copytree(fixture, workspace, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    if profile == "gtg":
        install(ROOT, workspace, "antigravity", "workspace")
    manifest = {"schema_version": 1, "trial_id": uuid.uuid4().hex, "case_id": case_id,
                "prepared_at": datetime.now(timezone.utc).isoformat(), "profile": profile,
                "definition_digest": definition_digest(), "baseline": snapshot(workspace),
                "runtime_observation": None}
    (target / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (target / "prompt.txt").write_text(case["prompt"] + "\n", encoding="utf-8")
    return {"trial": str(target), "workspace": str(workspace), "prompt": case["prompt"], "model_called": False}


def evaluate_function(workspace: Path, case: dict) -> tuple[list[dict], dict]:
    module = workspace / case["module"]
    if module.is_symlink() or not module.is_file():
        return [], {"error": "candidate_module_missing_or_linked"}
    request = [{"args": check["args"]} for check in case["checks"]]
    # 환경 인증값을 전달하지 않습니다. 별도 프로세스이며 OS 샌드박스는 아닙니다.
    environment = {"PATH": os.defpath, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        process = subprocess.Popen([sys.executable, "-I", str(PROBE), str(workspace), case["module"], case["function"]],
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
                      "error" not in actual and actual.get("value") == expected["expected"])
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
    case = case_by_id(manifest["case_id"])
    workspace = target / "workspace"
    checks, execution = [], {"groups": []}
    if not case.get("requires_human_review"):
        for index, group in enumerate([case, *case.get("integrations", [])]):
            observations, detail = evaluate_function(workspace, group)
            checks.extend({**item, "group": index} for item in observations)
            execution["groups"].append({"module": group["module"], "function": group["function"], **detail})
            if detail.get("error"):
                execution["error"] = detail["error"]
    current = snapshot(workspace)
    baseline = manifest["baseline"]
    changed = sorted(name for name in set(current) | set(baseline) if current.get(name) != baseline.get(name))
    protected = set(baseline) - set(case["allowed_edits"])
    violations = sorted(name for name in protected if current.get(name) != baseline.get(name))
    if not case["allowed_edits"]:
        violations = changed
    unchanged_oracle = definition_digest() == manifest["definition_digest"]
    scope_passed = not violations and unchanged_oracle
    human = bool(case.get("requires_human_review"))
    functional_passed = None if human else bool(checks) and not execution.get("error") and all(c["passed"] for c in checks)
    result = {"kind": "artifact_grade", "trial_id": manifest["trial_id"], "case_id": manifest["case_id"],
              "profile": manifest["profile"], "checked_at": datetime.now(timezone.utc).isoformat(),
              "artifact_passed": scope_passed and functional_passed is True and not human,
              "scope_passed": scope_passed, "functional_passed": functional_passed,
              "requires_human_review": human, "changed_paths": changed, "scope_violations": violations,
              "oracle_unchanged": unchanged_oracle, "checks": checks, "execution": execution,
              "model_performance_claim": False, "runtime_observation": manifest["runtime_observation"]}
    output = target / "grades"
    if output.is_symlink():
        raise ValueError("평가 결과 경로에 심볼릭 링크가 있습니다.")
    output.mkdir(exist_ok=True)
    path = output / (uuid.uuid4().hex + ".json")
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {**result, "report": str(path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("prepare")
    start.add_argument("case_id")
    start.add_argument("target", type=Path)
    start.add_argument("--profile", choices=("baseline", "gtg"), default="baseline")
    score = commands.add_parser("grade")
    score.add_argument("target", type=Path)
    args = parser.parse_args()
    try:
        result = prepare(args.case_id, args.target, args.profile) if args.command == "prepare" else grade(args.target)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return int(args.command == "grade" and not result["artifact_passed"])
    except (OSError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
```
