# `tests/test_workspace_argument.py`

- 형식: `100644`
- 바이트: 3601
- SHA-256: `ac68a115aec5fff77aab4aa515d5b3181f92a5b83658ca019ea29469d54b698f`
- 인코딩: `utf-8`

```
"""실제 모델이 실패했던 호출 형태를 지원해 낭비를 없앱니다."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gtg.install import install


ROOT = Path(__file__).resolve().parents[1]


class WorkspaceArgumentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name).resolve() / "project"
        self.workspace.mkdir()
        self.elsewhere = Path(self.temp.name).resolve() / "elsewhere"
        self.elsewhere.mkdir()
        package = install(ROOT, self.workspace, "antigravity", "workspace")
        self.runner = str(Path(package["target"]) / "run.py")
        (self.workspace / "source.py").write_text("value = 1\n")
        spec = {"schema_version": 1, "goal": "작업공간 인자를 확인합니다.", "checks": [
            {"id": "ok", "criterion": "검사가 통과합니다.",
             "argv": [sys.executable, "-c", "pass"], "watch": ["source.py"]}]}
        (self.workspace / "task.json").write_text(json.dumps(spec))
        self.task = self.command("start", "--spec", "task.json", "--workspace", ".")["task_id"]

    def command(self, *args, cwd=None, expect=0):
        done = subprocess.run([sys.executable, self.runner, *args], cwd=cwd or self.workspace,
                              capture_output=True, text=True)
        self.assertEqual(done.returncode, expect, done.stdout + done.stderr)
        return json.loads(done.stdout)

    def test_status_accepts_workspace_from_another_directory(self):
        result = self.command("status", self.task, "--workspace", str(self.workspace), cwd=self.elsewhere)
        self.assertEqual(result["task_id"], self.task)
        self.assertEqual(Path(result["state_path"]), self.workspace / ".gtg/state.sqlite3")

    def test_verify_and_certify_accept_workspace(self):
        verified = self.command("verify", self.task, "--workspace", str(self.workspace), cwd=self.elsewhere)
        self.assertTrue(verified["verified"])
        issued = self.command("certify", self.task, "--workspace", str(self.workspace), cwd=self.elsewhere)
        self.assertTrue(issued["verified"])

    def test_lookup_from_a_directory_without_state_does_not_create_one(self):
        self.command("status", self.task, cwd=self.elsewhere, expect=1)
        self.assertFalse((self.elsewhere / ".gtg").exists(), "조회 실패가 새 상태 DB를 만들지 않습니다.")

    def test_explicit_state_path_takes_precedence_over_workspace(self):
        state = self.workspace / ".gtg/state.sqlite3"
        result = self.command("--state", str(state), "status", self.task,
                              "--workspace", str(self.elsewhere), cwd=self.elsewhere)
        self.assertEqual(Path(result["state_path"]), state)
        self.assertFalse((self.elsewhere / ".gtg").exists())

    def test_recover_and_checkpoint_accept_workspace(self):
        note = self.elsewhere / "note.json"
        note.write_text(json.dumps({"summary": "진행 메모입니다.", "next_action": "다음 검사를 실행합니다.", "files": []}))
        recovered = self.command("recover", self.task, "--workspace", str(self.workspace), cwd=self.elsewhere)
        self.assertEqual(recovered["recovered"], 0)
        noted = self.command("checkpoint", self.task, "--note", str(note),
                             "--workspace", str(self.workspace), cwd=self.elsewhere)
        self.assertTrue(noted["checkpoint_id"])


if __name__ == "__main__":
    unittest.main()
```
