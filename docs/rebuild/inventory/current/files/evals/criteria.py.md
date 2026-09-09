# `evals/criteria.py`

- 형식: `100644`
- 바이트: 4138
- SHA-256: `8180267a54d9d4e79036345c5f6221d67b55dc3e0ee36a53161a3ce8358f184d`
- 인코딩: `utf-8`

```
"""산출물이 사례의 범위 조건을 지켰는지 판정합니다.

여기서는 후보 코드를 실행하지 않습니다. 준비 시점의 기준과 현재 파일, 그리고 실행 관측
기록만 봅니다. 기능 검사는 `grading`이 별도로 수행합니다.
"""

from __future__ import annotations

import ast
from pathlib import Path

from .workspace import git_state


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


def protected_violations(case: dict, baseline: dict, current: dict, changed: list[str]) -> list[str]:
    """허용하지 않은 변경입니다. 허용 목록이 비어 있으면 모든 변경이 위반입니다."""
    if not case["allowed_edits"]:
        return list(changed)
    protected = set(baseline) - set(case["allowed_edits"])
    violations = sorted(name for name in protected if current.get(name) != baseline.get(name))
    if "allowed_new_files" in case:
        violations.extend(sorted(set(current) - set(baseline) - set(case["allowed_new_files"])))
    return violations


def untouched_required(case: dict, baseline: dict, current: dict) -> list[str]:
    """동작이 그대로여야 하는 사례에서 무작업 통과를 막습니다."""
    return sorted(name for name in case.get("required_edits", [])
                  if current.get(name) == baseline.get(name))


def symbols_still_present(case: dict, workspace: Path) -> list[str] | None:
    """지워야 할 이름이 남아 있는지입니다. 읽지 못한 파일은 남아 있는 것으로 봅니다."""
    if not case.get("removed_symbols"):
        return None
    remaining = []
    for name, symbols in case["removed_symbols"].items():
        defined = defined_symbols(workspace / name)
        if defined is None:
            remaining.append(name)
            continue
        remaining.extend(f"{name}:{symbol}" for symbol in symbols if symbol in defined)
    return sorted(remaining)


def execution_observed(case: dict, manifest: dict) -> bool | None:
    """산출물이 그대로여야 하는 사례의 유일한 증거입니다. 관측이 없으면 None입니다."""
    if not case.get("requires_execution"):
        return None
    observation = manifest.get("runtime_observation")
    if not isinstance(observation, dict):
        return None
    return (observation.get("executed_workspace_file_count") or 0) > 0


def git_findings(manifest: dict, workspace: Path) -> tuple[bool | None, dict | None]:
    """사용자 변경을 보존해야 하는 사례에서 Git 상태를 비교합니다."""
    if manifest.get("git_baseline") is None:
        return None, None
    observed = git_state(workspace)
    return observed == manifest["git_baseline"], observed


def scope_findings(case: dict, manifest: dict, workspace: Path,
                   baseline: dict, current: dict) -> dict:
    """범위 판정에 필요한 사실을 한 번에 모읍니다."""
    changed = sorted(name for name in set(current) | set(baseline)
                     if current.get(name) != baseline.get(name))
    violations = protected_violations(case, baseline, current, changed)
    git_unchanged, observed_git = git_findings(manifest, workspace)
    if git_unchanged is False:
        violations = [*violations, ".git"]
    return {"changed": changed, "violations": violations,
            "untouched": untouched_required(case, baseline, current),
            "still_present": symbols_still_present(case, workspace),
            "executed": execution_observed(case, manifest),
            "git_unchanged": git_unchanged, "observed_git": observed_git}
```
