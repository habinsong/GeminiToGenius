from __future__ import annotations

from pathlib import Path

from .arguments import clean_text_argument


def record_succeeded(record: dict) -> bool:
    """Only completed transcript records can contribute tool evidence."""

    if record.get("error"):
        return False
    status = str(record.get("status", "")).upper()
    return status in {"DONE", "SUCCESS", "COMPLETED"}


def _integer_argument(args: dict, *keys: str) -> int | None:
    for key in keys:
        value = args.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return None


def _file_line_count(path: Path) -> int | None:
    try:
        with path.open("rb") as stream:
            newlines = 0
            last = b""
            while chunk := stream.read(1024 * 1024):
                newlines += chunk.count(b"\n")
                last = chunk[-1:]
        return newlines + (1 if last and last != b"\n" else 0)
    except OSError:
        return None


def viewed_line_ranges(calls: list[dict]) -> dict[Path, list[tuple[int, int | None]]]:
    result: dict[Path, list[tuple[int, int | None]]] = {}
    for call in calls:
        if str(call.get("name", "")).lower() != "view_file":
            continue
        args = call.get("args")
        if not isinstance(args, dict):
            continue
        value = clean_text_argument(args.get("AbsolutePath", args.get("absolutePath")))
        if not value:
            continue
        try:
            path = Path(value).expanduser().resolve()
        except OSError:
            continue
        start = _integer_argument(args, "StartLine", "startLine")
        end = _integer_argument(args, "EndLine", "endLine")
        interval = (
            (1, None)
            if start is None and end is None
            else (max(1, start or 1), max(1, end) if end is not None else None)
        )
        result.setdefault(path, []).append(interval)
    return result


def path_coverage(calls: list[dict], path: Path) -> tuple[int, int | None, bool]:
    intervals = viewed_line_ranges(calls).get(path.resolve(), [])
    total = _file_line_count(path)
    if not intervals:
        return 0, total, False
    if total == 0:
        return 0, 0, True
    if total is None:
        return 0, None, any(start == 1 and end is None for start, end in intervals)
    merged_end = 0
    for start, end in sorted(intervals, key=lambda item: item[0]):
        if start > merged_end + 1:
            break
        merged_end = max(merged_end, total if end is None else min(total, end))
        if merged_end >= total:
            return total, total, True
    return merged_end, total, False


def fully_viewed_paths(calls: list[dict]) -> set[Path]:
    return {
        path
        for path in viewed_line_ranges(calls)
        if path_coverage(calls, path)[2]
    }
