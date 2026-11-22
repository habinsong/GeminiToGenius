"""문체 습관 항목. 정규식 한 줄로는 못 잡고 비율이나 빈도로 판단하는 것들.

문서 전체에 걸린 항목은 길이 0인 구간(start == end)에 두어 다른 항목을 가리지도 가려지지도 않게 한다.
근거와 약점은 docs/research.md 8절. 대부분 C등급이고, 비율 신호는 집단 통계라 개인 문체를 오탐할 수 있다.
"""
from __future__ import annotations

import re
import statistics
from typing import Dict, List, Optional, Sequence, Tuple

from . import linkers
from .analyzers import _register
from .model import Edit, Finding, weigh

Span = Tuple[int, int]
SKIP = ("#", ">", "|", "```", "<!--")
LISTISH = re.compile(r"^[ \t]*(?:[-*•+]|\d+[.)])[ \t]+")
GENRE = {"technical": 0.3, "literary": 0.5, "academic": 0.7}
BAND = {"en": (8, 20), "ko": (6, 15), "es": (9, 22), "fr": (9, 22), "pt": (9, 22), "it": (9, 22), "de": (7, 18),
        "ru": (7, 16)}
SYN_EN = [("company", "firm", "organization", "enterprise", "corporation", "outfit"),
          ("tool", "solution", "platform", "application", "offering"),
          ("approach", "method", "technique", "strategy", "methodology"),
          ("issue", "problem", "challenge", "obstacle", "hurdle"),
          ("developers", "engineers", "programmers", "practitioners", "builders")]
SYN_KO = [("회사", "기업", "업체", "법인", "조직"), ("도구", "솔루션", "플랫폼", "서비스", "시스템"),
          ("방법", "방식", "기법", "접근법", "전략"), ("문제", "이슈", "과제", "난제"),
          ("사용자", "이용자", "고객", "소비자"), ("개발자", "엔지니어", "프로그래머")]
GENERIC_HEAD = {"overview", "key points", "key takeaways", "summary", "conclusion", "introduction", "final thoughts",
                "개요", "핵심 요약", "요약", "결론", "서론", "마치며", "정리하며", "들어가며"}
CONNECTIVE_END = re.compile(r"(?:[았었였했갔왔봤썼났냈렸졌됐겼켰섰줬쳤]고|하고|이고|하며|이며|으며|면서|지만|는데|인데|한데|으나|니까|"
                            r"아서|어서|해서)(?P<c>[,，])?(?=[ \t])")
KO_CONJ = re.compile(r"(?:(?<=[.!?])[ \t]+|^[ \t]*)(?P<w>그러나|하지만|그리고|그런데|그래서|따라서|또한|한편|특히|결국|즉|그러므로|"
                     r"다시\s*말해|예를\s*들어)(?P<c>[,，])", re.M)
KO_CONJ_ALL = re.compile(r"(?:(?<=[.!?])[ \t]+|^[ \t]*)(?:그러나|하지만|그리고|그런데|그래서|따라서|또한|한편|특히|결국|즉|그러므로|"
                         r"다시\s*말해|예를\s*들어)(?![가-힣])", re.M)
GLOSS = re.compile(r"(?<=[가-힣])[ \t]?\([A-Za-z][A-Za-z0-9 .,'/-]{1,40}\)")
LABEL = re.compile(r"^[ \t]*(?:[-*•+]|\d+[.)])?[ \t]*(?P<lab>[^\s:：.!?。*#`|][^:：\n.!?。]{0,15}?)[:：][ \t]+\S")


def _mk(rid: str, cat: str, grade: str, start: int, end: int, w: float, genre: str, note: str, *, sugg: str = "",
        text: str = "", lang: str = "any", gmap: Optional[Dict[str, float]] = None,
        edit: Optional[Edit] = None) -> Finding:
    return Finding(rule_id=rid, category=cat, grade=grade, start=start, end=end, text=text[:60], line=0, col=0,
                   weight=weigh(cat, grade, w, gmap or GENRE, genre), note=note, sugg=sugg,
                   tier=edit.tier if edit else "none", fixable=edit is not None, lang=lang, edit=edit)


def _body(masked: str, paras: Sequence[Span]) -> List[Span]:
    return [p for p in paras if not masked[p[0]:p[1]].lstrip().startswith(SKIP + ("- ", "* ", "+ ", "1. ", "2. "))]


def label_colon(masked: str, genre: str) -> List[Finding]:
    """'라벨: 설명' 꼴 줄이 목록과 문단에 줄줄이 있다(제목형 콜론). 굵은 라벨 불릿은 any.format.bold-lead가 찾는다."""
    lines = [(m.start(), m.group(0)) for m in re.finditer(r"^[^\n]+$", masked, re.M)]
    items = [(p, t) for p, t in lines if t.strip() and not t.lstrip().startswith(SKIP) and len(t.split()) >= 3
             and not t.lstrip().startswith("**")]
    hits = [(p, t) for p, t in items if LABEL.match(t) and "\x00" not in t[:20]]
    if len(hits) < 5 or len(hits) < 0.4 * len(items):
        return []
    p = hits[0][0]
    return [_mk("any.format.label-colon", "format", "C", p, p, 0.3, genre,
                f"'라벨: 설명' 꼴 줄이 {len(hits)}/{len(items)}줄이다(제목형 콜론). Lines shaped 'Label: text' dominate.",
                sugg="라벨을 문장 안으로 풀거나 꼭 필요한 곳에만 둔다.", text=hits[0][1].strip())]


def english_gloss(masked: str, units: int, genre: str) -> List[Finding]:
    """한국어 문장에 영문 병기 괄호('고객 경험(CX)')가 잇달아 붙는다."""
    if not re.search(r"[가-힣]", masked):
        return []
    hits = list(GLOSS.finditer(masked))
    if len(hits) < 4 or 1000 * len(hits) / max(units, 1) < 4:
        return []
    return [_mk("ko.format.english-gloss", "format", "C", hits[0].start(), hits[0].start(), 0.0, genre,
                f"영문 병기 괄호가 {len(hits)}번 붙는다(영어 인용 과다).", lang="ko",
                sugg="처음 한 번만 병기하고 나머지는 한국어로 쓴다. 독자가 모를 용어에만 병기한다.", text=hits[0].group(0))]


def ko_commas(masked: str, genre: str) -> List[Finding]:
    """한국어 규범은 접속부사와 연결어미 뒤에 쉼표를 두지 않는 쪽을 자연스럽게 본다. 영어식 쉼표가 몰리면 찾는다."""
    if not re.search(r"[가-힣]", masked):
        return []
    out: List[Finding] = []
    gm = {"literary": 0.5, "technical": 0.5}
    starts = len(KO_CONJ_ALL.findall(masked))
    conj = list(KO_CONJ.finditer(masked))
    if starts >= 4 and len(conj) >= 0.6 * starts:
        for m in conj:
            cs = m.start("c")
            edit = Edit(cs, cs + 1, "", "ko.punct.conj-comma", "strong", before=m.group("c"))
            out.append(_mk("ko.punct.conj-comma", "rhythm", "C", cs, cs + 1, 0.25, genre,
                           "문장 첫 접속부사 뒤에 쉼표를 찍었다(영어식). 한국어 규범은 쉼표를 두지 않는 쪽이다.",
                           lang="ko", gmap=gm, edit=edit, text=m.group("w") + m.group("c"),
                           sugg="접속부사 뒤 쉼표를 지운다."))
    ends = list(CONNECTIVE_END.finditer(masked))
    commas = [m for m in ends if m.group("c")]
    if len(ends) >= 8 and len(commas) >= 0.4 * len(ends):
        p = commas[0].start("c")
        out.append(_mk("ko.punct.ending-comma", "rhythm", "C", p, p, 0.3, genre,
                       f"연결어미 {len(ends)}곳 중 {len(commas)}곳 뒤에 쉼표가 있다. 사람이 쓴 글 4~13%, LLM이 쓴 글 16~28%라는 보고(KatFishNet)와 비교한다.",
                       lang="ko", gmap=gm, text=commas[0].group(0),
                       sugg="숨 쉬는 자리에만 쉼표를 둔다. 개인 문체일 수 있으니 필자 확인 뒤에 줄인다."))
    return out


def synonym_cycling(masked: str, sents: Sequence[Span], paras: Sequence[Span], genre: str) -> List[Finding]:
    """한 문단에서 같은 대상을 동의어로 돌려 부른다(elegant variation). 핵심 용어는 바꾸지 말고 반복하는 편이 낫다."""
    out: List[Finding] = []
    for ps, pe in _body(masked, paras):
        seg = masked[ps:pe]
        if len([1 for s in sents if ps <= s[0] < pe]) < 4:
            continue
        ko = bool(re.search(r"[가-힣]", seg))
        for group in (SYN_KO if ko else SYN_EN):
            found = []
            for w in group:
                rx = (rf"(?<![가-힣]){w}(?:을|를|이|가|은|는|의|에|와|과|도|로|들)?(?![가-힣])" if ko
                      else rf"\b{w}s?\b")
                m = re.search(rx, seg, re.I)
                if m:
                    found.append((m.start(), w))
            if len(found) >= 3:
                pos = ps + sorted(found)[2][0]
                out.append(_mk(f"{'ko' if ko else 'en'}.vocab.synonym-cycling", "vocab", "C", pos, pos, 0.25, genre,
                               "한 문단에서 " + ", ".join(w for _, w in sorted(found)) + "을(를) 번갈아 쓴다(같은 대상이면 동의어 돌려쓰기)."
                               if ko else "One paragraph rotates " + ", ".join(w for _, w in sorted(found)) +
                               " (synonym cycling if they name the same thing).",
                               lang="ko" if ko else "en", gmap={"academic": 0.5, "technical": 0.4},
                               sugg="같은 대상이면 가장 분명한 말 하나로 통일한다. 서로 다른 대상이면 그대로 둔다.",
                               text=seg[sorted(found)[2][0]:][:30]))
    return out


_ECHO_SUFFIX = re.compile(r"(?:입니다|이다|이며|이고|으로는|에서는|으로|에서|에게|까지|부터|보다|처럼|이|가|은|는|을|를|의|에|도|로|과|와|만|들)$")
_ECHO_SKIP = {"우리", "그것", "이것", "때문", "이후", "이상", "경우", "정도", "하나", "모두", "위해", "대한", "통해", "다른", "여기",
              "저기", "거기", "자신", "사람", "이전", "이하", "관련", "이번", "다음", "동안", "사이", "가운데"}


def word_echo(masked: str, sents: Sequence[Span], paras: Sequence[Span], genre: str) -> List[Finding]:
    """한 문단에서 같은 명사가 세 번 이상 되풀이된다. 핵심 용어를 지키는 반복과 습관적으로 되풀이하는 말은 글쓴이가 가려야 한다."""
    out: List[Finding] = []
    for ps, pe in _body(masked, paras):
        seg = masked[ps:pe]
        if len([1 for s in sents if ps <= s[0] < pe]) < 3 or not re.search(r"[가-힣]", seg):
            continue
        seen: Dict[str, List[int]] = {}
        for m in re.finditer(r"[가-힣]{2,}", seg):
            tok = m.group(0)
            stem = _ECHO_SUFFIX.sub("", tok, count=1)
            if stem == tok or len(stem) < 2 or stem in _ECHO_SKIP or stem[-1] in "하지되라다고며":
                continue
            seen.setdefault(stem, []).append(m.start())
        hot = sorted(((w, p) for w, p in seen.items() if len(p) >= 3), key=lambda x: -len(x[1]))[:2]
        for w, pos in hot:
            at = ps + pos[2]
            out.append(_mk("ko.vocab.word-echo", "vocab", "C", at, at, 0.25, genre,
                           f"한 문단에서 '{w}'이(가) {len(pos)}번 되풀이된다.", lang="ko",
                           gmap={"academic": 0.5, "technical": 0.3, "literary": 0.5},
                           sugg="핵심 용어면 두고, 아니면 대명사나 생략으로 줄이거나 문장을 합친다.", text=seg[pos[2]:][:30]))
    return out


_TRACE_DETAIL = re.compile(r"자국|얼룩|상처|흠집|긁|발자국|그을|파편|지문|핏|부서진|깨진|찢어진|눌린|패인|닳은|바랜")


def trace_word(masked: str, paras: Sequence[Span], genre: str) -> List[Finding]:
    """'흔적'이 어떤 흔적인지 앞에서 서술하지 않고 불쑥 나온다. 앞 150자(같은 문단) 안에 구체적인 자국 낱말이 없으면 찾는다."""
    out: List[Finding] = []
    for ps, pe in _body(masked, paras):
        seg = masked[ps:pe]
        for m in re.finditer(r"흔적", seg):
            before = seg[max(0, m.start() - 150):m.start()]
            if _TRACE_DETAIL.search(before):
                continue
            at = ps + m.start()
            out.append(_mk("ko.vocab.trace-bare", "vocab", "B", at, at + 2, 0.4, genre,
                           "'흔적'. 앞에서 어떤 자국인지 서술하지 않고 '흔적'이라는 말만 쓴다.", lang="ko",
                           sugg="무엇이 어디에 남았는지 구체적으로 쓰거나 '흔적'을 빼고 쓴다.", text=seg[m.start():][:20]))
    return out


_SELF_REF = {"필자": r"필자(?:는|가|의|도)", "본 연구": r"본\s*(?:연구|논문)(?:는|에서는|에서|의|은)", "우리": r"(?<![가-힣])우리(?:는|가)(?![가-힣])",
             "저자": r"(?<![가-힣])저자(?:는|가|들은)", "연구자": r"(?<![가-힣])연구자(?:는|가)(?![가-힣])"}


def self_reference(masked: str, genre: str) -> List[Finding]:
    """학술 글에서 글쓴이를 가리키는 말('필자', '본 연구', '우리')이 둘 이상 섞인다."""
    found = [(k, m.start()) for k, rx in _SELF_REF.items() for m in [re.search(rx, masked)] if m]
    if len(found) < 2:
        return []
    names = ", ".join(sorted(k for k, _ in found))
    at = sorted(p for _, p in found)[1]
    return [_mk("ko.genre.self-reference-mix", "structure", "C", at, at, 0.35, genre,
                f"글쓴이를 가리키는 말이 섞였다({names}).", lang="ko", gmap={"everyday": 0.3, "literary": 0.3},
                sugg="투고처 관행에 맞춰 하나로 통일한다.", text=masked[at:at + 20])]


def rhythm_band(masked: str, sents: Sequence[Span], paras: Sequence[Span], genre: str) -> List[Finding]:
    """문장 길이가 한 구간에 몰려 있다. 위키백과(2026)는 최근 출력이 8~20낱말 한도에 붙는다고 적는다."""
    body = _body(masked, paras)
    texts = [re.sub(r"\x00+", "X", masked[a:b]) for a, b in sents if any(p[0] <= a < p[1] for p in body)]
    if len(texts) < 10:
        return []
    lang = linkers.detect(" ".join(texts))
    if lang not in BAND:
        return []
    lo, hi = BAND[lang]
    lens = [linkers.length_units(t, lang) for t in texts]
    inside = sum(1 for n in lens if lo <= n <= hi) / len(lens)
    mean = statistics.mean(lens)
    cv = statistics.pstdev(lens) / mean if mean else 1.0
    if inside < 0.9 or cv > 0.3:
        return []
    first = next(a for a, b in sents if any(p[0] <= a < p[1] for p in body))
    return [_mk("any.rhythm.band-lock", "rhythm", "C", first, first, 0.4, genre,
                f"문장 {len(lens)}개 중 {inside:.0%}가 {lo}~{hi}{'어절' if lang == 'ko' else '낱말'} 구간에 있고 편차가 작다(변동계수 {cv:.2f}).",
                sugg="쪼개거나 붙여서 길이를 맞추지 않는다. 한 문장으로 끝낼 것은 짧게, 이어질 것은 한 문장으로 합친다.",
                gmap={"technical": 0.4, "academic": 0.6, "literary": 0.6}, text=texts[0])]


def punct_flat(masked: str, sents: Sequence[Span], paras: Sequence[Span], genre: str) -> List[Finding]:
    """쉼표와 마침표뿐이다. 대시를 걷어 낸 최근 출력은 다른 부호도 함께 줄었다는 보고(위키백과 2026)."""
    body = _body(masked, paras)
    text = "\n".join(masked[a:b] for a, b in body)
    if len(re.findall(r"[.!?]", text)) < 15 or linkers.detect(text) not in ("en", "es", "fr", "pt", "it", "de", "ru"):
        return []
    if re.search(r"[;:()（）?？!！—–\"“”‘’]", text):
        return []
    return [_mk("any.rhythm.punct-flat", "rhythm", "C", body[0][0], body[0][0], 0.25, genre,
                "글 전체에 쉼표와 마침표 말고는 구두점이 없다(세미콜론, 콜론, 괄호, 물음표, 따옴표 없음).",
                sugg="의도적으로 부호를 넣지 않는다. 필요한 자리(콜론으로 설명, 괄호로 부연)에만 쓴다.",
                gmap={"technical": 0.4, "literary": 0.5}, text=text[:40])]


def headings(masked: str, genre: str) -> List[Finding]:
    """제목을 되풀이하는 첫 문장, 내용 없는 정형 제목."""
    out: List[Finding] = []
    heads = [(m.start(), m.group(1).strip(), m.end()) for m in re.finditer(r"^#{1,6}[ \t]+(.+?)[ \t]*$", masked, re.M)]
    echo = []
    for pos, text, end in heads:
        nxt = re.match(r"\s*([^\n#|>`-][^\n]*)", masked[end:end + 400])
        if not nxt:
            continue
        first = re.split(r"(?<=[.!?。])\s", nxt.group(1), maxsplit=1)[0]
        strip = lambda s: {w.lower()[:5] for w in re.findall(r"[A-Za-z]{4,}|[가-힣]{2,}", s)}  # noqa: E731
        a, b = strip(text), strip(first)
        if len(a) >= 2 and len(a & b) >= 0.7 * len(a) and len(first.split()) <= 12:
            echo.append((end + nxt.start(1), first))
    if len(echo) >= 2:
        out.append(_mk("any.structure.heading-echo", "structure", "C", echo[0][0], echo[0][0], 0.4, genre,
                       f"제목 {len(echo)}개가 바로 아래 첫 문장에서 되풀이된다.", text=echo[0][1],
                       sugg="제목이 한 일을 첫 문장이 반복하지 않게 바로 내용으로 들어간다."))
    generic = [h for h in heads if re.sub(r"[\s\d.:)]+$", "", h[1].lower()) in GENERIC_HEAD]
    if len(generic) >= 3:
        out.append(_mk("any.structure.generic-headings", "structure", "C", generic[0][0], generic[0][0], 0.3, genre,
                       f"제목 {len(generic)}개가 내용 없는 정형 이름이다(개요, 요약, 결론 등).",
                       sugg="제목에 그 절의 내용을 담는다.", text=generic[0][1]))
    return out


def doc_register(masked: str, sents: Sequence[Span], paras: Sequence[Span], genre: str) -> List[Finding]:
    """문서 전체에서 합니다체와 평어가 섞였다(문단 안 혼용은 ko.register.mixed가 찾는다)."""
    body = _body(masked, paras)
    elig = []
    for a, b in sents:
        seg = masked[a:b]
        if not any(p[0] <= a < p[1] for p in body) or re.search(r"[\"“”「」]", seg) or "|" in seg \
                or len(re.findall(r"[가-힣]", seg)) < 6:
            continue
        k = _register(seg)
        if k in ("polite", "plain"):
            elig.append((a, k))
    if len(elig) < 20:
        return []
    polite = sum(1 for _, k in elig if k == "polite")
    minority = "plain" if polite >= len(elig) - polite else "polite"
    n = len(elig) - polite if minority == "plain" else polite
    if n < 3 or n < 0.1 * len(elig):
        return []
    pos = next(a for a, k in elig if k == minority)
    return [_mk("ko.register.doc-mixed", "rhythm", "C", pos, pos, 0.4, genre,
                f"문서 전체 {len(elig)}문장 중 {n}문장({n / len(elig):.0%})이 다른 말투다(합니다체와 평어).", lang="ko",
                gmap={"literary": 0.3, "technical": 0.5},
                sugg="문서 종류에 맞는 말투 하나로 맞춘다. 의도한 섞임이면 그대로 둔다.")]


UNDEF_LABEL = re.compile(r"\b(?:[A-Z]{2,4}v\d+|[a-z]{1,4}\d{1,3}(?:-[a-z0-9]+){1,4}|[A-Z][A-Z0-9]*_[A-Z0-9_]{2,}|"
                         r"[A-Z][A-Z0-9_]{3,}\.md)\b")
LABEL_GLOSS = re.compile(r"(?:called|named|known as|so-called|라는|이라는|이라고|라고 부르는)[ \t\"'“‘]*$", re.I)


def opaque_labels(masked: str, genre: str) -> List[Finding]:
    """코드 밖 줄글에 정의 없이 쓰인 내부 이름(MAv2, q23-grades-strict, TAME_GUIDANCE, NOTES.md)이 여럿이다.
    쓴 사람은 알지만 독자는 모르는 이름이다. 처음 나올 때 풀이(called, 괄호)가 없는 것만 찾는다."""
    seen: Dict[str, int] = {}
    first = -1
    for m in UNDEF_LABEL.finditer(masked):
        lab = m.group(0)
        if lab in seen:
            seen[lab] += 1
            continue
        before = masked[max(0, m.start() - 24):m.start()]
        after = masked[m.end():m.end() + 4]
        if LABEL_GLOSS.search(before) or after.lstrip().startswith("("):
            continue
        seen[lab] = 1
        if first < 0:
            first = m.start()
    if len(seen) < 3 or sum(seen.values()) < 4:
        return []
    return [_mk("any.opaque.undefined-labels", "opaque", "C", first, first, 0.5, genre,
                f"처음 나올 때 풀이 없는 내부 이름이 {len(seen)}개다(예: {', '.join(list(seen)[:3])}). "
                "Internal names are used without ever being introduced.", gmap={"technical": 0.4},
                sugg="이름을 처음 쓸 때 무엇인지 한 줄로 풀거나, 이름 대신 실제 동작을 쓴다.", text=next(iter(seen)))]


_PRED_END = ("합니다|됩니다|했습니다|됐습니다|하였습니다|되었습니다|한다|된다|했다|됐다|하며|되며|하고|되고|하여|되어|하면서|되면서|"
             "시킵니다|시키며|시킨다")
_PRED = re.compile(r"(?<![가-힣])(?P<r>[가-힣]{2,6}?)(?P<e>" + _PRED_END + r")(?![가-힣])")
_FINAL = {"합니다", "됩니다", "했습니다", "됐습니다", "하였습니다", "되었습니다", "한다", "된다", "했다", "됐다"}
# 하다/되다 계열은 어간이 달라도('연결합니다', '유지됩니다') 같은 종결 어미로 읽히므로 한 묶음으로 센다.
_ENDING_CLASS = {"합니다": "~합니다/~됩니다", "됩니다": "~합니다/~됩니다", "했습니다": "~했습니다/~됐습니다",
                 "됐습니다": "~했습니다/~됐습니다", "하였습니다": "~했습니다/~됐습니다", "되었습니다": "~했습니다/~됐습니다",
                 "한다": "~한다/~된다", "된다": "~한다/~된다", "했다": "~했다/~됐다", "됐다": "~했다/~됐다"}


def predicate_repeat(masked: str, sents: Sequence[Span], genre: str) -> List[Finding]:
    """같은 서술어를 어미만 바꿔 잇달아 쓴다('유지되며 ... 유지됩니다'), 같은 종결 어미가 두 문장 연속된다."""
    out: List[Finding] = []
    ko = [sp for sp in sents if re.search(r"[가-힣]", masked[sp[0]:sp[1]])
          and not masked[sp[0]:sp[1]].lstrip().startswith(SKIP) and not LISTISH.match(masked[sp[0]:sp[1]])]
    prev_roots: List[str] = []
    prev_end = ""
    run = 1
    for a, b in ko:
        seg = masked[a:b]
        found = [(m.group("r"), m.group("e")) for m in _PRED.finditer(seg)]
        finals = [(r, e) for r, e in found if e in _FINAL]
        last_root, last_end = finals[-1] if finals and re.search(rf"{re.escape(finals[-1][1])}[^가-힣]*$", seg) else ("", "")
        if last_root:
            same_in = [r for r, e in found[:-1] if r == last_root]
            if same_in:
                out.append(_mk("ko.rhythm.verb-restate", "rhythm", "C", a, b, 0.35, genre,
                               f"한 문장에서 '{last_root}'를 어미만 바꿔 되풀이한다.", lang="ko", text=seg[:40],
                               sugg="앞 절은 다른 동사로 바꾸거나 한 번만 쓴다."))
            elif last_root in prev_roots:
                out.append(_mk("ko.rhythm.verb-restate", "rhythm", "C", a, b, 0.35, genre,
                               f"앞 문장에 나온 '{last_root}'를 어미만 바꿔 다시 쓴다.", lang="ko", text=seg[:40],
                               sugg="앞 문장과 합치거나 다른 동사로 바꾼다."))
        last_end = _ENDING_CLASS.get(last_end, "")
        if last_end and last_end == prev_end:
            run += 1
            if run == 2:
                out.append(_mk("ko.rhythm.pair-ending", "rhythm", "C", a, b, 0.2, genre,
                               f"같은 종결 어미('{last_end}')가 두 문장 연속된다(어간만 다르다).", lang="ko", text=seg[:40],
                               sugg="한쪽 문장의 구조나 종결 형태를 바꾼다."))
        else:
            run = 1
        prev_end = last_end
        prev_roots = [r for r, _ in found]
    return out


def signals(text: str, masked: str, sents: Sequence[Span], paras: Sequence[Span], units: int,
            genre: str) -> List[Finding]:
    return (label_colon(masked, genre) + english_gloss(masked, units, genre) + ko_commas(masked, genre) +
            synonym_cycling(masked, sents, paras, genre) + word_echo(masked, sents, paras, genre) + trace_word(masked, paras, genre) + self_reference(masked, genre) +
            rhythm_band(masked, sents, paras, genre) +
            punct_flat(masked, sents, paras, genre) + headings(masked, genre) +
            doc_register(masked, sents, paras, genre) + opaque_labels(masked, genre) +
            predicate_repeat(masked, sents, genre))
