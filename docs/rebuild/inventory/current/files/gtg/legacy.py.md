# `gtg/legacy.py`

- 형식: `100644`
- 바이트: 2362
- SHA-256: `ad6f1d8a48d9a7f55e82a9988bd1576a3d73b877fd66d9b7ba6bd033bc7951a3`
- 인코딩: `utf-8`

```
"""기존 v2 설치기가 소유한 링크만 보존·해제합니다."""

from __future__ import annotations

import json
import os
from pathlib import Path
import uuid


LINKS = {"GEMINI.md": "config/agy-focus/current/GEMINI.md",
         "config/hooks.json": "agy-focus/current/hooks/hooks.json",
         "config/skills": "agy-focus/current/skills"}


def prepare_migration(home: Path, working: Path) -> tuple[Path | None, list[tuple[Path, Path]]]:
    from .install_journal import durable_json, sync_directory

    gemini = home / ".gemini"
    owned = [name for name, expected in LINKS.items()
             if (gemini / name).is_symlink() and os.readlink(gemini / name) == expected]
    if not owned:
        return None, []
    backup = working / ("legacy-" + uuid.uuid4().hex)
    backup.mkdir()
    for name in owned:
        (backup / name).parent.mkdir(parents=True, exist_ok=True)
    durable_json(backup / "legacy.json", {"home": str(home), "links": owned})
    sync_directory(working)
    return backup, [(gemini / name, backup / name) for name in owned]


def restore_moves(home: Path, backup: Path) -> list[tuple[Path, Path]]:
    metadata = json.loads((backup / "legacy.json").read_text())
    if metadata.get("home") != str(home) or not isinstance(metadata.get("links"), list):
        raise ValueError("이 홈 디렉터리의 이전 링크 기록이 아닙니다.")
    names = metadata["links"]
    for name in names:
        if not isinstance(name, str) or name not in LINKS:
            raise ValueError("알 수 없는 이전 링크입니다.")
        current, saved = home / ".gemini" / name, backup / name
        if current.exists() or current.is_symlink():
            raise ValueError("복구 위치에 사용자 파일이 있습니다. 덮어쓰지 않습니다.")
        if not saved.is_symlink() or os.readlink(saved) != LINKS[name]:
            raise ValueError("보존된 이전 링크가 변경되었습니다.")
    return [(backup / name, home / ".gemini" / name) for name in names]


def restore(home: Path, backup: Path):
    moves = restore_moves(home, backup)
    moved = []
    try:
        for source, target in moves:
            source.rename(target)
            moved.append((source, target))
    except BaseException:
        for source, target in reversed(moved):
            target.rename(source)
        raise
```
