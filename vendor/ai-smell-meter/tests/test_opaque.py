"""해독 부담 규칙: 규칙마다 걸리는 글과 안 걸리는 글. 되풀이해야 세는 규칙은 반복해서 넣는다.

예문은 모두 이 저장소에서 새로 쓴 것이다. 커뮤니티 글을 옮기지 않았다.
"""
import unittest

import _path  # noqa: F401
from ai_smell.detect import analyze
from ai_smell.rules import en_opaque, ko_opaque

# (규칙 id, 걸려야 하는 한 문장, 걸리면 안 되는 한 문장, 반복 횟수)
CASES = [
    ("en.opaque.the-noun", "The fix is small. The ask is clear.", "The patch is small. The request is clear.", 2),
    ("en.opaque.file-ref", "See NOTES_INTERNAL.md section 4 for it.", "See the design notes for it.", 2),
    ("en.opaque.arrow", "Cache miss -> retry -> timeout.", "A cache miss causes a retry and then a timeout.", 4),
    ("en.opaque.inanimate-verb", "The goal bites here. The modules sit on each other.", "The goal is hard here.", 2),
    ("en.opaque.telegraphic", "Route override absent in five regions; thirty megabyte default; four times slower tail.",
     "The route override is absent in five regions; the default is thirty megabytes; the tail is four times slower.", 2),
    ("en.opaque.abstract-chain", "The consolidation of governance reduces fragmentation of accountability.",
     "Merging the teams means each person knows who answers for what.", 2),
    ("en.opaque.vague-move", "Here the right move is to wait. There the real move is to ship.", "Here we wait.", 3),
    ("en.vocab.load-bearing", "That check is load-bearing.", "That check is required.", 1),
    ("en.vocab.claude-stock", "A smoking gun. A footgun. Hand-waving.", "A clear cause. A risky default. A vague claim.", 1),
    ("en.signpost.pushback", "Here's where I'd push back.", "I disagree with this part.", 1),
    ("en.signpost.candor-plain", "Honest framing: it is slow.", "It is slow.", 1),
    ("en.puffery.is-the-lever", "Caching is the unlock.", "Caching cuts the load.", 1),
    ("en.puffery.self-rank", "This is the cleanest idea. That is the deepest point.", "This is one idea.", 1),
    ("en.puffery.matters-because", "This matters because it is slow. That matters because it fails.", "It is slow.", 1),

    ("ko.opaque.differ-on", "결과는 입력 품질에서 갈린다. 여기서 갈립니다.", "결과는 입력 품질로 정해진다.", 1),
    ("ko.opaque.divide", "에세이는 잘 나뉘었고 시는 나뉘지 않았다.", "에세이는 정확도가 높았다.", 1),
    ("ko.opaque.cut-apart", "에세이는 잘 갈랐고 시는 약하게만 갈랐다.", "에세이는 정확도가 높았다.", 1),
    ("ko.figure.moat", "이 검증이 해자다. 저 단계가 방어선이다.", "이 검증이 오류를 막는다.", 2),
    ("ko.opaque.closes-on", "논의는 여기서 결론에 닫힌다.", "논의는 여기서 끝난다.", 1),
    ("ko.opaque.self-qa-dash", "그럼 무엇이 문제인가 — 기준이 없다. 그럼 어디서 막히는가 — 입력이다.", "문제는 기준이 없다는 점이다.", 2),
    ("ko.opaque.arrow", "캐시 실패 -> 재시도 -> 시간 초과.", "캐시가 실패하면 재시도하고 시간이 넘는다.", 4),
    ("ko.opaque.telegraphic-end", "배포 전 점검 필요.", "배포 전에 점검해야 합니다.", 4),
    ("ko.opaque.vague-referent", "그 부분을 고친다.", "설정 파일을 고친다.", 6),
    ("ko.opaque.inanimate-verb", "코드가 말한다. 테스트가 버틴다.", "코드가 실행된다.", 2),
    ("ko.figure.load-bearing", "이 검사는 하중을 받는 부분이다.", "이 검사는 반드시 필요하다.", 1),
]


class OpaqueRules(unittest.TestCase):
    def test_every_rule_has_a_case(self):
        ids = {r.id for r in en_opaque.RULES} | {r.id for r in ko_opaque.RULES}
        self.assertEqual(ids, {c[0] for c in CASES})

    def test_cases(self):
        for rid, pos, neg, n in CASES:
            hit = {f.rule_id for f in analyze((pos + " ") * n).findings}
            miss = {f.rule_id for f in analyze((neg + " ") * n).findings}
            with self.subTest(rule=rid):
                self.assertIn(rid, hit, f"걸려야 한다: {pos!r}")
                self.assertNotIn(rid, miss, f"걸리면 안 된다: {neg!r}")

    def test_no_rule_edits_text(self):
        for r in list(en_opaque.RULES) + list(ko_opaque.RULES):
            with self.subTest(rule=r.id):
                self.assertEqual(r.tier, "none")

    def test_all_are_in_the_opaque_category_or_a_neighbour(self):
        for r in ko_opaque.RULES:
            self.assertEqual(r.category, "opaque")


class UndefinedLabels(unittest.TestCase):
    TEXT = ("MAv2 now reads q23-grades-strict first. TAME_GUIDANCE overrides it. "
            "CBv9 skips q23-grades-strict. MAv2 and CBv9 differ.")

    def test_fires_when_names_are_never_introduced(self):
        self.assertIn("any.opaque.undefined-labels", {f.rule_id for f in analyze(self.TEXT).findings})

    def test_silent_when_names_are_introduced(self):
        text = ("The MAv2 (the second multi-agent design) reads a file called q23-grades-strict first, "
                "and a setting named TAME_GUIDANCE overrides it. MAv2 is the default.")
        self.assertNotIn("any.opaque.undefined-labels", {f.rule_id for f in analyze(text).findings})

    def test_silent_for_ordinary_text(self):
        self.assertNotIn("any.opaque.undefined-labels",
                         {f.rule_id for f in analyze("We moved the job to a new queue and it now runs faster.").findings})


class ScoresRise(unittest.TestCase):
    """같은 내용을 해독이 필요하게 쓴 글이 풀어 쓴 글보다 점수가 높다."""

    OPAQUE = ("The fix is the unlock. The ask is clear. The goal bites; modules sit on modules. "
              "That check is load-bearing, a smoking gun, a footgun. Here's where I'd push back. "
              "Cache miss -> retry -> timeout -> page. Cache miss -> retry -> timeout -> page.")
    PLAIN = ("Adding a cache makes the page load faster. The team asked for it. If a cache miss happens, the "
             "service retries and may time out. I disagree with skipping the retry test, because it covers that path.")

    def test_opaque_scores_higher(self):
        self.assertGreater(analyze(self.OPAQUE).score, analyze(self.PLAIN).score)

    def test_opaque_category_reported(self):
        cats = {f.category for f in analyze(self.OPAQUE).findings}
        self.assertIn("opaque", cats)


if __name__ == "__main__":
    unittest.main()
