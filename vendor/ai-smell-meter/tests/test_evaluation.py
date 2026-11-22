"""평가 도구와 이번에 고친 동작(줄표, 출처 없는 권위, 접속어 도배, 긴 입력 시간)의 회귀 시험."""
import json
import re
import subprocess
import sys
import tempfile
import time
import unittest

import _path
from ai_smell.detect import analyze
from ai_smell.verify import verify

sys.path.insert(0, str(_path.ROOT / "tools"))
import evaluate  # noqa: E402


def ids(text, **kw):
    return {f.rule_id for f in analyze(text, **kw).findings if f.weight > 0 and not f.shadowed}


def seen(text, **kw):
    return {f.rule_id for f in analyze(text, **kw).findings}


class EvaluateTool(unittest.TestCase):
    def test_wilson_interval(self):
        lo, hi = evaluate.wilson(0, 100)
        self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, 0.037, places=2)
        lo, hi = evaluate.wilson(50, 100)
        self.assertTrue(0.40 < lo < 0.41 and 0.59 < hi < 0.60)
        self.assertEqual(evaluate.wilson(0, 0), (0.0, 0.0))

    def test_auroc(self):
        self.assertEqual(evaluate.auroc([3, 4], [1, 2]), 1.0)
        self.assertEqual(evaluate.auroc([1, 2], [3, 4]), 0.0)
        self.assertEqual(evaluate.auroc([1, 1], [1, 1]), 0.5)           # 같은 값은 0.5
        self.assertIsNone(evaluate.auroc([], [1]))

    def test_cli_end_to_end(self):
        rows = []
        for i in range(12):
            rows.append({"id": i, "lang": "en", "label": "human", "source": "t", "genre": "x",
                         "text": "I fixed the sink on Saturday. It took two tries and a bucket."})
            rows.append({"id": 100 + i, "lang": "en", "label": "ai", "source": "t", "genre": "x",
                         "text": "Certainly! In today's fast-paced world, it plays a crucial role. I hope this helps!"})
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
        out = subprocess.run([sys.executable, str(_path.ROOT / "tools" / "evaluate.py"), fh.name, "--jobs", "1", "--min-n", "5"],
                             capture_output=True, text=True, encoding="utf-8", check=True).stdout
        self.assertIn("en/x", out)
        self.assertIn("1.0", out)                                       # AI 글 점수가 모두 더 높다


class DashesAndAttribution(unittest.TestCase):
    def test_only_real_em_dashes_count(self):
        human = "He left - quietly - and came back -- late. The plan 2020–2022 worked - mostly - fine - or so he said - really."
        self.assertNotIn("any.format.em-dash", seen(human))
        ai = "The plan — which was new — worked. It was fast — really fast. Done — truly."
        self.assertIn("any.format.em-dash", seen(ai))

    def test_dashes_are_normal_punctuation_in_russian(self):
        ru = "Москва — столица России. Петербург — культурная столица. Казань — столица Татарстана. Сочи — курорт."
        self.assertNotIn("any.format.em-dash", seen(ru))

    def test_plain_mentions_are_not_vague_attribution(self):
        self.assertNotIn("en.attribution.vague", seen("Some historians assume that he never faced a trial."))
        self.assertNotIn("en.attribution.vague", seen("The scholars of Gothic literature met in Vienna."))
        self.assertIn("en.attribution.vague", seen("Experts agree that this approach is best."))
        self.assertIn("en.attribution.vague", seen("Studies show that it works."))


class Flood(unittest.TestCase):
    CHOP = ("캐시는 60초 동안 응답을 저장합니다. 프로세스마다 따로 있습니다. 워커 둘이 다른 값을 줄 수 있습니다. "
            "항목이 만료되면 맞춰집니다. 로그는 별도 저장소에 쌓입니다. 알림은 메일로 갑니다.")

    def gamed(self):
        parts = re.split(r"(?<=다\.)\s", self.CHOP)
        return " ".join(w + " " + s for w, s in zip(["그리고", "또한", "그래서", "하지만", "게다가", "따라서"], parts))

    def test_flood_is_reported_but_not_scored(self):
        a = analyze(self.gamed())
        flood = [f for f in a.findings if f.rule_id.endswith("cohesion.flood")]
        self.assertTrue(flood)
        self.assertEqual(flood[0].weight, 0)
        self.assertEqual(a.metrics["cohesion"]["flood_paragraphs"], 1)

    def test_verify_warns_when_connectives_are_stuffed(self):
        v = verify(self.CHOP, self.gamed())
        self.assertTrue(any("접속어를 붙인 문단" in m for _, m in v.messages), v.messages)
        natural = ("캐시는 60초 동안 응답을 저장하는데, 프로세스마다 따로 있어서 워커 둘이 다른 값을 줄 수 있습니다. "
                   "다만 항목이 만료되면 맞춰집니다. 로그는 별도 저장소에 쌓이고 알림은 메일로 갑니다.")
        self.assertFalse(any("접속어를 붙인 문단" in m for _, m in verify(self.CHOP, natural).messages))


class Robustness(unittest.TestCase):
    """긴 입력이 제곱으로 느려지지 않는다(예전엔 5만 자 한 줄이 40초를 넘겼다)."""

    def test_long_single_runs_finish_quickly(self):
        for text in ("가" * 60000, "." * 60000, "a1" * 30000, "가, " * 15000):
            t0 = time.time()
            analyze(text)
            self.assertLess(time.time() - t0, 8, text[:6])

    def test_every_rule_is_linear_on_repeated_input(self):
        from ai_smell.rules import load_rules
        inputs = ["가" * 12000, "a" * 12000, "가 " * 6000, "a, " * 6000, "(a " * 4000, "1" * 12000]
        slow = []
        for r in load_rules():
            for t in inputs:
                t0 = time.time()
                for _ in r.pattern.finditer(t):
                    pass
                if time.time() - t0 > 1.0:
                    slow.append((r.id, t[:3]))
        self.assertEqual(slow, [])

    def test_email_protection_still_works(self):
        from ai_smell.textutil import protected_spans
        t = "문의는 a.b+c@example.co.kr 로 보내 주세요."
        self.assertEqual(len(protected_spans(t)), 1)


class LanguageNotes(unittest.TestCase):
    def test_languages_without_smell_rules_are_labelled(self):
        notes = analyze("Я не слушал эти наушники. Мое мнение основано на августовских обзорах и записях пользователей. "
                         "Высокие приглушены, поэтому жалоб на шипение мало. Тарелки звучат плоско, а бас есть, но слабый.").notes
        self.assertTrue(any("AI 냄새 규칙이 없" in n for n in notes), notes)
        self.assertFalse(any("AI 냄새 규칙이 없" in n for n in analyze("The cache stores responses for 60 seconds.").notes))

    def test_report_shows_the_join_warning(self):
        from ai_smell.report import render_analysis
        text = "캐시는 60초 저장합니다. 프로세스마다 따로 있습니다. 워커 값이 다릅니다."
        self.assertIn("연결 단절", render_analysis(analyze(text), text))


class Calibration(unittest.TestCase):
    """언어별 기준은 사람 글(위키백과·뉴스·소설) 오탐이 5~10% 안에 들도록 실측으로 맞췄다(docs/evaluation.md)."""

    def test_korean_cohesion_is_graded_higher_than_the_others(self):
        from ai_smell import linkers
        ko = "캐시는 60초 저장합니다. 프로세스마다 따로 있습니다. 워커 값이 다릅니다. 만료되면 맞춰집니다."
        en = "The cache stores data. Each process has one. Workers can differ. Entries expire."
        wk = max(f.weight for f in analyze(ko).findings if f.category == "cohesion")
        we = max(f.weight for f in analyze(en).findings if f.category == "cohesion")
        self.assertGreater(wk, we)                          # 한국어 B(2025년 모델 글에서 재현), 영어 C(판별력 없음)
        self.assertEqual(linkers.SHORT["ko"], 6)

    def test_japanese_needs_a_longer_run(self):
        from ai_smell import linkers
        self.assertEqual(linkers.RUN["ja"], 4)
        two_runs = "雨が降る。風も強い。波が高い。"
        self.assertFalse([f for f in analyze(two_runs).findings if f.category == "cohesion"])     # 3문장은 세지 않는다
        four = "雨が降る。風も強い。波が高い。船は出ない。"
        self.assertTrue([f for f in analyze(four).findings if f.category == "cohesion"])           # 4문장부터

    def test_korean_comma_density_threshold(self):
        dense = " ".join("이 방식은 빠르고, 단순해서 쓰기 좋다." for _ in range(6))
        self.assertIn("ko.rhythm.commas", {f.rule_id for f in analyze(dense).findings})
        sparse = " ".join("이 방식은 빠르고 단순해서 쓰기 좋다." for _ in range(6))
        self.assertNotIn("ko.rhythm.commas", {f.rule_id for f in analyze(sparse).findings})
        w = lambda g: max(f.weight for f in analyze(dense, genre=g).findings if f.rule_id == "ko.rhythm.commas")  # noqa: E731
        self.assertLess(w("academic"), w("general"))

    def test_korean_second_tier_run(self):
        five = ("이 장비는 현장에서 쓰는 물건입니다. 점검 주기는 한 달에 한 번입니다. 담당자는 매번 기록을 남깁니다. "
                "교체 비용은 별도로 청구됩니다. 보증 기간은 이 년으로 정해져 있습니다.")
        four = " ".join(five.split(". ")[:4]) + "."
        self.assertTrue([f for f in analyze(five).findings if f.rule_id == "ko.cohesion.choppy-run"])
        self.assertFalse([f for f in analyze(four).findings if f.rule_id == "ko.cohesion.choppy-run"])

    def test_evaluate_cli_groups_by_generator(self):
        rows = []
        for i in range(12):
            rows.append({"id": i, "lang": "en", "label": "human", "source": "h", "genre": "x", "gen": "human",
                         "text": "I fixed the sink on Saturday. It took two tries and a bucket."})
            rows.append({"id": 100 + i, "lang": "en", "label": "ai", "source": "m", "genre": "y", "gen": "model-a",
                         "text": "Certainly! In today's fast-paced world, it plays a crucial role. I hope this helps!"})
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
        out = subprocess.run([sys.executable, str(_path.ROOT / "tools" / "evaluate.py"), fh.name, "--jobs", "1", "--min-n", "5",
                              "--group", "gen", "--match", "all"], capture_output=True, text=True, encoding="utf-8",
                             check=True).stdout
        self.assertIn("en/model-a", out)


if __name__ == "__main__":
    unittest.main()
