"""문서의 AI 문체 신호(상투구·과장·번역투·리듬·서식)를 줄 번호와 함께 찾습니다. 글의 판정이 아니라 고칠 곳의 목록입니다."""

from __future__ import annotations

import bisect
import io
from pathlib import Path
import re
import statistics

from .inspection import ChangedDuringRead, read_text, workspace_path
from .prose_patterns import PATTERNS


MAX_BYTES = 1024 * 1024
MAX_FILES = 64
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"(`+)[^`\n]*?\1")
URL = re.compile(r"\b(?:https?|file)://\S+")
COMMENT = re.compile(r"<!--.*?-->")
# 제목·목록·표·인용·HTML 줄은 리듬 측정에서 뺍니다. 문장으로 이어 읽는 산문이 아니기 때문입니다.
NOT_PROSE = re.compile(r"^\s*(?:#{1,6}\s|[-*+]\s|\d+[.)]\s|\||>|<)")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
SENTENCE = re.compile(r"(?<=[.!?])\s+")
HANGUL = re.compile(r"[가-힣]")
LATIN = re.compile(r"[A-Za-z]")
TRAIL = re.compile(r"[\s.!?…\"'”’)\]]+$")
# 한국어는 공백을 뺀 글자 수, 영어는 단어 수입니다.
SHORT = {"ko": 20, "en": 7}
LONG = {"ko": 70, "en": 28}
SAME_ENDING_RUN = 5
SHORT_RUN = 4
MONOTONE_SENTENCES = 15
MONOTONE_VARIATION = 0.35
LIMITATIONS = ("표현 목록과 문장 길이로 찾는 신호입니다. 통과가 자연스러운 글을 보장하지 않고, 검토 신호가 틀린 글을 뜻하지도 "
               "않습니다. 코드 블록·인라인 코드·URL은 보지 않으며 내용의 사실 여부는 확인하지 않습니다.")


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
    """빈 줄과 제목으로 나눈 문단입니다. 각 문단은 줄 번호(0부터) 목록입니다."""
    groups, current = [], []
    for index, line in enumerate(lines):
        if line.strip() and not HEADING.match(line):
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


def language(sentence: str) -> str | None:
    korean, latin = len(HANGUL.findall(sentence)), len(LATIN.findall(sentence))
    if korean and korean >= latin:
        return "ko"
    return "en" if latin else None


def length(sentence: str, lang: str) -> int:
    return len(re.sub(r"\s", "", sentence)) if lang == "ko" else len(sentence.split())


def sentences(lines: list[str], groups: list[list[int]]) -> list[list[tuple[int, str]]]:
    """산문 줄을 이어 문장으로 나눕니다. 연속한 산문 줄 묶음마다 (시작 줄 번호, 문장) 목록을 돌려줍니다."""
    blocks = []
    for group in groups:
        run = []
        for index in group + [None]:
            if index is not None and lines[index].strip() and not NOT_PROSE.match(lines[index]):
                run.append(index)
                continue
            if run:
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
            run = []
    return blocks


def finding(rule: str, severity: str, path: str, line: int, excerpt: str, hint: str, **measure) -> dict:
    return {"id": rule, "severity": severity, "path": path, "line": line, "excerpt": excerpt.strip()[:100],
            "hint": hint, "measure": measure}


def phrases(path: str, lines: list[str], groups: list[list[int]]) -> list[dict]:
    owner = {index: number for number, group in enumerate(groups) for index in group}
    found = []
    for rule in PATTERNS:
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
        for items in grouped.values():
            if len(items) >= rule.minimum:
                index, match = items[0]
                found.append(finding(rule.id, rule.severity, path, index + 1, match.group(0), rule.hint,
                                     count=len(items), lines=[i + 1 for i, _ in items][:12]))
    return found


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


def rhythm(path: str, blocks: list[list[tuple[int, str]]]) -> list[dict]:
    found, measured = [], {"ko": [], "en": []}
    for items in blocks:
        for run in runs(items, ending):
            if len(run) >= SAME_ENDING_RUN:
                found.append(finding("rhythm-same-ending", "review", path, run[0][0], run[0][1],
                                     f"'~{ending(run[0][1])}'로 끝나는 문장이 {len(run)}번 이어집니다. 문장을 잇거나 어미를 바꾸세요.",
                                     count=len(run)))
        for run in runs(items, short):
            if len(run) >= SHORT_RUN:
                found.append(finding("rhythm-choppy", "review", path, run[0][0], run[0][1],
                                     f"짧은 문장이 {len(run)}개 연달아 끊깁니다. 이어지는 내용은 연결어미로 묶으세요. "
                                     "/ Short sentences in a row; join the ones that belong together.", count=len(run)))
        for _, sentence in items:
            lang = language(sentence)
            if lang:
                measured[lang].append(length(sentence, lang))
    lang = max(measured, key=lambda name: len(measured[name]))
    values = measured[lang]
    if len(values) >= MONOTONE_SENTENCES:
        variation = statistics.pstdev(values) / statistics.mean(values)
        if variation < MONOTONE_VARIATION and max(values) < LONG[lang]:
            first = next((items[0][0] for items in blocks if items), 1)
            found.append(finding("rhythm-monotone", "review", path, first, "",
                                 "문장 길이가 고르고 긴 문장이 없습니다. 짧은 문장과 이어진 긴 문장을 섞으세요. "
                                 "/ Sentence lengths are uniform; vary them.",
                                 sentences=len(values), variation=round(variation, 3), longest=max(values)))
    return found


def examine(path: str, text: str) -> tuple[list[dict], int]:
    lines = visible(text)
    groups = paragraphs(lines)
    blocks = sentences(lines, groups)
    return phrases(path, lines, groups) + rhythm(path, blocks), sum(len(items) for items in blocks)


def check(root: Path, paths: list[str]) -> dict:
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("작업공간 폴더가 필요합니다.")
    if not paths or len(paths) > MAX_FILES:
        raise ValueError(f"한 번에 1~{MAX_FILES}개 문서를 지정하세요.")
    files, findings = [], []
    for value in paths:
        entry = {"path": value, "status": "ok"}
        try:
            name = workspace_path(root, value)
            entry["path"] = name.as_posix()
            text = read_text(root, name, MAX_BYTES)
            if text is None:
                entry["status"] = "binary_large_or_encoding"
            else:
                found, count = examine(entry["path"], text)
                entry["sentences"] = count
                findings += found
        except ChangedDuringRead:
            entry["status"] = "changed_during_read"
        except FileNotFoundError:
            entry["status"] = "missing"
        except io.UnsupportedOperation:
            entry["status"] = "not_regular"
        except NotImplementedError:
            entry["status"] = "unsupported_platform"
        except (OSError, ValueError):
            entry["status"] = "denied"
        files.append(entry)
    blocking = sum(1 for f in findings if f["severity"] == "block")
    readable = all(entry["status"] == "ok" for entry in files)
    return {"kind": "prose_check", "workspace": str(root), "files": files, "findings": findings,
            "blocking": blocking, "review": len(findings) - blocking, "all_files_read": readable,
            "passed": readable and blocking == 0, "limitations": LIMITATIONS}
