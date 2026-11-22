"""본뜻과 다르게 되풀이되는 낱말 규칙과 서술어 반복 분석기."""
import unittest

import _path  # noqa: F401
from ai_smell.detect import analyze
from ai_smell.rules import ko_wordhabit

# (규칙 id, 걸려야 하는 한 문장, 걸리면 안 되는 한 문장, 반복 횟수)
CASES = [
    ("ko.tic.surface", "문제의 표면만 다룬다.", "지구 표면은 대부분 바다다.", 1),
    ("ko.tic.atomic", "원자적으로 처리한다.", "원자료와 원자핵을 본다.", 1),
    ("ko.tic.and-start", "그리고 값을 읽는다.", "또 값을 읽는다.", 3),
    ("ko.tic.write-diff", "두 글의 차이를 씁니다.", "두 글의 차이를 비교합니다.", 1),
    ("ko.tic.write-use", "점수를 쓴다. 표를 쓴다. 규칙을 쓴다.", "보고서를 쓴다. 초안을 쓴다. 편지를 쓴다.", 1),
    ("ko.tic.turn-verb", "시험을 돌린다.", "나사를 돌린다. 열쇠를 돌려 문을 연다.", 1),
    ("ko.tic.link-verb", "두 규칙을 잇는다.", "두 점을 선으로 잇는다.", 1),
    ("ko.tic.window", "관찰 창을 열어 둔다.", "컨텍스트 창이 넘친다. 햇살이 창문으로 든다.", 1),
    ("ko.tic.frame-noun", "구조에 틈이 생긴다.", "문틈으로 바람이 든다. 액자 테두리가 굵다.", 1),
    ("ko.tic.deal-with", "이 문서는 규칙을 다룬다.", "이 문서는 규칙을 설명한다. 강아지를 다루는 법을 배웠다.", 1),
    ("ko.tic.split-verb", "이 값이 승부를 가른다.", "빵을 반으로 가른다. 다섯 가지로 나눈다.", 1),
    ("ko.tic.contain-verb", "표에 결과를 담는다.", "그릇에 밥을 담는다. 담배를 끊는다.", 1),
    ("ko.tic.impression-give", "결과가 좋은 인상을 준다.", "그는 얼굴 인상이 부드럽다. 가격 인상을 발표했다.", 1),
    ("ko.tic.impression-bare", "인상적인 결과다.", "임금 인상률이 높다. 얼굴이 순한 인상이다.", 1),
    ("ko.tic.fit-together", "두 값이 맞아떨어집니다.", "톱니가 맞물린다. 퍼즐 조각이 들어맞는다.", 1),
    ("ko.tic.bind-verb", "비슷한 항목을 묶습니다.", "머리를 끈으로 묶는다. 짐을 줄로 묶어 둔다.", 1),
    ("ko.tic.generation", "차세대 모델이 나왔다. 이전 세대와 비교한다.", "부모 세대와 자녀 세대는 다르다. 아파트 200세대가 입주했다.", 1),
    ("ko.tic.destination", "이 글의 목적지는 결론이다.", "택시가 목적지에 도착했다.", 1),
    ("ko.tic.jot-verb", "결과를 표에 적습니다.", "오류가 적습니다. 적어도 하나는 필요하다.", 1),
    ("ko.tic.same-opener", "같은 방식으로 본다.", "이 방식으로 본다.", 2),
    ("ko.tic.add-verb", "깊이를 더한다.", "표현을 보탠다.", 2),
    ("ko.tic.evidence-grade", "증거 등급을 매긴다.", "근거의 수준을 매긴다.", 1),
    ("ko.tic.grade-bare", "등급을 매긴다.", "수준을 매긴다. 영화 관람 등급을 본다.", 2),
    ("ko.tic.anchor", "기준점을 정한다.", "기준을 정한다.", 1),
    ("ko.tic.same-meaning", "두 값이 같다는 뜻이다.", "두 값이 같다.", 1),
    ("ko.tic.means-that", "더 낮다는 뜻입니다.", "더 낮다.", 2),
    ("ko.tic.numbering", "첫 줄은 요약이다.", "요약부터 쓴다.", 1),
    ("ko.tic.section-word", "한 언어에 있는 절은 여섯 언어 모두에 들어갑니다. 이 절에서는 규칙을 설명한다.", "절에 가서 큰절을 올렸다. 법당 앞에서 절을 한다. 절차와 절반을 본다.", 1),
    ("ko.tic.a-set", "규칙 한 벌을 만든다.", "양복 한 벌을 샀다.", 1),
]


class WordHabit(unittest.TestCase):
    def test_every_rule_has_a_case(self):
        self.assertEqual({r.id for r in ko_wordhabit.RULES}, {c[0] for c in CASES})

    def test_cases(self):
        for rid, pos, neg, n in CASES:
            hit = {f.rule_id for f in analyze((pos + " ") * n).findings}
            miss = {f.rule_id for f in analyze((neg + " ") * n).findings}
            with self.subTest(rule=rid):
                self.assertIn(rid, hit, f"걸려야 한다: {pos!r}")
                self.assertNotIn(rid, miss, f"걸리면 안 된다: {neg!r}")

    def test_number_before_beol(self):
        for n in ("한", "두", "세", "네", "다섯", "열", "3", "12"):
            with self.subTest(n=n):
                self.assertIn("ko.tic.a-set", {f.rule_id for f in analyze(f"예시 {n} 벌을 만든다.").findings})
        for ok in ("정장 두 벌을 맡겼다.", "한복 세 벌을 빌렸다.", "벌이 날아온다.", "벌을 받는다."):
            with self.subTest(ok=ok):
                self.assertNotIn("ko.tic.a-set", {f.rule_id for f in analyze(ok).findings})

    def test_report_only(self):
        for r in ko_wordhabit.RULES:
            self.assertEqual(r.tier, "none", r.id)


class PredicateRepeat(unittest.TestCase):
    def ids(self, text):
        return {f.rule_id for f in analyze(text).findings}

    def test_same_verb_restated_in_one_sentence(self):
        text = "입력 순서는 유지되며 출력 순서도 유지됩니다. 파일을 저장했습니다."
        self.assertIn("ko.rhythm.verb-restate", self.ids(text))

    def test_same_verb_in_next_sentence(self):
        text = "목록은 순서를 유지한다. 표는 열 순서를 유지한다."
        self.assertIn("ko.rhythm.verb-restate", self.ids(text))

    def test_different_verbs_pass(self):
        text = "입력 순서는 유지되며 출력은 정렬됩니다. 파일을 저장했습니다."
        self.assertNotIn("ko.rhythm.verb-restate", self.ids(text))

    def test_pair_of_same_ending_class(self):
        text = "각 항목을 연결합니다. 순서는 유지됩니다. 마지막에 결과를 보여 줍니다."
        self.assertIn("ko.rhythm.pair-ending", self.ids(text))

    def test_single_ending_passes(self):
        text = "각 항목을 연결합니다. 순서는 그대로 두었고, 결과를 보여 줍니다."
        self.assertNotIn("ko.rhythm.pair-ending", self.ids(text))


if __name__ == "__main__":
    unittest.main()
