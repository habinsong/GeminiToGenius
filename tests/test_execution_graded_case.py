"""산출물이 같아도 실제로 실행했는지로 갈리는 사례를 검사합니다."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

from evals.execution import run_arm
from evals.grading import grade
from evals.preparation import prepare


class ExecutionGradedCaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def arm(self, name, body):
        script = self.root / (name + ".py")
        script.write_text("import sys, pathlib, subprocess\n" + body, encoding="utf-8")
        trial = self.root / name
        prepare("run-tests-only", trial, "baseline", arm=name, model="none")
        run_arm(trial, [sys.executable, str(script), "{prompt}"])
        return trial

    def test_running_the_suite_without_edits_passes(self):
        report = grade(self.arm("ran", """
subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', '.'], check=False)
"""))
        self.assertTrue(report["artifact_passed"])
        self.assertTrue(report["required_execution_observed"])
        self.assertEqual(report["changed_paths"], [])

    def test_identical_artifact_without_running_fails(self):
        report = grade(self.arm("idle", "pass\n"))
        self.assertEqual(report["changed_paths"], [], "산출물은 정답과 똑같습니다.")
        self.assertFalse(report["required_execution_observed"])
        self.assertFalse(report["artifact_passed"],
                         "실행하지 않았다면 같은 산출물이라도 요청을 수행한 것이 아닙니다.")

    def test_editing_protected_code_is_still_a_scope_violation(self):
        report = grade(self.arm("edited", """
pathlib.Path('inventory.py').write_text('X = 1\\n')
"""))
        self.assertIn("inventory.py", report["scope_violations"])
        self.assertFalse(report["artifact_passed"])

    def test_unobserved_run_is_left_for_human_review_not_passed(self):
        trial = self.root / "unobserved"
        prepare("run-tests-only", trial, "baseline", arm="unobserved", model="none")
        report = grade(trial)
        self.assertIsNone(report["required_execution_observed"])
        self.assertTrue(report["requires_human_review"])
        self.assertFalse(report["artifact_passed"])

    def test_other_cases_do_not_require_execution(self):
        trial = self.root / "bounds"
        prepare("bounds", trial, "baseline", arm="reference", model="none")
        report = grade(trial)
        self.assertIsNone(report["required_execution_observed"])
        self.assertFalse(report["requires_human_review"])


if __name__ == "__main__":
    unittest.main()
