from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from .config import (
    CONFIG_SUFFIXES,
    DOC_NAMES,
    DOC_SUFFIXES,
    INSTRUCTION_NAMES,
    MANIFEST_NAMES,
    SENSITIVE_NAME_RE,
    SKIPPED_SCOPE_PARTS,
    SOURCE_SUFFIXES,
)


def read_payload() -> dict:
    try:
        value = json.load(sys.stdin)
        return value if isinstance(value, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def tool_name(payload: dict) -> str:
    call = payload.get("toolCall")
    return str(call.get("name", "")) if isinstance(call, dict) else ""


def command_line(payload: dict) -> str:
    call = payload.get("toolCall")
    args = call.get("args") if isinstance(call, dict) else None
    if not isinstance(args, dict):
        return ""
    for key in ("CommandLine", "commandLine", "command_line", "command", "cmd"):
        value = args.get(key)
        if isinstance(value, str):
            return value
    return ""


def write_target_path(payload: dict) -> Path | None:
    call = payload.get("toolCall")
    args = call.get("args") if isinstance(call, dict) else None
    if not isinstance(args, dict):
        return None
    for key in (
        "TargetFile",
        "targetFile",
        "AbsolutePath",
        "absolutePath",
        "FilePath",
        "filePath",
        "path",
    ):
        value = args.get(key)
        if isinstance(value, str) and value:
            try:
                return Path(value).expanduser().resolve()
            except OSError:
                return None
    return None


def transcript_records(payload: dict) -> list[dict]:
    transcript_path = payload.get("transcriptPath")
    if not isinstance(transcript_path, str) or not transcript_path:
        return []
    try:
        lines = Path(transcript_path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    records: list[dict] = []
    for line in lines:
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            records.append(value)
    return records


def latest_request_records(payload: dict) -> list[dict]:
    records = transcript_records(payload)
    for index in range(len(records) - 1, -1, -1):
        if records[index].get("type") == "USER_INPUT":
            return records[index:]
    return records


def latest_user_prompt(payload: dict) -> str:
    for record in reversed(latest_request_records(payload)):
        content = record.get("content")
        if record.get("type") == "USER_INPUT" and isinstance(content, str):
            return content
    return ""


def prompt_matches(payload: dict, pattern) -> bool:
    return bool(pattern.search(latest_user_prompt(payload)))


def workspace_roots(payload: dict) -> list[Path]:
    values = payload.get("workspacePaths")
    if not isinstance(values, list):
        return []
    roots: list[Path] = []
    for value in values:
        if not isinstance(value, str):
            continue
        try:
            path = Path(value).expanduser().resolve()
        except OSError:
            continue
        if path.is_dir():
            roots.append(path)
    return sorted(set(roots))


def tracked_or_untracked_paths(root: Path) -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-co", "--exclude-standard"],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )
        return [root / line for line in result.stdout.splitlines() if line]
    except (OSError, subprocess.SubprocessError):
        return sorted(path for path in root.rglob("*") if path.is_file())


def safe_text_path(root: Path, path: Path) -> bool:
    try:
        resolved = path.resolve()
        relative = resolved.relative_to(root)
    except (OSError, ValueError):
        return False
    if any(part in SKIPPED_SCOPE_PARTS for part in relative.parts):
        return False
    if SENSITIVE_NAME_RE.search(relative.as_posix()):
        return False
    try:
        with resolved.open("rb") as stream:
            return b"\0" not in stream.read(8192)
    except OSError:
        return False


def scope_candidate_path(path: Path) -> bool:
    name = path.name.lower()
    suffix = path.suffix.lower()
    parts = {part.lower() for part in path.parts}
    return (
        name in INSTRUCTION_NAMES
        or name in MANIFEST_NAMES
        or suffix in SOURCE_SUFFIXES | CONFIG_SUFFIXES | DOC_SUFFIXES
        or (not suffix and bool(parts & {"bin", "scripts"}))
    )


def intake_priority(path: Path) -> tuple[int, str]:
    name = path.name.lower()
    stem = path.stem.lower()
    parts = {part.lower() for part in path.parts}
    suffix = path.suffix.lower()
    if name in INSTRUCTION_NAMES:
        bucket = 0
    elif name in MANIFEST_NAMES or name.endswith(".xcodeproj"):
        bucket = 1
    elif "test" in parts or "tests" in parts or "spec" in parts or name.startswith(("test_", "spec_")):
        bucket = 3
    elif suffix in SOURCE_SUFFIXES:
        bucket = 2
    elif suffix in CONFIG_SUFFIXES:
        bucket = 4
    elif suffix in DOC_SUFFIXES or "docs" in parts or stem in DOC_NAMES:
        bucket = 6
    else:
        bucket = 5
    return bucket, path.as_posix().lower()


def scope_text_paths(payload: dict) -> list[Path]:
    paths: set[Path] = set()
    for root in workspace_roots(payload):
        for candidate in tracked_or_untracked_paths(root):
            if scope_candidate_path(candidate) and safe_text_path(root, candidate):
                paths.add(candidate.resolve())
    return sorted(paths, key=intake_priority)


def transcript_tool_calls(payload: dict) -> list[dict]:
    calls: list[dict] = []
    for record in latest_request_records(payload):
        for key in ("tool_calls", "toolCalls"):
            value = record.get(key)
            if isinstance(value, list):
                calls.extend(call for call in value if isinstance(call, dict))
        value = record.get("toolCall")
        if isinstance(value, dict):
            calls.append(value)
    return calls


def fully_viewed_paths(payload: dict) -> set[Path]:
    result: set[Path] = set()
    for call in transcript_tool_calls(payload):
        if str(call.get("name", "")).lower() != "view_file":
            continue
        args = call.get("args")
        if not isinstance(args, dict):
            continue
        if any(key in args for key in ("StartLine", "EndLine", "startLine", "endLine")):
            continue
        value = args.get("AbsolutePath", args.get("absolutePath"))
        if not isinstance(value, str):
            continue
        try:
            result.add(Path(value).expanduser().resolve())
        except OSError:
            continue
    return result
