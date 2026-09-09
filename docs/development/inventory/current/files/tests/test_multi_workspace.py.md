# `tests/test_multi_workspace.py`

- 형식: `100644`
- 바이트: 4050
- SHA-256: `01c24919407e6073b80061da4f575e11508e023ecfcceb0c2514e2373251ffde`
- 인코딩: `utf-8`

```
"""여러 폴더의 동일 호스트 세션을 하나의 완료 판정으로 모읍니다."""

from pathlib import Path
import sys
import tempfile
import unittest

from gtg.hooks import handle
from gtg.runner import execute
from gtg.sessions import Sessions, key
from gtg.store import Store


class MultiWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name).resolve()
        self.roots, self.stores, self.tasks = [], [], []
        self.session = key("antigravity", "multi-folder")
        for name in ("frontend", "backend"):
            root = base / name
            root.mkdir()
            (root / "result.txt").write_text("ready")
            store = Store(root / ".gtg/state.sqlite3")
            self.addCleanup(store.close)
            task = store.create(root, {"schema_version": 1, "goal": name + " 작업", "checks": [{
                "id": "result", "criterion": "검증할 결과 파일이 준비됩니다.", "watch": ["result.txt"],
                "argv": [sys.executable, "-c", "from pathlib import Path; assert Path('result.txt').read_text() == 'ready'"]}]})
            Sessions(store).bind(self.session, task)
            self.roots.append(root)
            self.stores.append(store)
            self.tasks.append(task)
        self.payload = {"conversationId": "multi-folder", "workspacePaths": [str(p) for p in self.roots],
                        "invocationNum": 0, "fullyIdle": True, "terminationReason": "model_stop", "executionNum": 0}

    def test_all_mounted_tasks_must_pass_before_stopping(self):
        context = handle("antigravity", "PreInvocation", self.payload)
        for task in self.tasks:
            self.assertIn(task, str(context))
        execute(self.stores[0], self.tasks[0], "result")
        self.assertEqual(handle("antigravity", "Stop", self.payload)["decision"], "continue")
        execute(self.stores[1], self.tasks[1], "result")
        self.assertEqual(handle("antigravity", "Stop", {**self.payload, "executionNum": 1})["decision"], "stop")

    def test_order_changes_and_duplicates_do_not_reset_retry_budget(self):
        self.assertEqual(handle("antigravity", "Stop", self.payload)["decision"], "continue")
        reordered = {**self.payload, "workspacePaths": list(reversed(self.payload["workspacePaths"])), "executionNum": 1}
        self.assertEqual(handle("antigravity", "Stop", reordered)["decision"], "continue")
        for store in self.stores:
            self.assertEqual(Sessions(store).get(self.session)["retries"], 2)
        duplicated = {**self.payload, "workspacePaths": self.payload["workspacePaths"] * 2, "executionNum": 2}
        self.assertEqual(handle("antigravity", "Stop", duplicated)["decision"], "stop")

    def test_a_pause_in_either_folder_prevents_automatic_retry(self):
        Sessions(self.stores[1]).pause(self.session, "사용자 답변 대기")
        self.assertEqual(handle("antigravity", "Stop", self.payload)["decision"], "stop")
        self.assertEqual(Sessions(self.stores[0]).get(self.session)["retries"], 0)

    def test_host_cancel_pauses_every_bound_task(self):
        handle("antigravity", "Stop", {**self.payload, "terminationReason": "user_cancelled"})
        for store in self.stores:
            self.assertTrue(Sessions(store).get(self.session)["paused"])

    def test_projectless_turn_does_not_need_a_workspace(self):
        self.assertEqual(handle("antigravity", "Stop", {**self.payload, "workspacePaths": []}), {"decision": "stop"})

    def test_unregistered_folder_does_not_create_a_database(self):
        root = self.roots[0].parent / "notes"
        root.mkdir()
        payload = {**self.payload, "workspacePaths": [str(root)], "modelName": "unreleased-model-fixture"}
        context = handle("antigravity", "PreInvocation", payload)
        self.assertIn("multi-folder", str(context))
        self.assertFalse((root / ".gtg").exists())


if __name__ == "__main__":
    unittest.main()
```
