from __future__ import annotations

import json
import re
from pathlib import Path


DOCUMENTATION_PATH_RE = re.compile(
    r"(?:README(?:\.[A-Za-z0-9_.-]+)?|CHANGELOG(?:\.[A-Za-z0-9_.-]+)?|"
    r"CONTRIBUTING(?:\.[A-Za-z0-9_.-]+)?|(?:^|/)docs?(?=$|[^A-Za-z0-9_/-])|\.mdx?\b)",
    re.IGNORECASE,
)
DOCUMENTATION_READER_RE = re.compile(
    r"(?:\b(?:cat|head|tail|sed|awk|nl|less|more|bat|rg|grep|read|open|inspect|"
    r"analy[sz]e|explore|list(?:[_ -]?directory|[_ -]?files)?|directory|folder|workspace)\b|"
    r"\bgit\s+(?:show|diff|grep|log)\b|"
    r"\b(?:python3?|pypy3?|node|ruby|perl)\b[^\n]*(?:open\s*\(|read_text\b|"
    r"readFile(?:Sync)?\s*\(|File\.read\b))",
    re.IGNORECASE,
)
WORKSPACE_EXPLORER_RE = re.compile(
    r"(?:\banaly[sz]e(?:\b|[_-])|\bexplor(?:e|ing)(?:\b|[_-])|\bscan\b|\bindex\b|"
    r"\blist(?:[_ -]?(?:directory|files?|tree))?\b|\b(?:file|workspace|directory|folder)[_-]?(?:tree|map|index|overview)\b|"
    r"\b(?:get|read)[_-]?(?:workspace|file[_-]?tree|directory)\b)",
    re.IGNORECASE,
)
SHELL_WORKSPACE_EXPLORER_RE = re.compile(
    r"(?:^|[;&|]\s*|\b(?:env|command)\s+)"
    r"(?:find|ls|tree|fd|fdfind|exa|eza)\b|"
    r"\b(?:rg|grep)\b[^\n]*(?:--files\b|-l\b|--files-with-matches\b)|"
    r"\bgit\s+(?:ls-files|ls-tree)\b|"
    r"\b(?:os\.walk|os\.listdir|Path\([^\n]*\)\.(?:glob|rglob)|glob\.glob|readdir)\b",
    re.IGNORECASE,
)


def reads_documentation(command: str) -> bool:
    """Return whether a shell command is trying to inspect Markdown/docs content."""

    return bool(DOCUMENTATION_READER_RE.search(command) and DOCUMENTATION_PATH_RE.search(command))


def tool_documentation_read_denied(payload: dict, status: dict) -> bool:
    """Catch IDE-native file analyzers that bypass run_command/view_file names."""

    call = payload.get("toolCall")
    if not isinstance(call, dict):
        return False
    name = str(call.get("name", ""))
    if not DOCUMENTATION_READER_RE.search(name):
        return False
    args = call.get("args", {})
    serialized = json.dumps(args, ensure_ascii=False) if isinstance(args, dict) else str(args)
    return documentation_read_denied(f"{name} {serialized}", status)


def _argument_strings(value: object):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for nested in value.values():
            yield from _argument_strings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _argument_strings(nested)


def workspace_exploration_denied(payload: dict, status: dict) -> bool:
    """Reject directory/tree exploration until actual source intake is complete."""

    call = payload.get("toolCall")
    if not isinstance(call, dict):
        return False
    name = str(call.get("name", ""))
    args = call.get("args", {})
    serialized_args = " ".join(_argument_strings(args))
    is_workspace_tool = bool(
        re.search(r"\b(?:workspace|tree|directory|folder|list|scan|index)\b", name, re.IGNORECASE)
    )
    is_workspace_shell = name.lower() == "run_command" and bool(
        SHELL_WORKSPACE_EXPLORER_RE.search(serialized_args)
    )
    has_directory_argument = False
    for value in _argument_strings(args):
        try:
            if Path(value).expanduser().resolve().is_dir():
                has_directory_argument = True
                break
        except (OSError, ValueError):
            continue
    is_workspace_candidate = is_workspace_tool or is_workspace_shell or (
        bool(WORKSPACE_EXPLORER_RE.search(name)) and has_directory_argument
    )
    if not status.get("codeTask") or not status.get("sources") or not is_workspace_candidate:
        return False
    if (
        len(status.get("implementationViewed", [])) >= status.get("minimum", 0)
        and len(status.get("sourcesViewed", [])) >= status.get("sourceMinimum", 0)
        and status.get("targetRead", False)
        and (
            not status.get("testRequired")
            or len(status.get("testsViewed", [])) >= len(status.get("tests", []))
        )
    ):
        return False
    return is_workspace_candidate


def documentation_read_denied(command: str, status: dict) -> bool:
    if not reads_documentation(command) or not status.get("codeTask") or not status.get("sources"):
        return False
    return bool(
        len(status.get("implementationViewed", [])) < status.get("minimum", 0)
        or len(status.get("sourcesViewed", [])) < status.get("sourceMinimum", 0)
        or not status.get("targetRead", False)
        or (
            status.get("testRequired")
            and len(status.get("testsViewed", [])) < len(status.get("tests", []))
        )
    )
