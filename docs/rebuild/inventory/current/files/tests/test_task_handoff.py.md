# `tests/test_task_handoff.py`

- 형식: `100644`
- 바이트: 12227
- SHA-256: `c02bc092e9be30433aba54d06a413be6a7215a20e3b86b55a2838cf7f3deaa19`
- 인코딩: `utf-8`

```
"""다른 세션에서도 기존 목표·검증·메모를 찾아 안전하게 연결합니다."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from gtg.checkpoints import record
from gtg.hooks import handle
from gtg.runner import execute
from gtg.sessions import Sessions, key
from gtg.store import Store
from gtg.discovery import discover


ROOT = Path(__file__).resolve().parents[1]


class TaskHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.path = self.root / ".gtg/state.sqlite3"
        for name, content in (("first", "ready"), ("second", "pending")):
            (self.root / (name + ".txt")).write_text(content)
        self.store = Store(self.path)
        self.addCleanup(self.store.close)
        self.sessions = Sessions(self.store)
        self.old = key("antigravity", "old-session")
        self.spec = {"schema_version": 1, "goal": "기존 두 단계를 모두 마칩니다.", "checks": [
            {"id": name, "criterion": name + " 단계가 준비됩니다.", "watch": [name + ".txt"],
             "argv": [sys.executable, "-c", f"from pathlib import Path; assert Path('{name}.txt').read_text() == 'ready'"]}
            for name in ("first", "second")]}
        self.task = self.sessions.start(self.old, self.root, self.spec)
        execute(self.store, self.task, "first")
        record(self.store, self.task, {"summary": "첫 단계 통과", "next_action": "second를 마칩니다.", "files": ["first.txt"]})
        self.sessions.pause(self.old, "다음 세션에서 이어갑니다.")

    def call(self, *args):
        return subprocess.run([sys.executable, "-m", "gtg", *args], cwd=ROOT, capture_output=True, text=True)

    def attach(self, session="new-session", *extra):
        return self.call("attach", self.task, "--workspace", str(self.root),
                         "--platform", "gemini-cli", "--session", session, *extra)

    def test_tasks_reads_saved_progress_without_creating_or_changing_state(self):
        before = hashlib.sha256(self.path.read_bytes()).hexdigest()
        result = self.call("tasks", "--workspace", str(self.root))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertFalse(data["current_files_checked"])
        self.assertEqual(data["tasks"][0]["task_id"], self.task)
        self.assertEqual(data["tasks"][0]["checkpoint"]["next_action"], "second를 마칩니다.")
        self.assertEqual(hashlib.sha256(self.path.read_bytes()).hexdigest(), before)
        empty = self.root / "empty"
        empty.mkdir()
        result = self.call("tasks", "--workspace", str(empty))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["tasks"], [])
        self.assertFalse((empty / ".gtg").exists())

    def test_attach_preserves_task_evidence_checkpoint_and_retries_on_repeat(self):
        result = self.attach()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["task_id"], self.task)
        self.assertEqual(data["checks"][0]["status"], "passed")
        self.assertEqual(data["checkpoint"]["next_action"], "second를 마칩니다.")
        self.assertFalse(data["verified"])
        self.assertEqual(data["spec"]["checks"][0]["argv"], self.spec["checks"][0]["argv"])
        new = key("gemini-cli", "new-session")
        self.sessions.nudge(new, "one")
        self.assertEqual(self.attach().returncode, 0)
        self.assertEqual(self.sessions.get(new)["retries"], 1)
        self.assertEqual(self.store.connection.execute("SELECT count(*) FROM tasks").fetchone()[0], 1)
        self.assertEqual(self.sessions.get(self.old)["reason"], "다음 세션에서 이어갑니다.")
        with self.assertRaises(ValueError):
            self.sessions.resume(self.old)

    def test_active_or_unknown_host_needs_explicit_stopped_confirmation(self):
        self.sessions.resume(self.old)
        refused = self.attach()
        self.assertEqual(refused.returncode, 1, refused.stdout + refused.stderr)
        self.assertIsNone(self.sessions.get(key("gemini-cli", "new-session")))
        result = self.attach("new-session", "--previous-host-stopped")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(self.sessions.get(self.old)["paused"])

    def test_running_check_cannot_be_overridden(self):
        run = self.store.begin(self.task, "second")
        try:
            result = self.attach("new-session", "--previous-host-stopped")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIsNone(self.sessions.get(key("gemini-cli", "new-session")))
        finally:
            self.store.finish(run, {"status": "interrupted", "returncode": None})

    def test_completed_host_can_transfer_but_new_invocation_invalidates_idle_state(self):
        self.sessions.resume(self.old)
        (self.root / "second.txt").write_text("ready")
        execute(self.store, self.task, "second")
        payload = {"conversationId": "old-session", "workspacePaths": [str(self.root)],
                   "executionNum": 0, "fullyIdle": True, "terminationReason": "NO_TOOL_CALL"}
        handle("antigravity", "Stop", payload)
        handle("antigravity", "PreInvocation", {**payload, "invocationNum": 0})
        self.assertEqual(self.attach().returncode, 1)
        handle("antigravity", "Stop", {**payload, "executionNum": 1})
        (self.root / "first.txt").write_text("changed")
        result = self.attach()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["checks"][0]["status"], "stale")

    def test_first_context_shows_candidates_without_attaching_them(self):
        result = handle("antigravity", "PreInvocation", {"conversationId": "new-session",
                        "workspacePaths": [str(self.root)], "invocationNum": 0})
        self.assertIn(self.task, json.dumps(result))
        self.assertIsNone(self.sessions.get(key("antigravity", "new-session")))

    def test_listing_is_workspace_scoped_paginated_and_not_a_fresh_pass(self):
        second = self.store.create(self.root, self.spec)
        other = self.root / "other"
        other.mkdir()
        self.store.create(other, self.spec)
        (self.root / "first.txt").write_text("changed")
        first_page = json.loads(self.call("tasks", "--workspace", str(self.root), "--limit", "1").stdout)
        next_page = json.loads(self.call("tasks", "--workspace", str(self.root), "--limit", "1", "--offset", "1").stdout)
        self.assertEqual(first_page["total"], 2)
        self.assertEqual(first_page["next_offset"], 1)
        self.assertIsNone(next_page["next_offset"])
        items = first_page["tasks"] + next_page["tasks"]
        self.assertEqual({item["task_id"] for item in items}, {self.task, second})
        old = next(item for item in items if item["task_id"] == self.task)
        self.assertEqual(old["recorded_check_counts"]["passed"], 1)
        self.assertNotIn("verified", old)
        self.assertFalse(first_page["current_files_checked"])

    def test_private_or_linked_state_is_rejected_before_database_access(self):
        private = self.root / ".env"
        private.write_text("synthetic-private-marker")
        linked = self.root / "linked.sqlite3"
        linked.symlink_to(self.path)
        with patch("gtg.discovery.sqlite3.connect", side_effect=AssertionError("상태 파일을 열면 안 됩니다.")):
            for state in (private, linked):
                with self.subTest(path=state), self.assertRaises(ValueError):
                    discover(self.root, state)

    def test_concurrent_attach_does_not_create_two_active_owners(self):
        commands = [[sys.executable, "-m", "gtg", "attach", self.task, "--workspace", str(self.root),
                     "--platform", "gemini-cli", "--session", name] for name in ("one", "two")]
        processes = [subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                     for command in commands]
        try:
            for process in processes:
                process.communicate(timeout=5)
            self.assertEqual(sorted(p.returncode for p in processes), [0, 1])
            rows = self.sessions.for_task(self.task)
            self.assertEqual(sum(not row["paused"] for row in rows), 1)
        finally:
            for process in processes:
                if process.poll() is None:
                    process.kill()
                process.wait()

    def test_conflicting_current_goal_rolls_back_attachment(self):
        current = key("gemini-cli", "new-session")
        other_spec = {**self.spec, "goal": "다른 활성 목표"}
        other = self.sessions.start(current, self.root, other_spec)
        before = self.sessions.get(self.old)
        result = self.attach("new-session", "--previous-host-stopped")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.sessions.get(current)["task_id"], other)
        self.assertEqual(self.sessions.get(self.old), before)

    def test_wrong_workspace_or_non_native_state_path_does_not_attach(self):
        other = self.root / "other"
        other.mkdir()
        result = self.call("--state", str(self.path), "attach", self.task, "--workspace", str(other),
                           "--platform", "antigravity", "--session", "new-session")
        self.assertEqual(result.returncode, 1)
        self.assertIsNone(self.sessions.get(key("antigravity", "new-session")))
        self.assertFalse((other / ".gtg").exists())

    def test_corrupt_saved_contract_cannot_be_attached_or_reported_passed(self):
        self.store.connection.execute("UPDATE tasks SET spec=? WHERE id=?", (json.dumps({"schema_version": 1, "goal": "bad", "checks": []}), self.task))
        self.store.connection.commit()
        result = self.attach()
        self.assertEqual(result.returncode, 1)
        self.assertIsNone(self.sessions.get(key("gemini-cli", "new-session")))
        self.assertEqual(self.call("tasks", "--workspace", str(self.root)).returncode, 1)

    def test_long_saved_goal_is_partial_in_the_list_and_complete_in_status(self):
        long_goal = "중요한 요구를 보존합니다. " * 80
        task = self.store.create(self.root, {**self.spec, "goal": long_goal})
        listed = json.loads(self.call("tasks", "--workspace", str(self.root)).stdout)
        item = next(t for t in listed["tasks"] if t["task_id"] == task)
        self.assertTrue(item["goal_truncated"])
        self.assertEqual(len(item["goal"]), 320)
        full = self.call("--state", str(self.path), "status", task)
        self.assertEqual(full.returncode, 0)
        self.assertEqual(json.loads(full.stdout)["goal"], long_goal)

    def test_new_session_finishes_remaining_check_with_the_original_contract(self):
        result = self.attach()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = {"session_id": "new-session", "cwd": str(self.root), "hook_event_name": "BeforeAgent"}
        context = handle("gemini-cli", "BeforeAgent", payload)
        self.assertIn("second를 마칩니다", json.dumps(context, ensure_ascii=False))
        (self.root / "second.txt").write_text("ready")
        checked = self.call("--state", str(self.path), "verify", self.task, "--check", "second")
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        data = json.loads(checked.stdout)
        self.assertTrue(data["verified"])
        self.assertEqual(data["goal"], self.spec["goal"])
        self.assertTrue(data["checkpoint"]["files_unchanged"])
        self.assertEqual(self.store.connection.execute("SELECT count(*) FROM tasks").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
```
