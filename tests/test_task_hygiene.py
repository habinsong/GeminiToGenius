"""상태 폴더가 사용자 저장소를 오염시키지 않고, 증거가 될 수 없는 검사를 등록하지 않습니다."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gtg.store import Store


def spec(argv=None):
    return {"schema_version": 1, "goal": "검사 명령을 확인합니다.", "checks": [
        {"id": "only", "criterion": "실제 결과를 확인합니다.",
         "argv": argv or [sys.executable, "-c", "pass"], "watch": ["source.py"]}]}


class StateHygieneTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name).resolve()
        (self.workspace / "source.py").write_text("value = 1\n")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.workspace), *args], capture_output=True, text=True,
                              env={"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1",
                                   "GIT_CONFIG_GLOBAL": "/dev/null"})

    def test_state_folder_ignores_itself_in_a_git_repository(self):
        self.assertEqual(self.git("-c", "init.templateDir=", "init", "-q").returncode, 0)
        store = Store(self.workspace / ".gtg/state.sqlite3")
        self.addCleanup(store.close)
        self.assertTrue((self.workspace / ".gtg/.gitignore").is_file())
        untracked = self.git("status", "--porcelain", "--untracked-files=all")
        self.assertEqual(untracked.returncode, 0, untracked.stderr)
        self.assertNotIn(".gtg", untracked.stdout)
        self.assertIn("source.py", untracked.stdout)

    def test_existing_ignore_file_is_not_overwritten(self):
        (self.workspace / ".gtg").mkdir()
        (self.workspace / ".gtg/.gitignore").write_text("사용자 내용\n")
        store = Store(self.workspace / ".gtg/state.sqlite3")
        self.addCleanup(store.close)
        self.assertEqual((self.workspace / ".gtg/.gitignore").read_text(), "사용자 내용\n")

    def test_state_outside_a_gtg_folder_does_not_create_an_ignore_file(self):
        store = Store(self.workspace / "custom/state.sqlite3")
        self.addCleanup(store.close)
        self.assertFalse((self.workspace / "custom/.gitignore").exists())


class EvidenceCommandTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name).resolve()
        (self.workspace / "source.py").write_text("value = 1\n")
        self.store = Store(self.workspace / ".gtg/state.sqlite3")
        self.addCleanup(self.store.close)

    def test_no_op_commands_cannot_be_registered_as_evidence(self):
        for argv in (["true"], ["/bin/true"], [":"], ["echo", "ok"], ["printf", "done"], ["yes"]):
            with self.subTest(argv=argv), self.assertRaisesRegex(ValueError, "증거"):
                self.store.create(self.workspace, spec(argv))

    def test_real_commands_are_still_accepted(self):
        task = self.store.create(self.workspace, spec())
        self.assertTrue(task)
        self.assertTrue(self.store.create(self.workspace, spec(["make", "test"])))

    def test_previously_stored_specs_remain_readable(self):
        task = self.store.create(self.workspace, spec())
        stored = json.loads(self.store.connection.execute(
            "SELECT spec FROM tasks WHERE id=?", (task,)).fetchone()["spec"])
        stored["checks"][0]["argv"] = ["echo", "legacy"]
        self.store.connection.execute("UPDATE tasks SET spec=? WHERE id=?",
                                      (json.dumps(stored, ensure_ascii=False), task))
        self.store.connection.commit()
        self.assertEqual(self.store.task(task)["spec"]["checks"][0]["argv"], ["echo", "legacy"])


if __name__ == "__main__":
    unittest.main()
