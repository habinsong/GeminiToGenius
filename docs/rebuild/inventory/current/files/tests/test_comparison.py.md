# `tests/test_comparison.py`

- 형식: `100644`
- 바이트: 6954
- SHA-256: `4b67e9939117de6d0a7860f5375fa156f6decfbc117883f46fb67bb9456b74f3`
- 인코딩: `utf-8`

```
"""같은 조건에서만 하네스를 비교하고, 조건이 다르면 승패를 만들지 않습니다."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from evals.comparison import compare
from evals.preparation import prepare


ROOT = Path(__file__).resolve().parents[1]


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.counter = 0

    def trial(self, arm, case_id="bounds", *, passed=True, prompt="p1", definition="d1", model="model-a",
              reports=None):
        self.counter += 1
        target = self.root / f"trial-{self.counter}"
        (target / "grades").mkdir(parents=True)
        manifest = {"schema_version": 1, "trial_id": f"t{self.counter}", "case_id": case_id, "profile": "baseline",
                    "arm": arm, "model": model, "definition_digest": definition, "prompt_sha256": prompt}
        (target / "manifest.json").write_text(json.dumps(manifest))
        for index, outcome in enumerate(reports if reports is not None else [passed]):
            grade = {"kind": "artifact_grade", "trial_id": manifest["trial_id"], "case_id": case_id,
                     "definition_digest": definition, "prompt_sha256": prompt, "profile": "baseline",
                     "checked_at": f"2026-09-08T0{index}:00:00+00:00", "artifact_passed": outcome,
                     "scope_passed": outcome, "functional_passed": outcome, "requires_human_review": False,
                     "scope_violations": [] if outcome else ["app.py"]}
            (target / "grades" / f"{index}.json").write_text(json.dumps(grade))
        return target

    def test_same_conditions_produce_a_per_arm_result(self):
        trials = [self.trial("gtg"), self.trial("gtg", "report-export"),
                  self.trial("codex-cli", passed=False), self.trial("codex-cli", "report-export")]
        report = compare(trials)
        self.assertTrue(report["comparable"])
        self.assertEqual(report["blocking_reasons"], [])
        arms = {arm["arm"]: arm for arm in report["arms"]}
        self.assertEqual(arms["gtg"]["passed"], 2)
        self.assertEqual(arms["codex-cli"]["passed"], 1)
        self.assertEqual(arms["gtg"]["trials"], 2)
        self.assertEqual(sorted(arms["codex-cli"]["cases"]), ["bounds", "report-export"])
        self.assertTrue(report["labels_are_self_declared"])
        self.assertFalse(report["model_performance_claim"])

    def test_different_grading_definitions_block_the_comparison(self):
        report = compare([self.trial("gtg"), self.trial("codex-cli", definition="d2")])
        self.assertFalse(report["comparable"])
        self.assertIn("definition_digest", report["blocking_reasons"])

    def test_different_prompts_for_the_same_case_block_the_comparison(self):
        report = compare([self.trial("gtg"), self.trial("codex-cli", prompt="p2")])
        self.assertFalse(report["comparable"])
        self.assertIn("prompt_sha256", report["blocking_reasons"])

    def test_unequal_case_coverage_blocks_the_comparison(self):
        report = compare([self.trial("gtg"), self.trial("gtg", "report-export"), self.trial("codex-cli")])
        self.assertFalse(report["comparable"])
        self.assertIn("case_coverage", report["blocking_reasons"])

    def test_conflicting_reports_are_not_silently_resolved(self):
        trials = [self.trial("gtg", reports=[False, True]), self.trial("codex-cli")]
        report = compare(trials)
        self.assertFalse(report["comparable"])
        self.assertIn("unstable_grades", report["blocking_reasons"])
        arms = {arm["arm"]: arm for arm in report["arms"]}
        self.assertEqual(arms["gtg"]["unstable"], 1)
        self.assertEqual(arms["gtg"]["passed"], 0, "엇갈린 결과를 통과로 세지 않습니다.")

    def test_ungraded_trial_is_reported_instead_of_counted_as_a_loss(self):
        pending = self.trial("codex-cli")
        for report_file in (pending / "grades").iterdir():
            report_file.unlink()
        report = compare([self.trial("gtg"), pending])
        self.assertFalse(report["comparable"])
        self.assertIn("ungraded", report["blocking_reasons"])
        arms = {arm["arm"]: arm for arm in report["arms"]}
        self.assertEqual(arms["codex-cli"]["ungraded"], 1)
        self.assertEqual(arms["codex-cli"]["trials"], 1)
        self.assertEqual(arms["codex-cli"]["passed"], 0)

    def test_one_arm_alone_is_not_a_comparison(self):
        report = compare([self.trial("gtg"), self.trial("gtg", "report-export")])
        self.assertFalse(report["comparable"])
        self.assertIn("single_arm", report["blocking_reasons"])

    def test_same_arm_label_with_two_models_stays_separate(self):
        report = compare([self.trial("gtg", model="model-a"), self.trial("gtg", model="model-b")])
        self.assertEqual({(arm["arm"], arm["model"]) for arm in report["arms"]},
                         {("gtg", "model-a"), ("gtg", "model-b")})


class PreparedArmTests(unittest.TestCase):
    def test_prepare_records_the_declared_arm_and_model_without_installing_for_baseline(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory).resolve() / "trial"
            prepare("bounds", target, "baseline", arm="codex-cli", model="gpt-x")
            manifest = json.loads((target / "manifest.json").read_text())
            self.assertEqual(manifest["arm"], "codex-cli")
            self.assertEqual(manifest["model"], "gpt-x")
            self.assertFalse((target / "workspace/.agents/plugins/geminitogenius").exists())

    def test_arm_defaults_to_the_profile_name(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory).resolve() / "trial"
            prepare("bounds", target, "baseline")
            manifest = json.loads((target / "manifest.json").read_text())
            self.assertEqual(manifest["arm"], "baseline")
            self.assertIsNone(manifest["model"])

    def test_cli_reports_blocking_reasons_with_a_nonzero_exit_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            first, second = root / "a", root / "b"
            prepare("bounds", first, "baseline", arm="one")
            prepare("bounds", second, "baseline", arm="two")
            done = subprocess.run([sys.executable, "-m", "evals.harness", "compare", str(first), str(second)],
                                  cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
            report = json.loads(done.stdout)
            self.assertFalse(report["comparable"])
            self.assertIn("ungraded", report["blocking_reasons"])


if __name__ == "__main__":
    unittest.main()
```
