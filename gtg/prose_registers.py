"""문체 검사를 글 갈래에 맞춥니다. 갈래마다 기본 규칙을 끄거나 완화하고, 그 갈래에서만 문제가 되는 표현을 더합니다.

학술문에서 '~라고 할 수 있다'는 관례적인 완곡이고, 구어에서 '맛있다, 이거.' 같은 도치는 자연스럽습니다.
같은 표현이라도 갈래에 따라 판단이 달라지므로 규칙을 데이터로 나눠 둡니다. 근거는 docs/verification/3.3.0.md에 둡니다.
"""

from __future__ import annotations

from typing import NamedTuple

from .prose_patterns import PATTERNS, START, Pattern, pattern


class Register(NamedTuple):
    disabled: frozenset
    relaxed: dict  # 규칙 id → (심각도, 범위, 최소 횟수)
    extra: tuple
    short_run: int | None  # 짧은 문장이 이만큼 이어지면 알립니다. None이면 보지 않습니다.
    monotone: bool
    formality: str | None  # consistent: 높임 등급 혼용, haera: 해라체 기대, conversational: 일상 어미 변주
    unscored: frozenset = frozenset()  # 이 갈래에서는 알리기만 하고 점수에서 빼는 신호
    verse: bool = False  # 줄이 호흡 단위인 시를 다루는 갈래입니다. 분량을 줄 수로 잽니다.


# KatFish 에세이에서 LLM 글의 13~29%, 사람 글의 0~8%에 나온 표현입니다. 보정용 절반만 보고 골랐고, 확인용 절반에서는
# 문장 첫머리 '이러한'을 쓴 사람 글이 1.1%에서 7.8%로 늘었습니다(3.3.0 검증 기록). 초록에서는 문장 첫머리 '이러한' 계열을
# 쓴 글이 사람 12.0%, LLM 11.5%로 같았으므로 일반 갈래에만 둡니다.
GENERAL = (
    pattern("ko-this-is-open", "review", "document", 2, START + r"이는\s",
            "'이는 ~'으로 앞 문장을 받아 여는 문장이 반복됩니다. 앞 문장과 한 문장으로 잇거나 '이 결과는'처럼 대상을 밝히세요."),
    pattern("ko-demonstrative-open", "review", "document", 2, START + r"(?:이러한|이와\s?같은|이처럼)\s",
            "'이러한 ~'으로 여는 문장이 반복됩니다. 가리키는 대상을 명사로 다시 쓰거나 앞 문장과 이으세요."),
    pattern("ko-diverse", "review", "document", 2, r"다양한",
            "'다양한'이 반복됩니다. 무엇이 몇 가지인지, 어떤 것인지 구체적으로 쓰세요."),
)

ACADEMIC = (
    pattern("academic-we", "review", "paragraph", 2, START + r"우리는\s",
            "영어 we를 옮긴 '우리는'이 반복됩니다. 주어를 생략하거나 '본 연구는'을 쓰세요."),
    # '~에 의해 매개된다', '~로 알려져 있다' 같은 학술 피동은 정형이라 두고, 사람이 한 일을 피동으로 쓴 것만 봅니다.
    pattern("academic-agent-passive", "review", "match", 1,
            r"에\s?의해\s?(?:제안|개발|수행|작성|발견|보고|발표|설계|구축|제시|수집|측정|분석|실시|진행|고안|도입)"
            r"(?:되었|됐|된|되어|돼)",
            "사람이 한 일을 영어식 피동으로 썼습니다. '저자들이 제안한 방법'처럼 능동으로 쓰세요."),
    # KatFish 초록에서 LLM 글의 34~36%, 사람 글의 0~2%에 나왔습니다(3.3.0 검증 기록).
    pattern("academic-this-paper", "review", "match", 1, START + r"이\s(?:논문|연구)(?:은|는|에서는|에서)\s",
            "영어 This paper를 옮긴 꼴입니다. 국문 논문은 '본 논문은'이라고 쓰거나 주어를 생략합니다."),
    pattern("academic-figure-label", "review", "match", 1, r"\b(?:Figure|Fig\.|Table)\s?\d",
            "한국어 본문에서는 '그림 1', '표 2'로 씁니다."),
    pattern("academic-archaic", "review", "match", 1, r"사료(?:된다|됨|되는|됩니다)|하는\s?바이다",
            "예스러운 논문투입니다. '판단한다', '본다'처럼 쓰세요."),
    pattern("academic-novelty", "review", "match", 1, r"(?:세계\s?)?최초(?:로|의)|획기적(?:인|으로)",
            "최초·획기적이라는 주장에는 비교 대상과 인용이 필요합니다."),
)

EVERYDAY = (
    pattern("everyday-empathy", "review", "document", 2,
            r"(?:정말|많이|진짜)\s?힘(?:드셨|들었)겠|충분히\s?이해(?:합니다|해요|가\s?돼요|됩니다)"
            r"|그런\s?마음이\s?(?:드는|드시는)\s?(?:게|것이|것도|건)\s?당연|마음이\s?(?:아프|무거우)시겠|공감(?:합니다|해요|이\s?돼요)"
            r"|충분히\s?잘\s?하고\s?있|(?:너무|많이)\s?자책하지\s?(?:마|말)",
            "공감 상투구가 반복됩니다. 상대가 실제로 한 말을 받아서 답하세요."),
    pattern("everyday-object-honorific", "review", "match", 1, r"(?:나오|품절이)(?:셨|십니다|세요|실게요)|말씀이\s?계시",
            "사물이나 상황을 높였습니다. '나왔습니다', '품절입니다', '말씀이 있겠습니다'처럼 쓰세요."),
    pattern("everyday-stiff-notice", "review", "match", 1,
            r"참고하시기\s?바랍니다|양해\s?부탁드립니다|추천\s?드립니다|(?:안내|전달|말씀)드리도록\s?하겠|안내드립니다",
            "안내문 말투입니다. 일상 글에서는 '~해 보세요', '~하면 돼요', '보내 드릴게요'처럼 쓰세요."),
    pattern("everyday-exclaim", "review", "paragraph", 4, r"!",
            "느낌표가 몰렸습니다. 정말 놀랄 때만 쓰세요."),
)

LITERARY = (
    pattern("literary-ineffable", "block", "match", 1,
            r"형언할\s?수\s?없|이루\s?말할\s?수\s?없|말로\s?(?:다\s?)?(?:표현할|설명할|할)\s?수\s?없",
            "말로 할 수 없다고 쓰는 대신, 무엇이 보이고 들리고 만져졌는지 쓰세요."),
    pattern("literary-emotion-cliche", "review", "document", 2,
            r"가슴이\s?(?:벅차|먹먹|뭉클|아려)|눈시울이\s?(?:붉어|뜨거워)|마음\s?한\s?(?:켠|편)|가슴\s?깊(?:이|은\s?곳)"
            r"|마음\s?깊은\s?곳|따스한|포근한|시간이\s?멈춘\s?(?:듯|것)|심장이\s?(?:쿵|내려앉)|온몸에\s?전율",
            "닳은 감정 표현이 반복됩니다. 인물의 행동이나 장면으로 보여 주세요."),
    pattern("literary-emotion-surge", "review", "paragraph", 2,
            r"(?:슬픔|기쁨|외로움|그리움|분노|두려움|설렘|행복|불안|공허함|안도감)(?:이|가|을|를)?\s?(?:밀려|차올|북받|휩싸|가득|스며|번져)",
            "감정 이름이 밀려오는 식의 서술이 이어집니다. 감정은 이름 대신 몸짓과 사물로 드러내세요."),
    pattern("literary-seems", "review", "paragraph", 3, r"(?:것|듯)만\s?같았다|듯했다|것\s?같았다",
            "'~것 같았다'가 몰렸습니다. 인물이 확실히 아는 것은 단정하세요."),
    pattern("literary-epiphany", "review", "match", 1,
            r"(?:그제야|비로소)\s?(?:깨달|알게\s?되)|(?:삶|인생|사랑)(?:이란|은|이라는\s?것은)\s?(?:결국|어쩌면)",
            "깨달음이나 교훈으로 닫는 문장입니다. 장면에서 멈추고 판단은 독자에게 맡기세요."),
    pattern("literary-pronoun", "review", "paragraph", 3, r"그녀(?:는|가|의|를|에게|와|도)",
            "'그녀'가 몰렸습니다. 이름을 쓰거나 주어를 생략하세요."),
    pattern("literary-reflective", "review", "document", 4, r"어쩌면|비로소|천천히|조용히|문득",
            "성찰하는 부사가 습관처럼 반복됩니다."),
    # 시의 행 끝 쉼표는 KatFish 시 자료에서 LLM 쪽으로 크게 치우쳤습니다. 행갈이가 이미 쉼표 몫을 합니다.
    pattern("literary-line-comma", "review", "paragraph", 3, r"^(?=.{2,30}$).*,\s*$",
            "시행 끝마다 쉼표를 찍었습니다. 행갈이가 쉼을 만들므로 꼭 끊어 읽어야 할 곳만 남기세요."),
)

REGISTERS = {
    "general": Register(frozenset(), {}, GENERAL, 4, True, "consistent"),
    "academic": Register(frozenset(), {"ko-hedged-copula": ("review", "document", 3)}, ACADEMIC, 4, True, "haera"),
    # 구어에서는 오른쪽으로 미룬 도치와 짧은 문장이 자연스럽고, 같은 말로 이어 시작하는 일도 흔합니다.
    "everyday": Register(frozenset({"ko-inversion"}), {}, EVERYDAY, None, False, "conversational",
                         frozenset({"rhythm-repeated-opening"})),
    # 문학에서는 의도한 단문과 반복 첫머리(수미상관·후렴)를 허용하고 한두 번의 도치도 둡니다. KatFish 시에서는
    # 짧은 문장 연쇄가 사람 글에 더 많았습니다(12% 대 5%). 서술과 대사의 높임 차이는 따지지 않습니다.
    "literary": Register(frozenset(), {"ko-inversion": ("review", "document", 2)}, LITERARY, 6, True, None,
                         frozenset({"rhythm-repeated-opening", "rhythm-choppy"}), True),
}


def rules(name: str) -> tuple[list[Pattern], Register]:
    """갈래에 맞춘 규칙 목록과 리듬 설정입니다."""
    if name not in REGISTERS:
        raise ValueError(f"글 갈래는 {', '.join(REGISTERS)} 가운데 하나여야 합니다.")
    register = REGISTERS[name]
    chosen = []
    for rule in PATTERNS:
        if rule.id in register.disabled:
            continue
        if rule.id in register.relaxed:
            severity, scope, minimum = register.relaxed[rule.id]
            rule = rule._replace(severity=severity, scope=scope, minimum=minimum)
        chosen.append(rule)
    return chosen + list(register.extra), register
