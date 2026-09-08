"""재개 평가에 필요한 부분 완료 상태를 실제 검사로 준비합니다."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from .workspace import digest, private


def seed_progress(workspace: Path, filename: str) -> dict:
    from gtg.checkpoints import record
    from gtg.runner import execute
    from gtg.sessions import Sessions, key
    from gtg.store import Store

    relative = Path(filename)
    if relative.is_absolute() or ".." in relative.parts or private(relative):
        raise ValueError("진행 상태 입력은 시험 폴더 내부 파일이어야 합니다.")
    data = json.loads((workspace / relative).read_text(encoding="utf-8"))
    store = Store(workspace / ".gtg/state.sqlite3")
    try:
        sessions = Sessions(store)
        session = key("antigravity", "fixture-prior-session")
        task = sessions.start(session, workspace, data["spec"])
        for check_id in data["completed_checks"]:
            if execute(store, task, check_id)["status"] != "passed":
                raise ValueError("사전 완료 검사에 실제로 통과하지 못했습니다.")
        record(store, task, data["checkpoint"])
        sessions.pause(session, "다음 세션에서 남은 작업을 이어갑니다.")
        expected = digest(workspace / "README.md")
        command = "from pathlib import Path; import hashlib; assert hashlib.sha256(Path('README.md').read_bytes()).hexdigest() == " + repr(expected)
        completed = store.create(workspace, {"schema_version": 1, "goal": "문서 원문 보존 확인", "checks": [{
            "id": "document", "criterion": "검증 문서의 원문이 유지됩니다.",
            "argv": [sys.executable, "-B", "-c", command], "watch": ["README.md"]}]})
        if execute(store, completed, "document")["status"] != "passed":
            raise ValueError("완료된 비교 작업을 준비하지 못했습니다.")
        return {"task_id": task, "previous_session_key": session, "completed_task_id": completed,
                "completed_checks": data["completed_checks"], "created_by_fixture": True}
    finally:
        store.close()
