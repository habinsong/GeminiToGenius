"""긴 작업의 자동 재개 예산을 작업 명세로 정하고 상한을 강제합니다."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

from gtg.hooks import handle
from gtg.sessions import Sessions, key
from gtg.spec import MAX_RESUMES, validate
from gtg.store import Store


def spec(max_resumes=None):
    document = {"schema_version": 1, "goal": "긴 작업을 이어서 수행합니다.", "checks": [
        {"id": "regression", "criterion": "등록 검사가 통과합니다.",
         "argv": [sys.executable, "-c", "raise SystemExit(1)"], "watch": ["source.py"]}]}
    if max_resumes is not None:
        document["max_resumes"] = max_resumes
    return document


class SpecBudgetTests(unittest.TestCase):
    def test_default_budget_is_two_and_is_recorded(self):
        self.assertEqual(validate(spec())["max_resumes"], 2)

    def test_declared_budget_is_kept_within_the_hard_cap(self):
        self.assertEqual(validate(spec(6))["max_resumes"], 6)
        self.assertEqual(validate(spec(MAX_RESUMES))["max_resumes"], MAX_RESUMES)
        for value in (0, -1, MAX_RESUMES + 1, 2.5, True, "3", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate({**spec(), "max_resumes": value})


class HookBudgetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name).resolve()
        (self.workspace / "source.py").write_text("value = 1\n")

    def register(self, max_resumes=None):
        store = Store(self.workspace / ".gtg/state.sqlite3")
        self.addCleanup(store.close)
        session = key("antigravity", "long-session")
        Sessions(store).start(session, self.workspace, spec(max_resumes))
        return store

    def stop(self, execution):
        return handle("antigravity", "Stop",
                      {"conversationId": "long-session", "workspacePaths": [str(self.workspace)],
                       "executionNum": execution, "fullyIdle": True, "terminationReason": "model_stop"})

    def resumes_until_pause(self):
        for execution in range(MAX_RESUMES + 3):
            result = self.stop(execution)
            if result.get("decision") != "continue":
                return execution, result
        self.fail("자동 재개가 멈추지 않았습니다.")

    def test_default_budget_pauses_after_two_resumes(self):
        self.register()
        count, result = self.resumes_until_pause()
        self.assertEqual(count, 2)
        self.assertEqual(result["decision"], "stop")
        self.assertIn("상한", result["reason"])

    def test_declared_budget_allows_more_resumes_for_a_long_task(self):
        self.register(5)
        count, _ = self.resumes_until_pause()
        self.assertEqual(count, 5)

    def test_stored_state_keeps_the_pause_reason_and_count(self):
        store = self.register(3)
        self.resumes_until_pause()
        link = Sessions(store).get(key("antigravity", "long-session"))
        self.assertTrue(link["paused"])
        self.assertEqual(link["retries"], 3)
        self.assertIn("3", link["reason"])

    def test_a_second_workspace_with_a_smaller_budget_wins(self):
        other = Path(self.temp.name).resolve() / "second"
        other.mkdir()
        (other / "source.py").write_text("value = 2\n")
        self.register(5)
        second = Store(other / ".gtg/state.sqlite3")
        self.addCleanup(second.close)
        Sessions(second).start(key("antigravity", "long-session"), other, spec(2))
        for execution in range(6):
            result = handle("antigravity", "Stop",
                            {"conversationId": "long-session", "workspacePaths": [str(self.workspace), str(other)],
                             "executionNum": execution, "fullyIdle": True, "terminationReason": "model_stop"})
            if result.get("decision") != "continue":
                self.assertEqual(execution, 2, "가장 작은 예산을 따릅니다.")
                return
        self.fail("자동 재개가 멈추지 않았습니다.")


class VerifyAllTests(unittest.TestCase):
    def test_verify_all_runs_every_check_instead_of_stopping_at_the_first_failure(self):
        from gtg.install import install
        import subprocess

        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory).resolve()
            package = install(root, workspace, "antigravity", "workspace")
            runner = str(Path(package["target"]) / "run.py")
            (workspace / "source.py").write_text("value = 1\n")
            document = {"schema_version": 1, "goal": "두 검사를 모두 확인합니다.", "checks": [
                {"id": "failing", "criterion": "첫 검사는 실패합니다.",
                 "argv": [sys.executable, "-c", "raise SystemExit(1)"], "watch": ["source.py"]},
                {"id": "passing", "criterion": "둘째 검사는 통과합니다.",
                 "argv": [sys.executable, "-c", "pass"], "watch": ["source.py"]}]}
            (workspace / "task.json").write_text(json.dumps(document))

            def command(*args, expect=0):
                done = subprocess.run([sys.executable, runner, *args], cwd=workspace, capture_output=True, text=True)
                self.assertEqual(done.returncode, expect, done.stdout + done.stderr)
                return json.loads(done.stdout)

            task = command("start", "--spec", "task.json", "--workspace", ".")["task_id"]
            stopped = command("verify", task, expect=1)
            self.assertEqual({c["id"]: c["status"] for c in stopped["checks"]},
                             {"failing": "failed", "passing": "pending"})
            every = command("verify", task, "--all", expect=1)
            self.assertEqual({c["id"]: c["status"] for c in every["checks"]},
                             {"failing": "failed", "passing": "passed"})
            self.assertFalse(every["verified"])


if __name__ == "__main__":
    unittest.main()
