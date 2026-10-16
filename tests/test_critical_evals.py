"""의미 판단을 자동 통과시키지 않고 독립 검토 기준과 변경 위반을 보존합니다."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

from evals.comparison import compare
from evals.definitions import CASES
from evals.execution import run_arm
from evals.grading import grade
from evals.preparation import prepare


class CriticalEvaluationTests(unittest.TestCase):
    def test_each_review_case_retains_independent_criteria_without_auto_passing(self):
        cases = json.loads(CASES.read_text(encoding="utf-8"))["cases"]
        for case_id, case in cases.items():
            if case.get("fixture") != "critical-review":
                continue
            with self.subTest(case=case_id), tempfile.TemporaryDirectory() as directory:
                trial = Path(directory).resolve() / "trial"
                prepare(case_id, trial)
                result = grade(trial)
                self.assertTrue(result["scope_passed"])
                self.assertIsNone(result["functional_passed"])
                self.assertFalse(result["artifact_passed"])
                self.assertTrue(result["requires_human_review"])
                self.assertEqual(result["human_review_criteria"], case["human_review_criteria"])
                self.assertTrue(result["human_review_criteria"])
                for criterion in result["human_review_criteria"]:
                    self.assertTrue(criterion["requirement"])
                    for source in criterion["evidence"]:
                        self.assertTrue((trial / "workspace" / source).is_file())
                # 채점 기준은 작업 폴더에 배포하지 않습니다. 공개 사례이므로 비밀을 보장하지는 않습니다.
                self.assertFalse((trial / "workspace/cases.json").exists())
                self.assertFalse(result["model_performance_claim"])

    def test_read_only_review_fails_scope_when_candidate_rewrites_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            trial = Path(directory).resolve() / "trial"
            prepare("critical-environment", trial, "gtg")
            (trial / "workspace/evidence.md").write_text("모든 조건에서 통과했습니다.\n", encoding="utf-8")
            result = grade(trial)
            self.assertFalse(result["scope_passed"])
            self.assertEqual(result["scope_violations"], ["evidence.md"])
            self.assertFalse(result["artifact_passed"])

    def test_confident_false_answer_is_preserved_for_review_instead_of_scored_as_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            trials = []
            for arm in ("one", "two"):
                trial = root / arm
                prepare("critical-facts", trial, arm=arm)
                run_arm(trial, [sys.executable, "-c", "import sys; print('모든 API와 실사용 안정성이 검증됐습니다.')", "{prompt}"],
                        timeout=30)
                result = grade(trial)
                self.assertTrue(result["scope_passed"])
                self.assertTrue(result["requires_human_review"])
                self.assertFalse(result["artifact_passed"])
                self.assertIn("실사용 안정성", (trial / "arm-stdout.log").read_text(encoding="utf-8"))
                trials.append(trial)
            report = compare(trials)
            self.assertFalse(report["comparable"])
            self.assertIn("human_review", report["blocking_reasons"])

if __name__ == "__main__":
    unittest.main()
