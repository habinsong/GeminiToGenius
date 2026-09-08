"""파일을 다시 검사하지 않고 저장된 작업 후보를 읽기 전용으로 찾습니다."""

from contextlib import closing
from collections import Counter
import json
from pathlib import Path
import sqlite3

from .spec import sensitive, validate
from .checkpoints import normalize as normalize_checkpoint


def saved_tasks(db: sqlite3.Connection, workspace: Path, limit: int = 10, offset: int = 0) -> dict:
    if type(limit) is not int or not 1 <= limit <= 50 or type(offset) is not int or offset < 0:
        raise ValueError("작업 목록 범위가 올바르지 않습니다.")
    tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if not {"tasks", "runs", "checkpoints"} <= tables:
        raise ValueError("GTG 작업 상태 데이터베이스가 아닙니다.")
    total = db.execute("SELECT count(*) FROM tasks WHERE workspace=?", (str(workspace),)).fetchone()[0]
    rows = db.execute("""SELECT t.id, t.spec, t.created,
        max(t.created,
            coalesce((SELECT max(coalesce(finished, started)) FROM runs WHERE task_id=t.id), t.created),
            coalesce((SELECT max(created) FROM checkpoints WHERE task_id=t.id), t.created)) AS activity
        FROM tasks t WHERE workspace=? ORDER BY activity DESC, t.id DESC LIMIT ? OFFSET ?""",
                      (str(workspace), limit, offset)).fetchall()
    tasks = []
    for row in rows:
        spec = validate(json.loads(row["spec"]))
        latest = {}
        for run in db.execute("""SELECT check_id, finished, result FROM runs WHERE id IN
                (SELECT max(id) FROM runs WHERE task_id=? GROUP BY check_id)""", (row["id"],)):
            result = json.loads(run["result"]) if run["result"] else {}
            if not isinstance(result, dict) or not isinstance(result.get("status", "unknown"), str):
                raise ValueError("저장된 검사 결과 형식이 올바르지 않습니다.")
            latest[run["check_id"]] = "running" if run["finished"] is None else result.get("status", "unknown")
        note = db.execute("SELECT note FROM checkpoints WHERE task_id=? ORDER BY id DESC LIMIT 1", (row["id"],)).fetchone()
        checkpoint = normalize_checkpoint(json.loads(note[0])) if note else None
        checkpoint_truncated = False
        if checkpoint:
            checkpoint_truncated = len(checkpoint["summary"]) > 320 or len(checkpoint["next_action"]) > 160
            checkpoint = {"summary": checkpoint["summary"][:320], "next_action": checkpoint["next_action"][:160]}
        links = []
        if "sessions" in tables:
            for link in db.execute("SELECT * FROM sessions WHERE task_id=? ORDER BY paused, key LIMIT 21", (row["id"],)):
                data = dict(link)
                links.append({name: data.get(name) for name in ("key", "paused", "retries", "reason", "turn_open")})
        tasks.append({"task_id": row["id"], "goal": spec["goal"][:320], "goal_truncated": len(spec["goal"]) > 320,
                      "created_at": row["created"], "last_activity_at": row["activity"],
                      "checkpoint": checkpoint, "checkpoint_truncated": checkpoint_truncated,
                      "connections": links[:20], "connections_truncated": len(links) > 20,
                      "recorded_check_counts": dict(Counter(latest.get(check["id"], "pending") for check in spec["checks"]))})
    return {"workspace": str(workspace), "tasks": tasks, "total": total, "offset": offset,
            "next_offset": offset + len(tasks) if offset + len(tasks) < total else None,
            "current_files_checked": False, "content_trust": "saved_task_data"}


def discover(workspace: Path, state: Path, limit: int = 10, offset: int = 0) -> dict:
    if sensitive(workspace) or sensitive(state) or any(p.is_symlink() for p in [state, *state.parents]):
        raise ValueError("민감 경로나 심볼릭 링크에서 작업 상태를 찾지 않습니다.")
    if type(limit) is not int or not 1 <= limit <= 50 or type(offset) is not int or offset < 0:
        raise ValueError("작업 목록 범위가 올바르지 않습니다.")
    if not state.exists():
        return {"workspace": str(workspace), "state_path": str(state), "tasks": [], "total": 0,
                "offset": offset, "next_offset": None, "current_files_checked": False,
                "content_trust": "saved_task_data"}
    with closing(sqlite3.connect(state.as_uri() + "?mode=ro", uri=True)) as db:
        db.row_factory = sqlite3.Row
        db.execute("BEGIN")
        return {**saved_tasks(db, workspace, limit, offset), "state_path": str(state)}
