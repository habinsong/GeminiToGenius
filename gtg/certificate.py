"""완료 주장을 실행 증거에 묶고, 상태 DB 없이 다시 실행해 같은 결과가 나오는지 확인합니다.

증명서는 주장을 대신하지 않습니다. `replay`가 현재 파일에서 명령을 다시 실행한 결과만 근거입니다.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

from .runner import status
from .spec import relative, sensitive
from .store import Store

SCHEMA = 1
BODY = ("schema_version", "task_id", "goal", "workspace", "verified", "checks", "unverified_scope", "created")


def canonical(document: dict) -> bytes:
    body = {name: document[name] for name in BODY}
    return json.dumps(body, sort_keys=True, ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(document: dict) -> str:
    try:
        return hashlib.sha256(canonical(document)).hexdigest()
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("증명서 본문 형식이 올바르지 않습니다.") from error


def build(store: Store, task_id: str) -> dict:
    """현재 상태를 그대로 옮깁니다. 통과하지 않은 검사를 통과로 바꾸지 않습니다."""
    task = store.task(task_id)
    report = status(store, task_id)
    latest = store.latest(task_id)
    states = {check["id"]: check["status"] for check in report["checks"]}
    checks = []
    ran_anywhere, missed_anywhere = set(), set()
    for check in task["spec"]["checks"]:
        result = (latest.get(check["id"]) or {}).get("result") or {}
        state = states[check["id"]]
        passed = state == "passed"
        missed = result.get("unexecuted_watch") if passed else None
        if passed:
            ran_anywhere.update(result.get("executed_watch") or [])
            missed_anywhere.update(missed or [])
        checks.append({"id": check["id"], "criterion": check["criterion"], "argv": list(check["argv"]),
                       "watch": sorted(set(check["watch"])), "timeout_seconds": check.get("timeout_seconds", 120),
                       "status": state, "returncode": result.get("returncode"),
                       # 통과한 실행의 증거만 남깁니다. 실패·미실행에는 지문을 붙이지 않습니다.
                       "evidence_fingerprint": result.get("after") if passed else None,
                       "coverage_observed": bool(result.get("coverage_observed")) if passed else False,
                       "unexecuted_watch": missed})
    document = {"schema_version": SCHEMA, "task_id": task_id, "goal": task["spec"]["goal"],
                "workspace": task["workspace"], "verified": report["verified"], "checks": checks,
                # 어떤 검사도 실행하지 않은 검증 대상입니다. 이 증명서가 확인하지 못한 범위입니다.
                "unverified_scope": sorted(missed_anywhere - ran_anywhere),
                "created": round(time.time(), 3)}
    return {**document, "digest": digest(document)}


def validated(document: dict) -> list[dict]:
    if not isinstance(document, dict) or document.get("schema_version") != SCHEMA:
        raise ValueError("schema_version 1 증명서가 필요합니다.")
    if digest(document) != document.get("digest"):
        raise ValueError("증명서 본문과 digest가 일치하지 않습니다.")
    checks = document["checks"]
    if not isinstance(checks, list) or not checks:
        raise ValueError("증명서에 검사가 없습니다.")
    for check in checks:
        argv = check.get("argv")
        if not isinstance(argv, list) or not argv or any(not isinstance(arg, str) or "\0" in arg for arg in argv):
            raise ValueError("증명서의 검증 명령이 올바르지 않습니다.")
        if any(sensitive(Path(arg)) for arg in argv):
            raise ValueError("민감 경로를 포함한 명령은 재실행하지 않습니다.")
        for name in check.get("watch") or []:
            relative(name)
    return checks


def run(check: dict, workspace: Path) -> dict:
    from .spec import fingerprint

    outcome = {"id": check["id"], "criterion": check["criterion"], "reconstructed": False, "reason": None,
               "returncode": None, "fingerprint": None}
    try:
        process = subprocess.run(check["argv"], cwd=workspace, stdin=subprocess.DEVNULL,
                                 capture_output=True, timeout=check.get("timeout_seconds", 120),
                                 env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    except subprocess.TimeoutExpired:
        outcome["reason"] = "timeout"
        return outcome
    except (OSError, ValueError):
        outcome["reason"] = "error"
        return outcome
    outcome["returncode"] = process.returncode
    if process.returncode != 0:
        outcome["reason"] = "returncode"
        return outcome
    try:
        outcome["fingerprint"] = fingerprint(workspace, list(check["watch"]))
    except (OSError, ValueError):
        outcome["reason"] = "error"
        return outcome
    if check.get("evidence_fingerprint") != outcome["fingerprint"]:
        outcome["reason"] = "fingerprint"
        return outcome
    outcome["reconstructed"] = True
    return outcome


def replay(document: dict, workspace: Path, *, trust_commands: bool = False) -> dict:
    """증명서만 읽어 다시 실행합니다. 상태 DB를 읽지도 만들지도 않습니다."""
    checks = validated(document)
    workspace = Path(workspace).resolve(strict=True)
    if not workspace.is_dir():
        raise ValueError("작업공간 폴더가 필요합니다.")
    matches = str(workspace) == document["workspace"]
    if not matches and not trust_commands:
        raise ValueError("증명서에 기록된 작업공간과 다릅니다. 명령을 신뢰할 때만 --trust-commands로 실행하세요.")
    outcomes = [run(check, workspace) for check in checks]
    return {"task_id": document["task_id"], "goal": document["goal"], "workspace": str(workspace),
            "workspace_matches": matches, "claimed_verified": bool(document["verified"]),
            "reconstructed": bool(document["verified"]) and all(item["reconstructed"] for item in outcomes),
            # 재현에 성공해도 이 목록의 파일은 어떤 검사도 실행하지 않았습니다.
            "unverified_scope": list(document.get("unverified_scope") or []),
            "checks": outcomes}
