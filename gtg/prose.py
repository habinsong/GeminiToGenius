"""문서의 AI 문체 신호(상투구·과장·번역투·대구·도치·리듬·서식)를 줄 번호와 함께 찾습니다. 글의 판정이 아니라 고칠 곳의 목록입니다."""

from __future__ import annotations

import math
from pathlib import Path
import re

from .prose_fidelity import compare
from .prose_input import MAX_FILES, given, load
from .prose_patterns import Pattern
from .prose_registers import REGISTERS, rules
from .prose_rhythm import finding, rhythm, sentences, volume
from .prose_score import LIMITATIONS as SCORE_LIMITATIONS, UNSCORED, score


# 문서 전체·한 문단 안의 최소 횟수는 이 분량(문장)의 글에 맞춰 잰 값입니다. 더 긴 글은 기준을 비례해 늘려야
# 긴 문서가 글 길이만으로 경고를 쏟아내지 않습니다. KatFish 에세이는 중앙 11~17문장, 문단은 대개 3~6문장입니다.
DOCUMENT_REFERENCE = 20
PARAGRAPH_REFERENCE = 6
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"(`+)[^`\n]*?\1")
URL = re.compile(r"\b(?:https?|file)://\S+")
COMMENT = re.compile(r"<!--.*?-->")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
# 목록 항목과 표 행은 서로 이어지는 글이 아니므로 문단 단위 규칙(대구 연쇄 등)에서 각각 따로 셉니다.
ITEM = re.compile(r"^\s{0,3}(?:[-*+]|\d+[.)])\s|^\s*\|")
LIMITATIONS = ("표현 목록과 문장 길이로 찾는 신호입니다. 통과가 자연스러운 글을 보장하지 않고, 검토 신호가 틀린 글을 뜻하지도 "
               "않습니다. 코드 블록·인라인 코드·URL은 보지 않으며 내용의 사실 여부는 확인하지 않습니다.")
FIDELITY_LIMITATIONS = ("윤문 전후 비교는 수치·인용·URL·코드·영문 표기가 남았는지와 바뀐 단어 비율만 봅니다. 의미가 같은지, "
                        "고친 글이 더 나은지는 판정하지 않습니다.")


def visible(text: str) -> list[str]:
    """머리말·코드 블록·인라인 코드·URL·HTML 주석을 비운 줄 목록입니다. 줄 번호는 원문과 같습니다."""
    lines = text.splitlines()
    front = bool(lines) and lines[0].strip() == "---" and any(line.strip() == "---" for line in lines[1:])
    shown, fence = [], None
    for index, line in enumerate(lines):
        if front:
            shown.append("")
            front = not (index > 0 and line.strip() == "---")
            continue
        match = FENCE.match(line)
        if fence or match:
            shown.append("")
            if fence is None:
                fence = match.group(1)
            elif match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
                fence = None
            continue
        shown.append(COMMENT.sub(" ", URL.sub(" ", INLINE_CODE.sub(" ", line))))
    return shown


def paragraphs(lines: list[str]) -> list[list[int]]:
    """빈 줄과 제목으로 나눈 문단입니다. 목록 항목과 표 행은 각각 한 문단이고, 항목에 이어 쓴 줄은 그 항목에 붙습니다.
    각 문단은 줄 번호(0부터) 목록입니다."""
    groups, current = [], []
    for index, line in enumerate(lines):
        if line.strip() and not HEADING.match(line):
            if current and ITEM.match(line):
                groups.append(current)
                current = []
            current.append(index)
            continue
        if current:
            groups.append(current)
            current = []
        if line.strip():
            groups.append([index])
    if current:
        groups.append(current)
    return groups


def paragraph_sizes(groups: list[list[int]], blocks: list[list[tuple[int, str]]]) -> dict[int, int]:
    """문단 번호별 문장 수입니다."""
    owner = {index: number for number, group in enumerate(groups) for index in group}
    sizes = {}
    for items in blocks:
        for line, _ in items:
            number = owner.get(line - 1)
            if number is not None:
                sizes[number] = sizes.get(number, 0) + 1
    return sizes


def required(rule: Pattern, key: int, units: int, sizes: dict[int, int], verse: bool) -> int:
    """글 분량에 맞춘 최소 횟수입니다. 짧은 글은 규칙의 기본값 그대로, 긴 글은 분량에 비례해 늘립니다.

    시는 분량 단위가 문장이 아니라 행이라 환산이 맞지 않으므로 늘리지 않습니다. 환산했을 때 KatFish 시의 판별력이
    떨어졌고(AUC 0.669 → 0.652), 행 끝 쉼표처럼 행마다 세는 규칙이 희석됐습니다. 차단 규칙도 늘리지 않습니다.
    경고 폭주를 줄이려는 보정이 한 문단의 대구 연쇄처럼 가장 엄격하게 막기로 한 신호를 긴 문단에서 놓치면 안 됩니다."""
    if verse or rule.severity == "block":
        return rule.minimum
    scale = units / DOCUMENT_REFERENCE if rule.scope == "document" else sizes.get(key, 0) / PARAGRAPH_REFERENCE
    return max(rule.minimum, math.floor(rule.minimum * scale + 0.5))


def phrases(path: str, lines: list[str], groups: list[list[int]], patterns: list[Pattern],
            units: int, sizes: dict[int, int], verse: bool = False) -> list[dict]:
    owner = {index: number for number, group in enumerate(groups) for index in group}
    found = []
    for rule in patterns:
        hits = [(index, match) for index, line in enumerate(lines) if line.strip()
                for match in rule.regex.finditer(line)]
        if rule.scope == "match":
            found += [finding(rule.id, rule.severity, path, index + 1, match.group(0), rule.hint)
                      for index, match in hits]
            continue
        grouped = {}
        for index, match in hits:
            key = owner.get(index, -1) if rule.scope == "paragraph" else 0
            grouped.setdefault(key, []).append((index, match))
        for key, items in grouped.items():
            if len(items) >= required(rule, key, units, sizes, verse):
                index, match = items[0]
                found.append(finding(rule.id, rule.severity, path, index + 1, match.group(0), rule.hint,
                                     count=len(items), lines=[i + 1 for i, _ in items][:12]))
    return found


def examine(path: str, text: str, register: str = "general") -> tuple[list[dict], dict]:
    """찾은 신호와 분량입니다. units는 점수의 분모(산문 문장에 목록·제목 줄을 더한 값, 시는 줄 수)이고
    unscored는 이 갈래에서 알리기만 하고 점수에서 빼는 신호입니다."""
    patterns, settings = rules(register)
    lines = visible(text)
    groups = paragraphs(lines)
    blocks = sentences(lines, groups)
    units = volume(lines, groups, blocks, settings.verse)
    found = (phrases(path, lines, groups, patterns, units, paragraph_sizes(groups, blocks), settings.verse)
             + rhythm(path, blocks, settings))
    return found, {"sentences": sum(len(items) for items in blocks), "units": units,
                   "unscored": UNSCORED | settings.unscored}


def compared(root: Path, original: str, name: str, polished: str | None) -> tuple[dict, list[dict]]:
    """윤문 전후 비교 결과입니다. 어느 쪽이든 읽지 못하면 이유만 담고 통과시키지 않습니다."""
    before_name, before, status = load(root, original)
    if before is None or polished is None:
        return {"original": before_name, "status": status if before is None else "polished_unreadable"}, []
    summary, found = compare(before, polished, name)
    return {"original": before_name, "status": "ok", **summary}, found


def check(root: Path, paths: list[str], register: str = "general", min_score: int | None = None, *,
          texts: tuple = (), original: str | None = None) -> dict:
    """문서마다 신호와 점수를 모읍니다. min_score를 주면 그보다 낮은 문서가 하나라도 있을 때 통과하지 않습니다.

    texts는 (표시 이름, 본문) 목록으로 파일이 아닌 글(채팅 답변 등)을 바로 검사합니다. original을 주면 문서 하나를
    윤문본으로 보고 이 원문과 견줘 수치·인용이 남았는지, 얼마나 고쳤는지도 확인합니다."""
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("작업공간 폴더가 필요합니다.")
    if not 1 <= len(paths) + len(texts) <= MAX_FILES:
        raise ValueError(f"한 번에 1~{MAX_FILES}개 문서를 지정하세요.")
    if min_score is not None and not 0 <= min_score <= 100:
        raise ValueError("기준 점수는 0~100 사이여야 합니다.")
    if original is not None and len(paths) + len(texts) != 1:
        raise ValueError("윤문 전후 비교는 윤문한 문서 하나와 함께 씁니다.")
    rules(register)
    loaded = [load(root, value) for value in paths]
    loaded += [given(label, text) for label, text in texts]
    files, findings, units, unscored, polished = [], [], 0, set(), None
    for name, text, status in loaded:
        entry = {"path": name, "status": status}
        if text is not None:
            found, measure = examine(name, text, register)
            entry["sentences"] = measure["sentences"]
            entry["score"] = score(found, measure["units"], measure["unscored"])
            findings += found
            units += measure["units"]
            unscored |= measure["unscored"]
            polished = text
        files.append(entry)
    fidelity, extra = compared(root, original, files[0]["path"], polished) if original is not None else (None, [])
    blocking = sum(1 for f in findings + extra if f["severity"] == "block")
    readable = all(entry["status"] == "ok" for entry in files) and (fidelity is None or fidelity["status"] == "ok")
    scored = [entry["score"]["value"] for entry in files if "score" in entry]
    below = [entry["path"] for entry in files
             if min_score is not None and "score" in entry and entry["score"]["value"] < min_score]
    limitations = LIMITATIONS + " " + SCORE_LIMITATIONS + (" " + FIDELITY_LIMITATIONS if fidelity else "")
    return {"kind": "prose_check", "workspace": str(root), "register": register, "files": files,
            "findings": findings + extra, "blocking": blocking, "review": len(findings + extra) - blocking,
            "score": score(findings, units, frozenset(unscored)) if scored else None,
            "lowest_score": min(scored, default=None), "min_score": min_score, "below_min_score": below,
            "fidelity": fidelity, "all_files_read": readable, "passed": readable and blocking == 0 and not below,
            "limitations": limitations, "registers": sorted(REGISTERS)}
