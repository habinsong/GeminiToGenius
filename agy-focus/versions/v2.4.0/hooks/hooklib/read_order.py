from __future__ import annotations

import json
import re


DOCUMENTATION_PATH_RE = re.compile(
    r"(?:README(?:\.[A-Za-z0-9_.-]+)?|CHANGELOG(?:\.[A-Za-z0-9_.-]+)?|"
    r"CONTRIBUTING(?:\.[A-Za-z0-9_.-]+)?|(?:^|/)docs?(?:/|$)|\.mdx?\b)",
    re.IGNORECASE,
)
DOCUMENTATION_READER_RE = re.compile(
    r"(?:\b(?:cat|head|tail|sed|awk|nl|less|more|bat|rg|grep|read|open|inspect|"
    r"analy[sz]e|explore)\b|"
    r"\bgit\s+(?:show|diff|grep|log)\b|"
    r"\b(?:python3?|pypy3?|node|ruby|perl)\b[^\n]*(?:open\s*\(|read_text\b|"
    r"readFile(?:Sync)?\s*\(|File\.read\b))",
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
