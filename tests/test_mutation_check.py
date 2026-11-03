"""변형 시험 도구가 잡힌 변형과 살아남은 변형을 구분하고, 낡은 목록과 깨진 기준 시험을 통과시키지 않는지 확인합니다.

3.2.0의 변형 시험 26개는 저장소 밖 임시 폴더에만 있어 다른 사람이 다시 돌릴 수 없었습니다.
전체 변형 실행(약 2분)은 CI에 넣지 않고, 목록이 코드와 어긋나지 않았는지만 빠르게 확인합니다.
"""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("mutation_check", ROOT / "scripts/mutation_check.py")
tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tool)

CALC = "def add(a, b):\n    return a + b\n\n\ndef sign(x):\n    return 1 if x >= 0 else -1\n"
TESTS = ("import unittest\nfrom mini.calc import add, sign\n\n\nclass T(unittest.TestCase):\n    def test_add(self):\n"
         "        self.assertEqual(add(1, 2), 3)\n\n    def test_sign(self):\n        self.assertEqual(sign(5), 1)\n"
         "        self.assertEqual(sign(-5), -1)\n")


class MiniProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name, text in (("mini/__init__.py", ""), ("mini/calc.py", CALC), ("tests/__init__.py", ""),
                           ("tests/test_calc.py", TESTS)):
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
            (self.root / name).write_text(text, encoding="utf-8")

    def run_tool(self, mutations, timeout=60):
        return tool.run(self.root, mutations, ("tests.test_calc",), ("mini", "tests"), timeout)

    def test_a_caught_mutant_and_a_surviving_boundary_mutant_are_told_apart(self):
        report = self.run_tool([
            tool.m("add-minus", "mini/calc.py", "return a + b", "return a - b", "덧셈이다"),
            tool.m("sign-boundary", "mini/calc.py", "x >= 0", "x > 0", "0의 부호는 1이다")])
        self.assertEqual((report["total"], report["killed"], report["survived"]), (2, 1, ["sign-boundary"]))
        self.assertEqual({r["id"]: r["outcome"] for r in report["results"]}, {"add-minus": "failed", "sign-boundary": "passed"})

    def test_the_working_tree_is_never_touched(self):
        self.run_tool([tool.m("add-minus", "mini/calc.py", "return a + b", "return a - b", "덧셈이다")])
        self.assertEqual((self.root / "mini/calc.py").read_text(encoding="utf-8"), CALC)

    def test_a_mutant_that_hangs_counts_as_caught(self):
        report = self.run_tool([tool.m("hang", "mini/calc.py", "return a + b", "while True:\n        pass", "멈추지 않는다")], timeout=3)
        self.assertEqual(report["results"][0]["outcome"], "timeout")
        self.assertEqual(report["survived"], [])

    def test_a_stale_or_ambiguous_target_is_an_error_not_a_pass(self):
        with self.assertRaisesRegex(ValueError, "0번"):
            self.run_tool([tool.m("gone", "mini/calc.py", "return a * b", "return a", "낡은 대상")])
        with self.assertRaisesRegex(ValueError, "2번"):
            self.run_tool([tool.m("many", "mini/calc.py", "return", "pass", "여러 곳")])

    def test_a_failing_baseline_stops_everything(self):
        (self.root / "mini/calc.py").write_text(CALC.replace("a + b", "a - b"), encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "통과하지 않아"):
            self.run_tool([tool.m("any", "mini/calc.py", "return a - b", "return 0", "무엇이든")])

    def test_a_missing_copy_target_is_reported(self):
        with self.assertRaises(FileNotFoundError):
            tool.run(self.root, [], ("tests.test_calc",), ("mini", "no-such-dir"), 10)


class ShippedMutationTests(unittest.TestCase):
    def test_every_shipped_mutation_still_has_exactly_one_target_and_is_unique(self):
        ids = [item["id"] for item in tool.MUTATIONS]
        self.assertEqual(len(ids), len(set(ids)), "변형 id가 겹칩니다.")
        for item in tool.MUTATIONS:
            with self.subTest(mutation=item["id"]):
                text = (ROOT / item["file"]).read_text(encoding="utf-8")
                self.assertEqual(text.count(item["old"]), 1, "코드가 바뀌어 변형 대상이 낡았습니다. 목록을 고치세요.")
                self.assertNotEqual(item["old"], item["new"])
                self.assertTrue(item["guards"].strip())

    def test_list_option_prints_the_invariants_without_running_anything(self):
        process = subprocess.run([sys.executable, str(ROOT / "scripts/mutation_check.py"), "--list", "--only", "fidelity"],
                                 cwd=ROOT, capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(process.returncode, 0, process.stderr)
        listed = json.loads(process.stdout)
        self.assertGreaterEqual(len(listed), 10)
        self.assertTrue(all("fidelity" in item["id"] and item["guards"] for item in listed))


if __name__ == "__main__":
    unittest.main()
