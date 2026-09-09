# `gtg/store.py`

- 형식: `100644`
- 바이트: 9855
- SHA-256: `9403bec019e32b1e2ebb481acb635ac48e0be3d596481dffc1175d674c2a0b37`
- 인코딩: `utf-8`

```
"""검증 실행의 시작과 종료를 SQLite 트랜잭션으로 기록합니다.

실행 중인지 여부는 PID가 아니라 실행하는 동안만 유지되는 파일 잠금으로 판단합니다.
PID는 재부팅과 재사용으로 다른 프로세스를 가리키므로 신원이 되지 못합니다.
"""

from __future__ import annotations

from contextlib import nullcontext
import json
import os
from pathlib import Path
import socket
import sqlite3
import time
import uuid

try:
    import fcntl
except ImportError:  # 윈도우에는 없습니다. 이때는 PID 판단으로 물러납니다.
    fcntl = None

from .spec import evidential, task_scope, validate


def lock_path(state: Path, run_id: int) -> Path:
    return state.parent / "runs" / f"{run_id}.lock"


def hold(path: Path) -> int | None:
    """실행하는 동안만 유지되는 잠금을 잡습니다. 잠글 수 없으면 None입니다."""
    if fcntl is None:
        return None
    try:
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        descriptor = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    except OSError:
        return None
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        os.close(descriptor)
        return None
    return descriptor


def running(path: Path) -> bool | None:
    """잠금을 붙잡은 프로세스가 남아 있는지 봅니다. 판단할 수 없으면 None입니다."""
    if fcntl is None or not path.exists():
        return None
    try:
        descriptor = os.open(path, os.O_RDWR)
    except OSError:
        return None
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        # 소유 프로세스나 잠금을 물려받은 검사 프로세스가 아직 살아 있습니다.
        return True
    except OSError:
        return None
    else:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        return False
    finally:
        os.close(descriptor)


def pid_alive(pid: int) -> bool:
    """잠금 기록이 없는 예전 실행에만 씁니다. PID만으로는 신원을 확인하지 못합니다."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # 다른 사용자의 프로세스입니다. 이 상태 파일을 만든 검사는 여기에 해당하지 않습니다.
        return False
    return True


class Store:
    def __init__(self, path: Path):
        self.path = path = path.absolute()
        self.locks: dict[int, int] = {}
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
        for run_id in list(self.locks):
            self.release(run_id)
        self.connection.close()

    def release(self, run_id: int):
        descriptor = self.locks.pop(run_id, None)
        if descriptor is not None:
            os.close(descriptor)
        # 끝난 실행의 잠금 파일만 지웁니다. 파일을 지워도 남은 프로세스가 쥔 잠금은 유지됩니다.
        lock_path(self.path, run_id).unlink(missing_ok=True)

    def inherited(self, run_id: int) -> tuple[int, ...]:
        """검사 프로세스에 물려줄 잠금 파일입니다. 소유자보다 오래 살아도 실행 중으로 드러납니다."""
        descriptor = self.locks.get(run_id)
        return () if descriptor is None else (descriptor,)

    def create(self, workspace: Path, spec: dict) -> str:
        spec = evidential(validate(spec))
        workspace = workspace.resolve(strict=True)
        if not workspace.is_dir():
            raise ValueError("작업공간 폴더가 필요합니다.")
        # 훅 예산 안에서 상태를 만들 수 있는지 작업 전체 기준으로 확인합니다.
        task_scope(workspace, spec["checks"])
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
                run_id = cursor.lastrowid
            descriptor = hold(lock_path(self.path, run_id))
            if descriptor is not None:
                self.locks[run_id] = descriptor
            return run_id
        except sqlite3.IntegrityError as error:
            raise ValueError("이미 실행 중인 검사가 있습니다. 완료되거나 중단 복구가 필요합니다.") from error

    def finish(self, run_id: int, result: dict):
        with self.connection:
            cursor = self.connection.execute("UPDATE runs SET finished = ?, result = ? WHERE id = ? AND finished IS NULL",
                                             (time.time(), json.dumps(result), run_id))
            if cursor.rowcount != 1:
                raise ValueError("이미 종료되었거나 존재하지 않는 실행입니다.")
        self.release(run_id)

    def attach_process(self, run_id: int, pid: int):
        with self.connection:
            self.connection.execute("UPDATE runs SET child_pid=? WHERE id=? AND finished IS NULL", (pid, run_id))

    def latest(self, task_id: str) -> dict:
        self.task(task_id)
        rows = self.connection.execute("SELECT * FROM runs WHERE task_id = ? ORDER BY id", (task_id,))
        return {row["check_id"]: {"run_id": row["id"], "running": row["finished"] is None,
                                  "result": json.loads(row["result"]) if row["result"] else None}
                for row in rows}

    def alive(self, row: sqlite3.Row) -> bool:
        """검사를 붙잡은 프로세스가 남아 있는지 확인합니다.

        잠금은 비정상 종료와 재부팅에서 OS가 풀어 주므로 소유자·하위 프로세스를 함께 덮습니다.
        잠금 기록이 없는 예전 실행에만 PID로 물러납니다.
        """
        held = running(lock_path(self.path, row["id"]))
        if held is not None:
            return held
        return any(pid_alive(pid) for pid in (row["owner_pid"], row["child_pid"]) if pid is not None)

    def recover(self, task_id: str) -> int:
        self.task(task_id)
        rows = self.connection.execute("SELECT * FROM runs WHERE task_id = ? AND finished IS NULL", (task_id,)).fetchall()
        recovered = 0
        for row in rows:
            if row["host"] != socket.gethostname():
                raise ValueError("다른 호스트에서 시작된 검사는 여기서 복구할 수 없습니다.")
            if self.alive(row):
                raise ValueError("검사 프로세스가 아직 살아 있어 복구하지 않습니다. "
                                 "남은 하위 프로세스를 끝낸 뒤 다시 시도하세요.")
            self.finish(row["id"], {"status": "interrupted", "returncode": None})
            recovered += 1
        return recovered
```
