"""미완료 작업·완료된 비교 작업·사용자 수정을 가진 재개 입력을 검증합니다."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from evals.harness import grade, prepare
from gtg.discovery import discover
from gtg.runner import status
from gtg.sessions import Sessions
from gtg.store import Store


ROOT = Path(__file__).resolve().parents[1]


class ResumeEvalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.trial = Path(self.temp.name).resolve() / "trial"

    def test_gtg_setup_contains_one_partial_task_and_a_newer_completed_task(self):
        prepared = prepare("resume-export", self.trial, "gtg")
        self.assertFalse(prepared["model_called"])
        self.assertNotIn("/", prepared["prompt"])
        manifest = json.loads((self.trial / "manifest.json").read_text())
        seeded = manifest["seeded_progress"]
        workspace = self.trial / "workspace"
        store = Store(workspace / ".gtg/state.sqlite3")
        self.addCleanup(store.close)
        partial = status(store, seeded["task_id"])
        self.assertEqual([c["status"] for c in partial["checks"]], ["passed", "pending"])
        self.assertTrue(partial["checkpoint"]["files_unchanged"])
        self.assertTrue(Sessions(store).for_task(seeded["task_id"])[0]["paused"])
        self.assertTrue(status(store, seeded["completed_task_id"])["verified"])
        listed = discover(workspace, workspace / ".gtg/state.sqlite3")
        self.assertEqual(listed["tasks"][0]["task_id"], seeded["completed_task_id"])
        self.assertIn('DOWNLOAD_STEM = "현장 기록"', (workspace / "app.py").read_text())

    def test_partial_fixture_fails_and_only_connecting_the_existing_helper_passes(self):
        prepare("resume-export", self.trial)
        self.assertFalse(grade(self.trial)["artifact_passed"])
        app = self.trial / "workspace/app.py"
        content = app.read_text().replace("import to_json", "import to_json, to_csv")
        content = content.replace('    if format != "json":',
                                  '    if format == "csv":\n        return {"filename": DOWNLOAD_STEM + ".csv",\n                "media_type": "text/csv; charset=utf-8", "content": to_csv(records)}\n    if format != "json":')
        app.write_text(content)
        result = grade(self.trial)
        self.assertTrue(result["artifact_passed"])
        self.assertFalse(result["model_performance_claim"])
        self.assertEqual(len(result["checks"]), 8)

    def test_baseline_has_same_visible_progress_without_installing_gtg(self):
        prepare("resume-export", self.trial)
        self.assertTrue((self.trial / "workspace/progress.json").is_file())
        self.assertFalse((self.trial / "workspace/.gtg").exists())
        self.assertIsNone(json.loads((self.trial / "manifest.json").read_text())["seeded_progress"])

    def test_existing_module_and_script_entrypoints_remain_available(self):
        for command in ([sys.executable, "-m", "evals.harness", "--help"],
                        [sys.executable, str(ROOT / "evals/harness.py"), "--help"]):
            with self.subTest(command=command):
                result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("prepare", result.stdout)
                self.assertIn("grade", result.stdout)


if __name__ == "__main__":
    unittest.main()
