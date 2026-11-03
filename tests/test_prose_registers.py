"""글 갈래(일반·학술·일상·문학)마다 규칙이 바뀌는지, 대구·도치·번역투·높임 신호가 오탐 없이 잡히는지 확인합니다."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gtg.prose import check, examine
from gtg.prose_patterns import PATTERNS
from gtg.prose_registers import REGISTERS, rules


ROOT = Path(__file__).resolve().parents[1]


def found(text, register="general"):
    items, _ = examine("doc.md", text, register)
    return items


def ids(text, register="general", severity=None):
    return [f["id"] for f in found(text, register) if severity in (None, f["severity"])]


class RegisterRuleTests(unittest.TestCase):
    def test_unknown_register_is_rejected_before_any_file_is_read(self):
        with self.assertRaises(ValueError):
            rules("poetry")
        with tempfile.TemporaryDirectory() as temp, self.assertRaises(ValueError):
            check(Path(temp), ["missing.md"], "poetry")

    def test_a_hedge_needs_more_repetition_to_be_flagged_in_academic_text(self):
        once = "이 결과는 표본 편향의 영향이라고 볼 수 있다."
        twice = " ".join([once] * 2)
        self.assertNotIn("ko-hedged-copula", ids(once))
        self.assertIn("ko-hedged-copula", ids(twice, severity="review"))
        self.assertNotIn("ko-hedged-copula", ids(twice, "academic"), "학술문의 완곡 두 번은 관례입니다.")
        thrice = " ".join([once] * 3)
        self.assertIn("ko-hedged-copula", ids(thrice, "academic", "review"))

    def test_academic_conventions_are_kept_and_english_habits_are_flagged(self):
        self.assertIn("academic-agent-passive", ids("저자들에 의해 제안된 방법을 썼다.", "academic"))
        self.assertNotIn("academic-agent-passive", ids("이 효과는 불안에 의해 매개된다.", "academic"),
                         "학술 피동은 정형 표현입니다.")
        self.assertIn("academic-we", ids("우리는 표본을 모았다. 우리는 모형을 세웠다.", "academic"))
        self.assertNotIn("academic-we", ids("본 연구는 표본을 모았다. 모형도 세웠다.", "academic"))
        self.assertIn("academic-figure-label", ids("Figure 3에서 보듯이 오차가 줄었다.", "academic"))
        self.assertNotIn("academic-figure-label", ids("그림 3에서 보듯이 오차가 줄었다.", "academic"))
        self.assertIn("academic-archaic", ids("이 방법이 타당하다고 사료된다.", "academic"))
        self.assertIn("academic-novelty", ids("세계 최초로 제안한 방법이다.", "academic"))
        self.assertNotIn("academic-we", ids("우리는 표본을 모았다. 우리는 모형을 세웠다."), "학술 규칙은 학술 갈래에만 씁니다.")
        self.assertIn("academic-this-paper", ids("이 논문은 새 지표를 제안한다.", "academic"))
        self.assertNotIn("academic-this-paper", ids("본 논문은 새 지표를 제안한다.", "academic"))

    def test_verse_lines_ending_in_commas(self):
        poem = "바람이 불고,\n잎이 지고,\n해가 기울고,\n밤이 왔다"
        self.assertIn("literary-line-comma", ids(poem, "literary"))
        self.assertNotIn("literary-line-comma", ids(poem.replace(",", ""), "literary"))
        prose = "\n".join(["그날 아침 그는 오래 미뤄 둔 편지를 꺼내 다시 읽어 보았는데,"] * 3)
        self.assertNotIn("literary-line-comma", ids(prose, "literary"), "긴 산문 줄은 시행으로 보지 않습니다.")

    def test_every_register_keeps_the_shared_rules_it_does_not_disable(self):
        shared = {rule.id for rule in PATTERNS}
        for name, register in REGISTERS.items():
            with self.subTest(register=name):
                chosen = {rule.id for rule in rules(name)[0]}
                self.assertEqual(shared - chosen, set(register.disabled))
                self.assertTrue({rule.id for rule in register.extra} <= chosen)

    def test_inversion_is_natural_in_speech_and_limited_in_fiction(self):
        text = "정말 맛있다, 이 집 국밥은. 다시 와야겠다."
        self.assertIn("ko-inversion", ids(text))
        self.assertNotIn("ko-inversion", ids(text, "everyday"))
        self.assertNotIn("ko-inversion", ids(text, "literary"), "소설의 도치 한 번은 그대로 둡니다.")
        self.assertIn("ko-inversion", ids(text + " 정말 멀었다, 그 길은.", "literary"))


class ParallelismTests(unittest.TestCase):
    def test_one_antithesis_is_allowed_but_a_chain_in_one_paragraph_blocks(self):
        one = "문제는 속도가 아니라 순서였다. 그래서 순서를 바꿨다."
        self.assertNotIn("ko-antithesis", ids(one))
        self.assertNotIn("ko-antithesis-chain", ids(one))
        chain = "이것은 기술이 아니라 태도다. 실패가 아니라 과정이다."
        self.assertIn("ko-antithesis-chain", ids(chain, severity="block"))
        apart = "이것은 기술이 아니라 태도다.\n\n그 일은 실패가 아니라 과정이었다."
        self.assertNotIn("ko-antithesis-chain", ids(apart), "다른 문단이면 연쇄가 아닙니다.")
        self.assertIn("ko-antithesis", ids(apart, severity="review"))

    def test_addition_and_condition_are_not_counted_as_antithesis(self):
        text = "속도뿐만 아니라 비용도 줄었다. 그게 아니라면 다시 재야 한다. 성능뿐 아니라 메모리도 봤다."
        self.assertNotIn("ko-antithesis", ids(text))
        self.assertNotIn("ko-antithesis-chain", ids(text))

    def test_either_or_question_fronted_pronoun_and_reason_close(self):
        self.assertIn("ko-either-or", ids("이것은 진보인가, 아니면 퇴보인가?"))
        self.assertNotIn("ko-either-or", ids("어디로 갈까? 집에 가자."))
        self.assertIn("ko-fronted-resumptive", ids("꾸준함, 그것은 가장 큰 무기다."))
        self.assertNotIn("ko-fronted-resumptive", ids("회의가 끝났고, 그것은 다음 주에 다시 다룬다."))
        reason = "그래서 다들 이 방식을 쓰는 이유다. 결국 이것이 우리가 남는 이유다."
        self.assertIn("ko-reason-close", ids(reason))
        self.assertNotIn("ko-reason-close", ids("그래서 다들 이 방식을 쓰는 이유다."))
        self.assertIn("ko-rhetorical-hook", ids("왜 그럴까? 바로 비용 때문이다."))

    def test_repeated_sentence_openings_are_parallelism(self):
        text = "우리는 기록했다. 우리는 비교했다. 우리는 고쳤다."
        self.assertIn("rhythm-repeated-opening", ids(text))
        self.assertNotIn("rhythm-repeated-opening", ids("우리는 기록했다. 그리고 비교한 뒤 고쳤다."))
        listed = "\n".join(f"- 우리는 {verb}." for verb in ("기록했다", "비교했다", "고쳤다"))
        self.assertNotIn("rhythm-repeated-opening", ids(listed), "목록 항목은 산문이 아닙니다.")


class TranslationeseTests(unittest.TestCase):
    def test_future_assertion_and_light_verbs_count_only_when_they_pile_up(self):
        two = "시장이 커질 것이다. 투자도 늘어날 것이다."
        self.assertNotIn("ko-future-assertion", ids(two))
        self.assertIn("ko-future-assertion", ids(two + " 고용도 증가할 것이다."))
        self.assertNotIn("ko-future-assertion", ids("그건 이미 끝난 것이다. 그가 한 것이다. 내가 본 것이다."),
                         "과거 관형형 '~한 것이다'는 미래 단정이 아닙니다.")
        light = "회의를 진행했다. 조사를 실시했다. 실험을 수행했다."
        self.assertIn("ko-light-verb", ids(light))
        self.assertNotIn("ko-light-verb", ids("회의가 진행됐다. 진행 상황을 봤다. 실험을 했다."))

    def test_formal_noun_endings_and_teaser_sentences(self):
        close = "결국 사람이 만든 것이다. 그가 고른 것이다. 우리가 놓친 것이다."
        self.assertIn("ko-formal-noun-close", ids(close))
        self.assertNotIn("ko-formal-noun-close", ids("사람이 만들었다. 그가 골랐다. 우리가 놓쳤다."))
        self.assertNotIn("ko-formal-noun-close", ids("내일 비가 올 것이다. 늦을 것이다. 갈 것이다."),
                         "ㄹ 관형형은 미래 단정 규칙이 따로 셉니다.")
        for text in ("진짜 문제는 따로 있다. 사람이다.", "오히려 정반대다.", "흥미로운 점은 비용이다.",
                     "질문 자체가 잘못 던져졌다.", "이 모든 문제는 하나로 수렴한다."):
            with self.subTest(text=text):
                self.assertIn("ko-teaser", ids(text))
        self.assertNotIn("ko-teaser", ids("문제는 비용이다. 반대 의견도 있었다. 흥미로운 책을 샀다."))

    def test_abstract_subject_verbs_and_closing_formulas(self):
        self.assertIn("ko-abstract-verb", ids("이 기술은 큰 변화를 가져온다."))
        self.assertNotIn("ko-abstract-verb", ids("동생이 책을 가져왔다."), "구체적인 물건은 그대로 둡니다.")
        self.assertIn("ko-closing-formula", ids("이제는 바꿀 때다."))
        self.assertNotIn("ko-closing-formula", ids("밥 먹을 때 전화했다."))

    def test_plural_demonstrative_pronoun_and_comma_habits(self):
        self.assertIn("ko-plural-quantifier", ids("많은 사람들이 왔다. 다양한 기능들을 봤다."))
        self.assertNotIn("ko-plural-quantifier", ids("여러분들 오셨네요. 사람들이 왔다."))
        self.assertIn("ko-demonstrative", ids("해당 파일을 열고 해당 값을 바꾼 뒤 해당 서버에 올린다."))
        self.assertNotIn("ko-demonstrative", ids("이 값이 조건에 해당되면 서버에 올린다."))
        self.assertIn("ko-pronoun-repeat", ids("그것은 크다. 그것은 무겁다. 그것을 옮긴다."))
        self.assertIn("ko-comma-conjunction", ids("빠르다, 그리고 싸다. 좋다, 하지만 비싸다."))
        self.assertIn("ko-colon-intro", ids("설치 순서는 다음과 같습니다:"))
        self.assertNotIn("ko-colon-intro", ids("설치 순서는 다음과 같습니다."))
        self.assertIn("ko-jeok-chain", ids("구조적 한계와 전략적 함의, 근본적인 차이를 본다."))
        self.assertNotIn("ko-jeok-chain", ids("성적 차이와 실적 차이, 목적 기반 설계를 본다."))

    def test_measured_llm_essay_habits_need_repetition(self):
        self.assertIn("ko-importance-close", ids("소통이 중요합니다. 배려도 필요합니다."))
        self.assertNotIn("ko-importance-close", ids("소통이 중요합니다. 그래서 매주 만난다."))
        self.assertIn("ko-anaphoric-connective", ids("값을 모았다. 이를 통해서 원인을 찾았다."))
        self.assertNotIn("ko-anaphoric-connective", ids("그는 이를 통해 원인을 찾았다."), "문장 중간은 세지 않습니다.")
        self.assertIn("ko-moral-close", ids("우리 모두가 노력해야 합니다."))
        self.assertNotIn("ko-moral-close", ids("더 노력해야 합니다."))
        self.assertIn("ko-stock-phrase", ids("책, 영화 등 다양한 매체가 중요한 역할을 한다."))
        self.assertNotIn("ko-stock-phrase", ids("이 부품이 중요한 역할을 한다."))

    def test_comma_heavy_korean_text_is_flagged(self):
        heavy = " ".join(f"{i}번 값을 읽고, 저장한다." for i in range(10))
        light = " ".join(f"{i}번 값을 읽고 저장한다." for i in range(10))
        self.assertIn("rhythm-comma-heavy", ids(heavy))
        self.assertNotIn("rhythm-comma-heavy", ids(light))


class FormalityTests(unittest.TestCase):
    def test_mixing_formal_and_plain_endings_in_one_paragraph(self):
        mixed = "설정을 바꿨습니다. 그리고 서버를 다시 켰다."
        self.assertIn("register-mixed", ids(mixed))
        self.assertNotIn("register-mixed", ids("설정을 바꿨습니다.\n\n서버를 다시 켰다."))
        self.assertNotIn("register-mixed", ids(mixed, "literary"), "소설의 서술과 대사는 따로 판단합니다.")
        quoted = "나는 고개를 끄덕였다. \"다 끝났습니다.\" 그가 말했다."
        self.assertNotIn("register-mixed", ids(quoted), "인용한 말의 높임은 서술과 다를 수 있습니다.")

    def test_academic_text_written_in_formal_polite_endings(self):
        polite = " ".join(f"{i}번 실험에서 오차가 줄었습니다." for i in range(3))
        plain = " ".join(f"{i}번 실험에서 오차가 줄었다." for i in range(3))
        self.assertNotIn("register-academic-formal", ids(" ".join(polite.split(". ")[:2]), "academic"),
                         "두 문장만으로는 판단하지 않습니다.")
        self.assertIn("register-academic-formal", ids(polite, "academic"))
        self.assertNotIn("register-academic-formal", ids(plain, "academic"))
        self.assertNotIn("register-academic-formal", ids(polite), "일반 문서는 '~습니다'체가 기본입니다.")

    def test_everyday_text_with_one_flat_ending(self):
        stiff = " ".join(f"어제 {i}번 가게에 갔습니다." for i in range(10))
        self.assertIn("register-uniform-formal", ids(stiff, "everyday"))
        self.assertNotIn("register-uniform-formal", ids(stiff))
        flat = " ".join(f"어제 {i}번 가게에 갔어요." for i in range(8))
        self.assertIn("register-uniform-haeyo", ids(flat, "everyday"))
        spoken = flat + " 근데 거기 문을 닫았더라고요."
        self.assertNotIn("register-uniform-haeyo", ids(spoken, "everyday"))


class EverydayAndLiteraryTests(unittest.TestCase):
    def test_everyday_empathy_object_honorific_and_notice_tone(self):
        empathy = "정말 힘드셨겠어요. 그런 마음이 드는 게 당연해요."
        self.assertIn("everyday-empathy", ids(empathy, "everyday"))
        self.assertNotIn("everyday-empathy", ids("정말 힘드셨겠어요. 내일 같이 가요.", "everyday"))
        self.assertIn("everyday-object-honorific", ids("주문하신 커피 나오셨습니다.", "everyday"))
        self.assertNotIn("everyday-object-honorific", ids("주문하신 커피 나왔습니다.", "everyday"))
        self.assertIn("everyday-stiff-notice", ids("자세한 내용은 공지를 참고하시기 바랍니다.", "everyday"))
        self.assertNotIn("everyday-empathy", ids(empathy), "일반 문서에는 일상 규칙을 쓰지 않습니다.")

    def test_literary_ineffable_blocks_and_emotion_needs_density(self):
        self.assertIn("literary-ineffable", ids("형언할 수 없는 슬픔이었다.", "literary", "block"))
        self.assertEqual(ids("형언할 수 없는 슬픔이었다.", "literary", "block"), ["literary-ineffable"])
        one = "가슴이 먹먹했다. 그는 컵을 내려놓았다."
        self.assertNotIn("literary-emotion-cliche", ids(one, "literary"))
        self.assertIn("literary-emotion-cliche", ids(one + " 눈시울이 붉어졌다.", "literary"))
        surge = "그리움이 밀려왔다. 곧 슬픔이 차올랐다."
        self.assertIn("literary-emotion-surge", ids(surge, "literary"))
        self.assertIn("literary-epiphany", ids("그제야 깨달았다.", "literary"))

    def test_literary_text_allows_short_runs_that_general_text_flags(self):
        five = "비가 왔다. 문을 닫았다. 불을 껐다. 누웠다. 잠이 안 왔다."
        self.assertIn("rhythm-choppy", ids(five))
        self.assertNotIn("rhythm-choppy", ids(five, "literary"))
        self.assertIn("rhythm-choppy", ids(five + " 다시 일어났다.", "literary"))
        self.assertNotIn("rhythm-choppy", ids(five, "everyday"))


class CliTests(unittest.TestCase):
    def test_register_option_changes_the_exit_code_and_unknown_values_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "story.md").write_text("형언할 수 없는 슬픔이 방 안을 채웠다.\n", encoding="utf-8")

            def run(*extra):
                return subprocess.run([sys.executable, "-m", "gtg", "prose", "story.md", "--workspace", str(root), *extra],
                                      cwd=ROOT, capture_output=True, text=True,
                                      env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})

            general = run()
            literary = run("--register", "literary")
            self.assertEqual(general.returncode, 0, "표현을 포기하는 문장은 문학 갈래에서만 차단합니다.")
            self.assertEqual(literary.returncode, 1)
            self.assertEqual(json.loads(literary.stdout)["register"], "literary")
            unknown = run("--register", "poetry")
            self.assertEqual(unknown.returncode, 2)
            self.assertIn("poetry", unknown.stderr)


if __name__ == "__main__":
    unittest.main()
