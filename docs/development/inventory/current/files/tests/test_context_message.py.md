# `tests/test_context_message.py`

- 형식: `100644`
- 바이트: 8706
- SHA-256: `9bb4ff9cb0c4318137ab567190d12642a1aa314faf48cbd5796ba19a8b825f59`
- 인코딩: `utf-8`

```
"""짧은 훅 안내에도 현재 상태·경로·생략 정보가 유지되는지 검사합니다."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

from gtg.checkpoints import record
from gtg.hooks import handle
from gtg.runner import execute, status
from gtg.sessions import Sessions, key
from gtg.store import Store


def state_data(response):
    message = response["injectSteps"][0]["ephemeralMessage"]
    return json.loads(message.splitlines()[1])


class ContextMessageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        (self.root / "source.txt").write_text("ready")
        self.store = Store(self.root / ".gtg/state.sqlite3")
        self.addCleanup(self.store.close)
        self.session = key("antigravity", "context-session")
        self.payload = {"conversationId": "context-session", "workspacePaths": [str(self.root)], "invocationNum": 1}

    def task(self, goal="결과를 검증합니다.", count=1):
        spec = {"schema_version": 1, "goal": goal, "checks": [{
            "id": f"check-{i}", "criterion": "현재 입력을 확인합니다.", "watch": ["source.txt"],
            "argv": [sys.executable, "-B", "-c", "from pathlib import Path; assert Path('source.txt').read_text() == 'ready'"]
        } for i in range(count)]}
        task = self.store.create(self.root, spec)
        Sessions(self.store).bind(self.session, task)
        return task

    def context(self):
        return handle("antigravity", "PreInvocation", self.payload)

    def test_self_contained_status_reuses_workspace_without_repeating_path(self):
        task = self.task()
        result = self.context()
        data = state_data(result)
        self.assertEqual(data["session"], "context-session")
        item = data["tasks"][0]
        self.assertEqual(data["workspaces"][item["workspace"]], str(self.root))
        self.assertEqual(item["task_id"], task)
        self.assertEqual(item["unverified"], {"check-0": "pending"})
        self.assertEqual(result["injectSteps"][0]["ephemeralMessage"].count(str(self.root)), 1)

    def test_passed_check_reports_what_it_never_executed(self):
        (self.root / "covered.py").write_text("VALUE = 1\n")
        (self.root / "skipped.py").write_text("OTHER = 2\n")
        spec = {"schema_version": 1, "goal": "일부만 실행합니다.", "checks": [
            {"id": "partial", "criterion": "덮인 파일만 확인합니다.", "watch": ["covered.py", "skipped.py"],
             "argv": [sys.executable, "-c", "import covered; assert covered.VALUE == 1"]},
            {"id": "pending", "criterion": "아직 실행하지 않았습니다.", "watch": ["covered.py"],
             "argv": [sys.executable, "-c", "pass"]}]}
        task = self.store.create(self.root, spec)
        Sessions(self.store).bind(self.session, task)
        execute(self.store, task, "partial")
        item = state_data(self.context())["tasks"][0]
        self.assertEqual(item["unverified"], {"pending": "pending"})
        self.assertEqual(item["unexecuted"], ["skipped.py"])

    def test_fully_covered_task_says_nothing_extra(self):
        (self.root / "covered.py").write_text("VALUE = 1\n")
        spec = {"schema_version": 1, "goal": "전부 실행합니다.", "checks": [
            {"id": "full", "criterion": "덮인 파일을 확인합니다.", "watch": ["covered.py"],
             "argv": [sys.executable, "-c", "import covered; assert covered.VALUE == 1"]},
            {"id": "rest", "criterion": "남은 검사입니다.", "watch": ["covered.py"],
             "argv": [sys.executable, "-c", "pass"]}]}
        task = self.store.create(self.root, spec)
        Sessions(self.store).bind(self.session, task)
        execute(self.store, task, "full")
        item = state_data(self.context())["tasks"][0]
        self.assertNotIn("unexecuted", item)

    def test_long_goal_note_and_check_list_report_omissions_and_keep_full_status(self):
        goal = "중요한 요구 " * 40
        task = self.task(goal, count=12)
        note = {"summary": "확인한 진행 " * 80, "next_action": "다음 할 일 " * 60, "files": ["source.txt"]}
        record(self.store, task, note)
        item = state_data(self.context())["tasks"][0]
        self.assertEqual(set(item["truncated"]), {"goal", "checkpoint.summary", "checkpoint.next_action"})
        self.assertEqual(item["omitted_checks"] + len(item["unverified"]), 12)
        self.assertTrue(item["checkpoint"]["files_unchanged"])
        full = status(self.store, task)
        self.assertEqual(full["goal"], goal)
        self.assertEqual(full["checkpoint"]["summary"], note["summary"].strip())
        self.assertEqual(len(full["checks"]), 12)

    def test_each_invocation_rechecks_files_and_does_not_rely_on_previous_message(self):
        task = self.task(count=2)
        execute(self.store, task, "check-0")
        first = state_data(self.context())
        self.payload["invocationNum"] = 2
        self.assertEqual(state_data(self.context()), first)
        (self.root / "source.txt").write_text("changed")
        current = state_data(self.context())["tasks"][0]
        self.assertEqual(current["unverified"], {"check-0": "stale", "check-1": "pending"})
        self.assertEqual(Sessions(self.store).get(self.session)["retries"], 0)

    def test_gemini_turns_receive_the_same_current_state(self):
        task = self.task()
        Sessions(self.store).bind(key("gemini-cli", "context-session"), task)
        payload = {"session_id": "context-session", "cwd": str(self.root), "hook_event_name": "BeforeAgent"}
        first = handle("gemini-cli", "BeforeAgent", payload)
        second = handle("gemini-cli", "BeforeAgent", payload)
        self.assertEqual(first, second)
        data = json.loads(first["hookSpecificOutput"]["additionalContext"].splitlines()[1])
        self.assertEqual(data["platform"], "gemini-cli")
        self.assertEqual(data["tasks"][0]["task_id"], task)

    def test_omitted_workspaces_still_control_running_and_paused_stop(self):
        roots, stores, tasks = [], [], []
        for i in range(9):
            root = self.root / f"folder-{i}"
            root.mkdir()
            (root / "source.txt").write_text("ready")
            store = Store(root / ".gtg/state.sqlite3")
            self.addCleanup(store.close)
            task = store.create(root, {"schema_version": 1, "goal": root.name, "checks": [{
                "id": "check", "criterion": "입력 확인", "watch": ["source.txt"],
                "argv": [sys.executable, "-B", "-c", "from pathlib import Path; assert Path('source.txt').read_text() == 'ready'"]}]})
            Sessions(store).bind(self.session, task)
            roots.append(root)
            stores.append(store)
            tasks.append(task)
        self.payload["workspacePaths"] = [str(p) for p in reversed(roots)]
        data = state_data(self.context())
        self.assertEqual(data["omitted_tasks"], 1)
        self.assertEqual(len(data["tasks"]), 8)
        for item in data["tasks"]:
            self.assertEqual(data["workspaces"][item["workspace"]], str(roots[tasks.index(item["task_id"])]))
        run = stores[-1].begin(tasks[-1], "check")
        stop = {**self.payload, "executionNum": 0, "fullyIdle": True, "terminationReason": "NO_TOOL_CALL"}
        self.assertEqual(handle("antigravity", "Stop", stop)["decision"], "stop")
        stores[-1].finish(run, {"status": "interrupted", "returncode": None})
        Sessions(stores[-1]).pause(self.session, "사용자 응답 대기")
        self.assertEqual(handle("antigravity", "Stop", stop)["decision"], "stop")
        for store in stores:
            self.assertEqual(Sessions(store).get(self.session)["retries"], 0)

    def test_active_and_unbound_workspaces_keep_candidate_origin(self):
        active = self.task()
        other = self.root / "other"
        other.mkdir()
        store = Store(other / ".gtg/state.sqlite3")
        self.addCleanup(store.close)
        candidate = store.create(other, self.store.task(active)["spec"])
        self.payload.update(workspacePaths=[str(other), str(self.root)], invocationNum=0)
        data = state_data(self.context())
        item = data["candidates"][0]
        self.assertEqual(item["task_id"], candidate)
        self.assertEqual(data["workspaces"][item["workspace"]], str(other))
        self.assertFalse(data["candidates_current_files_checked"])
        self.assertFalse(data["candidate_list_complete"])
        self.assertIsNone(Sessions(store).get(self.session))


if __name__ == "__main__":
    unittest.main()
```
