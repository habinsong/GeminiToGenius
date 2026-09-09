# `tests/test_refactor_case.py`

- 형식: `100644`
- 바이트: 3994
- SHA-256: `50eb2e21248ce8964504923884e0ee90f708daea42593eb9c3d41fd274dd1267`
- 인코딩: `utf-8`

```
"""동작이 그대로여야 하는 사례에서 무작업 통과를 막는지 검사합니다."""

import json
from pathlib import Path
import tempfile
import unittest

from evals.definitions import case_by_id
from evals.grading import grade
from evals.preparation import prepare


REFACTORED = '''"""주문 금액을 계산합니다."""


def _discounted(items, rate):
    total = 0
    for item in items:
        count = item["count"]
        if count < 0:
            raise ValueError("수량은 음수일 수 없습니다.")
        total += item["price"] * count
    return round(max(total - total * rate, 0), 2)


def member_total(items, rate):
    return _discounted(items, rate)


def guest_total(items):
    return _discounted(items, 0.0)


def staff_total(items):
    return _discounted(items, 0.3)
'''


class RefactorCaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def trial(self, name):
        target = self.root / name
        prepare("refactor-pricing", target, "baseline", arm="reference", model="none")
        return target

    def test_case_declares_the_file_that_must_change(self):
        case = case_by_id("refactor-pricing")
        self.assertEqual(case["required_edits"], ["pricing.py"])
        self.assertIn("pricing.py", case["allowed_edits"])

    def test_doing_nothing_keeps_behaviour_but_fails_the_scope(self):
        report = grade(self.trial("nothing"))
        self.assertTrue(report["functional_passed"], "동작은 그대로이므로 기능 검사는 통과합니다.")
        self.assertFalse(report["scope_passed"])
        self.assertEqual(report["untouched_required_edits"], ["pricing.py"])
        self.assertFalse(report["artifact_passed"])

    def test_reference_refactor_passes_every_check(self):
        trial = self.trial("fixed")
        (trial / "workspace/pricing.py").write_text(REFACTORED, encoding="utf-8")
        report = grade(trial)
        self.assertTrue(report["artifact_passed"])
        self.assertEqual(report["changed_paths"], ["pricing.py"])
        self.assertEqual(report["untouched_required_edits"], [])
        self.assertTrue(all(check["passed"] for check in report["checks"]))

    def test_breaking_a_public_contract_is_caught(self):
        trial = self.trial("broken")
        (trial / "workspace/pricing.py").write_text(
            REFACTORED.replace("_discounted(items, 0.3)", "_discounted(items, 0.5)"), encoding="utf-8")
        report = grade(trial)
        self.assertFalse(report["artifact_passed"])
        self.assertFalse(report["functional_passed"])

    def test_touching_an_unrelated_file_is_a_scope_violation(self):
        trial = self.trial("noisy")
        (trial / "workspace/pricing.py").write_text(REFACTORED, encoding="utf-8")
        (trial / "workspace/notes.txt").write_text("다른 사람 메모를 바꿨습니다.\n", encoding="utf-8")
        report = grade(trial)
        self.assertIn("notes.txt", report["scope_violations"])
        self.assertFalse(report["artifact_passed"])

    def test_deleting_a_public_function_is_caught(self):
        trial = self.trial("deleted")
        (trial / "workspace/pricing.py").write_text(
            REFACTORED.replace('''def staff_total(items):
    return _discounted(items, 0.3)
''', ""), encoding="utf-8")
        report = grade(trial)
        self.assertFalse(report["artifact_passed"])

    def test_existing_cases_without_required_edits_are_unaffected(self):
        target = self.root / "bounds"
        prepare("bounds", target, "baseline", arm="reference", model="none")
        report = grade(target)
        self.assertEqual(report["untouched_required_edits"], [])
        self.assertFalse(report["artifact_passed"], "초기 버그는 여전히 기능 검사에서 실패합니다.")
        self.assertTrue(report["scope_passed"])


if __name__ == "__main__":
    unittest.main()
```
