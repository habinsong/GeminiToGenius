"""필수 시험 누락·skip·컴파일 이후의 참조 오류를 실제 실행으로 잡습니다."""

from pathlib import Path
import os
import py_compile
import subprocess
import sys
import tempfile
import unittest

from gtg.testing import run_unittest


class RequiredUnittestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.test = self.root / "test_app.py"
        (self.root / "sdk.py").write_text("def encode(value):\n    return value\n")
        self.test.write_text("import unittest\nclass Checks(unittest.TestCase):\n    def test_good(self):\n        self.assertEqual(2 + 2, 4)\n")
        self.required = "test_app.Checks.test_good"

    def test_success_requires_real_executed_cases_and_required_ids(self):
        result = run_unittest(self.root, required=[self.required])
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["observation"]["tests_run"], 1)
        self.assertEqual(result["required_not_passed"], [])

    def test_empty_discovery_does_not_pass(self):
        self.test.unlink()
        result = run_unittest(self.root)
        self.assertFalse(result["passed"])
        self.assertEqual(result["observation"]["tests_run"], 0)

    def test_unrelated_success_does_not_cover_a_missing_required_test(self):
        # 기본 unittest에서는 관련 없는 시험 하나만 실행해도 성공합니다.
        native = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", str(self.root)],
                                capture_output=True)
        self.assertEqual(native.returncode, 0)
        required = "test_app.Checks.test_prd_missing"
        result = run_unittest(self.root, required=[required])
        self.assertFalse(result["passed"])
        self.assertEqual(result["required_not_passed"], [required])

    def test_required_skipped_or_expected_failure_case_is_not_a_success(self):
        for decorator, assertion in (("skip('대상 환경 없음')", "self.assertTrue(True)"),
                                      ("expectedFailure", "self.fail('미구현')")):
            with self.subTest(decorator=decorator):
                self.test.write_text("import unittest\nclass Checks(unittest.TestCase):\n"
                                     "    def test_other(self):\n        self.assertTrue(True)\n"
                                     f"    @unittest.{decorator}\n    def test_good(self):\n        {assertion}\n")
                result = run_unittest(self.root, required=[self.required])
                self.assertFalse(result["passed"])
                self.assertEqual(result["required_not_passed"], [self.required])

    def test_all_skipped_suite_without_explicit_ids_does_not_pass(self):
        self.test.write_text("import unittest\n@unittest.skip('불가')\nclass Checks(unittest.TestCase):\n"
                             "    def test_good(self):\n        pass\n")
        result = run_unittest(self.root)
        self.assertFalse(result["passed"])

    def test_syntax_valid_but_nonexistent_api_field_and_function_fail(self):
        for body in ("from sdk import nonexistent_api", "self.nonexistent_field", "nonexistent_function()"):
            with self.subTest(body=body):
                self.test.write_text("import unittest\nclass Checks(unittest.TestCase):\n    def test_good(self):\n        " + body + "\n")
                compile(self.test.read_text(), "test_app.py", "exec")
                result = run_unittest(self.root, required=[self.required])
                self.assertFalse(result["passed"])
                self.assertGreater(result["observation"]["errors"], 0)

    def test_early_process_exit_is_not_a_valid_observation(self):
        for body in ("raise SystemExit(0)", "import os; os._exit(0)"):
            with self.subTest(body=body):
                self.test.write_text(body + "\n")
                self.assertFalse(run_unittest(self.root, required=[self.required])["passed"])

    def test_sibling_or_linked_discovery_paths_are_rejected(self):
        for path in ("../", ".gtg"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                run_unittest(self.root, path)
        (self.root / "link").symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            run_unittest(self.root, "link")

    def test_subprocess_output_does_not_corrupt_the_observation(self):
        self.test.write_text("import unittest, subprocess, sys\nclass Checks(unittest.TestCase):\n"
                             "    def test_good(self):\n"
                             "        subprocess.run([sys.executable, '-c', \"print('native-output')\"], check=True)\n")
        self.assertTrue(run_unittest(self.root, required=[self.required])["passed"])

    def test_stale_bytecode_does_not_replace_current_source(self):
        source = self.root / "api.py"
        source.write_text("def value():\n    return 1\n")
        timestamp = source.stat().st_mtime
        py_compile.compile(str(source), doraise=True)
        source.write_text("def value():\n    return 2\n")
        os.utime(source, (timestamp, timestamp))
        self.test.write_text("import unittest\nfrom api import value\nclass Checks(unittest.TestCase):\n"
                             "    def test_good(self):\n        self.assertEqual(value(), 1)\n")
        cached = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", str(self.root)],
                                cwd=self.root, capture_output=True)
        self.assertEqual(cached.returncode, 0, "오래된 캐시가 기존 성공 코드를 읽는 대조 경로입니다.")
        self.assertFalse(run_unittest(self.root, required=[self.required])["passed"])


if __name__ == "__main__":
    unittest.main()
