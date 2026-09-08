# `tests/test_scenario.py`

- 형식: `100644`
- 바이트: 3646
- SHA-256: `a7ebbc4cd9657114235d9e8d06db0232a4800f19cc46822327f747e08006c70d`
- 인코딩: `utf-8`

```
"""설치된 코드로 실패→수정→통과→재변경을 수행하는 오프라인 통합 사례입니다."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gtg.install import install


ROOT = Path(__file__).resolve().parents[1]


class ScenarioTests(unittest.TestCase):
    def test_installed_harness_tracks_real_failure_fix_and_stale_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory).resolve()
            package = install(ROOT, workspace, "antigravity", "workspace")
            runner = str(Path(package["target"]) / "run.py")
            implementation = workspace / "clamp.py"
            implementation.write_text("def clamp(value, lower, upper):\n    return min(value, upper)\n")
            (workspace / "check.py").write_text(
                "from clamp import clamp\nassert clamp(-2, 0, 10) == 0\nassert clamp(5, 0, 10) == 5\nassert clamp(12, 0, 10) == 10\n")
            spec = {"schema_version": 1, "goal": "음수 제한 오류를 수정하고 정상 범위를 유지합니다.", "checks": [{
                "id": "bounds", "criterion": "상한·하한·범위 안의 값이 올바릅니다.",
                "argv": [sys.executable, "check.py"], "watch": ["clamp.py", "check.py"]}]}
            (workspace / ".gtg/task.json").write_text(json.dumps(spec))

            def command(*args, payload=None):
                return subprocess.run([sys.executable, runner, *args], cwd=workspace,
                                      input=json.dumps(payload) if payload is not None else None,
                                      capture_output=True, text=True)

            start = command("start", "--spec", ".gtg/task.json", "--workspace", ".",
                            "--platform", "antigravity", "--session", "offline-scenario")
            self.assertEqual(start.returncode, 0, start.stdout + start.stderr)
            task = json.loads(start.stdout)["task_id"]
            failed = command("verify", task)
            self.assertEqual(failed.returncode, 1)
            self.assertIn("AssertionError", failed.stderr)
            self.assertFalse(json.loads(failed.stdout)["verified"])
            payload = {"conversationId": "offline-scenario", "workspacePaths": [str(workspace)],
                       "executionNum": 0, "fullyIdle": True, "terminationReason": "model_stop"}
            unfinished = command("hook", "antigravity", "Stop", payload=payload)
            self.assertEqual(json.loads(unfinished.stdout)["decision"], "continue")

            # 참조 수정은 테스트가 수행합니다. LLM이 해결했다고 주장하지 않습니다.
            implementation.write_text("def clamp(value, lower, upper):\n    return max(lower, min(value, upper))\n")
            passed = command("verify", task)
            self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)
            self.assertTrue(json.loads(passed.stdout)["verified"])
            stopped = command("hook", "antigravity", "Stop", payload={**payload, "executionNum": 1})
            self.assertEqual(json.loads(stopped.stdout)["decision"], "stop")

            implementation.write_text("def clamp(value, lower, upper):\n    return value\n")
            stale = command("status", task)
            self.assertEqual(json.loads(stale.stdout)["checks"][0]["status"], "stale")
            retry = command("hook", "antigravity", "Stop", payload={**payload, "executionNum": 2})
            self.assertEqual(json.loads(retry.stdout)["decision"], "continue")


if __name__ == "__main__":
    unittest.main()
```
