"""문서의 AI 문체 신호(상투구·과장·번역투·대구·도치·리듬·서식)를 줄 번호와 함께 찾습니다. 글의 판정이 아니라 고칠 곳의 목록입니다."""

from __future__ import annotations

import io
from pathlib import Path
import re

from .inspection import ChangedDuringRead, read_text, workspace_path
from .prose_patterns import Pattern
from .prose_registers import REGISTERS, rules
from .prose_rhythm import NOT_PROSE, finding, rhythm, sentences
from .prose_score import LIMITATIONS as SCORE_LIMITATIONS, score


MAX_BYTES = 1024 * 1024
MAX_FILES = 64
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"(`+)[^`\n]*?\1")
URL = re.compile(r"\b(?:https?|file)://\S+")
COMMENT = re.compile(r"<!--.*?-->")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
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


def phrases(path: str, lines: list[str], groups: list[list[int]], patterns: list[Pattern]) -> list[dict]:
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
        for items in grouped.values():
            if len(items) >= rule.minimum:
                index, match = items[0]
                found.append(finding(rule.id, rule.severity, path, index + 1, match.group(0), rule.hint,
                                     count=len(items), lines=[i + 1 for i, _ in items][:12]))
    return found


def examine(path: str, text: str, register: str = "general") -> tuple[list[dict], dict]:
    """찾은 신호와 분량입니다. 분량의 units는 산문 문장에 목록·제목 줄을 더한 값이고, 줄마다 끊어 쓴 시는 줄 수를 씁니다."""
    patterns, settings = rules(register)
    lines = visible(text)
    groups = paragraphs(lines)
    blocks = sentences(lines, groups)
    count = sum(len(items) for items in blocks)
    filled = [line for line in lines if line.strip()]
    units = max(count + sum(1 for line in filled if NOT_PROSE.match(line)), len(filled))
    return (phrases(path, lines, groups, patterns) + rhythm(path, blocks, settings),
            {"sentences": count, "units": units})


def check(root: Path, paths: list[str], register: str = "general", min_score: int | None = None) -> dict:
    """문서마다 신호와 점수를 모읍니다. min_score를 주면 그보다 낮은 문서가 하나라도 있을 때 통과하지 않습니다."""
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("작업공간 폴더가 필요합니다.")
    if not paths or len(paths) > MAX_FILES:
        raise ValueError(f"한 번에 1~{MAX_FILES}개 문서를 지정하세요.")
    if min_score is not None and not 0 <= min_score <= 100:
        raise ValueError("기준 점수는 0~100 사이여야 합니다.")
    rules(register)
    files, findings, units = [], [], 0
    for value in paths:
        entry = {"path": value, "status": "ok"}
        try:
            name = workspace_path(root, value)
            entry["path"] = name.as_posix()
            text = read_text(root, name, MAX_BYTES)
            if text is None:
                entry["status"] = "binary_large_or_encoding"
            else:
                found, measure = examine(entry["path"], text, register)
                entry["sentences"] = measure["sentences"]
                entry["score"] = score(found, measure["units"])
                findings += found
                units += measure["units"]
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
    scored = [entry["score"]["value"] for entry in files if "score" in entry]
    below = [entry["path"] for entry in files
             if min_score is not None and "score" in entry and entry["score"]["value"] < min_score]
    return {"kind": "prose_check", "workspace": str(root), "register": register, "files": files,
            "findings": findings, "blocking": blocking, "review": len(findings) - blocking,
            "score": score(findings, units) if scored else None, "lowest_score": min(scored, default=None),
            "min_score": min_score, "below_min_score": below,
            "all_files_read": readable, "passed": readable and blocking == 0 and not below,
            "limitations": LIMITATIONS + " " + SCORE_LIMITATIONS, "registers": sorted(REGISTERS)}
