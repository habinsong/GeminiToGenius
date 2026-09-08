# `docs/rebuild/validation/2026-09-08-native-stop-recheck/capture_state.py`

- 형식: `100644`
- 바이트: 2954
- SHA-256: `32a5a3768f21824ddfef768214d0ea0d03bba1b511860adf7b04e7eb448296b0`
- 인코딩: `utf-8`

```
"""지정한 시험 세션의 상태 변화를 읽기 전용으로 짧게 관측합니다."""

import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time


def observe(state, session):
    with closing(sqlite3.connect(state.as_uri() + "?mode=ro", uri=True, timeout=0.2)) as db:
        db.row_factory = sqlite3.Row
        db.execute("BEGIN")
        row = db.execute("SELECT task_id, paused, retries, last_event, reason, last_stop FROM sessions WHERE key=?",
                         (session,)).fetchone()
        if row is None:
            return {"state": "not_registered"}
        result = dict(row)
        result["last_stop"] = json.loads(row["last_stop"]) if row["last_stop"] else None
        runs = []
        for run in db.execute("SELECT check_id, finished, result FROM runs WHERE task_id=? ORDER BY id", (row["task_id"],)):
            value = json.loads(run["result"]) if run["result"] else {}
            runs.append({"check_id": run["check_id"], "finished": run["finished"],
                         "status": value.get("status", "running"), "returncode": value.get("returncode")})
        result["runs"] = runs
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--session", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    state = args.state.resolve(strict=True)
    session = hashlib.sha256(("antigravity:" + args.session).encode()).hexdigest()
    descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    deadline, previous = time.monotonic() + 180, None
    print(json.dumps({"observer_started": True, "pid": os.getpid(), "timeout_seconds": 180}), flush=True)
    with os.fdopen(descriptor, "w", encoding="utf-8") as output:
        while time.monotonic() < deadline:
            try:
                value = observe(state, session)
            except (sqlite3.Error, ValueError) as error:
                value = {"state": "read_error", "error_type": type(error).__name__}
            if value != previous:
                recorded = {"observed_at": time.time(), **value}
                text = json.dumps(recorded, ensure_ascii=False)
                output.write(text + "\n")
                output.flush()
                print(text, flush=True)
                previous = value
            stop = value.get("last_stop")
            passed = bool(value.get("runs")) and all(run["status"] == "passed" for run in value["runs"])
            if stop and (value.get("paused") or (passed and str(stop.get("execution_num")) != value.get("last_event"))):
                return 0
            time.sleep(1)
    print(json.dumps({"observation_timeout": True}), flush=True)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
```
