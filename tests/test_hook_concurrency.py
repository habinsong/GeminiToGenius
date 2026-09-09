"""훅은 동시에 여러 번 발동할 수 있습니다. 재개 예산이 중복 소모되면 안 됩니다."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from gtg.install import install


ROOT = Path(__file__).resolve().parents[1]


class HookConcurrencyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name).resolve()
        (self.workspace / "src.py").write_text("VALUE = 1\n")
        package = install(ROOT, self.workspace, "antigravity", "workspace")
        self.runner = str(Path(package["target"]) / "run.py")

    def register(self, argv, timeout=30):
        spec = {"schema_version": 1, "goal": "동시 훅을 확인합니다.", "checks": [
            {"id": "only", "criterion": "검사입니다.", "argv": argv,
             "watch": ["src.py"], "timeout_seconds": timeout}]}
        (self.workspace / "task.json").write_text(json.dumps(spec))
        done = subprocess.run([sys.executable, self.runner, "start", "--spec", "task.json",
                               "--workspace", ".", "--platform", "antigravity", "--session", "concurrent"],
                              cwd=self.workspace, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        return json.loads(done.stdout)["task_id"]

    def stop_payload(self, execution=0):
        return json.dumps({"conversationId": "concurrent", "workspacePaths": [str(self.workspace)],
                           "executionNum": execution, "fullyIdle": True, "terminationReason": "model_stop"})

    def fire(self, event, payload):
        return subprocess.Popen([sys.executable, self.runner, "hook", "antigravity", event],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                cwd=self.workspace, text=True), payload

    def session_row(self):
        import sqlite3

        db = sqlite3.connect(self.workspace / ".gtg/state.sqlite3")
        db.row_factory = sqlite3.Row
        try:
            return dict(db.execute("SELECT retries, paused, last_event FROM sessions").fetchone())
        finally:
            db.close()

    def test_simultaneous_identical_stops_resume_exactly_once(self):
        self.register([sys.executable, "-c", "raise SystemExit(1)"])
        payload = self.stop_payload()
        processes = [self.fire("Stop", payload) for _ in range(8)]
        decisions = []
        for process, body in processes:
            out, _ = process.communicate(body)
            decisions.append(json.loads(out).get("decision"))
        self.assertEqual(decisions.count("continue"), 1,
                         "같은 종료 이벤트는 한 번만 재개해야 합니다.")
        self.assertEqual(decisions.count("stop"), 7)
        self.assertEqual(self.session_row()["retries"], 1, "예산이 중복 소모되면 안 됩니다.")

    def test_stop_during_a_running_check_does_not_resume(self):
        task = self.register([sys.executable, "-c", "import time; time.sleep(6)"])
        verify = subprocess.Popen([sys.executable, self.runner, "verify", task],
                                  cwd=self.workspace, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                import sqlite3

                db = sqlite3.connect(self.workspace / ".gtg/state.sqlite3")
                running = db.execute("SELECT COUNT(*) FROM runs WHERE finished IS NULL").fetchone()[0]
                db.close()
                if running:
                    break
                time.sleep(0.05)
            self.assertTrue(running, "검사가 실행 중이어야 합니다.")
            started = time.monotonic()
            process, body = self.fire("Stop", self.stop_payload())
            out, _ = process.communicate(body)
            elapsed = time.monotonic() - started
            self.assertEqual(json.loads(out).get("decision"), "stop",
                             "실행 중인 검사가 있으면 재개하지 않습니다.")
            self.assertEqual(self.session_row()["retries"], 0)
            self.assertLess(elapsed, 5, "훅이 검사 잠금에 막혀 예산을 넘기면 안 됩니다.")
        finally:
            verify.kill()
            verify.wait()

    def test_context_hook_reports_the_running_check(self):
        task = self.register([sys.executable, "-c", "import time; time.sleep(6)"])
        verify = subprocess.Popen([sys.executable, self.runner, "verify", task],
                                  cwd=self.workspace, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            time.sleep(1.0)
            process, body = self.fire("PreInvocation", json.dumps(
                {"conversationId": "concurrent", "workspacePaths": [str(self.workspace)], "invocationNum": 1}))
            out, _ = process.communicate(body)
            message = json.loads(out)["injectSteps"][0]["ephemeralMessage"]
            self.assertIn("running", message)
        finally:
            verify.kill()
            verify.wait()


if __name__ == "__main__":
    unittest.main()
