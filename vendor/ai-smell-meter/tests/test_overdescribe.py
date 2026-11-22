"""과서술 규칙: 규칙마다 걸리는 글과 안 걸리는 글. 여러 번 나와야 세는 규칙은 반복해서 넣는다."""
import unittest

import _path  # noqa: F401
from ai_smell.detect import analyze
from ai_smell.rules import ko_overdescribe

# (규칙 id, 걸려야 하는 한 문장, 걸리면 안 되는 한 문장, 반복 횟수)
CASES = [
    ("ko.over.self-intro", "이 폴더는 지침을 담고 있다.", "지침은 이 폴더에 있다.", 2),
    ("ko.over.purpose-narration", "목록을 정렬하려고 숫자를 붙였습니다.", "목록은 숫자순이다.", 1),
    ("ko.over.because-tail", "이름이 다른 것은 도구가 다르기 때문입니다.", "도구가 다르다.", 2),
    ("ko.over.gloss", "이 값은 한도를 의미합니다.", "이 값이 한도다.", 2),
    ("ko.over.recorded", "근거를 따로 정리해 두었습니다.", "근거는 docs에 있다.", 2),
    ("ko.over.paren-stack", "경로(상대 경로)를 쓰고 값(문자열)을 넣는다.", "경로를 쓰고 값을 넣는다.", 3),
    ("ko.over.long-list", "사양, 가격, 점수, 출처, 한계를 적었다.", "사양과 가격을 적었다.", 3),
]


class OverDescribeRules(unittest.TestCase):
    def test_every_rule_has_a_case(self):
        self.assertEqual({r.id for r in ko_overdescribe.RULES}, {c[0] for c in CASES})

    def test_cases(self):
        for rid, pos, neg, n in CASES:
            hit = {f.rule_id for f in analyze((pos + " ") * n).findings}
            miss = {f.rule_id for f in analyze((neg + " ") * n).findings}
            with self.subTest(rule=rid):
                self.assertIn(rid, hit, f"걸려야 한다: {pos!r}")
                self.assertNotIn(rid, miss, f"걸리면 안 된다: {neg!r}")

    def test_none_of_them_edits_text(self):
        for r in ko_overdescribe.RULES:
            self.assertEqual(r.tier, "none", r.id)


if __name__ == "__main__":
    unittest.main()
