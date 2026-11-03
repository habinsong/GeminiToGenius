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
# 부정-긍정 대구입니다. 덧셈의 '뿐만 아니라'와 조건의 '아니라면'은 빼고 셉니다.
ANTITHESIS = (r"(?<!뿐만 )(?<!뿐만)(?<!뿐 )(?<!뿐)아니라(?=[\s,])|것이\s?아니(?:라|다)|것은\s?아니(?:다|에요|야)"
              r"|라기보다(?:는)?\s")


def batchim(final: int) -> str:
    """받침이 같은 한글 음절 전체를 문자 집합으로 만듭니다. 4는 ㄴ, 8은 ㄹ입니다."""
    return "[" + "".join(chr(0xAC00 + 28 * syllable + final) for syllable in range(19 * 21)) + "]"


# '한 것이다'의 ㄴ, '할 것이다'·'바꿀 때다'의 ㄹ처럼 관형형 받침으로 문장 끝 버릇을 찾습니다.
NIEUN, RIEUL = batchim(4), batchim(8)


def pattern(id_: str, severity: str, scope: str, minimum: int, expression: str, hint: str, flags: int = 0) -> Pattern:
    return Pattern(id_, severity, scope, minimum, re.compile(expression, flags), hint)


PATTERNS = (
    # 한국어 상투구: 지우거나 내용으로 바꾸면 글이 나아집니다.
    pattern("ko-conclusion-signpost", "block", "match", 1,
            START + r"(?:결론적으로|요약하자면|요약하면|종합하자면|종합하면|종합해\s?보면|정리하자면|정리하면)(?=[\s,])",
            "결론 신호어입니다. 지우고 결론 내용을 바로 쓰세요."),
    pattern("ko-significance", "block", "match", 1,
            r"시사하는\s?바가?\s?(?:크|큽|큰|많|적지)|주목할\s?만(?:한|하|합)|간과할\s?수\s?없|의미심장",
            "의의를 부풀리는 상투구입니다. 무엇이 왜 중요한지 사실로 쓰세요."),
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
    # 3.2.0까지는 차단이었습니다. KatFish 에세이에서 사람 5.5%, LLM 7.1%로 갈리지 않았고, 지우면 단정의 강도가
    # 달라지는 완곡이라 '지워도 뜻이 줄지 않는' 차단 기준에도 맞지 않아 반복될 때만 알립니다.
    pattern("ko-hedged-copula", "review", "document", 2,
            r"(?:라고|이라고|다고)\s?(?:할|볼)\s?수\s?(?:있습니다|있다|있을\s?것)|(?:이|)라\s?하겠(?:습니다|다)",
            "판단을 흐리는 서술이 반복됩니다. 단정할 근거가 있으면 단정하고, 없으면 무엇이 불확실한지 한 번만 밝히세요."),
    pattern("ko-hype-word", "review", "document", 3,
            r"혁신적|획기적|압도적|파격적|폭발적|전례\s?없는|강력한|최적의|원활한",
            "꾸밈말이 많습니다. 수치나 사실로 바꿀 수 있는지 보세요."),
    pattern("ko-overclaim", "review", "match", 1,
            r"완벽(?:하게|히|한|합니다)|완전히\s?(?:해결|제거|동작|호환)|모든\s?(?:경우|상황|환경)(?:에서|를)"
            r"|무결점|무결하|전혀\s?문제(?:가|는)?\s?없|문제(?:가|는)?\s?전혀\s?없|프로덕션\s?(?:준비|레디)|확실히\s?보장",
            "근거 없이 쓰면 과장입니다. 확인한 범위와 근거를 붙이거나 표현을 낮추세요."),
    pattern("ko-translationese", "review", "paragraph", 3,
            r"에\s?있어(?:서)?\s|함에\s?있어|하는\s?데\s?있어|에게\s?있어|[과와]\s?관련하여|에\s?기반하여|[을를]\s?통해"
            r"|에\s?대해(?:서)?\s|에\s?의해|가지고\s?있(?:습니다|다|는)|로부터|에서의|으로의|에로의|임에도\s?불구하고"
            r"|하기\s?위해서|중\s?하나(?:이다|입니다|로|는|가)|(?:라는|다는)\s?점에서",
            "번역투 연결이 한 문단에 몰렸습니다. 조사로 바로 잇거나 동사로 푸세요."),
    pattern("ko-progressive", "review", "paragraph", 3, r"고\s?있(?:다|습니다|어요)",
            "'~하고 있다'가 몰렸습니다. 진행이 중요하지 않으면 '~한다'로 쓰세요."),
    pattern("ko-future-assertion", "review", "paragraph", 3, RIEUL + r"\s?것(?:이다|입니다|이며|이고)",
            "'~할 것이다'가 몰렸습니다. 영어 will을 옮긴 꼴이라 확실한 일은 '~한다', 의지는 '~하겠다'로 쓰세요."),
    pattern("ko-formal-noun-close", "review", "paragraph", 3, NIEUN + r"\s?것(?:이다|입니다)[.!]",
            "'~한 것이다'로 맺는 문장이 몰렸습니다. '것이다'를 떼고 동사로 바로 끝내세요."),
    pattern("ko-teaser", "review", "match", 1,
            r"(?:문제|이유|답|핵심|결과|부작용|변수|해법)(?:은|는)\s?따로\s?있(?:다|습니다)|오히려\s?(?:정)?반대(?:다|입니다)"
            r"|흥미로운\s?(?:점|것|대목)은|여기서\s?(?:한\s?가지\s?)?(?:더\s?)?중요한\s?질문"
            r"|질문\s?(?:자체가|부터)\s?(?:잘못|틀렸|어긋)|(?:하나로|한\s?곳으로)\s?(?:수렴|귀결)",
            "다음 말을 예고하거나 억지로 뒤집는 문장입니다. 예고 없이 그 내용을 바로 쓰세요."),
    # 아래 넷은 KatFish 에세이에서 사람 글에는 0~1%만 나오고 LLM 글에는 5~35%에 나온 표현입니다(3.3.0 검증 기록).
    pattern("ko-importance-close", "review", "document", 2, r"(?:중요|필요)(?:합니다|하다)[.!]|필수적(?:입니다|이다)[.!]",
            "'~이 중요합니다', '~이 필요합니다'로 맺는 문장이 반복됩니다. 무엇을 왜 해야 하는지 바로 쓰세요."),
    pattern("ko-anaphoric-connective", "review", "match", 1,
            START + r"(?:이를\s?(?:통해(?:서)?|위해(?:서)?|바탕으로|토대로)|이로\s?인해)(?=[\s,])",
            "'이를 통해'로 앞 문장을 받아 여는 문장입니다. 앞 문장과 이어 쓰거나 무엇을 통해서인지 밝히세요."),
    pattern("ko-moral-close", "review", "document", 2,
            r"우리\s?모두(?:가|는|의)?\s|(?:노력해|힘써|관심을\s?가져)야\s?(?:합니다|한다|할\s?것)",
            "'우리 모두가 노력해야 합니다' 같은 당위 결말이 반복됩니다. 누가 무엇을 하면 되는지 구체적으로 쓰세요."),
    pattern("ko-stock-phrase", "review", "document", 2, r"등\s?다양한|중요한\s?역할을|역할을\s?(?:합니다|한다|하고\s?있)",
            "'등 다양한', '중요한 역할을 한다'가 반복됩니다. 무엇이 어떤 일을 하는지 쓰세요."),
    pattern("ko-closing-formula", "review", "match", 1,
            r"지금이야말로|" + RIEUL + r"\s?(?:때|시점)(?:다|이다|입니다)[.!]",
            "'~할 때다'로 맺는 결말 공식입니다. 무엇을 하자는 것인지 평서로 쓰세요."),
    pattern("ko-abstract-verb", "review", "match", 1,
            r"(?:변화|혁신|성과|효과|영향|발전|성장|이익|혜택|위기|혼란|변혁|전환|개선|향상|감동|즐거움|기쁨|행복|가치"
            r"|경험|결과|파장|돌파구|활력|도약)[을를]\s?(?:가져(?:온다|옵니다|왔다|왔습니다|올\s?것)|가져다\s?(?:준다|줍니다|줬다|주었다)"
            r"|불러일으(?:킨다|킵니다|켰다|켰습니다)|선사(?:한다|합니다|했다|했습니다))",
            "'변화를 가져온다'처럼 추상 명사에 만능 동사를 붙인 번역투입니다. 누가 무엇을 바꿨는지 쓰세요."),
    pattern("ko-jeok-chain", "review", "paragraph", 3,
            r"[가-힣]{1,4}(?<![목흔실업성기표궤누])적(?:인)?\s(?:함의|기반|한계|변화|차이|의미|영향|관점|측면|역할|가치"
            r"|접근|맥락|구조|요소|과제|토대|성과|시사점)",
            "'~적 + 추상 명사'가 몰렸습니다. '구조적 한계'는 '구조의 한계'처럼 풀어 쓰세요."),
    pattern("ko-light-verb", "review", "paragraph", 3, r"[을를]\s?(?:진행|실시|수행|시행)(?:하|했|합|한|할|해|됩|된|되|됐)",
            "'~을 진행하다'가 몰렸습니다. '테스트를 진행했다'는 '테스트했다'로 줄여 쓰세요."),
    pattern("ko-plural-quantifier", "review", "document", 2,
            r"(?:많은|여러|수많은|다양한|모든|각종|몇몇|온갖)\s[가-힣]{1,6}들(?=[이가을를은는의에도과와만]|[\s.,])",
            "수량을 밝힌 말에 '-들'을 또 붙였습니다. '많은 사람'처럼 한 번만 쓰세요."),
    pattern("ko-demonstrative", "review", "document", 3, r"(?<![가-힣])해당\s(?=[가-힣])",
            "'해당'이 반복됩니다. 행정 문서 말투라서 '이', '그'로 바꾸거나 빼도 됩니다."),
    pattern("ko-pronoun-repeat", "review", "paragraph", 3, r"(?<![가-힣])(?:그것|이것)(?:은|이|을|를|의|에)",
            "'그것·이것'이 몰렸습니다. 한국어는 대상이 분명하면 생략하거나 명사로 다시 씁니다."),
    pattern("ko-connective", "review", "paragraph", 3,
            START + r"(?:또한|아울러|나아가|더불어|게다가|더욱이|따라서|그러므로|즉)(?=[\s,])",
            "문장 첫 접속사가 한 문단에 몰렸습니다. 앞뒤 문장이 이미 이어지면 접속사를 빼세요."),
    pattern("ko-can", "review", "paragraph", 4, r"(?:할|될|있을|볼)\s?수\s?있(?:습니다|다)",
            "'~할 수 있다'가 반복됩니다. 실제로 하는 일이면 '~한다'로 쓰고, 가능성이면 조건을 쓰세요."),
    # 대구·도치: 사람 글보다 AI 글에서 훨씬 자주 측정된 구조입니다. 한 번은 사람도 쓰므로 반복·연쇄를 봅니다.
    pattern("ko-antithesis", "review", "document", 2, ANTITHESIS,
            "'A가 아니라 B' 대구가 반복됩니다. 가장 필요한 한 곳만 남기고 나머지는 바로 단언하세요."),
    pattern("ko-antithesis-chain", "block", "paragraph", 2, ANTITHESIS,
            "한 문단에서 대구가 이어집니다. 같은 틀을 연달아 쓰지 말고 비대칭 평서문으로 푸세요."),
    pattern("ko-either-or", "review", "match", 1,
            r"(?:인가|일까|는가|을까|할까|될까),\s?[^.?!\n]{1,40}(?:인가|일까|는가|을까|할까|될까)[?.!]",
            "'A인가, B인가' 대구 질문입니다. 질문을 거두고 판단을 바로 쓰세요."),
    pattern("ko-inversion", "review", "match", 1,
            r"(?:다|요|네),\s[^.?!\n,]{1,24}(?:은|는|이|가|을|를|도|만큼은|에게|에서)[.!?](?=\s|$)",
            "서술어 뒤로 주어나 목적어를 미룬 도치입니다. 글에서는 제자리로 돌려 쓰세요."),
    pattern("ko-fronted-resumptive", "review", "match", 1,
            r"(?<![고며서만데면니게지요다])\s?,\s?(?:그것은|그것이|이것은|이것이)\s",
            "'X, 그것은 Y' 강조 구조입니다. 'X는 Y다'로 바로 쓰세요."),
    pattern("ko-reason-close", "review", "document", 2, r"(?:는|은|던)\s?이유(?:다|이다|입니다)[.!]",
            "'~하는 이유다'로 끝맺는 도치형 결말이 반복됩니다. '그래서 ~'처럼 순서대로 쓰세요."),
    pattern("ko-rhetorical-hook", "review", "match", 1, r"\?\s*(?:바로|정답은|답은|이유는)\s",
            "질문을 던지고 곧바로 답하는 문장입니다. 답부터 쓰세요."),
    # 쉼표: LLM 한국어는 연결어미 뒤에 쉼표를 찍는 일이 사람보다 잦다고 측정됐습니다(KatFishNet).
    pattern("ko-comma-after-ending", "review", "document", 3,
            r"(?:하고|하며|하면서|지만|는데|어서|아서|해서|으며|으면서|니까|므로),\s",
            "연결어미 뒤 쉼표가 잦습니다. '~하고,'의 쉼표는 대개 빼도 뜻이 이어집니다."),
    pattern("ko-comma-conjunction", "review", "document", 2, r",\s?(?:그리고|하지만|그러나|따라서|그래서|그러므로)\s",
            "', 그리고'·', 하지만'은 영어 쉼표를 옮긴 꼴입니다. 문장을 끊거나 연결어미로 이으세요."),
    pattern("ko-colon-intro", "review", "match", 1, r"(?:다음과|아래와)\s?같(?:습니다|다|이|은)\s?:",
            "'다음과 같습니다:'는 영어 as follows를 옮긴 꼴입니다. 마침표로 끝내세요."),
    # 맞춤법: 사람 초안에 흔하고 LLM 글에는 거의 없어서 AI 문체 신호가 아닙니다. 점수에서는 빼고 고칠 곳으로만 알립니다.
    # '5일께'·'6월께'처럼 시기 뒤에 붙는 '께'를 오탐하지 않도록 활용형 어간을 적은 것만 찾습니다.
    pattern("ko-misspelling", "review", "match", 1,
            r"되요|됬|(?:할|갈|볼|줄|올|알|드릴|보낼|올릴|먹을|그럴|있을|없을)께요?(?![가-힣])|몇일|어떻해|금새|설레임"
            r"|웬지|왠만|왠일|희안|역활|일일히|번번히|곰곰히|틈틈히|깨끗히|오랫만|뵈요|않했|않해|아니예요|통채로|어의없",
            "맞춤법 오류입니다. 표준 표기는 되요→돼요, 됬→됐, 할께→할게, 몇일→며칠, 어떻해→어떡해, 금새→금세, "
            "설레임→설렘, 웬지→왠지, 왠만→웬만, 희안→희한, 역활→역할, 일일히→일일이, 오랫만→오랜만, 뵈요→봬요, "
            "않했→안 했, 아니예요→아니에요, 통채로→통째로, 어의없→어이없입니다."),
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
