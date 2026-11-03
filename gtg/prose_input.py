"""검사할 글을 읽습니다. 작업공간 파일과 표준 입력·명령줄의 글을 같은 모양, 곧 (표시 이름, 본문, 상태)으로 돌려줍니다.

읽지 못한 글은 본문 대신 이유를 상태에 적고, 내용이 없는 글도 100점으로 통과시키지 않고 `empty`로 알립니다. 분석은 prose.py가 맡습니다.
"""

from __future__ import annotations

import io
from pathlib import Path

from .inspection import ChangedDuringRead, read_text, workspace_path


MAX_BYTES = 1024 * 1024
MAX_FILES = 64


def read_stream(stream, label: str = "<stdin>") -> tuple[str, str]:
    """표준 입력 같은 바이트 스트림을 UTF-8 글 하나로 읽습니다. 상한을 넘거나 글이 아니면 ValueError입니다."""
    data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES or b"\0" in data:
        raise ValueError("입력이 너무 크거나 글이 아닙니다.")
    try:
        return label, data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("입력은 UTF-8 글이어야 합니다.") from error


def given(label: str, text: str) -> tuple[str, str | None, str]:
    """이미 메모리에 있는 글(표준 입력, --text)을 (표시 이름, 본문, 상태)로 바꿉니다."""
    return (label, text, "ok") if text.strip() else (label, None, "empty")


def load(root: Path, value: str) -> tuple[str, str | None, str]:
    """작업공간 문서 하나를 (표시 이름, 본문, 상태)로 읽습니다. 읽지 못하면 본문 대신 이유를 상태에 적습니다."""
    name, text, status = value, None, "ok"
    try:
        path = workspace_path(root, value)
        name = path.as_posix()
        text = read_text(root, path, MAX_BYTES)
        if text is None:
            status = "binary_large_or_encoding"
    except ChangedDuringRead:
        status = "changed_during_read"
    except FileNotFoundError:
        status = "missing"
    except io.UnsupportedOperation:
        status = "not_regular"
    except NotImplementedError:
        status = "unsupported_platform"
    except (OSError, ValueError):
        status = "denied"
    if status == "ok" and not text.strip():
        return name, None, "empty"
    return name, text, status
