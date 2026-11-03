"""scripts/prose_calibration.py가 AUC와 점수 분포를 맞게 내고, 모델 출력 폴더를 같은 잣대로 재며, 번들된 프롬프트와 손질본이
검사기와 어긋나지 않는지 확인합니다. 3.2.0까지는 이 스크립트에 시험이 없었습니다.
"""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gtg.prose import examine
from gtg.prose_fidelity import compare
from gtg.prose_registers import REGISTERS
from gtg.prose_score import score


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("prose_calibration", ROOT / "scripts/prose_calibration.py")
calibration = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(calibration)

CLEAN = "설정 파일을 열어 값을 바꾸고 저장했다. 서버를 다시 켜자 로그에 새 값이 찍혔다."
SLOPPY = "결론적으로 이 변화는 시사하는 바가 크다. 물론입니다. 새로운 지평을 엽니다."


def rows(pattern):
    """짝수 번째는 보정용, 홀수 번째는 확인용이므로 두 절반에 두 쪽이 모두 들어가게 둘씩 묶어 놓습니다."""
    return [{"written_by": who, "text": text} for who, text in pattern]


class MetricTests(unittest.TestCase):
    def test_auc_counts_wins_ties_and_losses(self):
        self.assertEqual(calibration.auc([2, 3], [0, 1]), 1.0)
        self.assertEqual(calibration.auc([0, 1], [2, 3]), 0.0)
        self.assertEqual(calibration.auc([1, 1], [1, 1]), 0.5)
        self.assertEqual(calibration.auc([1, 3], [2]), 0.5)

    def test_pass_shares_at_each_floor(self):
        self.assertEqual(calibration.passing([100, 92, 80, 70, 50]), {"ge_90": 0.4, "ge_75": 0.6, "ge_60": 0.8})
        self.assertEqual(calibration.passing([100, 90, 75, 60, 59]), {"ge_90": 0.4, "ge_75": 0.6, "ge_60": 0.8},
                         "기준 점수와 같은 점수도 통과입니다.")
        self.assertEqual(calibration.passing([]), {"ge_90": None, "ge_75": None, "ge_60": None})


class DatasetReportTests(unittest.TestCase):
    PATTERN = [("human", CLEAN), ("human", CLEAN), ("gpt", SLOPPY), ("gpt", SLOPPY)] * 3

    def test_a_perfectly_separable_set_gets_auc_one_in_both_halves(self):
        report = calibration.genre_report(rows(self.PATTERN), "general")
        self.assertEqual(report["auc"], {"calibration": 1.0, "holdout": 1.0})
        self.assertEqual(report["texts"], {"human": 6, "llm": 6})
        self.assertEqual(report["grades"]["human"], {"A": 6})
        self.assertEqual(report["pass"]["human"]["ge_90"], 1.0)
        self.assertLess(report["pass"]["llm"]["ge_90"], 1.0)
        self.assertEqual(report["median_score"]["human"], 100)
        self.assertNotIn("rules", report)

    def test_the_rule_table_reports_each_half_separately(self):
        report = calibration.genre_report(rows(self.PATTERN), "general", with_rules=True)
        slot = report["rules"]["ko-conclusion-signpost"]
        self.assertEqual(slot["calibration"], {"human": 0.0, "llm": 100.0})
        self.assertEqual(slot["holdout"], {"human": 0.0, "llm": 100.0})

    def test_paper_bodies_measure_only_human_long_form_text(self):
        body = " ".join([CLEAN] * 12)
        data = [{"written_by": "human", "text": "초록", "whole_paper_without_abstract": body},
                {"written_by": "gpt", "text": "초록", "whole_paper_without_abstract": SLOPPY},
                {"written_by": "human", "text": "초록", "whole_paper_without_abstract": ""}]
        report = calibration.bodies_report(data)
        self.assertEqual((report["papers"], report["grades"]), (1, {"A": 1}))
        self.assertEqual(report["mean_sentences"], 24)


class OutputsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.prompts = [
            {"id": "w1", "register": "general", "kind": "write", "prompt": "소개를 써 줘"},
            {"id": "w2", "register": "general", "kind": "write", "prompt": "공지를 써 줘"},
            {"id": "p1", "register": "general", "kind": "polish", "prompt": "고쳐 줘",
             "source": "결론적으로 사용자 1,624명이 참여했고 73.5%가 만족했다."},
            {"id": "gone", "register": "academic", "kind": "write", "prompt": "초록을 써 줘"},
        ]

    def test_outputs_are_scored_by_register_and_missing_ones_are_listed(self):
        (self.root / "w1.md").write_text(CLEAN, encoding="utf-8")
        (self.root / "w2.txt").write_text(SLOPPY, encoding="utf-8")
        (self.root / "p1.md").write_text("사용자 1,642명이 참여했고 대부분 만족했다.", encoding="utf-8")
        report = calibration.outputs_report(self.root, self.prompts, "arm-a")
        self.assertEqual((report["label"], report["missing"]), ("arm-a", ["gone"]))
        general = report["registers"]["general"]
        self.assertEqual(general["outputs"], 3)
        self.assertEqual(general["blocked_outputs"], 1, "차단 신호가 있는 출력 수입니다.")
        self.assertNotIn("academic", report["registers"])
        polish = general["polish"]
        self.assertEqual(polish["outputs"], 1)
        self.assertEqual(polish["fidelity_blocked"], 1, "자릿수가 바뀌고 통계가 빠진 윤문은 충실도에서 막힙니다.")
        detail = {row["id"]: row for row in report["details"]}
        self.assertLess(detail["p1"]["source_score"], 100)
        self.assertEqual(detail["w1"]["score"], 100)

    def test_a_blank_output_counts_as_missing_and_a_reference_is_shown_beside_it(self):
        (self.root / "w1.md").write_text("  \n", encoding="utf-8")
        (self.root / "w2.md").write_text(CLEAN, encoding="utf-8")
        reference = {"essay": {"median_score": {"human": 100}, "pass": {"human": {"ge_90": 0.9}, "llm": {"ge_90": 0.1}}}}
        report = calibration.outputs_report(self.root, self.prompts, "arm-b", reference)
        self.assertIn("w1", report["missing"])
        self.assertEqual(report["registers"]["general"]["katfish"]["human_pass"], {"ge_90": 0.9})

    def test_exported_prompts_carry_the_source_of_polish_requests(self):
        written = calibration.export_prompts(self.root / "out", self.prompts)
        self.assertEqual(written, ["w1", "w2", "p1", "gone"])
        self.assertEqual((self.root / "out/w1.prompt.txt").read_text(encoding="utf-8"), "소개를 써 줘\n")
        polish = (self.root / "out/p1.prompt.txt").read_text(encoding="utf-8")
        self.assertTrue(polish.startswith("고쳐 줘\n\n결론적으로 사용자 1,624명"))

    def test_duplicate_prompt_ids_are_rejected(self):
        path = self.root / "prompts.json"
        path.write_text(json.dumps({"prompts": [self.prompts[0], self.prompts[0]]}), encoding="utf-8")
        with self.assertRaises(ValueError):
            calibration.read_prompts(path)


class ShippedPromptTests(unittest.TestCase):
    """evals/prose/prompts.json의 프롬프트와 손질본(gold)이 지금의 검사기와 어긋나지 않는지 확인합니다."""

    @classmethod
    def setUpClass(cls):
        cls.prompts = calibration.read_prompts(calibration.PROMPTS)

    def test_every_prompt_is_complete_and_names_a_known_register(self):
        self.assertGreaterEqual(len(self.prompts), 24)
        for prompt in self.prompts:
            with self.subTest(prompt=prompt["id"]):
                self.assertIn(prompt["register"], REGISTERS)
                self.assertIn(prompt["kind"], {"write", "polish"})
                self.assertTrue(prompt["prompt"].strip())
                if prompt["kind"] == "polish":
                    self.assertTrue(prompt["source"].strip() and prompt["gold"].strip())
        self.assertEqual({p["register"] for p in self.prompts}, set(REGISTERS), "네 갈래를 모두 다룹니다.")

    def test_each_polish_source_is_flagged_and_its_gold_is_clean_and_faithful(self):
        polished = [p for p in self.prompts if p["kind"] == "polish"]
        self.assertGreaterEqual(len(polished), 6)
        for prompt in polished:
            with self.subTest(prompt=prompt["id"]):
                register = prompt["register"]
                source_found, source_measure = examine("source", prompt["source"], register)
                gold_found, gold_measure = examine("gold", prompt["gold"], register)
                self.assertTrue(source_found, "윤문 원문에서 아무 신호도 나오지 않으면 연습 사례가 아닙니다.")
                before = score(source_found, source_measure["units"], source_measure["unscored"])["value"]
                after = score(gold_found, gold_measure["units"], gold_measure["unscored"])["value"]
                self.assertGreaterEqual(after, 90)
                self.assertGreater(after, before)
                self.assertEqual([f["id"] for f in gold_found if f["severity"] == "block"], [])
                _, fidelity = compare(prompt["source"], prompt["gold"], "gold")
                self.assertEqual([f["id"] for f in fidelity if f["severity"] == "block"], [], "손질본이 수치·인용을 지켜야 합니다.")

    def test_the_reference_file_holds_only_aggregates_and_works_with_the_outputs_report(self):
        raw = (ROOT / "evals/prose/katfish-reference.json").read_text(encoding="utf-8")
        reference = json.loads(raw)
        self.assertLess(len(raw), 10_000, "집계 파일에 말뭉치 원문이 들어가면 안 됩니다. 라이선스를 확인하지 못했습니다.")
        self.assertEqual(set(reference) - {"_meta"}, {"essay", "abstract", "poetry"})
        for genre in ("essay", "abstract", "poetry"):
            with self.subTest(genre=genre):
                self.assertEqual(set(reference[genre]["pass"]), {"human", "llm"})
                self.assertIsInstance(reference[genre]["median_score"]["human"], (int, float))
                self.assertIn("holdout", reference[genre]["auc"])
        with tempfile.TemporaryDirectory() as temp:
            Path(temp, "general-readme-intro.md").write_text(CLEAN, encoding="utf-8")
            report = calibration.outputs_report(Path(temp), self.prompts, "t", reference)
        self.assertEqual(report["registers"]["general"]["katfish"]["human_pass"], reference["essay"]["pass"]["human"])

    def test_the_command_line_exports_every_prompt(self):
        with tempfile.TemporaryDirectory() as temp:
            process = subprocess.run([sys.executable, "-I", str(ROOT / "scripts/prose_calibration.py"), "--export-prompts", temp],
                                     cwd=ROOT, capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(len(json.loads(process.stdout)["exported"]), len(self.prompts))
            self.assertEqual(len(list(Path(temp).glob("*.prompt.txt"))), len(self.prompts))


if __name__ == "__main__":
    unittest.main()
