"""윤문 전후를 견줍니다. 원문의 수치·인용·URL·코드 표기가 남았는지, 얼마나 고쳤는지를 재서 읽기 좋게 만들다가
사실이 바뀌거나 새 글이 되는 일을 잡습니다. 문장이 나아졌는지는 판정하지 않습니다.

윤문 스킬은 수치와 인용을 고치지 않고 고친 분량이 많으면 지나치게 손대지 않았는지 살피라고 요구합니다. 모델의 자기 보고에
맡기지 않고 두 글을 직접 비교해 확인하는 것이 이 모듈의 일입니다.
"""

from __future__ import annotations

from collections import Counter
import difflib
import re

from .prose_rhythm import HANGUL, LATIN, finding


# 고친 분량이 이 비율을 넘으면 알리고(검토), 거의 새로 쓴 글이면 멈춥니다(차단). 단어 단위 비교라서 어미만 바꿔도
# 단어는 바뀐 것으로 세고, 상투구 문장을 지운 것도 바뀐 것으로 셉니다. 그래서 절반을 넘는 것만으로는 차단하지 않고
# 어떤 문장을 지웠는지 보고하게 합니다. 차단은 원문이 거의 남지 않은 경우에 한정합니다.
REVIEW_SHARE = 0.30
STRONG_SHARE = 0.50
BLOCK_SHARE = 0.80
# 단어가 이보다 적은 글은 한두 문장만 고쳐도 비율이 크게 뛰므로 차단하지 않고 알리기만 합니다.
MIN_WORDS_TO_BLOCK = 40
# 비교 비용을 제한합니다. 넘으면 고친 분량은 재지 않고 나머지 검사만 합니다.
MAX_WORDS = 12000
# 따옴표 안 글이 이 글자 수(공백 제외) 이상이면 인용문으로 보고 글자 그대로 남았는지 봅니다. 짧으면 강조용 따옴표입니다.
QUOTE_LENGTH = 8
SHOWN = 6

FENCE = re.compile(r"^[ \t]{0,3}(?P<mark>`{3,}|~{3,}).*?^[ \t]{0,3}(?P=mark)[ \t]*$", re.M | re.S)
INLINE = re.compile(r"(`+)[^`\n]+?\1")
URL = re.compile(r"\b(?:https?|file)://[^\s)>\]]+")
# 목록 번호('1. ', '2) ')와 번호 매긴 제목('## 3.1 실행')의 절 번호입니다. 연도처럼 큰 수는 사실이므로 한두 자리만 뺍니다.
LIST_MARK = re.compile(r"^[ \t]{0,3}(?:#{1,6}[ \t]*\d{1,2}(?:\.\d{1,2})*[.)]?[ \t]+|\d{1,2}(?:\.\d{1,2})*[.)][ \t]+)", re.M)
NUMBER = re.compile(r"(?P<n>(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)*)(?:\s?(?P<u>%p|%|퍼센트포인트|퍼센트))?")
UNITS = {"%p": "%p", "퍼센트포인트": "%p", "%": "%", "퍼센트": "%"}
QUOTE = re.compile(r"“([^”\n]+?)”|\"([^\"\n]+?)\"|‘([^’\n]+?)’|「([^」\n]+?)」|『([^』\n]+?)』")
TERM = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-_.][A-Za-z0-9]+)*")


def literals(text: str) -> tuple[Counter, str]:
    """글자 그대로 남아야 하는 코드 블록·인라인 코드·URL과, 그것들을 뺀 나머지 글입니다."""
    found = Counter()
    for pattern in (FENCE, INLINE, URL):
        for match in pattern.finditer(text):
            found[match.group(0).strip()] += 1
        text = pattern.sub(" ", text)
    return found, text


def canonical(match: re.Match) -> str:
    """쉼표·앞자리 0·'퍼센트' 표기 차이를 지운 수치입니다. 2026-11-03과 2026년 11월 3일이 같게 나옵니다."""
    number = re.sub(r"^0+(?=\d)", "", match.group("n").replace(",", ""))
    return number + UNITS.get(match.group("u") or "", "")


def significant(token: str) -> bool:
    """고치면 사실이 달라지는 수치입니다. 한 자리나 두 자리 자연수는 '세 가지'를 '3가지'로 쓰는 정도의 변화일 수 있습니다."""
    return "%" in token or "." in token or len(re.sub(r"\D", "", token)) >= 3


def numbers(text: str) -> Counter:
    text = LIST_MARK.sub("", text)
    return Counter(canonical(match) for match in NUMBER.finditer(text))


def quotes(text: str) -> Counter:
    found = Counter()
    for match in QUOTE.finditer(text):
        inner = re.sub(r"\s+", " ", next(group for group in match.groups() if group)).strip()
        if len(re.sub(r"\s", "", inner)) >= QUOTE_LENGTH:
            found[inner] += 1
    return found


def terms(text: str) -> Counter:
    return Counter(token for token in TERM.findall(text) if len(token) >= 2)


def changed_share(before: str, after: str) -> float | None:
    """원문 단어 가운데 윤문본에서 바뀐 비율입니다. 너무 긴 글은 None입니다."""
    old, new = before.split(), after.split()
    if len(old) + len(new) > MAX_WORDS:
        return None
    return round(1 - difflib.SequenceMatcher(None, old, new, autojunk=False).ratio(), 3)


def shown(items: Counter) -> list[str]:
    return sorted(items.elements())[:SHOWN]


def compare(original: str, polished: str, path: str) -> tuple[dict, list[dict]]:
    """윤문 요약과 발견 목록입니다. 발견은 점수에 넣지 않고 차단·검토로만 셉니다."""
    old_literals, old_text = literals(original)
    new_literals, new_text = literals(polished)
    old_numbers, new_numbers = numbers(old_text), numbers(new_text)
    old_quotes, new_quotes = quotes(old_text), quotes(new_text)
    korean = len(HANGUL.findall(old_text)) >= len(LATIN.findall(old_text))
    old_terms, new_terms = (terms(old_text), terms(new_text)) if korean else (Counter(), Counter())
    share = changed_share(original, polished)
    words = len(original.split())
    diff = {"literals": (old_literals - new_literals, new_literals - old_literals),
            "numbers": (old_numbers - new_numbers, new_numbers - old_numbers),
            "quotes": (old_quotes - new_quotes, new_quotes - old_quotes),
            "terms": (old_terms - new_terms, new_terms - old_terms)}
    summary = {"changed_share": share, "words": {"before": words, "after": len(polished.split())},
               **{name: {"lost": shown(lost), "added": shown(added)} for name, (lost, added) in diff.items()}}
    found = []

    def report(rule: str, severity: str, items: Counter, hint: str):
        if items:
            found.append(finding(rule, severity, path, 1, ", ".join(shown(items)), hint, count=sum(items.values())))

    lost, added = diff["literals"]
    report("fidelity-literal-lost", "block", lost, "원문의 URL·코드가 윤문본에서 바뀌었거나 사라졌습니다. 글자 그대로 되돌리세요.")
    report("fidelity-literal-added", "review", added, "원문에 없던 URL·코드가 생겼습니다. 어디서 가져온 것인지 확인하세요.")
    lost, added = diff["numbers"]
    report("fidelity-number-lost", "block", Counter({k: v for k, v in lost.items() if significant(k)}),
           "원문의 수치가 윤문본에 없습니다. 고친 문장에서 그 수치를 되살리세요.")
    report("fidelity-number-lost-minor", "review", Counter({k: v for k, v in lost.items() if not significant(k)}),
           "원문의 작은 수치가 윤문본에 없습니다. 의도한 변경인지 확인하세요.")
    report("fidelity-number-added", "block", Counter({k: v for k, v in added.items() if significant(k)}),
           "원문에 없던 수치가 윤문본에 생겼습니다. 지어낸 사실이 아닌지 확인하고 지우세요.")
    report("fidelity-number-added-minor", "review", Counter({k: v for k, v in added.items() if not significant(k)}),
           "원문에 없던 작은 수치가 생겼습니다. 한글 수를 숫자로 바꾼 것이 아니면 지우세요.")
    lost, added = diff["quotes"]
    report("fidelity-quote-lost", "block", lost, "원문의 인용문이 윤문본에서 바뀌었거나 사라졌습니다. 인용은 글자 그대로 둡니다.")
    report("fidelity-quote-added", "review", added, "원문에 없던 인용문이 생겼습니다. 지어낸 인용이 아닌지 확인하세요.")
    lost, added = diff["terms"]
    report("fidelity-term-lost", "review", lost, "원문의 영문 표기가 윤문본에 없습니다. 용어를 임의로 번역하거나 뺐는지 확인하세요.")
    report("fidelity-term-added", "review", added, "원문에 없던 영문 표기가 생겼습니다. 한국어로 충분한 말을 영어로 섞지 않았는지 보세요.")
    if share is not None:
        if share == 0:
            found.append(finding("fidelity-unchanged", "review", path, 1, "", "원문과 같은 글입니다. 고친 곳이 없습니다.", share=share))
        elif share > BLOCK_SHARE and words >= MIN_WORDS_TO_BLOCK:
            found.append(finding("fidelity-over-edit", "block", path, 1, f"{share:.0%}",
                                 f"원문 단어의 {share:.0%}가 바뀌어 원문이 거의 남지 않았습니다. 윤문이 아니라 새로 쓴 글입니다. "
                                 "필요한 곳만 고치거나, 새로 쓰는 것이 맞다면 윤문이 아니라고 밝히세요.", share=share))
        elif share > STRONG_SHARE:
            found.append(finding("fidelity-over-edit", "review", path, 1, f"{share:.0%}",
                                 f"원문 단어의 {share:.0%}가 바뀌었습니다. 새로 쓴 글에 가깝습니다. 상투구 문장을 지운 것이면 지운 문장과 "
                                 "이유를 보고하고, 아니면 필요한 곳만 고치세요.", share=share))
        elif share > REVIEW_SHARE:
            found.append(finding("fidelity-over-edit", "review", path, 1, f"{share:.0%}",
                                 f"원문 단어의 {share:.0%}가 바뀌었습니다. 지나치게 손대지 않았는지 보세요.", share=share))
    return summary, found
