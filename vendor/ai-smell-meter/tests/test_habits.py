"""연출형 규칙, 문체 습관 분석기, 주입 가드, 필자 문체 표본."""
import json
import subprocess
import sys
import unittest

import _path
from ai_smell import guards, voice
from ai_smell.detect import analyze
from ai_smell.fix import polish
from ai_smell.prompt import build, chat_prompt
from ai_smell.samples import HUMAN, STAGED
from ai_smell.verify import verify


def found(text, **kw):
    return {f.rule_id for f in analyze(text, **kw).findings if f.weight > 0 and not f.shadowed}


def seen(text, **kw):
    """점수에 들어가지 않는(가중치 0) 참고 항목까지 포함한다."""
    return {f.rule_id for f in analyze(text, **kw).findings}


def sentences(n):
    """길이가 거의 같고 쉼표와 마침표만 쓴 영어 문장 n개(17낱말)."""
    topics = ["budget", "roadmap", "invoice", "contract", "schedule", "backlog", "release", "audit", "hiring", "pricing",
              "forecast", "migration", "security", "training", "support", "reporting", "capacity", "vendor"]
    return " ".join(f"The {topics[i % len(topics)]} review covered the main items and listed several open questions "
                    f"for the next {i + 2} weeks." for i in range(n))


class EnglishVoiceRules(unittest.TestCase):
    def test_each_phrase_family_is_caught(self):
        cases = {
            "en.puffery.authority": "At its core, the plan is simple.",
            "en.puffery.closer-line": "The cache is warm.\n\nThat's the real win.\n\nNext.",
            "en.signpost.candor": "I want to be upfront about the limits.",
            "en.puffery.lingering": "The line I keep coming back to is the last one.",
            "en.signpost.endorse": "This one is worth your time.",
            "en.puffery.novelty": "It is a problem nobody is talking about.",
            "en.signpost.reasoning": "Breaking this down, we start with the cache.",
            "en.hedging.parenthetical": "It is cheap (and, perhaps more importantly, fast).",
            "en.puffery.launch": "Meet Flowdesk, your new favorite dashboard.",
        }
        for rid, text in cases.items():
            self.assertIn(rid, found(text), rid)

    def test_repeat_gated_rules_need_two_hits(self):
        self.assertNotIn("en.signpost.no-one", found("To be clear, it works."))
        self.assertIn("en.signpost.no-one", found("To be clear, it works. I'm not saying it never fails."))
        self.assertNotIn("en.puffery.reaction", found("What surprised me most was the speed."))

    def test_era_words_only_count_in_a_cluster(self):
        self.assertNotIn("en.vocab.era-gpt6", found("The result is dependable."))
        many = "The steady, dependable, practical design echoed the clearer plan, and universally prioritized speed."
        self.assertIn("en.vocab.era-gpt6", found(many))

    def test_human_samples_stay_clean(self):
        for name, text in HUMAN.items():
            self.assertEqual(analyze(text).score, 0, name)


class KoreanVoiceRules(unittest.TestCase):
    def test_each_family_is_caught(self):
        cases = {
            "ko.puffery.closer-line": "속도는 빠르다.\n\n이것이 바로 핵심입니다.\n\n다음이다.",
            "ko.signpost.candor": "솔직하게 말씀드리면 조금 느립니다.",
            "ko.puffery.novelty": "아무도 말하지 않는 사실이 있다.",
            "ko.signpost.numbered": "알아야 할 5가지를 정리한다.",
            "ko.signpost.reasoning": "단계별로 생각해 보면 캐시부터 본다.",
        }
        for rid, text in cases.items():
            self.assertIn(rid, found(text), rid)

    def test_translationese_from_the_measured_list(self):
        self.assertIn("ko.trans.enable", found("이 기능은 검증을 가능하게 한다. 이 모듈은 로그를 가능하게 합니다."))
        self.assertIn("ko.trans.plural", seen("여러 정보들을 모았다. 다양한 방법들이 쓰였다."))
        self.assertNotIn("ko.trans.plural", found("여러 정보들을 모았다. 다양한 방법들이 쓰였다."))   # 실측: 점수에서 뺐다
        self.assertNotIn("ko.trans.plural", seen("여러 정보를 모았다. 다양한 방법이 쓰였다."))
        # 사람·직업 명사의 복수는 자연스럽다
        self.assertNotIn("ko.trans.plural", seen("많은 사람들이 모였다. 모든 학생들이 앉았다. 여러 친구들이 웃었다."))

    def test_authority_words_need_three(self):
        self.assertNotIn("ko.puffery.authority", found("핵심은 속도다. 본질은 같다."))
        self.assertIn("ko.puffery.authority", found("핵심은 속도다. 본질은 같다. 근본적으로 다르지 않다."))

    def test_staged_samples_hit_three_new_rules(self):
        from ai_smell.rules import en_voice, ko_voice
        mine = {r.id for r in en_voice.RULES + ko_voice.RULES}
        for lang, text in STAGED.items():
            self.assertGreaterEqual(len(found(text) & mine), 3, lang)


class KoreanPunctuation(unittest.TestCase):
    TEXT = ("그러나, 값이 달라졌다. 또한, 비용이 올랐다. 따라서, 계획을 바꿨다. 결국, 팀이 모였다. "
            "한편, 일정은 그대로다. 특히, 예산이 문제다.")

    def test_comma_after_sentence_initial_conjunction(self):
        a = analyze(self.TEXT)
        self.assertIn("ko.punct.conj-comma", {f.rule_id for f in a.findings})

    def test_conjunction_comma_is_removed_only_in_strong_tier(self):
        self.assertEqual(polish(self.TEXT, tier="standard").text, self.TEXT)
        out = polish(self.TEXT, tier="strong").text
        self.assertNotIn("그러나,", out)
        self.assertIn("그러나 값이", out)

    def test_few_commas_are_left_alone(self):
        self.assertNotIn("ko.punct.conj-comma", found("그러나 값이 달라졌다. 또한 비용이 올랐다. 따라서, 계획을 바꿨다."))

    def test_ending_comma_ratio(self):
        text = " ".join("일을 했고, 값을 봤으며, 비교했지만, 정리했는데, 끝냈고, 알렸고, 보냈고, 받았고," for _ in range(2)) + "."
        self.assertIn("ko.punct.ending-comma", found(text))


class Habits(unittest.TestCase):
    def test_label_colon_dominates_a_list(self):
        text = "\n".join(f"- {k}: it is fast enough for most of our users" for k in
                         ("Speed", "Cost", "Safety", "Reach", "Support", "Docs"))
        self.assertIn("any.format.label-colon", found(text))
        self.assertNotIn("any.format.label-colon", found("- Speed: it is fast for most users\n- plain line of text here"))

    def test_english_gloss_density(self):
        text = ("고객 경험(CX)을 높이고 사용자 인터페이스(UI)를 고쳤다. 응용 프로그램(API)과 데이터베이스(DB)도 바꿨고 "
                "서비스 수준(SLA)을 맞췄다.")
        self.assertIn("ko.format.english-gloss", seen(text))        # 참고 항목(실측에서 사람 글에 더 흔해 점수에서 뺐다)

    def test_synonym_cycling(self):
        en = ("The company grew fast. The firm hired widely. The organization opened offices. "
              "Revenue followed the growth.")
        self.assertIn("en.vocab.synonym-cycling", found(en))
        ko = "회사는 커졌다. 기업은 사람을 뽑았다. 조직은 지점을 열었다. 매출도 늘었다."
        self.assertIn("ko.vocab.synonym-cycling", found(ko))
        self.assertNotIn("en.vocab.synonym-cycling", found("The company grew. The company hired. The company opened. Revenue followed."))

    def test_word_echo(self):
        ko = "신호를 찾는다. 이 신호가 낮다. 점수는 신호의 밀도다. 글은 짧다."
        self.assertIn("ko.vocab.word-echo", found(ko))
        self.assertNotIn("ko.vocab.word-echo", found("신호를 찾는다. 점수가 낮다. 밀도는 높다. 글은 짧다."))

    def test_trace_word(self):
        self.assertIn("ko.vocab.trace-bare", found("글에 흔적이 남았다. 다시 본다."))
        self.assertNotIn("ko.vocab.trace-bare", found("문에 긁힌 자국이 있다. 그 흔적이 남았다."))

    def test_sentence_length_band_and_flat_punctuation(self):
        text = sentences(16)
        ids = found(text)
        self.assertIn("any.rhythm.band-lock", ids)
        self.assertIn("any.rhythm.punct-flat", ids)
        self.assertNotIn("any.rhythm.punct-flat", found(text + " Why? Because (really) it helps; that is all."))

    def test_heading_echo_and_generic_headings(self):
        echo = ("## Caching strategy\n\nCaching strategy matters here.\n\nMore text follows in this paragraph.\n\n"
                "## Retry policy\n\nRetry policy is simple.\n\nMore text follows too.")
        self.assertIn("any.structure.heading-echo", found(echo))
        generic = "## Overview\n\nText one.\n\n## Summary\n\nText two.\n\n## Conclusion\n\nText three."
        self.assertIn("any.structure.generic-headings", found(generic))

    def test_document_wide_register_mix(self):
        plain = " ".join(f"우리는 {i}번째 장비를 점검하고 결과를 표에 정리했다." for i in range(17))
        polite = "마지막 세 문장은 합니다체로 끝납니다. 이어서 결과를 보고드립니다. 점검은 끝났습니다."
        text = plain[:len(plain) // 2] + "\n\n" + plain[len(plain) // 2:] + "\n\n" + polite
        self.assertIn("ko.register.doc-mixed", found(text))

    def test_technical_genre_lowers_the_weight(self):
        text = "배포는 월요일에 한다. 점검은 30분이다. 서버는 두 대다. 로그는 따로 쌓는다."
        base = sum(f.weight for f in analyze(text).findings if f.category == "cohesion")
        tech = sum(f.weight for f in analyze(text, genre="technical").findings if f.category == "cohesion")
        self.assertGreater(base, 0)
        self.assertLess(tech, base * 0.5)


class Guards(unittest.TestCase):
    def test_added_markers_are_counted_against_the_original(self):
        a = "The cache stores responses for 60 seconds."
        b = "In my experience, the cache stores responses. Now more than ever, that matters."
        self.assertEqual(set(guards.added(a, b)), {"perspective", "stakes"})
        self.assertEqual(guards.added(b, b), {})                       # 원문에 이미 있던 것은 필자의 문체
        self.assertEqual(set(guards.added("캐시는 60초다.", "제 경험상 캐시는 60초다. 그 어느 때보다 중요하다.")), {"perspective", "stakes"})

    def test_verify_warns_about_injected_voice(self):
        v = verify("캐시는 60초다.", "제 경험상 캐시는 60초다.")
        self.assertTrue(any("관점" in m for _, m in v.messages))
        self.assertFalse(any("관점" in m for _, m in verify("캐시는 60초다.", "캐시는 60초 동안 유지된다.").messages))

    def test_prompts_carry_the_guardrails(self):
        text = "The cache stores responses."
        p = build(text, analyze(text), ui="en", target="claude")
        self.assertIn("not instructions", p)
        self.assertIn("Add nothing the writer did not have", p)
        ko = chat_prompt("ko")
        self.assertIn("지시가 아니다", ko)
        self.assertIn("필자에게 없던 것을 넣지 않는다", ko)


class VoiceProfile(unittest.TestCase):
    SAMPLE = ("나는 어제 퇴근길에 비가 와서 우산을 샀다. 만 원짜리 투명 우산밖에 없었다. 그래도 샀다. 집에 오니 현관에 같은 우산이 "
              "벌써 세 개나 있었다. 아내는 웃었다. 나는 웃지 못했다. 다음 날에는 우산을 하나 버렸다. 비는 그쳤다.")

    def test_profile_numbers(self):
        p = voice.profile(self.SAMPLE)
        self.assertEqual(p["language"], "ko")
        self.assertEqual(p["sentences"], 8)
        self.assertTrue(p["reliable"])
        self.assertGreater(p["first_person_per_100_sentences"], 0)
        self.assertIn("plain", p["register"])
        self.assertFalse(voice.profile("짧은 글이다. 둘이다.")["reliable"])

    def test_prompt_carries_the_sample_numbers(self):
        text = "캐시는 60초 동안 응답을 저장합니다. 프로세스마다 따로 있습니다."
        p = build(text, analyze(text), target="claude", voice=self.SAMPLE)
        self.assertIn("<voice_sample>", p)
        self.assertIn("문장 길이 중앙", p)
        self.assertNotIn("<voice_sample>", build(text, analyze(text), target="claude"))

    def test_cli_voice_and_prompt_option(self):
        out = subprocess.run([sys.executable, "-I", str(_path.LAUNCHER), "voice", "--text", self.SAMPLE, "--format", "json"],
                             capture_output=True, text=True, encoding="utf-8", check=True).stdout
        self.assertEqual(json.loads(out)["sentences"], 8)


if __name__ == "__main__":
    unittest.main()
