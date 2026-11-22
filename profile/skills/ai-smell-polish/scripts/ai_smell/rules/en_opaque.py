"""영어: 독자가 풀기 어려운 문장. 정의 없는 지시, 해독이 필요한 은유, 압축된 조각, 혼자만 아는 이름.

2026년 하반기 개발자 커뮤니티(GitHub 이슈, Hacker News)가 Claude 계열 모델의 글을 두고 가장 많이 한 불만을 옮긴 것이다.
낱말 하나하나는 정상이고 기술 글에서는 실제 뜻으로도 쓰이므로 대부분 C등급이고, 되풀이될 때만 센다.
모두 보고만 하고 자동으로 고치지 않는다. 근거와 한계는 docs/research.md 11절.
"""
from __future__ import annotations

import re

from .build import R, alt

TECH = {"technical": 0.5}
SENT0 = r"(?:^|(?<=[.!?])[ \t]+)"
VERBS = re.compile(r"\b(?:is|are|was|were|be|been|has|have|had|does|do|did|will|would|can|could|should|must|may|"
                   r"get|gets|got|need|needs|means|mean|makes|make|keeps|keep|runs|run|takes|take|uses|use)\b", re.I)


def _no_verb(m, ctx) -> bool:
    """조각 문장이다: 흔한 정동사가 하나도 없다."""
    return VERBS.search(m.group(0)) is None


RULES = [
    R("en.opaque.the-noun", "en", "opaque", "C",
      SENT0 + r"the (?:fix|tail|ask|catch|trap|wedge|unlock|bar|gap|thing to watch|real (?:question|issue|risk|problem|test|cost))"
      r"(?=\s+(?:is|was|here|for|to|becomes|isn't)\b|[.:,])",
      "A sentence opens with 'The <label>' for something the reader was never told about.",
      w=0.3, min_count=2, genre=TECH, sugg="Name the thing the first time: say what the fix, the ask, or the catch actually is."),
    R("en.opaque.file-ref", "en", "opaque", "C", r"\b[A-Z][A-Z0-9_]{3,}\.md\b(?:\s+section\s+\d+)?",
      "Points at an internal notes file the reader may not have.", w=0.3, min_count=2, genre=TECH,
      sugg="Say what the file says, or link it where the reader can open it."),
    R("en.opaque.arrow", "en", "opaque", "C", r"[A-Za-z0-9)]\s*(?:→|⇒|=>|->)\s*[A-Za-z(]",
      "An arrow stands in for a verb or a causal link in running prose.", w=0.25, min_count=4, genre={"technical": 0.3},
      sugg="Write the relation out: 'causes', 'becomes', 'is replaced by'."),
    R("en.opaque.inanimate-verb", "en", "opaque", "C",
      r"\b(?:goal|spec|tests?|structs?|modules?|functions?|constraint|rule|file|config|metric|check|gate)\s+"
      + alt("bites", "breathes", "narrates", "narrate", "carries", "carry", "sits on", "sit on", "lives in", "live in",
            "rides along", "earns its keep", "pushes back", "wants", "cares", "speaks", "whispers", "insists") + r"\b",
      "A thing does what only a person does ('the goal bites', 'modules sit on modules').", w=0.4, min_count=2,
      genre=TECH, sugg="Say what actually happens in plain verbs."),
    R("en.opaque.telegraphic", "en", "opaque", "C",
      r"[^.!?\n;]{3,60};[^.!?\n;]{3,60};[^.!?\n]{0,80}[.!?]",
      "A verbless run of fragments joined by semicolons (label-style shorthand).", w=0.4, min_count=2,
      guard=_no_verb, genre=TECH, sugg="Write full sentences with a subject and a verb."),
    R("en.opaque.abstract-chain", "en", "opaque", "C",
      r"\b\w{3,}(?:tion|ment|ity|ness|ance|ence|ism)\b(?:[\s,/-]+\w+){0,2}[\s,/-]+\w{3,}(?:tion|ment|ity|ness|ance|ence|ism)\b"
      r"(?:[\s,/-]+\w+){0,2}[\s,/-]+\w{3,}(?:tion|ment|ity|ness|ance|ence|ism)\b",
      "Three abstract nouns packed into one stretch of a sentence.", w=0.3, min_count=2,
      genre={"academic": 0.4, "technical": 0.5}, sugg="Use a concrete subject and a verb instead of stacked abstractions."),
    R("en.opaque.vague-move", "en", "opaque", "C",
      r"\bthe (?:right|real|wrong|safe|smart|obvious) (?:move|play|call|angle)\b",
      "'The right move' names a choice without saying what it is.", w=0.25, min_count=3, genre=TECH),

    R("en.vocab.load-bearing", "en", "vocab", "B", r"\bload[- ]bearing\b",
      "'Load-bearing' as a general word for 'important' (reported as a Claude-family tic across several independent counts).",
      w=0.6, sugg="Say what depends on it, or use 'important' or 'required'."),
    R("en.vocab.claude-stock", "en", "vocab", "C",
      r"\b" + alt("smoking gun", "footgun", "blast radius", "belt and suspenders", "belt-and-suspenders",
                   "earns its keep", "earned its keep", "paper cut", "paper cuts", "landing the plane",
                   "term-locked", "term-locking", "counter-probe", "hand-waving", "hand-wavy", "hermetic",
                   "orthogonal", "non-trivial", "substrate", "capstone", "vacuous", "constellation") + r"\b",
      "Stock engineering metaphors that recent assistants reach for; each is fine alone and repeats across a text.",
      w=0.35, min_count=3, genre={"technical": 0.3, "academic": 0.5},
      sugg="Replace each with what it means in this sentence."),
    R("en.signpost.pushback", "en", "signpost", "C",
      r"\bhere'?s where i(?:'d| would) (?:push back|hold the line|disagree|draw the line)\b|"
      r"\bnow you'?re avoiding the real question\b|\bwhere (?:a|the) \w+ smells hand[- ]wav\w*",
      "Combat framing for an ordinary statement.", w=0.5, sugg="State the disagreement and the reason."),
    R("en.signpost.candor-plain", "en", "signpost", "C",
      r"\b" + alt("honest framing", "worth stating plainly", "worth naming precisely", "worth saying plainly",
                   "to put it plainly", "the honest take", "honest assessment") + r"\b",
      "Labels the next claim as plain or honest before making it.", w=0.5, sugg="Delete the label; keep the claim."),
    R("en.puffery.is-the-lever", "en", "puffery", "C",
      r"\b(?:is|are) the (?:unlock|lever|wedge|moat|bottleneck|forcing function|whole game|real (?:cost|work|test|story))\b",
      "Aphorism that names a single lever ('X is the unlock').", w=0.45, sugg="Say what changes and by how much."),
    R("en.puffery.self-rank", "en", "puffery", "C",
      r"\bthe (?:cleanest|deepest|sharpest) (?:organizing )?(?:idea|point|way|version|frame|distinction)\b",
      "Ranks its own claim instead of letting the reader judge.", w=0.35, min_count=2),
    R("en.puffery.matters-because", "en", "puffery", "C",
      r"\b(?:this|that|which) matters because\b|\bbecause they shape everything that follows\b",
      "Announces significance before giving the reason.", w=0.4, min_count=2, sugg="Give the reason directly."),
]
