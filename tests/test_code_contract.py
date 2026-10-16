"""빌드·필수 시험·PRD 근거를 고정하고 이전 시험 성공의 재사용을 제한합니다."""

import copy
from pathlib import Path
import sys
import tempfile
import unittest

from gtg.certificate import build as certificate, replay
from gtg.runner import execute, status
from gtg.store import Store


class CodeContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "app.py").write_text("def render(value):\n    return value.strip()\n")
        (self.root / "PRD.md").write_text("UT-01: 양끝 공백을 제거하고 내부 공백을 유지합니다.\n")
        (self.root / "check.py").write_text(
            "from pathlib import Path\nfrom app import render\n"
            "Path('test-ran').touch()\nassert render('  a b  ') == 'a b'\n")
        self.spec = {"schema_version": 1, "goal": "문자열 출력과 PRD 시험을 검증합니다.", "checks": [
            {"id": "build", "criterion": "제품 소스를 컴파일합니다.", "watch": ["app.py"],
             "argv": [sys.executable, "-c", "from pathlib import Path; compile(Path('app.py').read_text(), 'app.py', 'exec')"]},
            {"id": "unit", "criterion": "PRD UT-01을 실제 호출로 검사합니다.", "watch": ["check.py"],
             "argv": [sys.executable, "check.py"]}],
            "code_contract": {"build_check": "build", "test_checks": ["unit"],
                              "requirements": [{"id": "UT-01", "source": "PRD.md", "checks": ["unit"]}]}}
        self.store = Store(self.root / ".gtg/state.sqlite3")
        self.addCleanup(self.store.close)

    def task(self):
        return self.store.create(self.root, self.spec)

    def test_invalid_or_incomplete_code_contract_is_rejected_at_registration(self):
        policies = [None, {}, {"build_check": "missing", "test_checks": ["unit"]},
                    {"build_check": "build", "test_checks": []},
                    {"build_check": "build", "test_checks": ["build"]},
                    {"build_check": "build", "test_checks": ["unknown"]},
                    {"build_check": "unit", "test_checks": ["build"]},
                    {"build_check": "build", "test_checks": ["unit"], "typo": True},
                    {"build_check": "build", "test_checks": ["unit"], "requirements": [
                        {"id": "UT-01", "source": "PRD.md", "checks": []}]}]
        for policy in policies:
            spec = {**copy.deepcopy(self.spec), "code_contract": policy}
            with self.subTest(policy=policy), self.assertRaises(ValueError):
                self.store.create(self.root, spec)

    def test_missing_or_linked_prd_cannot_be_registered_as_existing_evidence(self):
        (self.root / "PRD.md").unlink()
        with self.assertRaises(ValueError):
            self.task()
        (self.root / "other.md").write_text("원본")
        (self.root / "PRD.md").symlink_to(self.root / "other.md")
        with self.assertRaises(ValueError):
            self.task()

    def test_tests_do_not_execute_without_a_current_successful_build(self):
        task = self.task()
        result = execute(self.store, task, "unit")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse((self.root / "test-ran").exists())
        (self.root / "app.py").write_text("def broken(:\n")
        self.assertEqual(execute(self.store, task, "build")["status"], "failed")
        self.assertEqual(execute(self.store, task, "unit")["status"], "blocked")
        self.assertFalse(certificate(self.store, task)["verified"])

    def test_symbol_or_field_fabrication_can_compile_but_cannot_pass_actual_calls(self):
        task = self.task()
        for implementation in ("return value.nonexistent_field", "return nonexistent_function(value)"):
            with self.subTest(implementation=implementation):
                (self.root / "app.py").write_text("def render(value):\n    " + implementation + "\n")
                self.assertEqual(execute(self.store, task, "build")["status"], "passed")
                self.assertEqual(execute(self.store, task, "unit")["status"], "failed")
                self.assertFalse(status(self.store, task)["verified"])

    def test_prd_and_build_inputs_invalidate_test_success_and_build_rerun_requires_fresh_tests(self):
        task = self.task()
        self.assertEqual(execute(self.store, task, "build")["status"], "passed")
        self.assertEqual(execute(self.store, task, "unit")["status"], "passed")
        report = status(self.store, task)
        self.assertTrue(report["verified"])
        self.assertTrue(report["requirements"][0]["verified"])
        self.assertTrue(report["code_contract_enforced"])
        self.assertEqual(execute(self.store, task, "build")["status"], "passed")
        self.assertEqual(status(self.store, task)["checks"][1]["status"], "stale")
        self.assertEqual(execute(self.store, task, "unit")["status"], "passed")
        (self.root / "PRD.md").write_text("UT-01: 요구 변경. 추가 검토가 필요합니다.\n")
        report = status(self.store, task)
        self.assertFalse(report["verified"])
        self.assertFalse(report["requirements"][0]["verified"])
        self.assertEqual(report["checks"][0]["status"], "stale")
        self.assertEqual(execute(self.store, task, "unit")["status"], "blocked")

    def test_replay_preserves_build_dependency_and_does_not_run_tests_after_compile_failure(self):
        task = self.task()
        execute(self.store, task, "build")
        execute(self.store, task, "unit")
        document = certificate(self.store, task)
        self.assertEqual(document["checks"][1]["depends_on"], ["build"])
        self.assertTrue(replay(document, self.root)["reconstructed"])
        (self.root / "test-ran").unlink()
        (self.root / "app.py").write_text("def broken(:\n")
        result = replay(document, self.root)
        self.assertEqual(result["verdict"], "invalid")
        self.assertEqual(result["checks"][1]["reason"], "prerequisite")
        self.assertFalse((self.root / "test-ran").exists())


if __name__ == "__main__":
    unittest.main()
