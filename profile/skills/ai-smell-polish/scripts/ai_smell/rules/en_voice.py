"""영어: 연출형 표지. 깊은 척하는 말, 솔직한 척하는 말, 반응·추천·논증의 틀, 최근 모델의 낱말.

대부분 실무 지침(blader/humanizer, conorbronsdon/avoid-ai-writing)과 위키백과 2026년판이 같이 드는 항목이다.
빈도 수치가 없는 것이 많아 C등급이고, 한 번 나온 것만으로는 판단하지 않도록 min_count나 군집 조건을 건다.
"""
from __future__ import annotations

from .build import R, alt

RULES = [
    R("en.puffery.authority", "en", "puffery", "B",
      r"\b" + alt("at its core", "make no mistake", "what really matters", "the heart of the matter",
                  "the deeper issue", "the deeper problem", "the deeper truth") + r"\b",
      "Asserts depth or stakes instead of showing them.", w=0.7, sugg="State the claim itself."),
    R("en.puffery.aphorism", "en", "puffery", "C",
      r"\b(?:is|are) the (?:language|currency|architecture|grammar|backbone|heartbeat) of\b",
      "Aphorism formula ('X is the language of Y').", w=0.4, min_count=2),
    R("en.puffery.closer-line", "en", "puffery", "B",
      r"^[ \t]*(?:that(?:'s| is)|this is) (?:the )?(?:real|whole|entire) (?:win|point|story|magic|difference|deal)\.?[ \t]*$|"
      r"^[ \t]*(?:and )?that (?:distinction )?matters\.?[ \t]*$|^[ \t]*full stop\.?[ \t]*$",
      "One-line closer that repeats the point.", w=0.8, sugg="Cut it unless it adds a new fact."),
    R("en.puffery.performed-insight", "en", "puffery", "C",
      r"\b" + alt("that's not nothing", "the punchline is", "worth naming", "you already know the answer",
                  "don't take my word for it", "is the entire business model", "that's the whole point") + r"\b",
      "Announces profundity instead of delivering it.", w=0.5, min_count=2),
    R("en.signpost.candor", "en", "signpost", "C",
      r"\b" + alt("i want to be upfront", "to be fully transparent", "rather than bury this",
                  "i could have left this out", "i would rather flag", "let's be honest", "real talk",
                  "being honest about", "i'll be honest with you", "in the interest of transparency") + r"\b",
      "Narrates its own candor instead of disclosing.", w=0.45,
      sugg="Delete the frame; keep the disclosure itself."),
    R("en.puffery.lingering", "en", "puffery", "C",
      r"\b" + alt("the line i keep coming back to", "i can't stop thinking about", "still thinking about this",
                  "rattling around in my head", "i've been chewing on", "has been living in my head") + r"\b",
      "Unfalsifiable claim about the writer's own lingering attention.", w=0.5),
    R("en.puffery.reaction", "en", "puffery", "C",
      r"\b" + alt("what surprised me most", "what struck me most", "what struck me was",
                  "i was fascinated to discover", "i was fascinated to learn", "the most interesting part",
                  "hits different", "hit differently") + r"\b",
      "Stock reaction frame. Keep a real reaction; cut the empty frame.", w=0.25, min_count=2),
    R("en.signpost.endorse", "en", "signpost", "C",
      r"\b" + alt("worth your time", "a must-read", "this one's a must-read", "i highly recommend giving this a read",
                  "do yourself a favor", "you won't want to miss", "thank me later") + r"\b",
      "Generic endorsement closer.", w=0.4, sugg="Give the reason, or drop it."),
    R("en.signpost.no-one", "en", "signpost", "C",
      r"\b" + alt("i'm not saying", "to be clear", "don't get me wrong", "this is not to say", "this isn't to say",
                  "a tempting approach would be", "one might be tempted to", "you might think",
                  "it would be easy to just") + r"\b",
      "Answers an objection nobody raised.", w=0.4, min_count=2),
    R("en.puffery.novelty", "en", "puffery", "B",
      r"\b" + alt("nobody is talking about", "nobody's talking about", "nobody talks about", "what nobody tells you",
                  "everyone is missing", "everyone's missing", "nobody is naming", "nobody's naming") + r"\b",
      "Claims scarcity of knowledge where none exists.", w=0.6),
    R("en.puffery.self-label", "en", "puffery", "C",
      r"\b(?:that|this|the)(?: (?:last|first|second|third|fourth|final|next))? (?:move|one|bullet|point|step|part|item|"
      r"idea) is the (?:contrarian|clever|surprising|counterintuitive|interesting|real|key|unusual|smart) "
      r"(?:one|part|story|move)\b|\bhere(?:'s| is) where it gets clever\b|\bthis is the interesting part\b",
      "Labels its own item as clever or surprising.", w=0.5),
    R("en.signpost.reasoning", "en", "signpost", "B",
      r"\b" + alt("let me think step by step", "let's think step by step", "breaking this down",
                  "here's my thought process", "to approach this systematically",
                  "working through this logically") + r"\b",
      "Reasoning scaffold left in the prose.", w=0.6),
    R("en.signpost.numbered", "en", "signpost", "C",
      r"\bhere are the top (?:three|four|five|six|seven|eight|nine|ten|\d+)\b|"
      r"\b(?:three|four|five|seven|\d+) key takeaways\b|\b(?:three|five|seven|\d+) things (?:to know|you need to know)\b",
      "Numbered list framing chosen for structure, not for the count of items.", w=0.3),
    R("en.hedging.parenthetical", "en", "hedging", "C",
      r"\((?:and|or),?\s+(?:increasingly|perhaps|more precisely|more importantly|arguably|more accurately)[^)\n]{0,60}\)",
      "Parenthetical aside that sounds nuanced without committing.", w=0.4,
      sugg="Give it its own sentence or cut it."),
    R("en.signpost.fake-casual", "en", "signpost", "C",
      r"\*(?:checks notes|chef's kiss|mic drop|sips tea|drops mic)\*|\b(?:hot take|unpopular opinion|fun fact)\s*[:—–]|"
      r"\((?:yes|no),\s*(?:really|seriously)\)",
      "Props that stand in for a casual voice.", w=0.3, min_count=2),
    R("en.puffery.launch", "en", "puffery", "B",
      r"^[ \t]*(?:meet|say hello to|introducing)\s+[A-Z][\w.-]*(?:\s+[A-Z][\w.-]*)?,\s*your new (?:favorite|go-to)\b",
      "Launch-copy introduction.", w=0.6, sugg="State what it is."),
    R("en.vocab.era-gpt6", "en", "vocab", "C",
      r"\b(?:dependable|echoed|universally|prioritiz(?:e|es|ed|ing)|clearer|steady|practical|matters)\b",
      "Words reported for GPT-6-era output (Wikipedia, 2026); only counted in a cluster.", w=0.3, cluster=3),
]
