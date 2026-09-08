# `evals/comparison.py`

- 형식: `100644`
- 바이트: 5128
- SHA-256: `d3ebbb55048da8c76cee0e005733e8d36a90929e0ac1f35163bd3494e6649964`
- 인코딩: `utf-8`

```
"""같은 작업·요청·채점 기준을 공유하는 시행만 하네스별로 모읍니다.

라벨은 사용자가 선언한 값입니다. 어떤 하네스가 실제로 실행됐는지 이 코드가 확인하지는 못합니다.
조건이 하나라도 다르면 비교 결과를 만들지 않고 막힌 이유를 그대로 보고합니다.
"""

from __future__ import annotations

import json
from pathlib import Path

FIELDS = ("case_id", "prompt_sha256", "definition_digest")


def load(trial: Path) -> dict:
    trial = Path(trial).absolute()
    manifest = json.loads((trial / "manifest.json").read_text(encoding="utf-8"))
    entry = {"trial": str(trial), "trial_id": manifest.get("trial_id"),
             "arm": manifest.get("arm") or manifest.get("profile"), "model": manifest.get("model"),
             "profile": manifest.get("profile"), **{name: manifest.get(name) for name in FIELDS},
             "state": "ungraded", "passed": False, "scope_violations": []}
    folder = trial / "grades"
    reports = sorted(folder.glob("*.json")) if folder.is_dir() else []
    grades = []
    for path in reports:
        grade = json.loads(path.read_text(encoding="utf-8"))
        if grade.get("kind") != "artifact_grade" or grade.get("trial_id") != manifest.get("trial_id"):
            raise ValueError("시행과 채점 보고서가 일치하지 않습니다.")
        grades.append(grade)
    if not grades:
        return entry
    grades.sort(key=lambda grade: grade.get("checked_at") or "")
    latest = grades[-1]
    for name in FIELDS:
        if latest.get(name) != manifest.get(name):
            raise ValueError("채점 보고서의 사례·요청·기준이 준비 기록과 다릅니다.")
    outcomes = {bool(grade.get("artifact_passed")) for grade in grades}
    if len(outcomes) > 1:
        # 엇갈린 결과 중 하나를 고르지 않습니다. 재현되지 않은 시행으로 표시합니다.
        entry.update(state="unstable", grades=len(grades))
        return entry
    entry.update(state="graded", passed=bool(latest.get("artifact_passed")), grades=len(grades),
                 scope_violations=latest.get("scope_violations") or [],
                 requires_human_review=bool(latest.get("requires_human_review")))
    return entry


def summarize(entries: list[dict]) -> list[dict]:
    arms = {}
    for entry in entries:
        arm = arms.setdefault((entry["arm"], entry["model"]),
                              {"arm": entry["arm"], "model": entry["model"], "trials": 0, "passed": 0,
                               "ungraded": 0, "unstable": 0, "human_review": 0, "scope_violation_trials": 0,
                               "cases": [], "profiles": []})
        arm["trials"] += 1
        arm["cases"].append(entry["case_id"])
        if entry["profile"] not in arm["profiles"]:
            arm["profiles"].append(entry["profile"])
        if entry["state"] == "ungraded":
            arm["ungraded"] += 1
        elif entry["state"] == "unstable":
            arm["unstable"] += 1
        else:
            arm["passed"] += int(entry["passed"])
            arm["human_review"] += int(entry.get("requires_human_review", False))
            arm["scope_violation_trials"] += int(bool(entry["scope_violations"]))
    for arm in arms.values():
        arm["cases"] = sorted(arm["cases"])
    return [arms[name] for name in sorted(arms, key=lambda name: (name[0], name[1] or ""))]


def blocking(entries: list[dict], arms: list[dict]) -> list[str]:
    reasons = []
    if len({(arm["arm"], arm["model"]) for arm in arms}) < 2:
        reasons.append("single_arm")
    if len({entry["definition_digest"] for entry in entries}) > 1:
        reasons.append("definition_digest")
    prompts = {}
    for entry in entries:
        if prompts.setdefault(entry["case_id"], entry["prompt_sha256"]) != entry["prompt_sha256"]:
            reasons.append("prompt_sha256")
            break
    coverage = {tuple(arm["cases"]) for arm in arms}
    if len(coverage) > 1:
        reasons.append("case_coverage")
    if any(arm["ungraded"] for arm in arms):
        reasons.append("ungraded")
    if any(arm["unstable"] for arm in arms):
        reasons.append("unstable_grades")
    return reasons


def compare(trials: list[Path]) -> dict:
    if not trials:
        raise ValueError("비교할 시행 폴더가 필요합니다.")
    entries = [load(Path(trial)) for trial in trials]
    if len({entry["trial"] for entry in entries}) != len(entries):
        raise ValueError("같은 시행 폴더를 두 번 지정했습니다.")
    arms = summarize(entries)
    reasons = blocking(entries, arms)
    return {"kind": "harness_comparison", "schema_version": 1, "comparable": not reasons,
            "blocking_reasons": reasons, "arms": arms, "trials": entries,
            "labels_are_self_declared": True, "model_performance_claim": False,
            "note": ("같은 사례·요청·채점 기준을 공유할 때만 comparable이 참입니다. "
                     "실행 하네스·모델·사용량은 사용자가 선언한 라벨이며 이 보고서가 확인하지 않습니다.")}
```
