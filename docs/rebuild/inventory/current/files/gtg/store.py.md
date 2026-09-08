# `gtg/store.py`

- 형식: `100644`
- 바이트: 6372
- SHA-256: `1d221b9db4143dc42d276fa23112122a4cf8562a4510ac12a11416fde628ac6a`
- 인코딩: `utf-8`

```
"""검증 실행의 시작과 종료를 SQLite 트랜잭션으로 기록합니다."""

from __future__ import annotations

from contextlib import nullcontext
import json
import os
from pathlib import Path
import socket
import sqlite3
import time
import uuid

from .spec import evidential, validate


class Store:
    def __init__(self, path: Path):
        path = path.absolute()
        if any(p.is_symlink() for p in [path, *path.parents]):
            raise ValueError("상태 저장 경로에 심볼릭 링크를 사용할 수 없습니다.")
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        ignore = path.parent / ".gitignore"
        # 상태 폴더가 사용자 저장소의 추적 목록에 나타나지 않게 합니다. 사용자 파일은 덮어쓰지 않습니다.
        if path.parent.name == ".gtg" and not ignore.exists() and not ignore.is_symlink():
            ignore.write_text("*\n", encoding="utf-8")
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            pass
        else:
            os.close(descriptor)
        self.connection = sqlite3.connect(path, timeout=5)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY, workspace TEXT NOT NULL, spec TEXT NOT NULL,
                created REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(id),
                check_id TEXT NOT NULL, started REAL NOT NULL, finished REAL,
                owner_pid INTEGER NOT NULL, host TEXT NOT NULL, result TEXT, child_pid INTEGER
            );
            CREATE UNIQUE INDEX IF NOT EXISTS one_running_per_task
                ON runs(task_id) WHERE finished IS NULL;
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(id),
                note TEXT NOT NULL, fingerprint TEXT, created REAL NOT NULL
            );
        """)
        columns = {row[1] for row in self.connection.execute("PRAGMA table_info(runs)")}
        if "child_pid" not in columns:
            self.connection.execute("ALTER TABLE runs ADD COLUMN child_pid INTEGER")
            self.connection.commit()

    def close(self):
        self.connection.close()

    def create(self, workspace: Path, spec: dict) -> str:
        spec = evidential(validate(spec))
        workspace = workspace.resolve(strict=True)
        if not workspace.is_dir():
            raise ValueError("작업공간 폴더가 필요합니다.")
        task_id = uuid.uuid4().hex
        with nullcontext() if self.connection.in_transaction else self.connection:
            self.connection.execute("INSERT INTO tasks VALUES (?, ?, ?, ?)",
                                    (task_id, str(workspace), json.dumps(spec, ensure_ascii=False), time.time()))
        return task_id

    def task(self, task_id: str) -> dict:
        row = self.connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise ValueError("작업을 찾을 수 없습니다.")
        return {"id": row["id"], "workspace": row["workspace"], "spec": validate(json.loads(row["spec"]))}

    def begin(self, task_id: str, check_id: str) -> int:
        task = self.task(task_id)
        if check_id not in {check["id"] for check in task["spec"]["checks"]}:
            raise ValueError("작업에 등록되지 않은 검사입니다.")
        try:
            with self.connection:
                cursor = self.connection.execute(
                    "INSERT INTO runs(task_id, check_id, started, owner_pid, host) VALUES (?, ?, ?, ?, ?)",
                    (task_id, check_id, time.time(), os.getpid(), socket.gethostname()))
                return cursor.lastrowid
        except sqlite3.IntegrityError as error:
            raise ValueError("이미 실행 중인 검사가 있습니다. 완료되거나 중단 복구가 필요합니다.") from error

    def finish(self, run_id: int, result: dict):
        with self.connection:
            cursor = self.connection.execute("UPDATE runs SET finished = ?, result = ? WHERE id = ? AND finished IS NULL",
                                             (time.time(), json.dumps(result), run_id))
            if cursor.rowcount != 1:
                raise ValueError("이미 종료되었거나 존재하지 않는 실행입니다.")

    def attach_process(self, run_id: int, pid: int):
        with self.connection:
            self.connection.execute("UPDATE runs SET child_pid=? WHERE id=? AND finished IS NULL", (pid, run_id))

    def latest(self, task_id: str) -> dict:
        self.task(task_id)
        rows = self.connection.execute("SELECT * FROM runs WHERE task_id = ? ORDER BY id", (task_id,))
        return {row["check_id"]: {"run_id": row["id"], "running": row["finished"] is None,
                                  "result": json.loads(row["result"]) if row["result"] else None}
                for row in rows}

    def recover(self, task_id: str) -> int:
        self.task(task_id)
        rows = self.connection.execute("SELECT * FROM runs WHERE task_id = ? AND finished IS NULL", (task_id,)).fetchall()
        recovered = 0
        for row in rows:
            if row["host"] != socket.gethostname():
                raise ValueError("다른 호스트에서 시작된 검사는 여기서 복구할 수 없습니다.")
            try:
                os.kill(row["owner_pid"], 0)
            except ProcessLookupError:
                if row["child_pid"] is not None:
                    try:
                        os.kill(row["child_pid"], 0)
                    except ProcessLookupError:
                        pass
                    else:
                        raise ValueError("검사 하위 프로세스가 아직 살아 있어 복구하지 않습니다.")
                self.finish(row["id"], {"status": "interrupted", "returncode": None})
                recovered += 1
            else:
                raise ValueError("검사 소유 프로세스가 살아 있어 복구하지 않습니다.")
        return recovered
```
