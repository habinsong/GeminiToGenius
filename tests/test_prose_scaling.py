"""문서 전체·한 문단의 최소 횟수가 글 분량에 비례하는지, 시는 늘리지 않는지, 일반 갈래 전용 규칙과 맞춤법 규칙이 맞게 걸리는지 확인합니다.

긴 문서가 글이 길다는 이유만으로 경고를 쏟아내면 모델이 쓸데없는 경고 수십 개를 읽고 과하게 고칩니다. 사람이 쓴 논문 본문
100편(평균 79문장)에서 번역투 경고가 97%에 걸리던 것이 이 보정 뒤 26%로 줄었습니다.
"""

import unittest

from gtg.prose import examine, required
from gtg.prose_patterns import pattern


FILLER = "서버를 다시 켠 뒤에도 로그에는 예전 값이 그대로 남아 있었다."


def ids(text, register="general"):
    return [f["id"] for f in examine("doc.md", text, register)[0]]


class ScaleTests(unittest.TestCase):
    def test_two_repeats_flag_a_short_text_but_not_one_three_times_longer(self):
        short = "다양한 방법을 썼다. 다양한 도구도 썼다."
        self.assertIn("ko-diverse", ids(short))
        long = short + " " + " ".join([FILLER] * 58)
        self.assertNotIn("ko-diverse", ids(long), "60문장 글의 두 번은 분량에 비해 드뭅니다.")
        crowded = long + " " + " ".join(["다양한 도구를 썼다."] * 4)
        self.assertIn("ko-diverse", ids(crowded), "분량에 맞게 늘어난 기준을 넘으면 걸립니다.")

    def test_a_long_paragraph_needs_proportionally_more_repeats(self):
        sparse = " ".join(["데이터를 통해 확인한다."] * 3 + [FILLER] * 9)
        pile = " ".join(["데이터를 통해 확인한다."] * 6 + [FILLER] * 6)
        short = " ".join(["데이터를 통해 확인한다."] * 3)
        self.assertIn("ko-translationese", ids(short), "세 문장 문단의 세 번은 몰린 것입니다.")
        self.assertNotIn("ko-translationese", ids(sparse), "열두 문장 문단의 세 번은 기준(6)에 못 미칩니다.")
        self.assertIn("ko-translationese", ids(pile))

    def test_required_count_follows_the_reference_length(self):
        document = pattern("x-doc", "review", "document", 4, "x", "")
        paragraph = pattern("x-par", "review", "paragraph", 3, "x", "")
        self.assertEqual(required(document, 0, 20, {}, False), 4, "기준 분량(20문장)에서는 규칙의 값 그대로입니다.")
        self.assertEqual(required(document, 0, 5, {}, False), 4, "짧은 글은 기준을 낮추지 않습니다.")
        self.assertEqual(required(document, 0, 60, {}, False), 12)
        self.assertEqual(required(paragraph, 1, 99, {1: 12}, False), 6)
        self.assertEqual(required(paragraph, 1, 99, {1: 2}, False), 3)

    def test_block_rules_are_never_scaled_so_a_long_paragraph_still_blocks_antithesis_chains(self):
        """가장 엄격하게 막기로 한 신호가 긴 문단에서는 느슨해지면 안 됩니다. 3.2.0은 열두 문장 문단의 대구 두 번을 차단했습니다."""
        block = pattern("x-block", "block", "paragraph", 2, "x", "")
        self.assertEqual(required(block, 1, 99, {1: 12}, False), 2)
        paragraph = " ".join(["이것은 기술이 아니라 태도다.", "실패가 아니라 과정이다."] + [FILLER] * 10)
        found = {(f["id"], f["severity"]) for f in examine("doc.md", paragraph)[0]}
        self.assertIn(("ko-antithesis-chain", "block"), found)

    def test_verse_is_never_scaled(self):
        """행이 호흡 단위인 시는 문장으로 환산하면 판별력이 떨어졌습니다(KatFish 시 AUC 0.669 → 0.652)."""
        document = pattern("x-doc", "review", "document", 4, "x", "")
        self.assertEqual(required(document, 0, 40, {}, True), 4)
        poem = "\n".join(f"{word} 피는 저녁" for word in ("꽃", "별", "달", "물", "풀", "새", "돌", "강", "산") * 4)
        poem += "\n" + "\n".join(["천천히 걸었다"] * 4)
        self.assertIn("literary-reflective", ids(poem, "literary"))


class GeneralOnlyRuleTests(unittest.TestCase):
    """KatFish 에세이에서 LLM 글의 13~29%, 사람 글의 0~8%에 나온 표현입니다. 초록에서는 사람과 LLM이 같은 비율로 썼습니다."""

    CASES = {
        "ko-this-is-open": "이는 비용 때문이다. 이는 시간 때문이기도 하다.",
        "ko-demonstrative-open": "이러한 변화가 있었다. 이와 같은 결과도 나왔다.",
        "ko-diverse": "다양한 방법을 썼다. 다양한 도구도 썼다.",
    }

    def test_they_fire_on_repeats_in_the_general_register_only(self):
        for rule, text in self.CASES.items():
            with self.subTest(rule=rule):
                self.assertIn(rule, ids(text))
                for register in ("academic", "everyday", "literary"):
                    self.assertNotIn(rule, ids(text, register))

    def test_a_single_use_is_left_alone_and_midsentence_uses_are_not_openings(self):
        for rule, text in self.CASES.items():
            with self.subTest(rule=rule):
                self.assertNotIn(rule, ids(text.split(". ")[0] + "."))
        midsentence = "원인은 비용이고 이는 곧 시간이다. 그 변화는 이러한 방식으로 나타났다. 이와 같이 쓰기도 한다."
        self.assertNotIn("ko-this-is-open", ids(midsentence))
        self.assertNotIn("ko-demonstrative-open", ids(midsentence))


class MisspellingTests(unittest.TestCase):
    WRONG = ("이러면 안되요?", "어제 밤을 샜더니 피곤했다. 그렇게 됬다.", "내일 연락할께요.", "몇일 걸려요.", "어떻해야 하나.", "금새 끝났다.",
             "설레임이 컸다.", "웬지 불안하다.", "왠만하면 그만하자.", "희안한 일이다.", "역활을 맡았다.", "일일히 확인했다.",
             "오랫만이다.", "내일 뵈요.", "숙제를 않했다.", "아니예요.", "통채로 삼켰다.")
    RIGHT = ("이러면 안 돼요?", "그렇게 됐다.", "내일 연락할게요.", "며칠 걸려요.", "어떡해야 하나.", "금세 끝났다.", "설렘이 컸다.",
             "왠지 불안하다.", "웬만하면 그만하자.", "희한한 일이다.", "역할을 맡았다.", "일일이 확인했다.", "오랜만이다.", "내일 봬요.",
             "숙제를 안 했다.", "아니에요.", "통째로 삼켰다.", "5일께 끝날 것이다.", "6월께 문을 연다.", "이달 말께 발표한다.",
             "함께 가자.", "할머니께 드렸다.")

    def test_common_misspellings_are_flagged_and_their_correct_forms_are_not(self):
        for text in self.WRONG:
            with self.subTest(text=text):
                self.assertIn("ko-misspelling", ids(text))
        for text in self.RIGHT:
            with self.subTest(text=text):
                self.assertNotIn("ko-misspelling", ids(text))

    def test_it_is_a_review_that_never_blocks(self):
        found, _ = examine("doc.md", "내일 연락할께요. 몇일 걸려요.")
        self.assertEqual({f["severity"] for f in found if f["id"] == "ko-misspelling"}, {"review"})


if __name__ == "__main__":
    unittest.main()
