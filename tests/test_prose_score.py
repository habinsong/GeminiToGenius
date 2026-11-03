"""문체 점수가 신호 밀도를 따라 움직이고, 사람 글에 더 흔한 신호로는 깎이지 않으며, 기준 점수로 실패하는지 확인합니다."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gtg.prose import check, examine
from gtg.prose_score import NOT_SMELL, grade, score


ROOT = Path(__file__).resolve().parents[1]
CLEAN = "설정 파일을 열어 값을 바꾸고 저장했다. 서버를 다시 켜자 로그에 새 값이 찍혔다."
SLOP = "결론적으로 이 변화는 시사하는 바가 크다."


def rated(text, register="general"):
    found, measure = examine("doc.md", text, register)
    return score(found, measure["units"])


def item(rule, severity="review"):
    return {"id": rule, "severity": severity}


class ScoreTests(unittest.TestCase):
    def test_clean_text_is_100_and_each_added_signal_lowers_the_score(self):
        self.assertEqual(rated(CLEAN)["value"], 100)
        self.assertEqual(rated(CLEAN)["grade"], "A")
        previous = 100
        text = CLEAN
        for extra in (SLOP, "이를 통해 문제를 풀었다.", "물론입니다. 좋은 질문입니다."):
            text += " " + extra
            current = rated(text)["value"]
            self.assertLess(current, previous, text)
            previous = current

    def test_a_block_costs_three_reviews_and_deductions_name_the_rules(self):
        self.assertEqual(score([item("a", "block")], 10)["value"], score([item("b")] * 3, 10)["value"])
        result = score([item("a", "block"), item("b"), item("b")], 10)
        self.assertEqual(result["deductions"], [{"id": "a", "points": 3.0}, {"id": "b", "points": 2.0}])

    def test_score_is_a_density_and_short_texts_are_not_blown_up(self):
        findings = [item("a", "block")]
        self.assertEqual(score(findings, 1)["value"], score(findings, 10)["value"], "열 문장보다 짧은 글은 열 문장으로 봅니다.")
        self.assertLess(score(findings, 10)["value"], score(findings, 40)["value"])

    def test_signals_more_common_in_human_writing_are_reported_but_not_deducted(self):
        self.assertEqual(score([item(rule) for rule in NOT_SMELL], 10)["value"], 100)
        mixed = "설정을 바꿨습니다. 그리고 서버를 다시 켰다."
        found, measure = examine("doc.md", mixed)
        self.assertIn("register-mixed", [f["id"] for f in found])
        self.assertEqual(score(found, measure["units"])["value"], 100)

    def test_grade_boundaries(self):
        self.assertEqual([grade(v) for v in (100, 90, 89, 75, 74, 60, 59, 0)], list("AABBCCDD"))

    def test_verse_lines_count_as_units(self):
        poem = "\n".join(f"{word} 피는 저녁" for word in ("꽃", "별", "달", "물", "풀", "새"))
        _, measure = examine("poem.md", poem, "literary")
        self.assertEqual(measure["units"], 6, "마침표 없는 시는 행 수로 분량을 잽니다.")


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "clean.md").write_text(CLEAN + "\n", encoding="utf-8")
        review = "이를 통해 값을 읽었다. 이를 통해 로그를 남겼다. 이를 위해 서버를 켰다.\n"
        (self.root / "review.md").write_text(review, encoding="utf-8")

    def test_min_score_fails_only_the_files_below_it(self):
        result = check(self.root, ["clean.md", "review.md"], min_score=90)
        self.assertEqual(result["blocking"], 0)
        self.assertEqual(result["below_min_score"], ["review.md"])
        self.assertFalse(result["passed"], "차단 신호가 없어도 기준 점수 미달이면 실패합니다.")
        self.assertTrue(check(self.root, ["clean.md", "review.md"], min_score=60)["passed"])
        self.assertTrue(check(self.root, ["review.md"])["passed"], "기준 점수를 주지 않으면 점수로 실패하지 않습니다.")
        self.assertEqual(result["lowest_score"], min(f["score"]["value"] for f in result["files"]))

    def test_invalid_threshold_and_unreadable_files(self):
        for value in (-1, 101):
            with self.subTest(value=value), self.assertRaises(ValueError):
                check(self.root, ["clean.md"], min_score=value)
        result = check(self.root, ["missing.md"], min_score=0)
        self.assertIsNone(result["score"])
        self.assertEqual(result["below_min_score"], [])
        self.assertFalse(result["passed"], "읽지 못한 문서는 점수와 상관없이 통과하지 않습니다.")

    def test_cli_min_score_sets_the_exit_code(self):
        def run(*extra):
            return subprocess.run([sys.executable, "-m", "gtg", "prose", "review.md", "--workspace", str(self.root), *extra],
                                  cwd=ROOT, capture_output=True, text=True,
                                  env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})

        strict, loose = run("--min-score", "95"), run("--min-score", "50")
        self.assertEqual((strict.returncode, loose.returncode), (1, 0))
        report = json.loads(strict.stdout)
        self.assertEqual(report["min_score"], 95)
        self.assertIn("AI가 썼을 확률이 아닙니다", report["limitations"])
        self.assertEqual(run("--min-score", "abc").returncode, 2)


if __name__ == "__main__":
    unittest.main()
