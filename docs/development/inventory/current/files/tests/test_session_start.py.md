# `tests/test_session_start.py`

- 형식: `100644`
- 바이트: 4328
- SHA-256: `c069bd350e175bc396442eebe6810275ec36c60fb97c0669933fae779f4fbba2`
- 인코딩: `utf-8`

```
"""응답 유실 뒤 재시도해도 작업을 중복 생성하거나 중단을 해제하지 않습니다."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gtg.sessions import Sessions, key
from gtg.store import Store


ROOT = Path(__file__).resolve().parents[1]


class SessionStartTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.state = self.root / ".gtg/state.sqlite3"
        self.spec = {"schema_version": 1, "goal": "재시도되는 작업", "checks": [{
            "id": "check", "criterion": "현재 파일을 검증합니다.", "watch": ["value.txt"],
            "argv": [sys.executable, "-c", "pass"]}]}
        (self.root / "value.txt").write_text("value")
        (self.root / "task.json").write_text(json.dumps(self.spec))
        self.command = [sys.executable, "-m", "gtg", "--state", str(self.state), "start",
                        "--workspace", str(self.root), "--spec", str(self.root / "task.json"),
                        "--platform", "antigravity", "--session", "retry-session"]

    def run_start(self):
        return subprocess.run(self.command, cwd=ROOT, capture_output=True, text=True)

    def test_identical_start_is_idempotent(self):
        first, second = self.run_start(), self.run_start()
        self.assertEqual(first.returncode, 0, first.stdout)
        self.assertEqual(second.returncode, 0, second.stdout)
        self.assertEqual(json.loads(first.stdout)["task_id"], json.loads(second.stdout)["task_id"])
        store = Store(self.state)
        self.addCleanup(store.close)
        self.assertEqual(store.connection.execute("SELECT count(*) FROM tasks").fetchone()[0], 1)

    def test_conflicting_start_does_not_leave_an_orphan(self):
        self.assertEqual(self.run_start().returncode, 0)
        self.spec["goal"] = "다른 요청"
        (self.root / "task.json").write_text(json.dumps(self.spec))
        self.assertEqual(self.run_start().returncode, 1)
        store = Store(self.state)
        self.addCleanup(store.close)
        self.assertEqual(store.connection.execute("SELECT count(*) FROM tasks").fetchone()[0], 1)

    def test_retry_does_not_unpause_or_reset_budget(self):
        first = json.loads(self.run_start().stdout)
        store = Store(self.state)
        self.addCleanup(store.close)
        sessions = Sessions(store)
        session = key("antigravity", "retry-session")
        sessions.nudge(session, "one")
        sessions.pause(session, "사용자 중단")
        repeated = self.run_start()
        self.assertEqual(repeated.returncode, 0, repeated.stdout)
        self.assertEqual(json.loads(repeated.stdout)["task_id"], first["task_id"])
        self.assertTrue(sessions.get(session)["paused"])
        self.assertEqual(sessions.get(session)["retries"], 1)

    def test_simultaneous_identical_starts_share_one_task(self):
        processes = [subprocess.Popen(self.command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                     for _ in range(2)]
        try:
            outputs = [process.communicate(timeout=5) for process in processes]
            for process, (output, errors) in zip(processes, outputs):
                self.assertEqual(process.returncode, 0, output + errors)
            self.assertEqual(json.loads(outputs[0][0])["task_id"], json.loads(outputs[1][0])["task_id"])
            store = Store(self.state)
            self.addCleanup(store.close)
            self.assertEqual(store.connection.execute("SELECT count(*) FROM tasks").fetchone()[0], 1)
        finally:
            for process in processes:
                if process.poll() is None:
                    process.kill()
                process.wait()

    def test_resume_of_active_task_does_not_refill_retry_budget(self):
        self.run_start()
        store = Store(self.state)
        self.addCleanup(store.close)
        sessions = Sessions(store)
        session = key("antigravity", "retry-session")
        sessions.nudge(session, "one")
        sessions.resume(session)
        self.assertEqual(sessions.get(session)["retries"], 1)


if __name__ == "__main__":
    unittest.main()
```
