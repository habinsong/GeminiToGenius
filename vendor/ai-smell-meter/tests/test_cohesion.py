"""문장 잇기: 끊긴 단문 연속, 이음 없는 문단, 8개 언어 사전, 언어 판별, 윤문이 이음을 해치지 않는지."""
import unittest

import _path  # noqa: F401
from ai_smell import cohesion, linkers
from ai_smell.detect import analyze
from ai_smell.fix import polish
from ai_smell.prompt import build
from ai_smell.samples import CHOPPY, CONNECTED
from ai_smell.textutil import count_units, mask, paragraph_spans, protected_spans, sentence_spans
from ai_smell.verify import verify

# 사용자가 보고한 글의 꼴: 짧은 -ㅂ니다 문장이 접속어 없이 이어진다(내용은 이 시험을 위해 새로 썼다)
KO_STACCATO = ("이 노트북을 사도 되는지 봐 달라고 하셨습니다. 직접 써 보지는 못했습니다. 리뷰 두 건과 사용자 글을 본 판단입니다. "
               "배터리 시간은 짧은 편입니다. 화면은 밝고 선명합니다. 팬 소리는 거의 없습니다. 무게는 1.2kg입니다.")
KO_CONNECTED = ("이 노트북을 사도 되는지 봐 달라고 하셨는데, 직접 써 보지는 못했고 리뷰 두 건과 사용자 글을 본 판단입니다. "
                "다만 배터리 시간은 짧은 편이지만 화면이 밝고 선명하며, 그래서 실내 작업에는 무리가 없습니다. 게다가 팬 소리는 "
                "거의 없고 무게도 1.2kg이라 들고 다니기 좋습니다.")


def cut(text, **kw):
    return [f for f in analyze(text, **kw).findings if f.category == "cohesion" and f.weight > 0 and not f.shadowed]


def ids(text, **kw):
    return {f.rule_id for f in cut(text, **kw)}


class UserReport(unittest.TestCase):
    """접속어 없이 끊긴 -습니다 문장 나열이 0점으로 나오던 문제."""

    def test_staccato_polite_sentences_are_flagged(self):
        a = analyze(KO_STACCATO)
        self.assertIn("ko.cohesion.choppy-run", {f.rule_id for f in a.findings})
        self.assertGreaterEqual(a.score, 15)

    def test_polite_endings_without_a_connective_are_flagged(self):
        text = "배포는 월요일에 진행합니다. 점검은 30분이 걸립니다. 문제가 생기면 되돌리고 알려 드립니다."
        hit = [f for f in analyze(text).findings if f.rule_id == "ko.cohesion.nida-run"]
        self.assertEqual(len(hit), 1)
        self.assertIn("3개", hit[0].note)

    def test_a_connective_adverb_breaks_the_run(self):
        text = ("배포는 월요일에 진행합니다. 그래서 점검은 30분이 걸립니다. 문제가 생기면 되돌리고 알려 드립니다. "
                "또한 결과는 메일로 보냅니다.")
        self.assertFalse([f for f in analyze(text).findings if f.rule_id == "ko.cohesion.nida-run"])

    def test_the_connective_counts_with_or_without_a_comma(self):
        for adv in ("그래서", "그래서,", "또한", "또한,", "다만", "다만,"):
            text = (f"배포는 월요일에 진행합니다. {adv} 점검은 30분이 걸립니다. 문제가 생기면 되돌리고 알려 드립니다. "
                    "결과는 메일로 보냅니다.")
            runs = [f.note for f in analyze(text).findings if f.rule_id == "ko.cohesion.nida-run"]
            self.assertEqual(len(runs), 1, adv)
            self.assertIn("3개", runs[0], adv)             # 앞 한 문장이 떨어져 나가고 뒤 세 문장이 남는다

    def test_long_polite_sentences_are_human_breathing(self):
        long = ("이번 배포는 월요일 오전에 운영팀이 직접 진행하고 결과는 같은 날 저녁까지 공유하기로 했습니다. "
                "점검은 배포가 끝난 뒤에 서른 분 동안 이어지며 그 사이에는 새 요청을 받지 않기로 정리했습니다. "
                "문제가 생기면 직전 버전으로 되돌린 다음 원인을 확인하고 다시 일정을 잡아 알리겠습니다.")
        self.assertFalse([f for f in analyze(long).findings if f.rule_id.startswith("ko.cohesion.nida")])

    def test_a_long_sentence_between_short_ones_breaks_the_run(self):
        mixed = ("배포는 월요일입니다. 점검은 배포가 끝난 뒤에 서른 분 동안 이어지며 그 사이에는 새 요청을 받지 않기로 했습니다. "
                 "되돌릴 수 있습니다. 알림은 메일로 갑니다.")
        self.assertFalse([f for f in analyze(mixed).findings if f.rule_id == "ko.cohesion.nida-run"])

    def test_two_polite_sentences_are_fine(self):
        text = "배포는 월요일에 진행합니다. 점검은 30분이 걸립니다."
        self.assertFalse([f for f in analyze(text).findings if f.rule_id == "ko.cohesion.nida-run"])

    def test_a_very_short_polite_sentence_after_a_polite_one_is_flagged(self):
        text = "배포는 월요일에 진행하기로 했습니다. 가능합니다."
        self.assertTrue([f for f in analyze(text).findings if f.rule_id == "ko.cohesion.nida-short"])
        ok = "배포는 월요일에 진행하기로 했습니다. 점검은 30분이 걸린다고 합니다."
        self.assertFalse([f for f in analyze(ok).findings if f.rule_id == "ko.cohesion.nida-short"])

    def test_connected_version_is_not_flagged(self):
        self.assertEqual(cut(KO_CONNECTED), [])

    def test_note_names_the_shared_ending(self):
        f = next(f for f in cut(KO_STACCATO) if f.rule_id.endswith("choppy-run"))
        self.assertIn("'-다'", f.note)

    def test_suggestion_lists_connectives_by_relation(self):
        f = cut(KO_STACCATO)[0]
        for word in ("하지만", "그래서", "연결어미"):
            self.assertIn(word, f.sugg)


class Languages(unittest.TestCase):
    def test_choppy_samples_are_flagged_in_every_language(self):
        for lang, text in CHOPPY.items():
            self.assertTrue(cut(text), lang)

    def test_connected_samples_are_not_flagged(self):
        for lang, text in CONNECTED.items():
            self.assertFalse(cut(text), lang)

    def test_detect_language(self):
        want = {"ko": "ko", "en": "en", "ja": "ja", "zh": "zh", "es": "es", "fr": "fr", "de": "de", "ru": "ru"}
        for lang, expect in want.items():
            self.assertEqual(linkers.detect(CHOPPY[lang]), expect, lang)
        self.assertEqual(linkers.detect("O cache guarda as respostas por 60 segundos, mas não é compartilhado também."), "pt")
        self.assertEqual(linkers.detect("La cache conserva le risposte per 60 secondi, ma non è condivisa con il resto."), "it")
        self.assertEqual(linkers.detect("12345 ... ###"), "other")

    def test_korean_with_many_latin_names_stays_korean(self):
        self.assertEqual(linkers.detect("digitalmarketer.co.kr, discuss.pytorch.kr, blog.pebblous.ai. 모두 풀리지 않았다."), "ko")

    def test_cjk_sentences_split_without_spaces(self):
        text = CHOPPY["ja"]
        sents = sentence_spans(mask(text, protected_spans(text)))
        self.assertEqual(len(sents), 4)
        self.assertGreaterEqual(count_units(text), 20)

    def test_report_names_the_detected_language(self):
        from ai_smell.report import render_analysis
        text = CHOPPY["ja"]
        self.assertIn("일본어", render_analysis(analyze(text), text))

    def test_other_languages_need_a_longer_run(self):
        four = "Kissa istuu aidalla. Koira nukkuu pihalla. Lintu laulaa puussa. Kala uiskentelee lammessa."
        five = four + " Hevonen juoksee pellolla."
        self.assertEqual(linkers.detect(five), "other")
        self.assertFalse(cut(four))
        self.assertTrue(cut(five))


class Bridges(unittest.TestCase):
    def lead(self, s, lang):
        return linkers.lead_link(s, lang)

    def test_korean_parts_of_speech(self):
        self.assertEqual(self.lead("그런데, 값이 다르다.", "ko")[:2], ("adv", "adversative"))
        self.assertEqual(self.lead("결국은 같은 값이다.", "ko")[:2], ("adv", "restate"))        # 조사 뗀 접속부사
        self.assertEqual(self.lead("이것은 캐시다.", "ko")[:2], ("ref", "reference"))          # 지시 대명사 + 조사
        self.assertEqual(self.lead("이 때문에 값이 다르다.", "ko")[:2], ("adv", "causal"))    # 두 어절을 한 말로
        self.assertEqual(self.lead("첫째, 시간이다.", "ko")[:2], ("ord", "temporal"))         # 수사
        self.assertIsNone(self.lead("이달에는 값이 다르다.", "ko"))                            # 접두 일치로 오인하지 않는다

    def test_english_longest_match_and_kinds(self):
        self.assertEqual(self.lead("As a result, it broke.", "en")[:2], ("adv", "causal"))
        self.assertEqual(self.lead("Because it broke, we left.", "en")[:2], ("sub", "causal"))
        self.assertEqual(self.lead("But it broke.", "en")[:2], ("conj", "adversative"))
        self.assertEqual(self.lead("That is why it broke.", "en")[2], "that is why")
        self.assertIsNone(self.lead("Cats sleep.", "en"))

    def test_inflected_demonstratives(self):
        for s, lang in (("Diesem Wert fehlt viel.", "de"), ("Этого значения нет.", "ru"), ("Estas cifras bajan.", "es"),
                        ("Cette valeur baisse.", "fr"), ("Questa cifra scende.", "it")):
            self.assertEqual(self.lead(s, lang)[:2], ("ref", "reference"), s)

    def test_japanese_and_chinese_prefix_match(self):
        self.assertEqual(self.lead("そのため、値は違う。", "ja")[:2], ("adv", "causal"))        # 그 + のため 중 가장 긴 말
        self.assertEqual(self.lead("しかし値は違う。", "ja")[:2], ("adv", "adversative"))
        self.assertEqual(self.lead("所以值不同。", "zh")[:2], ("adv", "causal"))
        self.assertEqual(self.lead("这些值不同。", "zh")[:2], ("ref", "reference"))

    def test_carry_over(self):
        self.assertTrue(cohesion.carry_over("값을 계산합니다. 결과는 캐시에 저장됩니다.", "캐시는 60초 뒤에 지워진다.", "ko"))
        self.assertFalse(cohesion.carry_over("값을 계산합니다.", "팬 소리는 거의 없다.", "ko"))
        self.assertTrue(cohesion.carry_over("The server restarts nightly.", "Nightly restarts clear every session.", "en"))
        self.assertFalse(cohesion.carry_over("The server restarts.", "Prices fell.", "en"))
        self.assertTrue(cohesion.carry_over("結果はキャッシュに保存されます。", "キャッシュは六十秒で消えます。", "ja"))

    def test_menu_lists_every_relation(self):
        for lang in linkers.SUPPORTED:
            menu = linkers.menu(lang, "en")
            self.assertGreaterEqual(menu.count("("), 4, lang)
        self.assertEqual(linkers.menu("other"), "")

    def test_every_language_has_a_complete_lexicon(self):
        for lang in linkers.SUPPORTED:
            kinds = {v[0] for v in linkers.lexicon(lang).items.values()}
            rels = {v[1] for v in linkers.lexicon(lang).items.values()}
            self.assertIn("ref", kinds, lang)
            self.assertTrue(set(linkers.RELATIONS) <= rels, lang)


class Signals(unittest.TestCase):
    def test_bridging_only_needs_one_device(self):
        text = "배포는 월요일에 한다. 점검은 30분이다. 대신 로그는 따로 쌓는다. 문제가 생기면 되돌린다."
        self.assertFalse(cut(text))                      # 세 번째 문장이 '대신'으로 잇는다

    def test_no_bridge_paragraph(self):
        text = ("배포는 월요일에 한다. 점검 시간은 30분이다. 서버는 두 대다. 로그는 따로 쌓는다. 알림은 메일로 간다. "
                "되돌리기는 수동이다.")
        self.assertIn("ko.cohesion.no-bridge", ids(text))

    def test_lists_tables_and_dialogue_are_skipped(self):
        self.assertFalse(cut("- 하나다. 둘이다. 셋이다. 넷이다.\n- 다섯이다."))
        self.assertFalse(cut("| 가 | 나 |\n|---|---|\n| 하나다. 둘이다. 셋이다. | 넷이다. |"))
        talk = '그가 "가자." 했다. 나는 "싫어." 했다. 그가 "왜." 했다. 나는 "그냥." 했다. 그가 "그래." 했다.'
        self.assertFalse(cut(talk))

    def test_literary_genre_lowers_the_weight(self):
        base = sum(f.weight for f in cut(KO_STACCATO))
        lit = sum(f.weight for f in cut(KO_STACCATO, genre="literary"))
        self.assertLess(lit, base * 0.5)

    def test_chinese_weight_is_lower_than_the_same_pattern_elsewhere(self):
        zh = sum(f.weight for f in cut(CHOPPY["zh"]))
        ja = sum(f.weight for f in cut(CHOPPY["ja"]))
        self.assertLess(zh, ja)

    def test_cohesion_does_not_shadow_other_signals(self):
        text = "좋아요! 최고예요! 정말 멋져요! 가요!"
        found = {f.rule_id for f in analyze(text).findings if not f.shadowed}
        self.assertIn("any.format.exclaim", found)
        self.assertIn("ko.cohesion.choppy-run", found)

    def test_metrics_describe_the_links(self):
        c = analyze(KO_CONNECTED).metrics["cohesion"]
        self.assertEqual(c["language"], "ko")
        self.assertGreater(c["bridge_ratio"], 0)
        self.assertEqual(c["linkers_by_relation"].get("additive"), 1)
        self.assertIn("평서·현재", c["ending_forms"])

    def test_korean_ending_forms(self):
        self.assertEqual(cohesion._ko_ending("값이 올랐습니다."), "평서·과거")
        self.assertEqual(cohesion._ko_ending("값이 오릅니다."), "평서·현재")
        self.assertEqual(cohesion._ko_ending("값이 있습니다."), "평서·현재")      # '있'의 ㅆ은 과거가 아니다
        self.assertEqual(cohesion._ko_ending("값이 오를까요?"), "의문")
        self.assertEqual(cohesion._ko_ending("값을 보세요."), "명령·청유")
        self.assertEqual(cohesion._ko_ending("값이 오를 것 같다."), "평서·현재")


class PolishKeepsLinks(unittest.TestCase):
    def test_polish_never_adds_cohesion_findings(self):
        for text in list(CHOPPY.values()) + list(CONNECTED.values()) + [KO_STACCATO, KO_CONNECTED]:
            for tier in ("safe", "standard", "strong"):
                out = polish(text, tier=tier).text
                self.assertLessEqual(len(cut(out)), len(cut(text)), (tier, text[:20]))

    def test_verify_warns_when_a_rewrite_chops_sentences(self):
        v = verify(KO_CONNECTED, KO_STACCATO)
        self.assertTrue(any("이음이 더 끊겼다" in m for _, m in v.messages), v.messages)
        self.assertFalse(any("이음이 더 끊겼다" in m for _, m in verify(KO_STACCATO, KO_CONNECTED).messages))

    def test_prompt_tells_the_editor_not_to_chop_and_gives_a_menu(self):
        text = CHOPPY["ja"]
        prompt = build(text, analyze(text), ui="en", target="claude")
        self.assertIn("<linking_sentences>", prompt)
        self.assertIn("Do not lower the score by chopping", prompt)
        self.assertIn("Japanese linking words by relation", prompt)
        self.assertIn("しかし", prompt)
        ko = build(KO_STACCATO, analyze(KO_STACCATO))
        self.assertIn("# 문장 잇기", ko)
        self.assertIn("의외성", ko)

    def test_cli_prints_the_link_table(self):
        import subprocess
        import sys
        out = subprocess.run([sys.executable, "-I", str(_path.LAUNCHER), "linkers", "--lang", "ja", "--ui", "en"],
                             capture_output=True, text=True, encoding="utf-8", check=True).stdout
        self.assertIn("[Japanese]", out)
        self.assertIn("そのため", out)


if __name__ == "__main__":
    unittest.main()
