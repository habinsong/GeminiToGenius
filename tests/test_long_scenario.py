"""설치된 코드로 부분 검증·메모·중단·재개·나머지 검증을 수행합니다."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gtg.install import install


ROOT = Path(__file__).resolve().parents[1]


class LongScenarioTests(unittest.TestCase):
    def test_installed_gemini_extension_resumes_without_losing_goal_or_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            workspace = base / "project"
            workspace.mkdir()
            (workspace / "first.txt").write_text("ready")
            (workspace / "second.txt").write_text("pending")
            package = install(ROOT, base / "home", "gemini-cli", "global")
            runner = str(Path(package["target"]) / "run.py")
            checks = [{"id": name, "criterion": name + " 작업이 준비됩니다.", "watch": [name + ".txt"],
                       "argv": [sys.executable, "-c", f"from pathlib import Path; assert Path('{name}.txt').read_text() == 'ready'"]}
                      for name in ("first", "second")]
            spec = {"schema_version": 1, "goal": "첫 번째와 두 번째 작업을 모두 완료합니다.", "checks": checks}
            (workspace / "task.json").write_text(json.dumps(spec))

            def call(*args, payload=None):
                process = subprocess.run([sys.executable, runner, *args], cwd=workspace, capture_output=True, text=True,
                                         input=json.dumps(payload) if payload is not None else None)
                return process.returncode, json.loads(process.stdout)

            code, start = call("start", "--spec", "task.json", "--platform", "gemini-cli", "--session", "long-scenario")
            self.assertEqual(code, 0)
            task = start["task_id"]
            code, partial = call("verify", task, "--check", "first")
            self.assertEqual(code, 0)
            self.assertTrue(partial["requested_verified"])
            self.assertFalse(partial["verified"])
            note = {"summary": "첫 작업의 실제 검증을 통과했습니다.", "next_action": "second만 수정하고 검증합니다.", "files": ["first.txt"]}
            (workspace / "note.json").write_text(json.dumps(note))
            self.assertEqual(call("checkpoint", task, "--note", "note.json")[0], 0)
            payload = {"session_id": "long-scenario", "cwd": str(workspace), "hook_event_name": "AfterAgent", "stop_hook_active": False}
            for number in range(3):
                _, response = call("hook", "gemini-cli", "AfterAgent", payload={**payload, "timestamp": str(number)})
            self.assertIs(response["continue"], False)
            _, paused = call("status", task)
            self.assertFalse(paused["verified"])
            self.assertTrue(paused["continuation"][0]["paused"])
            self.assertEqual(paused["checkpoint"]["next_action"], note["next_action"])
            self.assertEqual(paused["checks"][0]["status"], "passed")
            self.assertEqual(call("resume", "--platform", "gemini-cli", "--session", "long-scenario")[0], 0)
            (workspace / "second.txt").write_text("ready")
            code, completed = call("verify", task, "--check", "second")
            self.assertEqual(code, 0)
            self.assertTrue(completed["verified"])
            self.assertEqual(completed["goal"], spec["goal"])
            self.assertTrue(completed["checkpoint"]["files_unchanged"])


if __name__ == "__main__":
    unittest.main()
