"""모든 팔에 같은 요청 문자열을 기계적으로 전달하고 실행 관측을 기록합니다."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from evals.execution import run_arm
from evals.preparation import prepare


ROOT = Path(__file__).resolve().parents[1]


def fake_harness(target: Path, body: str, name: str = "fake_harness") -> Path:
    """시험용 가짜 하네스입니다. 이름을 달리하면 서로 다른 동작을 비교할 수 있습니다."""
    path = target / (name + ".py")
    path.write_text("import sys, pathlib\n" + body, encoding="utf-8")
    return path


class RunArmTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.trial = self.root / "trial"
        prepare("bounds", self.trial, "baseline", arm="fake", model="none")
        self.prompt = (self.trial / "prompt.txt").read_text(encoding="utf-8").strip()

    def test_prepared_prompt_is_passed_verbatim_and_observed(self):
        script = fake_harness(self.root, "pathlib.Path('got.txt').write_text(sys.argv[1])\n")
        result = run_arm(self.trial, [sys.executable, str(script), "{prompt}"])
        self.assertTrue(result["ok"])
        self.assertEqual(result["returncode"], 0)
        self.assertGreater(result["duration_seconds"], 0)
        self.assertEqual((self.trial / "workspace/got.txt").read_text(), self.prompt)
        manifest = json.loads((self.trial / "manifest.json").read_text())
        observation = manifest["runtime_observation"]
        self.assertEqual(observation["returncode"], 0)
        self.assertEqual(observation["prompt_sha256"], manifest["prompt_sha256"])
        self.assertEqual(observation["command"], [sys.executable, str(script), "{prompt}"])

    def test_missing_placeholder_is_refused(self):
        with self.assertRaisesRegex(ValueError, "prompt"):
            run_arm(self.trial, [sys.executable, "-c", "pass"])

    def test_failing_arm_is_recorded_rather_than_hidden(self):
        script = fake_harness(self.root, "raise SystemExit(3)\n")
        result = run_arm(self.trial, [sys.executable, str(script), "{prompt}"])
        self.assertFalse(result["ok"])
        self.assertEqual(result["returncode"], 3)
        manifest = json.loads((self.trial / "manifest.json").read_text())
        self.assertEqual(manifest["runtime_observation"]["returncode"], 3)

    def test_second_run_is_refused_so_one_trial_is_one_attempt(self):
        script = fake_harness(self.root, "pass\n")
        run_arm(self.trial, [sys.executable, str(script), "{prompt}"])
        with self.assertRaisesRegex(ValueError, "이미"):
            run_arm(self.trial, [sys.executable, str(script), "{prompt}"])

    def test_timeout_is_recorded_and_does_not_leave_the_child_running(self):
        script = fake_harness(self.root, "import time\ntime.sleep(30)\n")
        result = run_arm(self.trial, [sys.executable, str(script), "{prompt}"], timeout=1)
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "timeout")
        manifest = json.loads((self.trial / "manifest.json").read_text())
        self.assertEqual(manifest["runtime_observation"]["status"], "timeout")

    def test_grade_report_carries_the_observation(self):
        from evals.grading import grade

        script = fake_harness(self.root, """
source = pathlib.Path('mathlib.py')
source.write_text('''def clamp(value, lower, upper):
    if lower > upper:
        raise ValueError("lower must not exceed upper")
    return max(lower, min(value, upper))
''')
""")
        run_arm(self.trial, [sys.executable, str(script), "{prompt}"])
        report = grade(self.trial)
        self.assertTrue(report["artifact_passed"])
        self.assertEqual(report["runtime_observation"]["returncode"], 0)
        self.assertGreater(report["runtime_observation"]["duration_seconds"], 0)


class ComparisonDurationTests(unittest.TestCase):
    def test_compare_reports_observed_duration_per_arm(self):
        from evals.comparison import compare
        from evals.grading import grade

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            script = fake_harness(root, """
source = pathlib.Path('mathlib.py')
source.write_text('''def clamp(value, lower, upper):
    if lower > upper:
        raise ValueError("lower must not exceed upper")
    return max(lower, min(value, upper))
''')
""")
            trials = []
            for arm in ("alpha", "beta"):
                trial = root / arm
                prepare("bounds", trial, "baseline", arm=arm, model="none")
                run_arm(trial, [sys.executable, str(script), "{prompt}"])
                grade(trial)
                trials.append(trial)
            report = compare(trials)
            self.assertTrue(report["comparable"], report["blocking_reasons"])
            for entry in report["arms"]:
                self.assertGreater(entry["total_duration_seconds"], 0)
                self.assertEqual(entry["unobserved_runs"], 0)


class CliRunTests(unittest.TestCase):
    def test_cli_exposes_run_after_a_separator(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            trial = root / "trial"
            prepare("bounds", trial, "baseline", arm="cli", model="none")
            script = fake_harness(root, "pathlib.Path('seen.txt').write_text(sys.argv[1])\n")
            done = subprocess.run([sys.executable, "-m", "evals.harness", "run", str(trial),
                                   "--", sys.executable, str(script), "{prompt}"],
                                  cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertTrue(json.loads(done.stdout)["ok"])
            self.assertTrue((trial / "workspace/seen.txt").exists())


class ExecutionObservationTests(unittest.TestCase):
    """하네스가 실제로 프로젝트 코드를 실행했는지 자기 보고 없이 관측합니다."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.trial = self.root / "trial"
        prepare("bounds", self.trial, "baseline", arm="probe", model="none")

    def observation(self):
        return json.loads((self.trial / "manifest.json").read_text())["runtime_observation"]

    def test_arm_that_runs_the_project_tests_is_observed(self):
        script = fake_harness(self.root, """
import subprocess, sys
subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', '.'], check=False)
""")
        run_arm(self.trial, [sys.executable, str(script), "{prompt}"])
        observed = self.observation()
        self.assertGreater(observed["executed_workspace_file_count"], 0)
        self.assertIn("mathlib.py", observed["executed_workspace_files"])

    def test_arm_that_only_edits_without_running_is_observed_as_such(self):
        script = fake_harness(self.root, """
source = pathlib.Path('mathlib.py')
source.write_text('def clamp(value, lower, upper):\\n    return value\\n')
""")
        run_arm(self.trial, [sys.executable, str(script), "{prompt}"])
        observed = self.observation()
        self.assertEqual(observed["executed_workspace_files"], [],
                         "편집만 하고 실행하지 않은 것이 그대로 드러나야 합니다.")
        self.assertEqual(observed["executed_workspace_file_count"], 0)

    def test_comparison_counts_runs_that_executed_project_code(self):
        from evals.comparison import compare
        from evals.grading import grade

        fixed = """
source = pathlib.Path('mathlib.py')
source.write_text('''def clamp(value, lower, upper):
    if lower > upper:
        raise ValueError("lower must not exceed upper")
    return max(lower, min(value, upper))
''')
"""
        running = fake_harness(self.root, fixed + """
import subprocess, sys
subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', '.'], check=False)
""", name="runs_tests")
        quiet = fake_harness(self.root, fixed, name="edits_only")
        trials = []
        for arm, script in (("runs-tests", running), ("edits-only", quiet)):
            trial = self.root / arm
            prepare("bounds", trial, "baseline", arm=arm, model="none")
            run_arm(trial, [sys.executable, str(script), "{prompt}"])
            grade(trial)
            trials.append(trial)
        report = compare(trials)
        self.assertTrue(report["comparable"], report["blocking_reasons"])
        counts = {arm["arm"]: arm["runs_that_executed_code"] for arm in report["arms"]}
        self.assertEqual(counts, {"runs-tests": 1, "edits-only": 0})
        passed = {arm["arm"]: arm["passed"] for arm in report["arms"]}
        self.assertEqual(passed, {"runs-tests": 1, "edits-only": 1},
                         "산출물 점수는 같아도 실행 관측은 다릅니다.")


if __name__ == "__main__":
    unittest.main()
