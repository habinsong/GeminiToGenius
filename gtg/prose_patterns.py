"""문체 검사가 찾는 표현 목록입니다. 근거와 조정 기록은 docs/verification/3.1.0.md에 둡니다.

block은 지워도 뜻이 줄지 않는 상투구라서 한 번만 나와도 고칩니다. review는 사람도 쓰는 표현이라
밀도(minimum)를 넘을 때만 알리고 판단은 글쓴이에게 맡깁니다. 사람 글에서 더 자주 나온다고 측정된
`~에 대해`·`~를 통해` 같은 표현은 한 문단에 몰릴 때만 셉니다.
"""

from __future__ import annotations

import re
from typing import NamedTuple


class Pattern(NamedTuple):
    id: str
    severity: str  # block 또는 review
    scope: str  # match: 나올 때마다, paragraph: 한 문단 안 횟수, document: 문서 전체 횟수
    minimum: int
    regex: re.Pattern
    hint: str


# 문장 첫머리입니다. 줄 첫머리(목록·제목·인용 기호 뒤 포함)나 앞 문장의 끝 뒤에서만 맞춥니다.
START = r"(?:^\s*(?:(?:[-*+]|\d+[.)]|#{1,6}|>)\s+)?|(?<=[.!?]\s))"


def pattern(id_: str, severity: str, scope: str, minimum: int, expression: str, hint: str, flags: int = 0) -> Pattern:
    return Pattern(id_, severity, scope, minimum, re.compile(expression, flags), hint)


PATTERNS = (
    # 한국어 상투구: 지우거나 내용으로 바꾸면 글이 나아집니다.
    pattern("ko-conclusion-signpost", "block", "match", 1,
            START + r"(?:결론적으로|요약하자면|요약하면|종합하자면|종합하면|종합해\s?보면|정리하자면)(?=[\s,])",
            "결론 신호어입니다. 지우고 결론 내용을 바로 쓰세요."),
    pattern("ko-significance", "block", "match", 1,
            r"시사하는\s?바가?\s?(?:크|큽|큰|많|적지)|주목할\s?만(?:한|하|합)|간과할\s?수\s?없|의미심장",
            "의의를 부풀리는 상투구입니다. 무엇이 왜 중요한지 사실로 쓰세요."),
    pattern("ko-hedged-copula", "block", "match", 1,
            r"(?:라고|이라고|다고)\s?(?:할|볼)\s?수\s?(?:있습니다|있다|있을\s?것)|(?:이|)라\s?하겠(?:습니다|다)",
            "판단을 흐리는 서술입니다. '~입니다'로 단정할 근거가 있으면 단정하고, 없으면 무엇이 불확실한지 쓰세요."),
    pattern("ko-chatbot", "block", "match", 1,
            r"도움이\s?되(?:셨|었)(?:으면|기를)|궁금한\s?(?:점이|것이)\s?있으시면|더\s?자세한\s?(?:내용|정보)이\s?필요하시면"
            r"|알아보겠습니다|살펴보겠습니다|정리해\s?드리겠습니다|물론입니다|좋은\s?질문입니다",
            "대화용 인사·안내 문구입니다. 문서에서는 지우고 본론부터 쓰세요."),
    pattern("ko-double-passive", "block", "match", 1, r"되어(?:지|진|질|집)",
            "이중 피동입니다. '~된다'나 능동문으로 고치세요."),
    pattern("ko-hype-phrase", "block", "match", 1,
            r"새로운\s?지평|패러다임(?:의)?\s?전환|게임\s?체인저|새로운\s?장을\s?(?:열|여)|시대가\s?도래",
            "홍보 문구입니다. 실제로 바뀐 것을 구체적으로 쓰세요."),
    # 한국어 검토 신호: 맥락에 따라 맞을 수 있습니다.
    pattern("ko-cleft", "review", "match", 1, r"(?:중요한|필요한|핵심적인)\s?(?:것은|점은)",
            "'중요한 것은 X'는 'X가 중요하다'로 바로 쓰는 편이 읽기 쉽습니다."),
    pattern("ko-hype-word", "review", "document", 3,
            r"혁신적|획기적|압도적|파격적|폭발적|전례\s?없는|강력한|최적의|원활한",
            "꾸밈말이 많습니다. 수치나 사실로 바꿀 수 있는지 보세요."),
    pattern("ko-overclaim", "review", "match", 1,
            r"완벽(?:하게|히|한|합니다)|완전히\s?(?:해결|제거|동작|호환)|모든\s?(?:경우|상황|환경)(?:에서|를)"
            r"|무결점|무결하|전혀\s?문제(?:가|는)?\s?없|문제(?:가|는)?\s?전혀\s?없|프로덕션\s?(?:준비|레디)|확실히\s?보장",
            "근거 없이 쓰면 과장입니다. 확인한 범위와 근거를 붙이거나 표현을 낮추세요."),
    pattern("ko-translationese", "review", "paragraph", 3,
            r"에\s?있어(?:서)?\s|함에\s?있어|[과와]\s?관련하여|에\s?기반하여|[을를]\s?통해|에\s?대해(?:서)?\s|에\s?의해"
            r"|가지고\s?있(?:습니다|다|는)",
            "번역투 연결이 한 문단에 몰렸습니다. 조사로 바로 잇거나 동사로 푸세요."),
    pattern("ko-connective", "review", "paragraph", 3,
            START + r"(?:또한|아울러|나아가|더불어|게다가|더욱이|따라서|그러므로|즉)(?=[\s,])",
            "문장 첫 접속사가 한 문단에 몰렸습니다. 앞뒤 문장이 이미 이어지면 접속사를 빼세요."),
    pattern("ko-can", "review", "paragraph", 4, r"(?:할|될|있을|볼)\s?수\s?있(?:습니다|다)",
            "'~할 수 있다'가 반복됩니다. 실제로 하는 일이면 '~한다'로 쓰고, 가능성이면 조건을 쓰세요."),
    # 영어 상투구입니다.
    pattern("en-delve", "block", "match", 1, r"\bdelv(?:e|es|ed|ing)\b", "Say what you examine, plainly.", re.I),
    pattern("en-cliche", "block", "match", 1,
            r"\brich\s+tapestry\b|\btapestry\s+of\b|\btestament\s+to\b|\bin\s+today'?s\s+(?:fast-paced|digital|ever-changing"
            r"|rapidly\s+evolving)\b|\bever-evolving\s+landscape\b|\bnavigat(?:e|es|ing)\s+the\s+complexit(?:y|ies)\b"
            r"|\bunlock(?:s|ing)?\s+the\s+(?:full\s+)?potential\b|\bgame[- ]chang(?:er|ers|ing)\b|\bparadigm\s+shift\b",
            "Stock phrase. Replace it with the concrete fact.", re.I),
    pattern("en-note-filler", "block", "match", 1,
            r"\b(?:it'?s|it\s+is)\s+(?:important|worth|crucial|essential)\s+to\s+(?:note|mention|remember|highlight)\b"
            r"|\b(?:it'?s|it\s+is)\s+worth\s+noting\b",
            "Delete the lead-in and state the point.", re.I),
    pattern("en-chatbot", "block", "match", 1,
            r"\bI\s+hope\s+this\s+helps\b|\bfeel\s+free\s+to\b|\blet\s+me\s+know\s+if\s+you\b|\bgreat\s+question\b"
            r"|\bas\s+an\s+AI\b|\bcertainly!|\babsolutely!",
            "Chat filler does not belong in a document.", re.I),
    pattern("en-conclusion-signpost", "block", "match", 1, START + r"(?:In\s+conclusion|To\s+sum\s+up),",
            "Drop the signpost and write the conclusion.", re.I),
    pattern("en-ai-vocabulary", "review", "paragraph", 3,
            r"\b(?:pivotal|seamless(?:ly)?|robust|leverag(?:e|es|ed|ing)|foster(?:s|ed|ing)?|underscor(?:e|es|ed|ing)"
            r"|showcas(?:e|es|ed|ing)|intricate|multifaceted|holistic|synerg(?:y|ies)|paramount|realm|myriad"
            r"|meticulous(?:ly)?|vibrant|groundbreaking|cutting-edge|revolutioniz(?:e|es|ed|ing))\b",
            "Several stock words in one paragraph. Use plain, specific words.", re.I),
    pattern("en-negative-parallel", "review", "document", 2, r"\bnot\s+(?:just|only|merely)\b[^.\n]{0,80}?\bbut\b",
            "Repeated 'not just X but Y'. State Y directly unless you are correcting a real misconception.", re.I),
    pattern("en-copula-avoidance", "review", "paragraph", 2, r"\b(?:serves|stands|acts|functions)\s+as\s+(?:a|an|the)\b",
            "Prefer 'is' over 'serves as' unless the role matters.", re.I),
    pattern("en-overclaim", "review", "match", 1,
            r"\b(?:perfect(?:ly)?|flawless(?:ly)?|bulletproof|production[- ]ready|fully\s+(?:tested|working|functional"
            r"|compatible)|all\s+edge\s+cases|guarantee[sd]?|zero\s+(?:bugs|issues|risk)|works\s+perfectly)\b",
            "Overclaim unless you attach the evidence and its scope.", re.I),
    pattern("en-connective", "review", "document", 3,
            START + r"(?:Additionally|Moreover|Furthermore|Consequently|Notably|Importantly),",
            "Sentence-initial connectives pile up. Let the sentences connect on their own.", re.I),
    # 서식 신호입니다.
    pattern("format-bold", "review", "paragraph", 4, r"\*\*[^*\n]+\*\*",
            "굵은 글씨가 몰렸습니다. 정말 놓치면 안 되는 한 곳만 남기세요. / Too much bold."),
    pattern("format-dash", "review", "document", 4, r"^(?!\s{0,3}#{1,6}\s).*?—",
            "본문에 긴 줄표가 많습니다. 쉼표·괄호·새 문장으로 나누세요. / Many em dashes in body text."),
    pattern("format-emoji-heading", "review", "match", 1,
            r"^\s{0,3}#{1,6}\s.*[\U0001F300-\U0001FAFF☀-➿]",
            "제목의 이모지는 정보가 없습니다. / Emoji in a heading."),
)
