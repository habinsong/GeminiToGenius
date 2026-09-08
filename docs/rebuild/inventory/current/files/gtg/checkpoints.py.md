# `gtg/checkpoints.py`

- 형식: `100644`
- 바이트: 2771
- SHA-256: `891a3ce8ee3674e82e3004aaba0c22a31440f6b7c918ab85dbf283bf3eff46a7`
- 인코딩: `utf-8`

```
"""재개용 작업 메모를 검증 결과와 분리해 보존합니다."""

from __future__ import annotations

import json
from pathlib import Path
import time

from .spec import fingerprint, relative
from .store import Store


def normalize(note: dict) -> dict:
    if not isinstance(note, dict) or set(note) - {"summary", "next_action", "files"}:
        raise ValueError("작업 메모는 summary, next_action, files 필드만 사용합니다.")
    for name, limit in (("summary", 2048), ("next_action", 512)):
        if not isinstance(note.get(name), str) or not note[name].strip() or len(note[name]) > limit:
            raise ValueError(f"{name}은 비어 있지 않은 {limit}자 이하 문자열이어야 합니다.")
    files = note.get("files", [])
    if not isinstance(files, list) or len(files) > 64:
        raise ValueError("작업 메모의 기준 경로는 64개 이하여야 합니다.")
    paths = sorted({relative(name).as_posix() for name in files})
    return {"summary": note["summary"].strip(), "next_action": note["next_action"].strip(), "files": paths}


def record(store: Store, task_id: str, note: dict) -> int:
    task = store.task(task_id)
    note = normalize(note)
    digest = fingerprint(Path(task["workspace"]), note["files"]) if note["files"] else None
    encoded = json.dumps(note, ensure_ascii=False, sort_keys=True)
    store.connection.execute("BEGIN IMMEDIATE")
    try:
        latest = store.connection.execute("SELECT id, note, fingerprint FROM checkpoints WHERE task_id=? ORDER BY id DESC LIMIT 1",
                                          (task_id,)).fetchone()
        if latest and latest["note"] == encoded and latest["fingerprint"] == digest:
            store.connection.commit()
            return latest["id"]
        cursor = store.connection.execute("INSERT INTO checkpoints(task_id,note,fingerprint,created) VALUES (?,?,?,?)",
                                          (task_id, encoded, digest, time.time()))
        store.connection.commit()
        return cursor.lastrowid
    except BaseException:
        store.connection.rollback()
        raise


def latest(store: Store, task_id: str) -> dict | None:
    row = store.connection.execute("SELECT * FROM checkpoints WHERE task_id=? ORDER BY id DESC LIMIT 1", (task_id,)).fetchone()
    if row is None:
        return None
    note = normalize(json.loads(row["note"]))
    unchanged = None
    if note["files"]:
        try:
            unchanged = fingerprint(Path(store.task(task_id)["workspace"]), note["files"]) == row["fingerprint"]
        except (OSError, ValueError):
            unchanged = False
    return {"id": row["id"], **note, "recorded_at": row["created"], "files_unchanged": unchanged,
            "is_verification_evidence": False}
```
