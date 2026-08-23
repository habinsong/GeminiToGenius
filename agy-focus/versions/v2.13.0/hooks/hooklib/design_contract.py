from __future__ import annotations

import re


_HEADER_RE = re.compile(r"decision\s*id|결정\s*id|판단\s*id", re.IGNORECASE)
_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{2,}")


def decision_ledger_status(text: str) -> dict:
    """Check that design decisions have a local implementation and verification trail."""

    lines = text.splitlines()
    header_index = next(
        (index for index, line in enumerate(lines) if "|" in line and _HEADER_RE.search(line)),
        None,
    )
    failures: list[str] = []
    if header_index is None:
        return {
            "ok": False,
            "decisionCount": 0,
            "failures": ["decision-ledger:missing-header"],
        }

    header = [cell.strip().casefold() for cell in lines[header_index].strip().strip("|").split("|")]
    required = {
        "id": ("decision id", "결정 id", "판단 id"),
        "outcome": ("user outcome", "success signal", "사용자 결과", "성공 기준"),
        "decision": ("decision", "결정", "판단"),
        "rationale": ("rationale", "evidence", "근거", "출처"),
        "implementation": ("implemented in", "implementation", "구현 위치", "구현"),
        "verification": ("verified by", "verification", "검증 방법", "검증"),
    }
    missing_columns = [
        name for name, aliases in required.items()
        if not any(any(alias in cell for alias in aliases) for cell in header)
    ]
    failures.extend(f"decision-ledger:missing-column:{name}" for name in missing_columns)

    rows: list[list[str]] = []
    for line in lines[header_index + 1:]:
        stripped = line.strip()
        if not stripped or "|" not in stripped or _SEPARATOR_RE.match(stripped):
            if rows and stripped and not stripped.startswith("|"):
                break
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) >= len(header) and any(cells):
            rows.append(cells[: len(header)])

    if len(rows) < 2:
        failures.append(f"decision-ledger:rows:{len(rows)}/2")
    for row_index, row in enumerate(rows, start=1):
        empty = [header[index] or str(index + 1) for index, cell in enumerate(row) if not cell]
        if empty:
            failures.append(f"decision-ledger:row-{row_index}-empty:{','.join(empty[:3])}")

    return {
        "ok": not failures,
        "decisionCount": len(rows),
        "failures": failures,
    }
