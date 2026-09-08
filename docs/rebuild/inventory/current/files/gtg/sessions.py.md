# `gtg/sessions.py`

- 형식: `100644`
- 바이트: 8730
- SHA-256: `d0622586f1fc6a0aa1ba3617be8282fed31cbe3fb545769e7020f547eb0c58b4`
- 인코딩: `utf-8`

```
"""호스트 세션과 로컬 작업을 연결하고 자동 재개의 상한을 관리합니다."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from .store import Store
from .platforms import PLATFORMS
from .runner import status
from .spec import validate


def key(platform: str, session_id: str) -> str:
    if platform not in PLATFORMS:
        raise ValueError("지원하지 않는 호스트입니다.")
    if not isinstance(session_id, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,128}", session_id):
        raise ValueError("호스트 세션 식별자가 올바르지 않습니다.")
    return hashlib.sha256(f"{platform}:{session_id}".encode()).hexdigest()


class Sessions:
    def __init__(self, store: Store):
        self.store = store
        self.db = store.connection
        self.db.execute("""CREATE TABLE IF NOT EXISTS sessions (
            key TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(id),
            paused INTEGER NOT NULL DEFAULT 0, retries INTEGER NOT NULL DEFAULT 0,
            last_event TEXT, reason TEXT NOT NULL DEFAULT '', last_stop TEXT, turn_open INTEGER DEFAULT 1
        )""")
        self.db.commit()
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            columns = {row[1] for row in self.db.execute("PRAGMA table_info(sessions)")}
            if "last_stop" not in columns:
                self.db.execute("ALTER TABLE sessions ADD COLUMN last_stop TEXT")
            if "turn_open" not in columns:
                self.db.execute("ALTER TABLE sessions ADD COLUMN turn_open INTEGER")

    def start(self, session_key: str, workspace: Path, spec: dict) -> str:
        spec = validate(spec)
        workspace = workspace.resolve(strict=True)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            existing = self.get(session_key)
            if existing:
                task = self.store.task(existing["task_id"])
                if task["workspace"] == str(workspace) and task["spec"] == spec:
                    self.db.commit()
                    return task["id"]
            task_id = self.store.create(workspace, spec)
            self.bind(session_key, task_id)
            self.db.commit()
            return task_id
        except BaseException:
            self.db.rollback()
            raise

    def bind(self, session_key: str, task_id: str):
        self.store.task(task_id)
        with self.db:
            existing = self.get(session_key)
            if (existing and existing["task_id"] != task_id and not existing["paused"]
                    and not status(self.store, existing["task_id"])["verified"]):
                raise ValueError("다른 활성 작업이 있습니다. 이전 작업을 명시적으로 해제하세요.")
            # 같은 작업에 대한 재시도는 기존 상한과 중단 상태를 유지합니다.
            self.db.execute("INSERT INTO sessions(key, task_id, turn_open) VALUES (?, ?, 1) ON CONFLICT(key) DO NOTHING",
                            (session_key, task_id))
            if existing and existing["task_id"] != task_id:
                self.db.execute("UPDATE sessions SET task_id=?, paused=0, retries=0, last_event=NULL, reason='', last_stop=NULL, turn_open=1 WHERE key=?",
                                (task_id, session_key))

    def attach(self, session_key: str, task_id: str, workspace: Path, previous_host_stopped: bool = False):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            task = self.store.task(task_id)
            if Path(task["workspace"]) != workspace.resolve(strict=True):
                raise ValueError("작업과 현재 작업공간이 다릅니다.")
            existing = self.get(session_key)
            if existing and existing["task_id"] == task_id and not existing["paused"]:
                self.db.commit()
                return
            relevant = {task_id, existing["task_id"]} if existing else {task_id}
            if any(self.db.execute("SELECT 1 FROM runs WHERE task_id=? AND finished IS NULL", (value,)).fetchone()
                   for value in relevant):
                raise ValueError("실행 중인 검사가 있습니다. 종료 또는 명시적 복구 뒤 연결하세요.")
            if (existing and existing["task_id"] != task_id and not existing["paused"]
                    and not status(self.store, existing["task_id"])["verified"]):
                raise ValueError("현재 세션에 다른 활성 작업이 있습니다.")
            others = self.db.execute("SELECT turn_open FROM sessions WHERE task_id=? AND key<>? AND paused=0",
                                     (task_id, session_key)).fetchall()
            if any(row["turn_open"] != 0 for row in others) and not previous_host_stopped:
                raise ValueError("이전 호스트의 종료가 확인되지 않았습니다. 실제 종료를 확인한 경우에만 --previous-host-stopped를 사용하세요.")
            self.db.execute("UPDATE sessions SET paused=1, reason='이 작업의 연결을 다른 세션으로 옮겼습니다.' WHERE task_id=? AND key<>? AND paused=0",
                            (task_id, session_key))
            if existing:
                last_stop = existing["last_stop"] if existing["task_id"] == task_id else None
                self.db.execute("UPDATE sessions SET task_id=?, paused=0, retries=0, last_event=NULL, reason='', last_stop=?, turn_open=1 WHERE key=?",
                                (task_id, last_stop, session_key))
            else:
                self.db.execute("INSERT INTO sessions(key, task_id, turn_open) VALUES (?, ?, 1)", (session_key, task_id))
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise

    def get(self, session_key: str) -> dict | None:
        row = self.db.execute("SELECT * FROM sessions WHERE key=?", (session_key,)).fetchone()
        return dict(row) if row else None

    def for_task(self, task_id: str) -> list[dict]:
        rows = self.db.execute("SELECT key, paused, retries, reason, last_stop, turn_open FROM sessions WHERE task_id=? ORDER BY key", (task_id,))
        return [{**dict(row), "last_stop": json.loads(row["last_stop"]) if row["last_stop"] else None} for row in rows]

    def observe_stop(self, session_key: str, details: dict, event_id: str | None = None):
        turn_open = int(details.get("fully_idle") is False) if details["event"] == "Stop" else 0
        with self.db:
            cursor = self.db.execute("""UPDATE sessions SET last_stop=?, turn_open=
                CASE WHEN last_event=? AND turn_open=1 AND paused=0 THEN 1 ELSE ? END WHERE key=?""",
                                     (json.dumps(details), event_id, turn_open, session_key))
            if cursor.rowcount != 1:
                raise ValueError("연결된 작업이 없습니다.")

    def observe_start(self, session_key: str):
        with self.db:
            self.db.execute("UPDATE sessions SET turn_open=1 WHERE key=?", (session_key,))

    def pause(self, session_key: str, reason: str):
        if not reason.strip():
            raise ValueError("중단 이유가 필요합니다.")
        with self.db:
            cursor = self.db.execute("UPDATE sessions SET paused=1, reason=? WHERE key=?", (reason[:500], session_key))
            if cursor.rowcount != 1:
                raise ValueError("연결된 작업이 없습니다.")

    def resume(self, session_key: str):
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            existing = self.get(session_key)
            if existing is None:
                raise ValueError("연결된 작업이 없습니다.")
            if not existing["paused"]:
                return
            if self.db.execute("SELECT 1 FROM sessions WHERE task_id=? AND key<>? AND paused=0",
                               (existing["task_id"], session_key)).fetchone():
                raise ValueError("다른 세션에 연결된 작업입니다. 현재 연결을 확인한 뒤 attach로 선택하세요.")
            self.db.execute("UPDATE sessions SET paused=0, retries=0, last_event=NULL, reason='', turn_open=1 WHERE key=?", (session_key,))

    def nudge(self, session_key: str, event_id: str) -> bool:
        # 중복 이벤트와 동시에 도착한 종료 요청도 한 번만 처리합니다.
        with self.db:
            cursor = self.db.execute("""UPDATE sessions SET retries=retries+1, last_event=?, turn_open=1
                WHERE key=? AND paused=0 AND retries<2 AND (last_event IS NULL OR last_event<>?)""",
                                     (event_id, session_key, event_id))
            return cursor.rowcount == 1
```
