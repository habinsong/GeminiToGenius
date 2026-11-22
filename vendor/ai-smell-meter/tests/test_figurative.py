"""비유 어휘, 호응 어긋남, 문장틀 규칙: 규칙마다 걸리는 글과 안 걸리는 글. 여러 번 나와야 세는 규칙은 반복해서 넣는다."""
import unittest

import _path  # noqa: F401
from ai_smell.detect import analyze
from ai_smell.rules import ko_figurative

# (규칙 id, 걸려야 하는 한 문장, 걸리면 안 되는 한 문장, 반복 횟수)
CASES = [
    ("ko.figure.lens", "이 문제를 비용이라는 렌즈로 본다.", "카메라 렌즈를 닦았다.", 2),
    ("ko.figure.axis", "비교는 두 축으로 나뉜다.", "자전거 바퀴의 축이 휘었다.", 2),
    ("ko.figure.layer", "이 말에는 여러 겹의 뜻이 있다.", "눈이 쌓여도 길은 열렸다.", 2),
    ("ko.figure.weight", "결정의 무게를 견디기 어렵다.", "짐의 무게를 달았다.", 2),
    ("ko.figure.temperature", "조직의 온도가 달라졌다.", "방의 온도를 쟀다.", 2),
    ("ko.figure.landscape", "일터의 풍경이 바뀌고 있다.", "창밖 풍경이 아름답다.", 2),
    ("ko.figure.guide", "이 원칙이 나침반 역할을 한다.", "등산 가방에 나침반을 넣었다.", 1),
    ("ko.figure.journey", "디지털 여정을 시작한다.", "여행을 떠났다.", 2),
    ("ko.figure.pillar", "세 기둥이 체계를 받친다.", "집 기둥에 못을 박았다.", 2),
    ("ko.figure.weave", "서로 다른 이야기를 촘촘히 엮어 짠 글이다.", "스웨터를 짰다.", 1),
    ("ko.figure.joint", "시스템과 시스템 사이의 이음매가 문제다.", "배관 이음매를 조였다.", 1),
    ("ko.figure.resonance", "독자의 마음에 깊이 공명한다.", "스피커가 울린다.", 1),
    ("ko.figure.hold", "그는 끝까지 이 원칙을 붙들고 있다.", "그는 손잡이를 잡았다.", 3),
    ("ko.figure.draw", "글에서 의미를 길어 올린다.", "우물에서 물을 길었다.", 1),
    ("ko.figure.grammar-of", "플랫폼의 문법이 달라졌다.", "영어 문법을 배운다.", 2),
    ("ko.figure.unlock", "숫자가 살아 숨 쉬는 표가 된다.", "표를 만들었다.", 1),
    ("ko.figure.felt-fact", "통계는 서늘한 현실을 보여 준다.", "날씨가 서늘하다.", 2),
    ("ko.figure.hedge-verb", "논의를 깊이 파고들어 본다.", "땅을 팠다.", 2),
    ("ko.collocate.build", "이 도구는 이해를 구축한다.", "서버를 구축한다.", 1),
    ("ko.collocate.generate", "이 흐름은 공감을 생성한다.", "보고서를 생성한다.", 1),
    ("ko.collocate.deliver", "팀은 가치를 전달한다.", "택배를 전달한다.", 2),
    ("ko.collocate.formal-verb", "행사는 공감을 도모한다.", "예산을 제고한다.", 1),
    ("ko.collocate.enjoy", "편의를 향유한다.", "서비스를 이용한다.", 1),
    ("ko.collocate.perform", "점심 식사를 수행한다.", "시험을 수행한다.", 1),
    ("ko.collocate.informed", "정보에 입각한 결정을 내린다.", "정보를 모아 결정한다.", 1),
    ("ko.collocate.nuance", "뉘앙스 있는 이해가 필요하다.", "표현의 뉘앙스를 살린다.", 1),
    ("ko.collocate.success", "성공적으로 이해한다.", "시험에 합격했다.", 1),
    ("ko.frame.in-progress", "결과가 확인되고 있다. 값이 만들어지고 있다.", "변화가 일어났다.", 3),
    ("ko.frame.evident", "이 결과는 분명하다.", "이 결과는 표에 있다.", 2),
    ("ko.frame.foundation", "새 제도의 발판을 마련한다.", "벽돌로 담을 쌓는다.", 1),
    ("ko.frame.no-longer", "이제 더 이상 그는 학생이 아니다.", "그는 학생이다.", 2),
    ("ko.frame.either-or", "이것은 도구인가, 목적인가?", "이것은 도구다.", 2),
    ("ko.frame.time-to", "이제 움직일 때입니다.", "그때 그는 움직였다.", 1),
    ("ko.frame.from-to", "관리에서 협력으로 전환한다.", "집에서 학교로 갔다.", 2),
    ("ko.frame.leads-to", "결국 이 길은 한 점으로 이어진다.", "길이 이어진다.", 2),
    ("ko.frame.reason-close", "이것이 서두르는 이유다.", "이유를 적었다.", 2),
    ("ko.frame.horizon", "향후 확장한다. 앞으로 늘린다. 중장기적으로 본다. 장기적으로 줄인다.", "내일 확장한다.", 1),
    ("ko.frame.open-problem", "과제도 남아 있다.", "과제를 냈다.", 1),
    ("ko.frame.musing", "어쩌면 그렇다. 비로소 알았다. 천천히 걸었다.", "그렇다.", 1),
    ("ko.frame.personified", "데이터는 우리에게 말해 준다.", "데이터를 읽었다.", 2),
    ("ko.frame.nobody-says", "이득이 크다는 분석이다.", "김 교수는 이득이 크다고 분석했다.", 2),
    ("ko.frame.hedged-outlook", "내년에는 줄 것으로 보인다.", "내년에는 준다.", 3),
    ("ko.frame.formal-noun", "그렇다는 점은 안다.", "그렇게 안다.", 4),
    ("ko.frame.degree-adverb", "매우 크다. ", "크다. ", 8),
    ("ko.frame.policy-verb", "기능을 확대하고 강화하는 방안이다.", "기능을 늘린다.", 1),
    ("ko.frame.deictic-lead", "이는 사실이다. 이는 문제다.", "사실이다. 문제다.", 2),
    ("ko.frame.numbered-inline", "필요한 것은 1) 계획을 짜고 2) 일정을 잡고 3) 시작한다.", "계획을 짜고 일정을 잡는다.", 1),
    ("ko.frame.subtitle-heading", "# 설계: 구조와 선택\n", "# 설계\n", 3),
    ("ko.frame.quote-emphasis", "\"효율\"을 따진다. ", "효율을 따진다. ", 6),
]


class FigurativeRules(unittest.TestCase):
    def test_every_new_rule_has_a_case(self):
        self.assertEqual({r.id for r in ko_figurative.RULES}, {c[0] for c in CASES})

    def test_cases(self):
        for rid, pos, neg, n in CASES:
            sep = "" if pos.endswith("\n") else " "
            hit = {f.rule_id for f in analyze((pos + sep) * n).findings}
            miss = {f.rule_id for f in analyze((neg + sep) * n).findings}
            with self.subTest(rule=rid):
                self.assertIn(rid, hit, f"걸려야 한다: {pos!r}")
                self.assertNotIn(rid, miss, f"걸리면 안 된다: {neg!r}")

    def test_none_of_them_edits_text(self):
        for r in ko_figurative.RULES:
            self.assertEqual(r.tier, "none", r.id)


if __name__ == "__main__":
    unittest.main()
