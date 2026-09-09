# `gtg/runner.py`

- 형식: `100644`
- 바이트: 6600
- SHA-256: `1180c0835e96ba8ce91b67c4b3c97fcacfcd4c4a7ae4c20ed46e39f6f01f749e`
- 인코딩: `utf-8`

```
"""등록된 명령을 직접 실행하여 현재 파일 상태에 대한 증거를 만듭니다."""

from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from .coverage import collector, executed_watch
from .spec import fingerprint
from .store import Store
from .checkpoints import latest as latest_checkpoint


class CommandCancelled(KeyboardInterrupt):
    def __init__(self, signum: int):
        self.signum = signum
        super().__init__(f"signal {signum}")


@contextmanager
def cancellation_signals():
    """자체 CLI의 검증 실행에만 설치하며 호출자의 신호 처리를 복원합니다."""
    def cancel(signum, frame):
        raise CommandCancelled(signum)

    previous = signal.signal(signal.SIGTERM, cancel)
    try:
        yield
    finally:
        signal.signal(signal.SIGTERM, previous)


def group_alive(process: subprocess.Popen) -> bool:
    if os.name != "posix":
        return process.poll() is None
    try:
        os.killpg(process.pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # 재사용된 PID가 다른 사용자의 프로세스를 가리킵니다. 우리가 만든 그룹이 아닙니다.
        return False
    return True


def terminate(process: subprocess.Popen):
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            # 남의 프로세스 그룹은 종료하지 않습니다.
            pass
    else:
        process.kill()
    process.wait()


def execute(store: Store, task_id: str, check_id: str) -> dict:
    task = store.task(task_id)
    checks = {check["id"]: check for check in task["spec"]["checks"]}
    if check_id not in checks:
        raise ValueError("등록되지 않은 검사입니다.")
    check = checks[check_id]
    workspace = Path(task["workspace"])
    before = fingerprint(workspace, check["watch"])
    run_id = store.begin(task_id, check_id)
    started = time.monotonic()
    process = None
    result = {"status": "error", "returncode": None, "before": before, "after": None,
              "coverage_observed": False, "executed_watch": None, "unexecuted_watch": None,
              "unobservable_watch": None}
    try:
        with collector() as session:
            # 출력은 호스트에 바로 전달하며 상태 DB에 원문을 보관하지 않습니다.
            process = subprocess.Popen(check["argv"], cwd=workspace, stdin=subprocess.DEVNULL,
                                       stdout=sys.stderr, stderr=sys.stderr, env=session.environment(),
                                       start_new_session=os.name == "posix",
                                       # 실행 잠금을 물려줍니다. 소유자가 죽어도 검사가 살아 있으면 드러납니다.
                                       pass_fds=store.inherited(run_id))
            store.attach_process(run_id, process.pid)
            try:
                code = process.wait(timeout=check.get("timeout_seconds", 120))
            except subprocess.TimeoutExpired:
                terminate(process)
                result.update(status="timeout", returncode=process.returncode)
            else:
                result.update(status="passed" if code == 0 else "failed", returncode=code)
                if code == 0 and group_alive(process):
                    result["status"] = "background_processes"
            after = fingerprint(workspace, check["watch"])
            result["after"] = after
            if result["status"] == "passed" and before != after:
                result["status"] = "changed_during_check"
            # Python 실행을 하나도 관찰하지 못하면 미실행을 주장하지 않습니다.
            if session.observed():
                ran, missed, opaque = executed_watch(workspace, check["watch"], session.files())
                result.update(coverage_observed=True, executed_watch=ran, unexecuted_watch=missed,
                              unobservable_watch=opaque)
    except KeyboardInterrupt:
        if process is not None:
            terminate(process)
        result["status"] = "interrupted"
        raise
    except (OSError, ValueError) as error:
        result.update(status="error", error_type=type(error).__name__)
    finally:
        if process is not None and group_alive(process):
            terminate(process)
        result["duration_seconds"] = round(time.monotonic() - started, 6)
        store.finish(run_id, result)
    return result


def status(store: Store, task_id: str) -> dict:
    task = store.task(task_id)
    latest = store.latest(task_id)
    checks = []
    # 이 조회 안에서만 공유합니다. 다음 조회는 실제 내용을 다시 읽습니다.
    fingerprints = {}
    for check in task["spec"]["checks"]:
        run = latest.get(check["id"])
        state = "pending"
        if run:
            state = "running" if run["running"] else run["result"]["status"]
            if state == "passed":
                watched = tuple(sorted(set(check["watch"])))
                if watched not in fingerprints:
                    try:
                        fingerprints[watched] = fingerprint(Path(task["workspace"]), list(watched))
                    except (OSError, ValueError):
                        fingerprints[watched] = None
                if fingerprints[watched] is None or fingerprints[watched] != run["result"].get("after"):
                    state = "stale"
        # 통과한 검사에 대해서만 실행 관찰 결과를 전달합니다. 실패·미실행은 범위를 주장하지 않습니다.
        outcome = (run or {}).get("result") or {}
        passed = state == "passed"
        checks.append({"id": check["id"], "criterion": check["criterion"], "status": state,
                       "executed_watch": outcome.get("executed_watch") if passed else None,
                       "unexecuted_watch": outcome.get("unexecuted_watch") if passed else None,
                       # 미실행 목록이 없을 때 그 이유를 밝힙니다. 범위를 좁히면 다시 얻을 수 있습니다.
                       "unobservable_watch": outcome.get("unobservable_watch") if passed else None})
    return {"task_id": task_id, "goal": task["spec"]["goal"], "spec": task["spec"],
            "verified": all(check["status"] == "passed" for check in checks), "checks": checks,
            "checkpoint": latest_checkpoint(store, task_id)}
```
