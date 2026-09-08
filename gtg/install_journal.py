"""설치 파일 이동을 먼저 기록하여 프로세스 종료 뒤에도 되돌립니다."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import stat
import uuid

from .legacy import LINKS
from .platforms import INSTALL_ROOTS, NAME


def exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def identity(path: Path) -> list[int] | None:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    return [info.st_dev, info.st_ino, stat.S_IFMT(info.st_mode)]


def sync_directory(path: Path):
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def durable_json(path: Path, value: dict):
    temporary = path.with_name("journal-" + uuid.uuid4().hex + ".tmp")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        sync_directory(path.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


def sync_tree(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and not path.is_symlink():
            with path.open("rb") as stream:
                os.fsync(stream.fileno())
    directories = sorted((p for p in root.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True)
    for directory in [*directories, root]:
        sync_directory(directory)


class MoveJournal:
    """설치 잠금을 보유한 호출자만 사용합니다. 내용 대신 inode로 이동을 식별합니다."""

    def __init__(self, root: Path, working: Path):
        self.root = root.absolute()
        self.working = working.absolute()
        self.path = self.working / "pending.json"
        if self.path.is_symlink():
            raise ValueError("설치 기록에 심볼릭 링크를 사용할 수 없습니다.")

    def allowed(self, name: str) -> Path:
        if not isinstance(name, str) or not name or "\0" in name:
            raise ValueError("설치 기록 경로가 올바르지 않습니다.")
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("설치 기록이 지정 루트 밖을 가리킵니다.")
        path = self.root / relative
        targets = {*(self.root / parent / NAME for parent in INSTALL_ROOTS.values()),
                   *(self.root / ".gemini" / p for p in LINKS)}
        internal = path.is_relative_to(self.working) and path != self.working
        if internal:
            first = path.relative_to(self.working).parts[0]
            internal = bool(re.fullmatch(r"(?:stage|backup|removed|legacy)-[A-Za-z0-9_-]+", first))
        if path not in targets and not internal:
            raise ValueError("설치기가 관리하지 않는 경로가 기록에 있습니다.")
        if any(parent.is_symlink() for parent in path.parents):
            raise ValueError("설치 기록의 부모 경로가 심볼릭 링크입니다.")
        return path

    def read(self) -> dict:
        if self.path.stat().st_size > 64 * 1024:
            raise ValueError("설치 기록이 너무 큽니다.")
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if (not isinstance(data, dict) or data.get("schema_version") != 1 or data.get("root") != str(self.root)
                or data.get("state") not in {"pending", "committed"}):
            raise ValueError("설치 기록 형식이 올바르지 않습니다.")
        moves = data.get("moves")
        if not isinstance(moves, list) or not 1 <= len(moves) <= 8:
            raise ValueError("설치 이동 기록이 올바르지 않습니다.")
        for move in moves:
            if not isinstance(move, dict):
                raise ValueError("설치 이동 항목이 올바르지 않습니다.")
            self.allowed(move.get("source"))
            self.allowed(move.get("target"))
            ident = move.get("identity")
            if not isinstance(ident, list) or len(ident) != 3 or any(type(n) is not int or n < 0 for n in ident):
                raise ValueError("설치 파일 식별자가 올바르지 않습니다.")
        return data

    def prepare(self, moves: list[tuple[Path, Path]]):
        if exists(self.path):
            raise ValueError("미완료 설치를 먼저 복구해야 합니다.")
        if not 1 <= len(moves) <= 8:
            raise ValueError("설치 이동은 1개 이상 8개 이하여야 합니다.")
        records, vacated = [], set()
        for source, target in moves:
            src = source.relative_to(self.root).as_posix()
            dst = target.relative_to(self.root).as_posix()
            self.allowed(src)
            self.allowed(dst)
            if source == target or src in vacated:
                raise ValueError("중복된 설치 이동입니다.")
            ident = identity(source)
            if ident is None or (exists(target) and dst not in vacated):
                raise ValueError("설치 파일 상태가 이동 계획과 다릅니다.")
            records.append({"source": src, "target": dst, "identity": ident})
            vacated.add(src)
        durable_json(self.path, {"schema_version": 1, "root": str(self.root), "state": "pending", "moves": records})

    def move(self, source: Path, target: Path):
        if exists(target):
            raise ValueError("이동 대상에 다른 파일이 생겼습니다. 덮어쓰지 않습니다.")
        source.rename(target)
        sync_directory(source.parent)
        if source.parent != target.parent:
            sync_directory(target.parent)

    def apply(self):
        data = self.read()
        if data["state"] != "pending":
            raise ValueError("이미 완료된 설치 기록입니다.")
        for item in data["moves"]:
            source, target = self.allowed(item["source"]), self.allowed(item["target"])
            if identity(source) != item["identity"]:
                raise ValueError("설치 원본이 기록 이후 바뀌었습니다.")
            self.move(source, target)

    def clear(self):
        self.path.unlink()
        sync_directory(self.working)

    def commit(self):
        data = self.read()
        data["state"] = "committed"
        durable_json(self.path, data)
        self.clear()

    def recover(self) -> bool:
        if not exists(self.path):
            return False
        data = self.read()
        if data["state"] == "pending":
            for item in reversed(data["moves"]):
                source, target = self.allowed(item["source"]), self.allowed(item["target"])
                if identity(source) == item["identity"]:
                    continue
                if identity(target) != item["identity"] or exists(source):
                    raise ValueError("복구 경로에 다른 파일이 있습니다. 기록과 원본을 보존합니다.")
                self.move(target, source)
        self.clear()
        return True
