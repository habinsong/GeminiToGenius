"""선택한 텍스트 파일을 제한된 분량으로 읽고 범위와 생략을 반환합니다."""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import io
import os
from pathlib import Path
import stat

from .spec import private, relative


MAX_SCAN_BYTES = 8 * 1024 * 1024


class ChangedDuringRead(OSError):
    pass


@contextmanager
def open_regular(root: Path, path: Path):
    if not hasattr(os, "O_NOFOLLOW") or os.open not in os.supports_dir_fd:
        raise NotImplementedError("이 환경에서는 안전한 디렉터리 기반 읽기를 지원하지 않습니다.")
    directories = []
    descriptor = None
    try:
        if not path.parts:
            raise io.UnsupportedOperation("폴더가 아닌 파일을 지정하세요.")
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        directories.append(os.open(root, flags))
        for name in path.parts[:-1]:
            directories.append(os.open(name, flags, dir_fd=directories[-1]))
        descriptor = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directories[-1])
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise io.UnsupportedOperation("일반 파일이 아닙니다.")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = None
            yield stream
            try:
                current = os.stat(path.name, dir_fd=directories[-1], follow_symlinks=False)
                unchanged = signature(before) == signature(current) == signature(os.fstat(stream.fileno()))
                original_root = os.fstat(directories[0])
                current_root = os.stat(root, follow_symlinks=False)
                unchanged = unchanged and (original_root.st_dev, original_root.st_ino) == (current_root.st_dev, current_root.st_ino)
                for parent, name, child in zip(directories, path.parts[:-1], directories[1:]):
                    current = os.stat(name, dir_fd=parent, follow_symlinks=False)
                    opened = os.fstat(child)
                    unchanged = unchanged and (current.st_dev, current.st_ino) == (opened.st_dev, opened.st_ino)
            except OSError:
                unchanged = False
            if not unchanged:
                raise ChangedDuringRead()
    finally:
        if descriptor is not None:
            os.close(descriptor)
        for directory in reversed(directories):
            os.close(directory)


def signature(info: os.stat_result) -> tuple:
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def read_range(stream, start: int, end: int | None, budget: int) -> dict:
    before = os.fstat(stream.fileno())
    line, scanned, chunks = 1, 0, []
    while line < start:
        chunk = stream.readline(MAX_SCAN_BYTES - scanned + 1)
        scanned += len(chunk)
        if scanned > MAX_SCAN_BYTES:
            return {"status": "scan_limit", "text": "", "next_line": start}
        if not chunk:
            return {"status": "range_past_eof", "text": "", "next_line": None}
        line += 1
    remaining, reached_eof = budget, False
    state = "ok"
    while True:
        if remaining == 0 or (end is not None and line > end):
            reached_eof = not stream.read(1)
            state = "ok" if reached_eof or (end is not None and line > end) else "truncated"
            break
        chunk = stream.readline(min(remaining, MAX_SCAN_BYTES - scanned) + 1)
        scanned += len(chunk)
        if scanned > MAX_SCAN_BYTES:
            state = "scan_limit"
            break
        if not chunk:
            reached_eof = True
            break
        if b"\0" in chunk:
            return {"status": "binary", "text": "", "next_line": None}
        if len(chunk) > remaining:
            state = "truncated" if chunks else "line_exceeds_budget"
            break
        try:
            chunk.decode("utf-8")
        except UnicodeDecodeError:
            return {"status": "unsupported_encoding", "text": "", "next_line": None}
        chunks.append(chunk)
        remaining -= len(chunk)
        line += 1
    if signature(before) != signature(os.fstat(stream.fileno())):
        return {"status": "changed_during_read", "text": "", "next_line": start}
    raw = b"".join(chunks)
    complete = start == 1 and reached_eof
    return {"status": state, "text": raw.decode("utf-8"), "file_bytes": before.st_size,
            "start_line": start, "end_line": line - 1, "next_line": None if reached_eof else line,
            "complete": complete, "range_complete": reached_eof or (end is not None and line > end),
            "excerpt_sha256": hashlib.sha256(raw).hexdigest(),
            "file_sha256": hashlib.sha256(raw).hexdigest() if complete else None}


def inspect(root: Path, paths: list[str], max_bytes: int = 65536, start_line: int = 1, end_line: int | None = None) -> dict:
    original_root = root.expanduser().absolute()
    root = original_root.resolve(strict=True)
    if not root.is_dir() or private(root):
        raise ValueError("비민감 작업공간 폴더가 필요합니다.")
    if type(max_bytes) is not int or not 1 <= max_bytes <= 1024 * 1024:
        raise ValueError("내용 예산은 1바이트 이상 1MiB 이하여야 합니다.")
    if type(start_line) is not int or start_line < 1 or (end_line is not None and (type(end_line) is not int or end_line < start_line)):
        raise ValueError("줄 범위가 올바르지 않습니다.")
    if not paths or len(paths) > 32 or any(not isinstance(p, str) or len(p.encode()) > 4096 for p in paths):
        raise ValueError("한 번에 1~32개 파일 경로를 지정하세요.")
    results, seen, remaining = [], set(), max_bytes
    for name in paths:
        result = {"path": name, "status": "denied", "text": "", "complete": False, "range_complete": False, "file_sha256": None}
        try:
            path = Path(name)
            if path.is_absolute():
                base = root if path.is_relative_to(root) else original_root
                path = path.relative_to(base)
            path = relative(path.as_posix())
            result["path"] = path.as_posix()
            if path in seen:
                continue
            seen.add(path)
            if remaining == 0:
                result.update(status="budget_exhausted", next_line=start_line)
            else:
                with open_regular(root, path) as stream:
                    content = read_range(stream, start_line, end_line, remaining)
                result.update(content)
        except ChangedDuringRead:
            result.update(status="changed_during_read", next_line=start_line)
        except FileNotFoundError:
            result["status"] = "missing"
        except io.UnsupportedOperation:
            result["status"] = "not_regular"
        except NotImplementedError:
            result["status"] = "unsupported_platform"
        except (OSError, ValueError):
            result["status"] = "denied"
        remaining -= len(result["text"].encode("utf-8"))
        results.append(result)
    return {"workspace": str(root), "content_trust": "untrusted_workspace_data", "files": results,
            "content_bytes": max_bytes - remaining, "max_content_bytes": max_bytes,
            "complete": all(file["complete"] for file in results),
            "range_complete": all(file["range_complete"] for file in results)}
