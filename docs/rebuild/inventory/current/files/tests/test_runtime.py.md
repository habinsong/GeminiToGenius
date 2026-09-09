# `tests/test_runtime.py`

- 형식: `100644`
- 바이트: 14255
- SHA-256: `90801837cb59ddb038d434fbec85976dbdef917e0f363b5f270a1b2ba28dd7b0`
- 인코딩: `utf-8`

```
"""실제 프로세스 결과와 현재 파일 상태가 일치해야 검증을 인정합니다."""

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from gtg.runner import execute, status
from gtg.spec import fingerprint, validate
from gtg.store import Store


ROOT = Path(__file__).resolve().parents[1]


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.workspace = self.base / "프로젝트 with spaces"
        self.workspace.mkdir()
        (self.workspace / "value.txt").write_text("correct")
        self.path = self.base / "state.sqlite3"
        self.store = Store(self.path)
        self.addCleanup(self.store.close)
        self.spec = {"schema_version": 1, "goal": "파일의 결과를 검증합니다.", "checks": [{
            "id": "value", "criterion": "파일 내용이 correct여야 합니다.", "watch": ["value.txt"],
            "argv": [sys.executable, "-c", "from pathlib import Path; assert Path('value.txt').read_text() == 'correct'"],
            "timeout_seconds": 5}]}

    def start(self, spec=None):
        return self.store.create(self.workspace, spec or self.spec)

    def test_pass_and_changed_code_invalidates_prior_evidence(self):
        task = self.start()
        self.assertFalse(status(self.store, task)["verified"])
        self.assertEqual(execute(self.store, task, "value")["status"], "passed")
        self.assertTrue(status(self.store, task)["verified"])
        (self.workspace / "value.txt").write_text("wrong")
        self.assertEqual(status(self.store, task)["checks"][0]["status"], "stale")
        self.assertEqual(execute(self.store, task, "value")["status"], "failed")
        self.assertFalse(status(self.store, task)["verified"])

    def test_subsequent_failed_check_overrides_success(self):
        task = self.start()
        execute(self.store, task, "value")
        run = self.store.begin(task, "value")
        self.store.finish(run, {"status": "failed", "returncode": 7})
        self.assertFalse(status(self.store, task)["verified"])

    def test_command_cannot_change_watched_code_and_claim_pass(self):
        self.spec["checks"][0]["argv"] = [sys.executable, "-c", "from pathlib import Path; Path('value.txt').write_text('different')"]
        task = self.start()
        self.assertEqual(execute(self.store, task, "value")["status"], "changed_during_check")
        self.assertFalse(status(self.store, task)["verified"])

    def test_timeout_and_missing_executable_are_not_success(self):
        self.spec["checks"][0].update(argv=[sys.executable, "-c", "import time; time.sleep(10)"], timeout_seconds=0.03)
        task = self.start()
        self.assertEqual(execute(self.store, task, "value")["status"], "timeout")
        self.spec["checks"][0]["argv"] = [str(self.base / "nonexistent")]
        other = self.start()
        self.assertEqual(execute(self.store, other, "value")["status"], "error")

    def test_restart_and_task_isolation(self):
        one, two = self.start(), self.start()
        execute(self.store, one, "value")
        reopened = Store(self.path)
        self.addCleanup(reopened.close)
        self.assertTrue(status(reopened, one)["verified"])
        self.assertFalse(status(reopened, two)["verified"])

    def test_parallel_execution_is_rejected_and_running_is_not_complete(self):
        task = self.start()
        run = self.store.begin(task, "value")
        other = Store(self.path)
        self.addCleanup(other.close)
        with self.assertRaisesRegex(ValueError, "실행 중"):
            other.begin(task, "value")
        self.assertFalse(status(other, task)["verified"])
        with self.assertRaisesRegex(ValueError, "살아"):
            other.recover(task)
        self.store.finish(run, {"status": "interrupted", "returncode": None})

    def test_dead_owner_recovery_keeps_task_unverified(self):
        task = self.start()
        script = "from pathlib import Path; from gtg.store import Store; import sys; s=Store(Path(sys.argv[1])); s.begin(sys.argv[2], 'value')"
        subprocess.run([sys.executable, "-c", script, str(self.path), task], cwd=ROOT, check=True)
        self.assertEqual(self.store.recover(task), 1)
        self.assertFalse(status(self.store, task)["verified"])
        self.assertEqual(execute(self.store, task, "value")["status"], "passed")

    def owner_leaving_a_child(self, task: str) -> int:
        """검사를 시작한 프로세스는 끝났지만 검사 프로세스는 남아 있는 상태를 만듭니다."""
        script = ("import subprocess, sys; from pathlib import Path; from gtg.store import Store\n"
                  "s = Store(Path(sys.argv[1])); r = s.begin(sys.argv[2], 'value')\n"
                  "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'],\n"
                  "                         pass_fds=s.inherited(r), start_new_session=True,\n"
                  "                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,\n"
                  "                         stderr=subprocess.DEVNULL)\n"
                  "print(child.pid)\n")
        done = subprocess.run([sys.executable, "-c", script, str(self.path), task],
                              cwd=ROOT, check=True, capture_output=True, text=True)
        return int(done.stdout.strip())

    def test_recovery_rejects_a_still_running_child(self):
        task = self.start()
        child_pid = self.owner_leaving_a_child(task)
        try:
            with self.assertRaisesRegex(ValueError, "살아 있어"):
                self.store.recover(task)
        finally:
            os.kill(child_pid, 9)
        for _ in range(100):
            try:
                os.kill(child_pid, 0)
            except OSError:
                break
            time.sleep(0.02)
        self.assertEqual(self.store.recover(task), 1)

    def test_recovery_works_after_the_owner_pid_is_reused(self):
        """재부팅 뒤 PID가 다른 프로세스에 재사용된 상태에서도 복구할 수 있어야 합니다."""
        task = self.start()
        script = ("from pathlib import Path; from gtg.store import Store; import sys; "
                  "Store(Path(sys.argv[1])).begin(sys.argv[2], 'value')")
        subprocess.run([sys.executable, "-c", script, str(self.path), task], cwd=ROOT, check=True)
        # PID 1은 항상 살아 있고 다른 사용자 소유입니다. 재사용된 PID가 가리킬 수 있는 값입니다.
        with self.store.connection:
            self.store.connection.execute("UPDATE runs SET owner_pid = 1 WHERE finished IS NULL")
        self.assertEqual(self.store.recover(task), 1, "PID 판단이 아니라 잠금으로 복구해야 합니다.")
        self.assertEqual(execute(self.store, task, "value")["status"], "passed")

    def test_reused_pid_without_a_lock_record_does_not_crash(self):
        """잠금 기록이 없는 예전 실행에서도 다른 사용자의 PID를 오류로 흘리지 않습니다."""
        task = self.start()
        script = ("from pathlib import Path; from gtg.store import Store; import sys; "
                  "Store(Path(sys.argv[1])).begin(sys.argv[2], 'value')")
        subprocess.run([sys.executable, "-c", script, str(self.path), task], cwd=ROOT, check=True)
        for stale in (self.path.parent / "runs").glob("*.lock"):
            stale.unlink()
        with self.store.connection:
            self.store.connection.execute("UPDATE runs SET owner_pid = 1 WHERE finished IS NULL")
        self.assertEqual(self.store.recover(task), 1)

    def test_fixed_check_spec_cannot_be_replaced_by_caller(self):
        task = self.start()
        self.spec["checks"][0]["argv"] = ["echo", "pass"]
        self.assertNotEqual(self.store.task(task)["spec"]["checks"][0]["argv"], ["echo", "pass"])
        with self.assertRaises(ValueError):
            execute(self.store, task, "unregistered")

    def test_multiple_criteria_all_need_evidence(self):
        other = copy.deepcopy(self.spec["checks"][0])
        other["id"] = "second"
        self.spec["checks"].append(other)
        task = self.start()
        execute(self.store, task, "value")
        self.assertFalse(status(self.store, task)["verified"])
        execute(self.store, task, "second")
        self.assertTrue(status(self.store, task)["verified"])

    def test_directory_add_delete_mode_and_missing_file_change_fingerprint(self):
        original = fingerprint(self.workspace, ["."])
        path = self.workspace / "new.txt"
        path.write_text("new")
        added = fingerprint(self.workspace, ["."])
        self.assertNotEqual(original, added)
        path.chmod(0o700)
        self.assertNotEqual(added, fingerprint(self.workspace, ["."]))
        path.unlink()
        self.assertEqual(original, fingerprint(self.workspace, ["."]))
        missing = fingerprint(self.workspace, ["later.txt"])
        (self.workspace / "later.txt").write_text("created")
        self.assertNotEqual(missing, fingerprint(self.workspace, ["later.txt"]))

    def test_private_contents_not_read_and_symlinks_rejected(self):
        (self.workspace / ".env").write_text("private")
        before = fingerprint(self.workspace, ["."])
        (self.workspace / ".env").write_text("different-private")
        self.assertEqual(before, fingerprint(self.workspace, ["."]))
        (self.workspace / "linked").symlink_to(self.base)
        with self.assertRaisesRegex(ValueError, "심볼릭"):
            fingerprint(self.workspace, ["."])
        with self.assertRaises(ValueError):
            fingerprint(self.workspace, ["../state.sqlite3"])

    def test_invalid_spec_inputs_are_rejected(self):
        for field, value in [("id", "../../outside"), ("argv", "echo pass"), ("watch", []),
                             ("watch", [".env"]), ("watch", ["/etc"]), ("criterion", ""),
                             ("timeout_seconds", True), ("timeout_seconds", float("nan"))]:
            with self.subTest(field=field, value=value):
                invalid = copy.deepcopy(self.spec)
                invalid["checks"][0][field] = value
                with self.assertRaises(ValueError):
                    validate(invalid)

    def test_raw_output_is_not_persisted(self):
        self.spec["checks"][0]["argv"] = [sys.executable, "-c", "print('runtime-test-output')"]
        task = self.start()
        execute(self.store, task, "value")
        row = self.store.connection.execute("SELECT result FROM runs").fetchone()
        self.assertNotIn("runtime-test-output", row[0])

    def test_cli_runs_without_provider_and_returns_failure(self):
        spec_path = self.workspace / "task.json"
        spec_path.write_text(json.dumps(self.spec))
        cmd = [sys.executable, "-m", "gtg", "--state", str(self.path)]
        start = subprocess.run(cmd + ["start", "--spec", str(spec_path), "--workspace", str(self.workspace)],
                               cwd=ROOT, capture_output=True, text=True, check=True)
        task = json.loads(start.stdout)["task_id"]
        verify = subprocess.run(cmd + ["verify", task], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)
        self.assertTrue(json.loads(verify.stdout)["verified"])
        (self.workspace / "value.txt").write_text("wrong")
        failed = subprocess.run(cmd + ["verify", task], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(failed.returncode, 1)
        self.assertFalse(json.loads(failed.stdout)["verified"])

    def test_start_from_another_directory_uses_the_explicit_workspace(self):
        spec_path = self.base / "task.json"
        spec_path.write_text(json.dumps(self.spec))
        caller = self.base / "caller"
        caller.mkdir()
        command = [sys.executable, str(ROOT / "scripts/gtg_runner.py"), "start", "--spec", str(spec_path),
                   "--workspace", str(self.workspace), "--platform", "antigravity", "--session", "external-caller"]
        # 소스 checkout의 실행기에는 패키지 루트를 명시합니다.
        process = subprocess.run(command, cwd=caller, capture_output=True, text=True,
                                 env={**os.environ, "PYTHONPATH": str(ROOT)})
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertFalse((caller / ".gtg/state.sqlite3").exists())
        self.assertTrue((self.workspace / ".gtg/state.sqlite3").exists())
        self.assertEqual(json.loads(process.stdout)["state_path"], str(self.workspace / ".gtg/state.sqlite3"))

    def test_shared_watch_is_read_once_per_status_but_never_cached_across_queries(self):
        original = self.spec["checks"][0]
        self.spec["checks"] = [{**copy.deepcopy(original), "id": f"check-{number}"} for number in range(3)]
        task = self.start()
        for check in self.spec["checks"]:
            execute(self.store, task, check["id"])
        with patch("gtg.runner.fingerprint", wraps=fingerprint) as reads:
            self.assertTrue(status(self.store, task)["verified"])
            self.assertEqual(reads.call_count, 1)
            (self.workspace / "value.txt").write_text("changed")
            self.assertFalse(status(self.store, task)["verified"])
            self.assertEqual(reads.call_count, 2)

    def test_targeted_success_is_distinct_from_whole_task_completion(self):
        second = copy.deepcopy(self.spec["checks"][0])
        second["id"] = "second"
        self.spec["checks"].append(second)
        task = self.start()
        process = subprocess.run([sys.executable, "-m", "gtg", "--state", str(self.path), "verify", task, "--check", "value"],
                                 cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        result = json.loads(process.stdout)
        self.assertTrue(result["requested_verified"])
        self.assertFalse(result["verified"])


if __name__ == "__main__":
    unittest.main()
```
