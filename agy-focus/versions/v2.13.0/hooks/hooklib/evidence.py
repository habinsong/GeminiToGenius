from __future__ import annotations

import re


FABRICATED_EVIDENCE_COMMAND_RE = re.compile(
    r"(?:\becho\b|\bprintf\b|\bpython(?:3)?\s+-c\b|\bnode\b[^\n]*\s-e\b)[^\n]*"
    r"(?:https?://|github\.com/|duration/easing|evidence|출처|근거|verify)",
    re.IGNORECASE,
)


def is_fabricated_evidence_command(command: str) -> bool:
    return bool(FABRICATED_EVIDENCE_COMMAND_RE.search(command))
