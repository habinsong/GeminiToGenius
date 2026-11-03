"""문체 점수가 신호 밀도를 따라 움직이고, 사람 글에 더 흔한 신호로는 깎이지 않으며, 기준 점수로 실패하는지 확인합니다."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gtg.prose import check, examine
from gtg.prose_score import UNSCORED, grade, score


ROOT = Path(__file__).resolve().parents[1]
CLEAN = "설정 파일을 열어 값을 바꾸고 저장했다. 서버를 다시 켜자 로그에 새 값이 찍혔다."
SLOP = "결론적으로 이 변화는 시사하는 바가 크다."
CHOPPY = "설치가 끝났습니다. 설정을 엽니다. 값을 바꿉니다. 저장합니다."
SAME_OPENING = "우리는 기록했다. 우리는 비교했다. 우리는 고쳤다."
SIX_SHORT = "그가 왔다. 문이 열렸다. 비가 왔다. 불이 꺼졌다. 개가 짖었다. 아이가 울었다."


def rated(text, register="general"):
    found, measure = examine("doc.md", text, register)
    return score(found, measure["units"], measure["unscored"])


def flagged(text, register="general"):
    return {f["id"] for f in examine("doc.md", text, register)[0]}


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

    def test_signals_that_are_not_ai_smell_are_reported_but_not_deducted(self):
        """높임 혼용은 KatFish 에세이에서 사람 18.2%, LLM 5.1%였고 맞춤법 오류는 사람 초안에만 흔합니다."""
        self.assertEqual(score([item(rule) for rule in UNSCORED], 10)["value"], 100)
        for text, rule in (("설정을 바꿨습니다. 그리고 서버를 다시 켰다.", "register-mixed"),
                           ("서버를 다시 켜는 데 몇일 걸려요.", "ko-misspelling")):
            with self.subTest(rule=rule):
                self.assertIn(rule, flagged(text))
                self.assertEqual(rated(text)["value"], 100)

    def test_staccato_and_repeated_openings_lower_the_score_in_prose_registers(self):
        """3.2.0은 사람 에세이에 더 많다는 이유로 빼 두었지만 표본이 5편 대 4편이었고 초록에서는 반대였습니다(0% 대 4.3%)."""
        for register in ("general", "academic"):
            for text, rule in ((CHOPPY, "rhythm-choppy"), (SAME_OPENING, "rhythm-repeated-opening")):
                with self.subTest(register=register, rule=rule):
                    self.assertIn(rule, flagged(text, register))
                    self.assertLess(rated(text, register)["value"], 100)

    def test_the_same_signals_are_craft_in_speech_and_verse_so_they_are_reported_only(self):
        self.assertIn("rhythm-repeated-opening", flagged(SAME_OPENING, "everyday"))
        self.assertEqual(rated(SAME_OPENING, "everyday")["value"], 100, "구어에서는 같은 말로 이어 시작하는 일이 흔합니다.")
        for text, rule in ((SAME_OPENING, "rhythm-repeated-opening"), (SIX_SHORT, "rhythm-choppy")):
            with self.subTest(rule=rule):
                self.assertIn(rule, flagged(text, "literary"))
                self.assertEqual(rated(text, "literary")["value"], 100, "시는 짧은 문장 연쇄가 사람 쪽에 더 많았습니다(12% 대 5%).")

    def test_grade_boundaries(self):
        self.assertEqual([grade(v) for v in (100, 90, 89, 75, 74, 60, 59, 0)], list("AABBCCDD"))

    def test_verse_lines_count_as_units(self):
        poem = "\n".join(f"{word} 피는 저녁" for word in ("꽃", "별", "달", "물", "풀", "새"))
        _, measure = examine("poem.md", poem, "literary")
        self.assertEqual(measure["units"], 6, "마침표 없는 시는 행 수로 분량을 잽니다.")
        self.assertEqual(examine("poem.md", poem, "general")[1]["units"], 6, "마침표가 하나도 없으면 갈래와 상관없이 행 수입니다.")

    def test_headings_and_list_items_each_count_as_one_unit(self):
        text = "# 제목\n\n- 하나\n- 둘\n- 셋\n\n서버를 켰다. 값을 읽었다."
        sentences = examine("a.md", "서버를 켰다. 값을 읽었다.")[1]["units"]
        self.assertEqual(examine("a.md", text)[1]["units"], sentences + 1 + 3)

    def test_prose_folded_across_lines_is_counted_by_sentence_not_by_line(self):
        """80칸에 맞춰 접어 쓴 산문이 줄 수만큼 분량으로 잡히면 같은 신호가 있어도 점수가 후하게 나옵니다."""
        first = "서버를 다시 켠 뒤에도 로그에는 예전 값이 그대로 남아 있었고 원인을 찾느라"
        second = "점심도 거른 채 설정 파일과 배포 기록을 처음부터 끝까지 하나씩 맞춰 보았지만 한참을 헤맸다."
        self.assertGreater(len(first.replace(" ", "")), 30)
        self.assertGreater(len(second.replace(" ", "")), 30)
        one_line = " ".join([f"{first} {second}"] * 4)
        folded = "\n".join([f"{first}\n{second}"] * 4)
        self.assertEqual(len(folded.splitlines()), 8)
        self.assertEqual(examine("a.md", one_line)[1]["units"], 4)
        self.assertEqual(examine("a.md", folded)[1]["units"], 4, "접은 줄 수(8)가 아니라 문장 수여야 합니다.")
        self.assertEqual(examine("a.md", folded, "literary")[1]["units"], 4, "행이 긴 산문은 문학 갈래에서도 시로 세지 않습니다.")

    def test_a_signal_costs_the_same_whether_the_prose_is_folded_or_not(self):
        """열 문장이 넘는 글에서 줄바꿈 방식만 달라도 점수가 다르면 안 됩니다."""
        filler = "서버를 다시 켠 뒤에도 로그에는 예전 값이 그대로 남아 있었고 원인을 찾느라 한참을 헤맸다."
        sentences = [filler] * 14 + [SLOP, "이를 통해 문제를 풀었다."]
        one_line = " ".join(sentences)
        folded = "\n".join("\n".join(" ".join(s.split()[i:i + 3]) for i in range(0, len(s.split()), 3)) for s in sentences)
        self.assertGreater(len(folded.splitlines()), 3 * len(sentences))
        self.assertLess(rated(one_line)["value"], 100)
        self.assertEqual(rated(folded)["value"], rated(one_line)["value"])


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
