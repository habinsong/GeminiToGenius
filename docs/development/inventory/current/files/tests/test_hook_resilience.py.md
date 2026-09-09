# `tests/test_hook_resilience.py`

- 형식: `100644`
- 바이트: 3191
- SHA-256: `27687cf55e4c9d24cdd3f1c57001afe3c9452b03a009fcf486706fa26a9bf3da`
- 인코딩: `utf-8`

```
"""훅은 모든 턴에서 실행되므로 어떤 내부 오류에서도 유효한 JSON을 내야 합니다."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gtg.install import install


ROOT = Path(__file__).resolve().parents[1]


class HookResilienceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name).resolve()
        (self.workspace / "src.py").write_text("VALUE = 1\n")
        package = install(ROOT, self.workspace, "antigravity", "workspace")
        self.runner = str(Path(package["target"]) / "run.py")

    def call(self, event, payload):
        done = subprocess.run([sys.executable, self.runner, "hook", "antigravity", event],
                              input=payload if isinstance(payload, str) else json.dumps(payload),
                              cwd=self.workspace, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        return json.loads(done.stdout)

    def payload(self, **extra):
        return {"conversationId": "resilience", "workspacePaths": [str(self.workspace)], **extra}

    def corrupt(self):
        state = self.workspace / ".gtg/state.sqlite3"
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_bytes(b"not a database" * 300)

    def test_malformed_input_still_returns_valid_json(self):
        for payload in ("not json", "", "[]", "null", '{"conversationId": {"x": 1}}'):
            with self.subTest(payload=payload[:20]):
                self.assertEqual(self.call("PreInvocation", payload), {})

    def test_stop_defaults_to_allowing_completion_on_internal_error(self):
        self.corrupt()
        result = self.call("Stop", self.payload(executionNum=0, fullyIdle=True, terminationReason="model_stop"))
        self.assertEqual(result["decision"], "stop",
                         "상태를 못 읽을 때 종료를 막으면 무한 재시작이 됩니다.")

    def test_unreadable_state_is_announced_instead_of_staying_silent(self):
        self.corrupt()
        result = self.call("PreInvocation", self.payload(invocationNum=1))
        message = result["injectSteps"][0]["ephemeralMessage"]
        self.assertIn("GTG", message)
        self.assertLess(len(message), 400, "오류 안내는 짧아야 합니다.")
        self.assertNotIn("resilience", message, "세션 식별자나 원문 입력을 담지 않습니다.")

    def test_workspace_without_tasks_stays_silent(self):
        self.assertEqual(self.call("PreInvocation", self.payload(invocationNum=1)), {},
                         "등록된 작업이 없는 것은 오류가 아닙니다.")

    def test_unexpected_internal_failure_still_emits_json(self):
        broken = Path(self.runner).parent / "gtg/discovery.py"
        broken.write_text("def saved_tasks(*args, **kwargs):\n    raise RuntimeError('내부 결함')\n")
        result = self.call("PreInvocation", self.payload(invocationNum=1))
        self.assertIsInstance(result, dict)


if __name__ == "__main__":
    unittest.main()
```
