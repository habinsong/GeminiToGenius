"""검증 명령의 중단과 남은 하위 프로세스를 실제 프로세스로 확인합니다."""

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from gtg.runner import execute, status
from gtg.store import Store


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.name == "posix", "POSIX 프로세스 그룹 시험입니다.")
class ProcessLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.state = self.root / "state.sqlite3"
        self.store = Store(self.state)
        self.addCleanup(self.store.close)
        (self.root / "value.txt").write_text("value")

    def task(self, code):
        return self.store.create(self.root, {"schema_version": 1, "goal": "프로세스 종료 확인", "checks": [{
            "id": "process", "criterion": "검증 프로세스 전체가 종료됩니다.", "watch": ["value.txt"],
            "argv": [sys.executable, "-c", code], "timeout_seconds": 10}]})

    def cleanup_group(self, pid):
        if pid:
            try:
                os.killpg(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    def assert_interruption(self, signum):
        task = self.task("from pathlib import Path; import os,time; Path('ready.tmp').write_text(str(os.getpid())); Path('ready.tmp').replace('ready'); time.sleep(8)")
        with tempfile.TemporaryFile() as output:
            process = subprocess.Popen([sys.executable, "-m", "gtg", "--state", str(self.state), "verify", task],
                                       cwd=ROOT, stdout=output, stderr=output, start_new_session=True)
            child = None
            try:
                deadline = time.monotonic() + 4
                while not (self.root / "ready").exists() and process.poll() is None and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue((self.root / "ready").is_file())
                child = int((self.root / "ready").read_text())
                process.send_signal(signum)
                process.wait(timeout=4)
                self.assertEqual(process.returncode, 128 + signum)
                self.assertEqual(status(self.store, task)["checks"][0]["status"], "interrupted")
                with self.assertRaises(ProcessLookupError):
                    os.kill(child, 0)
            finally:
                self.cleanup_group(child)
                if process.poll() is None:
                    process.kill()
                process.wait()

    def test_sigterm_cancels_child_and_records_interruption(self):
        self.assert_interruption(signal.SIGTERM)

    def test_sigint_cancels_child_and_records_interruption(self):
        self.assert_interruption(signal.SIGINT)

    def test_successful_parent_with_background_child_is_not_verified(self):
        task = self.task("import subprocess,sys; subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(8)'])")
        try:
            result = execute(self.store, task, "process")
            self.assertEqual(result["status"], "background_processes")
            self.assertFalse(status(self.store, task)["verified"])
        finally:
            row = self.store.connection.execute("SELECT child_pid FROM runs WHERE task_id=?", (task,)).fetchone()
            self.cleanup_group(row[0] if row else None)

    def test_failure_to_record_process_does_not_leave_it_running(self):
        task = self.task("import time; time.sleep(8)")
        captured = []
        def fail(run, pid):
            captured.append(pid)
            raise ValueError("기록 실패 주입")
        try:
            with patch.object(self.store, "attach_process", side_effect=fail):
                result = execute(self.store, task, "process")
            self.assertEqual(result["status"], "error")
            self.assertEqual(len(captured), 1)
            with self.assertRaises(ProcessLookupError):
                os.kill(captured[0], 0)
        finally:
            for pid in captured:
                self.cleanup_group(pid)


if __name__ == "__main__":
    unittest.main()
