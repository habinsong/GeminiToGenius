"""문장과 문장이 이어지는지 본다. 끊긴 단문의 연속과, 이어지는 말 없이 나열만 된 문단을 찾는다.

기존 신호는 접속어를 '많이 쓴 것'만 감점해서 윤문이 접속어를 지우고 문장을 쪼개는 쪽으로 쏠렸다.
이 모듈은 반대쪽, 곧 '이음이 없는 것'을 찾는다. 두 문장이 이어졌다고 보는 증거(bridge)는 셋이다.
  1. 문장 첫머리의 접속부사·접속사·종속접속사·순서어·연결 구(linkers.lead_link)
  2. 문장 첫머리의 대명사·지시어(성·수·격이 바뀐 형태까지)
  3. 앞 문장 끝의 말을 다음 문장 첫머리가 되받음(어순: 새 정보가 주제로 올라오는 자리)
언어는 문단마다 따로 가린다. 사전이 없는 언어(other)는 길이만 보고, 더 길게 이어져야 센다.
이 신호는 접속어를 넣으라는 명령이 아니고, 문장 사이에 실제 관계가 있을 때만 이어지는 말을 넣는다.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List, Optional, Sequence, Tuple

from . import linkers
from .model import Finding, weigh

Span = Tuple[int, int]
Link = Tuple[str, str]                       # (종류, 관계)
NIDA_RUN = 3                                 # '-니다'로 끝나는 문장이 접속부사 없이 이 수만큼 이어지면 센다
NIDA_LEN = 9                                 # 이 어절 수를 넘는 문장은 길다고 본다. 길이가 들쭉날쭉하거나 내내 긴 글은 사람의 호흡이므로 연속에 넣지 않는다
NIDA_SHORT = 3                               # '-니다' 문장 바로 뒤의 '-니다' 문장이 이 어절 수 이하이면 센다
EXPLICIT = ("adv", "conj", "ord", "sub")         # 앞 문장과 잇는 말로 치는 종류. 지시어와 되받음은 여기에 넣지 않는다
RUN_MIN = 3                                  # 끊긴 단문이 이만큼 이어지면 센다
RUN_MIN_OTHER = 5                            # 사전이 없는 언어는 더 길 때만
NOBRIDGE_MIN_SENTS = 5
NOBRIDGE_RATIO = 0.2
FLOOD_MIN_SENTS = 5                          # 접속어 도배: 실측에서 사람·AI 글 모두 문단의 1% 안팎만 0.75를 넘는다(docs/research.md 10절)
FLOOD_RATIO = 0.75
SKIP_START = ("#", ">", "|", "```", "<!--", "- ", "* ", "+ ", "1. ", "2. ", "3. ", "1) ", "2) ")
GENRE = {"literary": 0.3, "academic": 0.8, "technical": 0.4}   # 문학은 병치가 문체, 기술 문서는 명세·변경 이력이 짧은 문장이다
_KO_TAIL = re.compile(r"(?:에서는|으로는|에게는|까지는|에서도|으로도|에서|으로|에게|까지|부터|보다|처럼|마다|"
                      r"이며|이고|이다|입니다|이라|라는|라고|은|는|이|가|을|를|의|에|로|와|과|도|만|며|고)$")
_WEAK = {"which", "there", "their", "would", "could", "should", "about", "these", "those", "other", "where",
         "while", "being", "after", "before", "because", "again", "every", "still"}
_ZH_FUNC = set("的了是在和有也不就都与及而")
LANG_FACTOR = {"zh": 0.7}                    # 중국어는 접속어 없이 병치하는 의합이 기본이라 감점을 낮춘다


def _clean(seg: str) -> str:
    return re.sub(r"\x00+", "X", seg)


def _norm_tok(t: str) -> str:
    return t.strip(linkers._PUNCT).lower().replace("’", "'")


def _ko_stem(tok: str) -> str:
    t = _norm_tok(tok)
    m = _KO_TAIL.search(t)
    return t[: m.start()] if m and m.start() >= 2 else t


def carry_over(prev: str, cur: str, lang: str) -> bool:
    """앞 문장 끝의 말이 다음 문장 첫머리에 다시 나오면 True(주제를 받아 잇는 어순)."""
    if lang in ("ja", "zh"):
        a = [c for c in prev if c.isalnum()][-14:]
        b = [c for c in cur if c.isalnum()][:14]
        grams = lambda xs: {xs[i] + xs[i + 1] for i in range(len(xs) - 1)}  # noqa: E731
        for g in grams(a) & grams(b):
            if lang == "zh" and all(ch in _ZH_FUNC for ch in g):
                continue
            if lang == "ja" and all("぀" <= ch <= "ゟ" for ch in g):
                continue
            return True
        return False
    pt, ct = prev.split()[-5:], cur.split()[:4]
    if lang == "ko":
        pa = {s for s in map(_ko_stem, pt[-4:]) if len(s) >= 2}
        cb = [s for s in map(_ko_stem, ct[:3]) if len(s) >= 2]
        return any(x == y or (min(len(x), len(y)) >= 3 and (x.startswith(y) or y.startswith(x)))
                   for x in pa for y in cb)
    pa = {w[:5] for w in map(_norm_tok, pt) if len(w) >= 5 and w not in _WEAK}
    return any(w[:5] in pa for w in map(_norm_tok, ct) if len(w) >= 5 and w not in _WEAK)


def bridge(prev: str, cur: str, lang: str) -> Optional[Link]:
    """prev에서 cur로 이어지는 증거가 있으면 (종류, 관계). 없으면 None."""
    hit = linkers.lead_link(cur, lang)
    if hit:
        return hit[0], hit[1]
    return ("echo", "reference") if carry_over(prev, cur, lang) else None


def bridge_survives(masked: str, prev: Span, cur: Span, drop_end: int) -> bool:
    """cur 첫머리의 접속어(drop_end까지)를 지워도 다른 수단으로 앞 문장과 이어지는가. 지워도 되는지 가릴 때 쓴다."""
    lang = linkers.detect(masked[prev[0]:cur[1]])
    rest = masked[drop_end:cur[1]]
    return bridge(_clean(masked[prev[0]:prev[1]]), _clean(rest), lang) is not None


def _group(sents: Sequence[Span], paras: Sequence[Span]) -> List[List[Span]]:
    out: List[List[Span]] = []
    i, n = 0, len(sents)
    for ps, pe in paras:
        while i < n and sents[i][0] < ps:
            i += 1
        grp: List[Span] = []
        while i < n and sents[i][1] <= pe:
            grp.append(sents[i])
            i += 1
        out.append(grp)
    return out


def _ko_ending(s: str) -> str:
    """한국어 종결 형태의 서법·시제. 형태소 분석 없이 어미 끝으로 짐작한다."""
    core = re.sub(r"[^가-힣?]+$", "", s.strip())
    tail = core.rstrip("?")
    if s.rstrip().endswith("?") or re.search(r"(?:까|니|냐|나요|가요)$", tail):
        return "의문"
    if re.search(r"(?:세요|십시오|어라|아라|해라|하라|자|ㅂ시다|읍시다)$", tail):
        return "명령·청유"
    if not tail.endswith(("다", "요", "죠", "지", "네", "군", "음", "함", "임")):
        return "체언·연결 종결"
    if "겠" in tail[-4:-1]:
        return "평서·추측"
    past = any((ord(c) - 0xAC00) % 28 == 20 for c in tail[-5:-1] if "가" <= c <= "힣" and c not in "있없")
    return "평서·과거" if past else "평서·현재"


def _mk(rid: str, grade: str, start: int, end: int, w: float, genre: str, note: str, sugg: str, lang: str,
        text: str) -> Finding:
    return Finding(rule_id=rid, category="cohesion", grade=grade, start=start, end=end, text=text, line=0, col=0,
                   weight=round(weigh("cohesion", grade, w, GENRE, genre) * LANG_FACTOR.get(lang, 1.0), 4),
                   note=note, sugg=sugg, tier="none",
                   fixable=False, lang=lang if lang in ("ko", "en") else "any", edit=None)


def _sugg(lang: str, is_ko: bool) -> str:
    menu = linkers.menu(lang, "ko" if is_ko else "en", per=2)
    if is_ko:
        return (f"관계를 정해 이어지는 말로 잇는다({menu}). 같은 흐름이면 연결어미(-고, -는데, -지만)로 합치거나 "
                "앞 문장 끝의 말을 다음 문장 첫머리에서 받는다. 관계가 없으면 넣지 않는다.")
    return ("Name the relation and link it" + (f" ({menu})" if menu else "") +
            ", merge with a conjunction or subordinate clause, or open with the previous sentence's last noun. "
            "Add no connective where there is no relation.")


def signals(masked: str, sents: Sequence[Span], paras: Sequence[Span], genre: str
            ) -> Tuple[List[Finding], Dict[str, object]]:
    """끊긴 단문 연속과 이음 없는 문단의 검출 항목, 그리고 이음 현황(metrics)."""
    out: List[Finding] = []
    kinds: Counter = Counter()
    rels: Counter = Counter()
    endings: Counter = Counter()
    langs: Counter = Counter()
    pairs = bridged = shorts = total = flood = 0
    is_ko = bool(re.search(r"[가-힣]", masked))
    for grp, (ps, pe) in zip(_group(sents, paras), paras):
        head = masked[ps:pe].lstrip()
        if len(grp) < 2 or head.startswith(SKIP_START):
            continue
        texts = [_clean(masked[a:b]) for a, b in grp]
        if sum(1 for t in texts if re.search(r"[\"“”「」『』]", t)) * 10 > len(texts) * 3:
            continue                                   # 대화가 많은 문단은 짧은 문장이 문체다
        lang = linkers.detect(" ".join(texts))
        langs[lang] += len(texts)
        lens = [linkers.length_units(t, lang) for t in texts]
        short = [n <= linkers.SHORT[lang] for n in lens]
        links: List[Optional[Link]] = [None] + [bridge(texts[i - 1], texts[i], lang) for i in range(1, len(texts))]
        for lk in links[1:]:
            pairs += 1
            if lk:
                bridged += 1
                kinds[lk[0]] += 1
                rels[lk[1]] += 1
        total += len(texts)
        shorts += sum(short)
        if lang == "ko":
            endings.update(_ko_ending(t) for t in texts)
        sg = _sugg(lang, is_ko)
        explicit = sum(1 for lk in links[1:] if lk and lk[0] in ("adv", "conj", "sub"))
        if len(texts) >= FLOOD_MIN_SENTS and explicit >= FLOOD_RATIO * (len(texts) - 1):
            flood += 1
            note = (f"문단의 문장 {len(texts)}개 중 {explicit + 1}개 안팎이 접속어로 시작한다. 관계 없는 곳에 접속어를 붙이면 가짜 인과·반전이 된다."
                    if is_ko else f"{explicit} of {len(texts) - 1} sentence joins in this paragraph open with a connective; "
                    "connectives added where no relation exists create false cause or contrast.")
            out.append(_mk(f"{lang if lang in ('ko', 'en') else 'any'}.cohesion.flood", "C", grp[0][0], grp[0][1], 0.0, genre,
                           note, "관계가 실제로 있는 곳에만 남기고 나머지는 지운다.", lang, masked[grp[0][0]:grp[0][1]][:60]))
        need = linkers.RUN.get(lang, RUN_MIN) if lang != "other" else RUN_MIN_OTHER
        tiers = [(short, need)]
        if lang in linkers.TIER2:
            thr2, need2 = linkers.TIER2[lang]
            tiers.append(([n <= thr2 for n in lens], need2))
        seen_starts: set = set()
        runs = []
        for flags, req in tiers:
            i = 0
            while i < len(texts):
                if not flags[i]:
                    i += 1
                    continue
                j = i
                while j + 1 < len(texts) and flags[j + 1] and links[j + 1] is None:
                    j += 1
                if j - i + 1 >= req and not any(k in seen_starts for k in range(i, j + 1)):
                    runs.append((i, j))
                    seen_starts.update(range(i, j + 1))
                i = j + 1
        for i, j in sorted(runs):
            n = j - i + 1
            same = lang == "ko" and len({texts[k].rstrip(" .!?")[-1:] for k in range(i, j + 1)}) == 1 \
                and texts[i].rstrip(" .!?")[-1:] == "다"
            note = (f"짧은 문장 {n}개가 접속어·지시어·되받는 말 없이 이어져 문장 사이 관계가 드러나지 않는다"
                    + (" (모두 '-다'로 끝난다)." if same else ".")) if is_ko else \
                f"{n} short sentences in a row with no connective, demonstrative or carried-over term between them."
            out.append(_mk(f"{lang if lang in ('ko', 'en') else 'any'}.cohesion.choppy-run", "A" if lang == "ko" else "C", grp[i][0],
                           grp[i][1], 1.4 if lang == "ko" else 1.0, genre, note, sg, lang, masked[grp[i][0]:grp[j][1]][:60]))
        if lang == "ko":
            polite = [bool(re.search(r"니다$", re.sub(r"[^가-힣]+$", "", x))) for x in texts]
            joined = [bool(lk) and lk[0] in EXPLICIT for lk in links]     # 문장 첫머리의 접속부사·접속사·순서어
            brief = [p and n <= NIDA_LEN for p, n in zip(polite, lens)]  # 짧은 '-니다' 문장. 긴 문장이 끼면 연속이 끊긴다
            i = 0
            while i < len(texts):
                if not brief[i]:
                    i += 1
                    continue
                j = i
                while j + 1 < len(texts) and brief[j + 1] and not joined[j + 1]:
                    j += 1
                if j - i + 1 >= NIDA_RUN:
                    out.append(_mk("ko.cohesion.nida-run", "A", grp[i][0], grp[j][1],
                                   min(0.8 + 0.4 * (j - i + 1 - NIDA_RUN), 2.4), genre,
                                   f"'-니다'로 끝나는 문장 {j - i + 1}개가 접속부사 없이 짧게 이어진다. 길이가 달라지는 자리가 없다.",
                                   sg, lang, masked[grp[i][0]:grp[j][1]][:60]))
                i = j + 1
            for k in range(1, len(texts)):
                if brief[k - 1] and polite[k] and lens[k] <= NIDA_SHORT:
                    out.append(_mk("ko.cohesion.nida-short", "A", grp[k][0], grp[k][1], 0.8, genre,
                                   f"'-니다'로 끝난 문장 바로 뒤에 {lens[k]}어절짜리 '-니다' 문장이 온다. 짧은 문장 뒤에 또 짧은 문장이 붙었다.",
                                   sg, lang, masked[grp[k][0]:grp[k][1]][:60]))
        n = len(texts)
        if (lang != "other" and n >= NOBRIDGE_MIN_SENTS
                and sum(1 for lk in links[1:] if lk) <= NOBRIDGE_RATIO * (n - 1)
                and sum(lens) / n <= linkers.MEDIUM[lang]):
            b = sum(1 for lk in links[1:] if lk)
            note = (f"문단의 문장 {n}개 사이 {n - 1}곳 중 {b}곳만 이어진다(접속어·지시어·되받음). 나열처럼 읽힌다."
                    if is_ko else f"Only {b} of {n - 1} sentence joins in this paragraph carry a connective, "
                    "demonstrative or carried-over term; it reads as a list of facts.")
            out.append(_mk(f"{lang if lang in ('ko', 'en') else 'any'}.cohesion.no-bridge", "B" if lang == "ko" else "C", grp[-1][0],
                           grp[-1][1], 0.8, genre, note, sg, lang, masked[grp[-1][0]:grp[-1][1]][:60]))
    main = langs.most_common(1)[0][0] if langs else "other"
    profile: Dict[str, object] = {
        "language": main,
        "bridge_ratio": round(bridged / pairs, 2) if pairs else None,
        "short_share": round(shorts / total, 2) if total else None,
        "linkers_by_kind": dict(kinds),
        "linkers_by_relation": dict(rels),
        "ending_forms": dict(endings),
        "flood_paragraphs": flood,
    }
    return out, profile
