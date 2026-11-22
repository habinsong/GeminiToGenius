"""장르별 윤문 지침에서 옮긴 규칙: 규칙마다 걸리는 글과 안 걸리는 글. 여러 번 나와야 세는 규칙은 반복해서 넣는다.

예문은 모두 이 저장소에서 새로 쓴 것이다.
"""
import unittest

import _path  # noqa: F401
from ai_smell.detect import analyze
from ai_smell.rules import ko_genre

# (규칙 id, 걸려야 하는 글, 걸리면 안 되는 글, 반복 횟수)
CASES = [
    ("ko.genre.pronoun-repeat", "그녀는 문을 열었다. 그녀는 창을 봤다.", "민지는 문을 열었다. 창을 봤다.", 2),
    ("ko.genre.synonym-pair", "빠르고 신속한 처리를 한다.", "빠른 처리를 한다.", 1),
    ("ko.genre.will-look", "이제 각 단계를 살펴보겠습니다.", "각 단계는 세 개입니다.", 1),
    ("ko.genre.strawman", "비싸다고 생각할 수 있지만 싸다.", "가격은 3만 원이다.", 1),
    ("ko.genre.vague-authority", "전문가들은 이 방식이 낫다고 말한다.", "김 교수는 이 방식이 낫다고 말했다.", 1),
    ("ko.genre.noun-chain", "성능의 향상을 통한 효율의 증대를 노린다.", "성능을 높여 효율을 올린다.", 1),
    ("ko.genre.genitive-chain", "연구의 결과의 의미의 해석을 다룬다.", "연구 결과가 뜻하는 바를 다룬다.", 1),
    ("ko.genre.ripple", "이 정책은 큰 파급 효과를 낳았다.", "이 정책으로 요금이 내렸다.", 1),
    ("ko.genre.rather-than", "속도보다는 정확도다. 양보다는 질이다. 말보다는 행동이다.", "정확도가 중요하다.", 1),
    ("ko.genre.contribution", "학계에 기여할 것으로 기대된다.", "오류를 3% 줄였다.", 1),
    ("ko.genre.must-have-been", "정말 속상하셨겠어요.", "배송이 이틀 늦었습니다.", 1),
    ("ko.genre.cheer", "앞으로도 응원합니다.", "다음 주에 다시 연락드리겠습니다.", 1),
    ("ko.genre.echo-question", "배송 기간이 궁금하셨군요.", "배송은 이틀 걸립니다.", 1),
    ("ko.genre.double-hedge", "효과가 있을 수 있을 것으로 사료된다.", "효과가 있는 것으로 보인다.", 1),
    ("ko.genre.about-repeat", "데이터에 관한 연구를 한다.", "데이터 연구를 한다.", 3),
    ("ko.genre.double-particle", "서울에서의 생활을 다룬다.", "서울에서 한 생활을 다룬다.", 2),
    ("ko.genre.aim-to", "속도를 높이는 것을 목표로 하였다.", "속도를 높이려 하였다.", 1),
    ("ko.genre.need-for", "개선의 필요성이 대두된다.", "개선이 필요하다.", 1),
    ("ko.genre.suffix-pile", "안정성을 높인다. 고도화를 한다.", "안정되게 만든다.", 6),
    ("ko.genre.would-you", "주문하시겠어요?", "주문을 받겠습니다.", 3),
    ("ko.genre.as-you-know", "너도 알다시피 우리는 형제야.", "우리는 형제야.", 1),
    ("ko.genre.realize-late", "그제야 그는 깨달았다.", "그는 문을 닫았다.", 1),
    ("ko.genre.ellipsis-dialogue", "“나는… 그러니까… 모르겠어.”", "“나는 모르겠어…”", 1),
    ("ko.genre.named-emotion", "그녀는 깊은 상실감에 빠졌다.", "그녀는 신발을 벗지 않았다.", 1),
    ("ko.genre.double-simile", "마치 바다처럼 넓고 꿈처럼 아득했다.", "바다는 넓었다.", 1),
]


class GenreRules(unittest.TestCase):
    def test_every_rule_has_a_case(self):
        self.assertEqual({r.id for r in ko_genre.RULES}, {c[0] for c in CASES})

    def test_cases(self):
        for rid, pos, neg, n in CASES:
            hit = {f.rule_id for f in analyze((pos + " ") * n).findings}
            miss = {f.rule_id for f in analyze((neg + " ") * n).findings}
            with self.subTest(rule=rid):
                self.assertIn(rid, hit, f"걸려야 한다: {pos!r}")
                self.assertNotIn(rid, miss, f"걸리면 안 된다: {neg!r}")

    def test_no_rule_edits_text(self):
        for r in ko_genre.RULES:
            with self.subTest(rule=r.id):
                self.assertEqual(r.tier, "none")


class SelfReferenceMix(unittest.TestCase):
    def test_mixed_self_reference(self):
        text = "필자는 이 문제를 다룬다. 본 연구는 자료를 모았다. 결과는 표 2에 있다."
        self.assertIn("ko.genre.self-reference-mix", {f.rule_id for f in analyze(text).findings})

    def test_single_self_reference(self):
        text = "본 연구는 이 문제를 다룬다. 본 연구는 자료를 모았다. 결과는 표 2에 있다."
        self.assertNotIn("ko.genre.self-reference-mix", {f.rule_id for f in analyze(text).findings})


if __name__ == "__main__":
    unittest.main()
