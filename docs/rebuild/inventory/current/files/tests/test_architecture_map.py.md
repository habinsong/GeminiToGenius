# `tests/test_architecture_map.py`

- 형식: `100644`
- 바이트: 1770
- SHA-256: `59ef056bd1058f4cd3b408dac34b609b7d1a521c692edaa0cb75c861c3863c54`
- 인코딩: `utf-8`

```
"""설계 문서의 모듈 책임 표가 실제 구현과 어긋나지 않게 합니다."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/rebuild/plan/architecture.md"


def documented() -> dict[str, str]:
    rows = re.findall(r"^\| `(gtg/[a-z_]+\.py)` \| (.+?) \|$", DOC.read_text(encoding="utf-8"), re.M)
    return {name: duty for name, duty in rows}


class ArchitectureMapTests(unittest.TestCase):
    def test_every_module_has_a_documented_responsibility(self):
        actual = {f"gtg/{path.name}" for path in (ROOT / "gtg").glob("*.py") if path.stem != "__init__"}
        missing = sorted(actual - set(documented()))
        self.assertEqual(missing, [], f"설계 문서에 책임이 없는 모듈입니다: {missing}")

    def test_the_table_names_no_module_that_was_removed(self):
        actual = {f"gtg/{path.name}" for path in (ROOT / "gtg").glob("*.py")}
        stale = sorted(set(documented()) - actual)
        self.assertEqual(stale, [], f"실제로 없는 모듈이 표에 있습니다: {stale}")

    def test_each_responsibility_is_a_single_sentence(self):
        for name, duty in documented().items():
            with self.subTest(module=name):
                self.assertTrue(duty.strip(), f"{name}의 책임이 비어 있습니다.")
                self.assertLess(len(duty), 90, f"{name}의 책임 설명이 너무 깁니다. 경계를 나누세요.")

    def test_evals_boundary_is_linked_rather_than_duplicated(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("evals/README.md", text)
        self.assertNotIn("| `evals/", text, "평가 경계는 평가 문서에서만 관리합니다.")


if __name__ == "__main__":
    unittest.main()
```
