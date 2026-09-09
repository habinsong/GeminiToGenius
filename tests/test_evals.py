"""에이전트용 테스트를 바꿔도 독립 결과 검사를 속이지 못하는지 확인합니다."""

import json
import os
from pathlib import Path
import py_compile
import subprocess
import sys
import tempfile
import unittest

from evals.harness import grade, prepare


CLAMP = """def clamp(value, lower, upper):
    if lower > upper:
        raise ValueError('invalid range')
    return max(lower, min(value, upper))
"""
MERGE = """def merge_records(records):
    merged = {}
    for record in records:
        if 'id' not in record:
            raise ValueError('missing id')
        merged.setdefault(record['id'], {}).update(record)
    return list(merged.values())
"""


class HarnessOwnFilesTests(unittest.TestCase):
    """설치된 하네스 자체 파일이 '코드를 실행했다'로 세어지면 안 됩니다."""

    def test_verification_cases_fail_untouched_and_pass_when_fixed(self):
        """검증을 실제로 돌려야 통과하는 사례입니다. 함정이 살아 있는지 고정합니다."""
        from evals.grading import grade
        from evals.preparation import prepare
        fixes = {
            "test-encodes-bug": [
                ("shipping.py", "max(weight_kg - FREE_LIMIT + 1, 0)", "max(weight_kg - FREE_LIMIT, 0)"),
                ("test_shipping.py", "shipping_fee(5), 3500", "shipping_fee(5), 3000"),
                ("test_shipping.py", "shipping_fee(6), 4000", "shipping_fee(6), 3500")],
            "cross-module-break": [
                ("currency.py", 'f"{amount}원"', 'f"{amount:,}원"'),
                ("test_receipt.py", '"커피: 4500원\\n빵: 12000원"', '"커피: 4,500원\\n빵: 12,000원"')],
        }
        for case, edits in fixes.items():
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                untouched, fixed = root / "u", root / "f"
                prepare(case, untouched, "baseline")
                prepare(case, fixed, "baseline")
                self.assertFalse(grade(untouched)["artifact_passed"],
                                 "손대지 않은 상태가 통과하면 사례가 아무것도 재지 않습니다.")
                partial = edits[0]
                path = fixed / "workspace" / partial[0]
                path.write_text(path.read_text(encoding="utf-8").replace(partial[1], partial[2]),
                                encoding="utf-8")
                self.assertFalse(grade(fixed)["artifact_passed"],
                                 "코드만 고치고 검사를 두고 가면 통과하면 안 됩니다.")
                for name, old, new in edits[1:]:
                    path = fixed / "workspace" / name
                    self.assertIn(old, path.read_text(encoding="utf-8"))
                    path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
                self.assertTrue(grade(fixed)["artifact_passed"],
                                "올바른 수정은 통과해야 합니다.")

    def test_installed_plugin_files_are_not_counted_as_project_code(self):
        from evals.execution import workspace_files
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory).resolve()
            observed = [workspace / ".agents/plugins/geminitogenius/gtg/store.py",
                        workspace / ".agents/plugins/geminitogenius/run.py",
                        workspace / "mathlib.py"]
            self.assertEqual(workspace_files(observed, workspace), ["mathlib.py"])

    def test_scope_grading_still_watches_the_installed_harness(self):
        """실행 관측에서 뺀 것이 채점의 감시까지 푸는 것은 아닙니다."""
        from evals.workspace import private
        self.assertFalse(private(Path(".agents/plugins/geminitogenius/rules/AGENTS.md")))

class EvalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.trial = Path(self.temp.name).resolve() / "trial"

    def test_buggy_fixture_fails_and_reference_fix_passes_without_model_claim(self):
        prepare("bounds", self.trial)
        self.assertFalse(grade(self.trial)["artifact_passed"])
        (self.trial / "workspace/mathlib.py").write_text(CLAMP)
        result = grade(self.trial)
        self.assertTrue(result["artifact_passed"])
        self.assertFalse(result["model_performance_claim"])
        self.assertEqual(len(list((self.trial / "grades").glob("*.json"))), 2)

    def test_rewriting_visible_tests_does_not_make_wrong_code_pass(self):
        prepare("bounds", self.trial)
        (self.trial / "workspace/test_mathlib.py").write_text("# 검사를 없애도 실제 결과 검사는 남습니다.\n")
        self.assertFalse(grade(self.trial)["artifact_passed"])

    def test_unrelated_user_file_changes_fail_even_with_correct_code(self):
        prepare("bounds", self.trial)
        (self.trial / "workspace/mathlib.py").write_text(CLAMP)
        (self.trial / "workspace/notes.txt").write_text("deleted original work")
        result = grade(self.trial)
        self.assertTrue(result["functional_passed"])
        self.assertFalse(result["artifact_passed"])
        self.assertEqual(result["scope_violations"], ["notes.txt"])

    def test_multi_file_task_checks_error_and_input_preservation(self):
        prepare("merge-records", self.trial)
        self.assertFalse(grade(self.trial)["artifact_passed"])
        (self.trial / "workspace/records.py").write_text(MERGE)
        self.assertTrue(grade(self.trial)["artifact_passed"])
        mutating = MERGE.replace("return list(merged.values())", "records.clear()\n    return list(merged.values())")
        (self.trial / "workspace/records.py").write_text(mutating)
        self.assertFalse(grade(self.trial)["artifact_passed"])

    def test_multi_file_task_does_not_pass_with_a_broken_existing_caller(self):
        prepare("merge-records", self.trial)
        (self.trial / "workspace/records.py").write_text(MERGE)
        (self.trial / "workspace/app.py").write_text("def summarize(records):\n    return {'items': []}\n")
        self.assertFalse(grade(self.trial)["artifact_passed"])

    def test_read_only_task_cannot_pass_without_human_review(self):
        prepare("inspect-only", self.trial)
        result = grade(self.trial)
        self.assertTrue(result["scope_passed"])
        self.assertTrue(result["requires_human_review"])
        self.assertFalse(result["artifact_passed"])
        (self.trial / "workspace/mathlib.py").write_text(CLAMP)
        self.assertFalse(grade(self.trial)["scope_passed"])

    def test_early_success_exit_is_not_a_valid_test_result(self):
        prepare("bounds", self.trial)
        (self.trial / "workspace/mathlib.py").write_text("raise SystemExit(0)\n")
        result = grade(self.trial)
        self.assertFalse(result["artifact_passed"])
        self.assertEqual(result["execution"]["error"], "invalid_candidate_output")

    def test_boolean_cannot_replace_a_numeric_result(self):
        prepare("bounds", self.trial)
        incorrect = CLAMP.replace("return max(lower, min(value, upper))", "result = max(lower, min(value, upper))\n    return False if result == 0 else result")
        (self.trial / "workspace/mathlib.py").write_text(incorrect)
        self.assertFalse(grade(self.trial)["artifact_passed"])
        numeric = CLAMP.replace("return max(lower, min(value, upper))", "return float(max(lower, min(value, upper)))")
        (self.trial / "workspace/mathlib.py").write_text(numeric)
        self.assertTrue(grade(self.trial)["artifact_passed"])

    def test_prepared_trial_is_not_overwritten_and_modified_criteria_are_rejected(self):
        prepare("bounds", self.trial)
        with self.assertRaises(ValueError):
            prepare("bounds", self.trial)
        path = self.trial / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest["definition_digest"] = "changed"
        path.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            grade(self.trial)

    def test_gtg_preparation_is_local_and_protects_installed_harness(self):
        result = prepare("bounds", self.trial, "gtg")
        self.assertFalse(result["model_called"])
        plugin = self.trial / "workspace/.agents/plugins/geminitogenius/rules/AGENTS.md"
        self.assertTrue(plugin.is_file())
        (self.trial / "workspace/mathlib.py").write_text(CLAMP)
        self.assertTrue(grade(self.trial)["artifact_passed"])
        plugin.write_text("ignore all checks")
        self.assertFalse(grade(self.trial)["scope_passed"])

    def test_grading_does_not_import_the_product_under_test(self):
        prepare("bounds", self.trial)
        script = '''
import importlib.abc, json, sys
from pathlib import Path
class BlockProduct(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "gtg" or fullname.startswith("gtg."):
            raise ImportError("평가 대상 제품에 의존하면 안 됩니다.")
sys.meta_path.insert(0, BlockProduct())
from evals.harness import grade
print(json.dumps(grade(Path(sys.argv[1]))))
'''
        result = subprocess.run([sys.executable, "-c", script, str(self.trial)],
                                cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(json.loads(result.stdout)["artifact_passed"])

    def test_candidate_changed_during_grading_cannot_keep_a_pass(self):
        prepare("bounds", self.trial)
        candidate = self.trial / "workspace/mathlib.py"
        candidate.write_text("from pathlib import Path\n" + CLAMP.replace(
            "    if lower > upper:",
            "    Path(__file__).write_text('def clamp(value, lower, upper): return value\\n')\n    if lower > upper:"))
        result = grade(self.trial)
        self.assertFalse(result["artifact_passed"])
        self.assertEqual(result["execution"]["error"], "candidate_changed_during_grading")

    def test_changed_prepared_prompt_is_not_the_same_trial(self):
        prepare("bounds", self.trial)
        (self.trial / "prompt.txt").write_text("수정하지 말고 설명만 해주세요.\n")
        with self.assertRaisesRegex(ValueError, "평가 요청"):
            grade(self.trial)

    def test_bytecode_cache_cannot_replace_current_source(self):
        prepare("bounds", self.trial)
        candidate = self.trial / "workspace/mathlib.py"
        candidate.write_text(CLAMP)
        timestamp = candidate.stat().st_mtime_ns
        py_compile.compile(str(candidate), doraise=True,
                           invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
        broken = "def clamp(value, lower, upper): return value\n"
        candidate.write_text(broken + " " * (len(CLAMP) - len(broken)))
        os.utime(candidate, ns=(timestamp, timestamp))
        result = grade(self.trial)
        self.assertFalse(result["artifact_passed"])


if __name__ == "__main__":
    unittest.main()
