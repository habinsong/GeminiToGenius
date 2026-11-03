"""문장 단위의 리듬과 높임 신호를 잽니다. 표현 목록 검사는 prose.py가 맡습니다.

같은 어미 반복, 짧은 문장 연쇄, 고른 문장 길이, 같은 첫머리 반복(대구), 쉼표 과다, 높임 등급의 혼용과
한 가지 어미만 이어지는 경어체를 봅니다. 모두 고칠 곳을 알리는 검토 신호이며 판정이 아닙니다.
"""

from __future__ import annotations

import bisect
import re
import statistics

from .prose_registers import Register


# 제목·목록·표·인용·HTML 줄은 리듬 측정에서 뺍니다. 문장으로 이어 읽는 산문이 아니기 때문입니다.
NOT_PROSE = re.compile(r"^\s*(?:#{1,6}\s|[-*+]\s|\d+[.)]\s|\||>|<)")
# 닫는 따옴표 뒤에서도 끊습니다. '"가자." 그가 말했다.'는 대사와 서술 두 문장입니다.
SENTENCE = re.compile(r"(?<=[.!?])\s+|(?<=[.!?][\"'”’」』])\s+")
HANGUL = re.compile(r"[가-힣]")
LATIN = re.compile(r"[A-Za-z]")
TRAIL = re.compile(r"[\s.!?…\"'”’)\]]+$")
# 줄이 문장 부호로 끝나는지 봅니다. 닫는 따옴표·괄호 뒤의 부호도 인정합니다.
TERMINAL = re.compile(r"[.!?…。][\"'”’)\]」』]*\s*$")
EDGE = re.compile(r"^[\"'“‘(\[]+|[,.!?…\"'”’)\]]+$")
QUOTES = re.compile(r"[\"“”‘’「」『』]")
# 일상 대화체에서 사람이 섞어 쓰는 해요체 어미입니다. 이것 없이 '~요.'만 이어지면 단조롭습니다.
SPOKEN = re.compile(r"(?:거든요|더라고요|잖아요|네요|죠|는데요|나요|군요|던데요|라서요|걸요|래요|게요)$")
# 시의 행은 대개 공백을 뺀 이 글자 수 이하입니다.
VERSE_LINE = 30
# 한국어는 공백을 뺀 글자 수, 영어는 단어 수입니다.
SHORT = {"ko": 20, "en": 7}
LONG = {"ko": 70, "en": 28}
SAME_ENDING_RUN = 5
OPENING_RUN = 3
MONOTONE_SENTENCES = 15
MONOTONE_VARIATION = 0.35
# 쉼표가 든 문장 비율은 LLM 한국어가 사람보다 훨씬 높다고 보고됐습니다(KatFishNet, ACL 2025).
COMMA_SENTENCES = 10
COMMA_SHARE = 0.5
# 높임 신호는 문장이 이만큼 모였을 때만 봅니다. 짧은 글의 어미 몇 개로 글 전체를 판단하지 않기 위해서입니다.
FORMAL_SENTENCES = 10
FORMAL_SHARE = 0.9
HAEYO_SENTENCES = 8
# 초록은 서너 문장이라 학술문의 높임은 세 문장부터 봅니다.
HAERA_SENTENCES = 3
HAERA_SHARE = 0.5


def finding(rule: str, severity: str, path: str, line: int, excerpt: str, hint: str, **measure) -> dict:
    return {"id": rule, "severity": severity, "path": path, "line": line, "excerpt": excerpt.strip()[:100],
            "hint": hint, "measure": measure}


def language(sentence: str) -> str | None:
    korean, latin = len(HANGUL.findall(sentence)), len(LATIN.findall(sentence))
    if korean and korean >= latin:
        return "ko"
    return "en" if latin else None


def length(sentence: str, lang: str) -> int:
    return len(re.sub(r"\s", "", sentence)) if lang == "ko" else len(sentence.split())


def prose_runs(lines: list[str], groups: list[list[int]]) -> list[list[int]]:
    """문단 안에서 제목·목록·표가 아닌 줄이 이어지는 구간입니다. 각 구간은 줄 번호(0부터) 목록입니다."""
    found = []
    for group in groups:
        run = []
        for index in group + [None]:
            if index is not None and lines[index].strip() and not NOT_PROSE.match(lines[index]):
                run.append(index)
                continue
            if run:
                found.append(run)
            run = []
    return found


def sentences(lines: list[str], groups: list[list[int]]) -> list[list[tuple[int, str]]]:
    """산문 줄을 이어 문장으로 나눕니다. 산문 구간마다 (시작 줄 번호, 문장) 목록을 돌려줍니다."""
    blocks = []
    for run in prose_runs(lines, groups):
        text, offsets = "", []
        for line in run:
            offsets.append(len(text))
            text += lines[line].strip() + " "
        position, items = 0, []
        for piece in SENTENCE.split(text):
            piece = piece.strip()
            if not piece:
                continue
            at = text.find(piece, position)
            position = at + len(piece)
            items.append((run[bisect.bisect_right(offsets, at) - 1] + 1, piece))
        blocks.append(items)
    return blocks


def verse_like(lines: list[str], run: list[int]) -> bool:
    """행이 짧아 시로 볼 수 있는 구간입니다. 접어 쓴 산문은 행이 더 깁니다."""
    widths = sorted(len(re.sub(r"\s", "", lines[index])) for index in run)
    return widths[len(widths) // 2] <= VERSE_LINE


def volume(lines: list[str], groups: list[list[int]], blocks: list[list[tuple[int, str]]], verse: bool = False) -> int:
    """점수의 분모가 되는 분량입니다. 산문은 문장 수, 제목·목록 줄은 한 줄에 하나로 셉니다.

    한 문장을 여러 줄에 걸쳐 접어 쓴 산문은 줄이 아니라 문장으로 세야 분량이 부풀지 않습니다. 마침표가 하나도 없는
    구간이나 행이 짧은 시(verse 갈래)는 줄이 곧 호흡 단위이므로 줄 수를 씁니다.
    """
    total = sum(1 for line in lines if line.strip() and NOT_PROSE.match(line))
    for run, items in zip(prose_runs(lines, groups), blocks):
        ended = any(TERMINAL.search(lines[index]) for index in run)
        by_line = not ended or (verse and verse_like(lines, run))
        total += max(len(items), len(run)) if by_line else len(items)
    return total


def runs(items: list[tuple[int, str]], key) -> list[list[tuple[int, str]]]:
    """key 값이 None이 아니고 같은 문장이 이어지는 구간들입니다."""
    found, current, previous = [], [], None
    for item in items:
        value = key(item[1])
        if value is not None and value == previous:
            current.append(item)
        else:
            if len(current) > 1:
                found.append(current)
            current = [item] if value is not None else []
        previous = value
    if len(current) > 1:
        found.append(current)
    return found


def ending(sentence: str) -> str | None:
    tail = TRAIL.sub("", sentence)
    return tail[-3:] if language(sentence) == "ko" and len(tail) >= 3 and HANGUL.match(tail[-1]) else None


def short(sentence: str) -> bool | None:
    lang = language(sentence)
    return True if lang and length(sentence, lang) < SHORT[lang] else None


def opening(sentence: str) -> str | None:
    """한국어 문장의 첫 어절입니다. 같은 첫머리로 문장을 줄줄이 시작하는 대구를 찾을 때 씁니다."""
    words = sentence.split()
    word = EDGE.sub("", words[0]) if words else ""
    return word if language(sentence) == "ko" and HANGUL.search(word) else None


def level(sentence: str) -> str | None:
    """서술문의 높임 등급입니다. 인용이 든 문장은 등장인물이나 인용문의 말이라 셈하지 않습니다."""
    if QUOTES.search(sentence) or language(sentence) != "ko":
        return None
    tail = TRAIL.sub("", sentence)
    if tail.endswith(("니다", "니까")):
        return "hapsyo"
    if tail.endswith("요") or SPOKEN.search(tail):
        return "haeyo"
    return "haera" if tail.endswith("다") else None


def formality(path: str, blocks: list[list[tuple[int, str]]], mode: str | None) -> list[dict]:
    if mode is None:
        return []
    found = []
    for items in blocks:
        levels = {level(sentence) for _, sentence in items}
        if {"hapsyo", "haera"} <= levels:
            found.append(finding("register-mixed", "review", path, items[0][0], items[0][1],
                                 "한 문단에서 '~습니다'체와 '~다'체가 섞였습니다. 하나로 맞추세요."))
    flat = [sentence for items in blocks for _, sentence in items]
    counted = [value for value in map(level, flat) if value]
    first = next((items[0][0] for items in blocks if items), 1)
    if mode == "haera" and len(counted) >= HAERA_SENTENCES and counted.count("hapsyo") / len(counted) >= HAERA_SHARE:
        found.append(finding("register-academic-formal", "review", path, first, "",
                             "논문과 보고서 본문은 보통 '~다'체(해라체)로 씁니다.",
                             share=round(counted.count("hapsyo") / len(counted), 2)))
    if mode != "conversational":
        return found
    if len(counted) >= FORMAL_SENTENCES and counted.count("hapsyo") / len(counted) >= FORMAL_SHARE:
        found.append(finding("register-uniform-formal", "review", path, first, "",
                             "일상 글인데 거의 모든 문장이 '~니다'로 끝납니다. 상대와 상황에 맞는 '~요'체를 섞으세요.",
                             share=round(counted.count("hapsyo") / len(counted), 2)))
    polite = [TRAIL.sub("", sentence) for sentence in flat if level(sentence) == "haeyo"]
    if len(polite) >= HAEYO_SENTENCES and not any(SPOKEN.search(sentence) for sentence in polite):
        found.append(finding("register-uniform-haeyo", "review", path, first, "",
                             "'~요'로만 끝나는 문장이 이어집니다. '~거든요', '~더라고요', '~네요', '~죠'처럼 말할 때 쓰는 어미를 섞으세요.",
                             sentences=len(polite)))
    return found


def rhythm(path: str, blocks: list[list[tuple[int, str]]], register: Register) -> list[dict]:
    found, measured, commas = [], {"ko": [], "en": []}, []
    for items in blocks:
        for run in runs(items, ending):
            if len(run) >= SAME_ENDING_RUN:
                found.append(finding("rhythm-same-ending", "review", path, run[0][0], run[0][1],
                                     f"'~{ending(run[0][1])}'로 끝나는 문장이 {len(run)}번 이어집니다. 문장을 잇거나 어미를 바꾸세요.",
                                     count=len(run)))
        for run in runs(items, opening):
            if len(run) >= OPENING_RUN:
                found.append(finding("rhythm-repeated-opening", "review", path, run[0][0], run[0][1],
                                     f"'{opening(run[0][1])}'로 시작하는 문장이 {len(run)}번 이어지는 대구입니다. 주어를 생략하거나 문장을 이으세요.",
                                     count=len(run)))
        if register.short_run:
            for run in runs(items, short):
                if len(run) >= register.short_run:
                    found.append(finding("rhythm-choppy", "review", path, run[0][0], run[0][1],
                                         f"짧은 문장이 {len(run)}개 연달아 끊깁니다. 이어지는 내용은 연결어미로 묶으세요. "
                                         "/ Short sentences in a row; join the ones that belong together.", count=len(run)))
        for _, sentence in items:
            lang = language(sentence)
            if lang:
                measured[lang].append(length(sentence, lang))
            if lang == "ko":
                commas.append("," in sentence)
    first = next((items[0][0] for items in blocks if items), 1)
    lang = max(measured, key=lambda name: len(measured[name]))
    values = measured[lang]
    if register.monotone and len(values) >= MONOTONE_SENTENCES:
        variation = statistics.pstdev(values) / statistics.mean(values)
        if variation < MONOTONE_VARIATION and max(values) < LONG[lang]:
            found.append(finding("rhythm-monotone", "review", path, first, "",
                                 "문장 길이가 고르고 긴 문장이 없습니다. 짧은 문장과 이어진 긴 문장을 섞으세요. "
                                 "/ Sentence lengths are uniform; vary them.",
                                 sentences=len(values), variation=round(variation, 3), longest=max(values)))
    if len(commas) >= COMMA_SENTENCES and sum(commas) / len(commas) >= COMMA_SHARE:
        found.append(finding("rhythm-comma-heavy", "review", path, first, "",
                             "쉼표가 든 문장이 절반을 넘습니다. 연결어미 뒤나 짧은 절 사이의 쉼표는 빼도 읽힙니다.",
                             share=round(sum(commas) / len(commas), 2)))
    return found + formality(path, blocks, register.formality)
