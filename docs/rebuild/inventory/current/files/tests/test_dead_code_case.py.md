# `tests/test_dead_code_case.py`

- 형식: `100644`
- 바이트: 3156
- SHA-256: `8e5e7c6d764046351a3bec00aaffd15657082f3f7b4103feb3e8d392df71f8bf`
- 인코딩: `utf-8`

```
"""참조를 확인하지 않은 제거와 남겨둔 죽은 코드를 모두 잡는지 검사합니다."""

from pathlib import Path
import re
import tempfile
import unittest

from evals.definitions import case_by_id
from evals.grading import defined_symbols, grade
from evals.preparation import prepare


def drop(path: Path, *names):
    source = path.read_text(encoding="utf-8")
    for name in names:
        source = re.sub(r"\ndef " + name + r"\(.*?(?=\ndef |\Z)", "\n", source, flags=re.S)
    path.write_text(source, encoding="utf-8")


class DeadCodeCaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def trial(self, name):
        target = self.root / name
        prepare("dead-code", target, "baseline", arm="reference", model="none")
        return target

    def test_case_names_the_symbol_that_must_go(self):
        case = case_by_id("dead-code")
        self.assertEqual(case["removed_symbols"], {"reporting.py": ["legacy_csv_header"]})

    def test_the_trap_is_invisible_to_a_text_search(self):
        trial = self.trial("trap")
        for name in ("dashboard.py", "test_reporting.py"):
            text = (trial / "workspace" / name).read_text(encoding="utf-8")
            self.assertNotIn("build_label", text,
                             "문자열로 조합해 부르므로 검색으로는 호출이 보이지 않아야 합니다.")

    def test_leaving_the_dead_symbol_fails_even_though_nothing_breaks(self):
        report = grade(self.trial("nothing"))
        self.assertTrue(report["functional_passed"])
        self.assertEqual(report["symbols_not_removed"], ["reporting.py:legacy_csv_header"])
        self.assertFalse(report["artifact_passed"])

    def test_removing_a_referenced_symbol_breaks_the_callers(self):
        trial = self.trial("naive")
        drop(trial / "workspace/reporting.py", "legacy_csv_header", "build_label")
        report = grade(trial)
        self.assertEqual(report["symbols_not_removed"], [])
        self.assertFalse(report["functional_passed"], "이름으로 부르는 호출자가 깨져야 합니다.")
        self.assertFalse(report["artifact_passed"])

    def test_removing_only_the_dead_symbol_passes(self):
        trial = self.trial("correct")
        drop(trial / "workspace/reporting.py", "legacy_csv_header")
        report = grade(trial)
        self.assertTrue(report["artifact_passed"])
        self.assertEqual(report["changed_paths"], ["reporting.py"])

    def test_symbol_reader_handles_broken_source(self):
        broken = self.root / "broken.py"
        broken.write_text("def oops(:\n", encoding="utf-8")
        self.assertIsNone(defined_symbols(broken))
        self.assertIsNone(defined_symbols(self.root / "missing.py"))

    def test_other_cases_report_no_removal_requirement(self):
        target = self.root / "bounds"
        prepare("bounds", target, "baseline", arm="reference", model="none")
        self.assertIsNone(grade(target)["symbols_not_removed"])


if __name__ == "__main__":
    unittest.main()
```
