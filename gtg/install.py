"""별도 디렉터리에 먼저 검증한 뒤 플러그인 하나를 교체합니다."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import tempfile
import uuid

from .package import MANIFEST, NAME, build, verify
from . import legacy
from .install_journal import MoveJournal, sync_tree


def destination(root: Path, platform: str, scope: str) -> Path:
    if platform == "antigravity":
        return root / (".agents/plugins" if scope == "workspace" else ".gemini/config/plugins") / NAME
    if platform == "gemini-cli" and scope == "global":
        return root / ".gemini/extensions" / NAME
    raise ValueError("Gemini CLI 확장은 전역 설치를 지원합니다. 워크스페이스별 활성화는 호스트가 관리합니다.")


def safe_path(path: Path):
    if any(parent.is_symlink() for parent in [path, *path.parents]):
        raise ValueError("설치 경로에 심볼릭 링크가 있습니다. 원본을 보존하고 설치를 중단합니다.")


@contextmanager
def lock(root: Path):
    if os.name != "posix":
        raise ValueError("현재 설치기는 macOS와 Linux에서 검증됩니다.")
    import fcntl
    path = root / "install.lock"
    safe_path(path)
    root.mkdir(parents=True, exist_ok=True)
    with path.open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError("다른 GTG 설치 작업이 진행 중입니다.") from error
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def install(source: Path, root: Path, platform: str, scope: str) -> dict:
    root = root.absolute()
    target = destination(root, platform, scope)
    working = root / (".gtg/installer" if scope == "workspace" else ".gemini/gtg-installer")
    safe_path(target)
    safe_path(working)
    with lock(working):
        journal = MoveJournal(root, working)
        recovered = journal.recover()
        if target.exists() and not (target / MANIFEST).is_file():
            raise ValueError("동일 이름의 사용자 폴더가 있습니다. 덮어쓰지 않습니다.")
        stage = Path(tempfile.mkdtemp(prefix="stage-", dir=working))
        backup = None
        legacy_backup = None
        try:
            build(source, stage, target, platform)
            verify(stage, installed=target)
            target.parent.mkdir(parents=True, exist_ok=True)
            moves = []
            if target.exists():
                backup = working / ("backup-" + uuid.uuid4().hex)
                moves.append((target, backup))
            if platform == "antigravity" and scope == "global":
                legacy_backup, links = legacy.prepare_migration(root, working)
                moves.extend(links)
            moves.append((stage, target))
            sync_tree(stage)
            journal.prepare(moves)
            journal.apply()
            report = verify(target)
            journal.commit()
        except BaseException:
            journal.recover()
            raise
        finally:
            if stage.exists() and not journal.path.exists():
                shutil.rmtree(stage)
        return {**report, "target": str(target), "backup": str(backup) if backup else None,
                "legacy_backup": str(legacy_backup) if legacy_backup else None, "recovered_transaction": recovered}


def uninstall(root: Path, platform: str, scope: str) -> dict:
    root = root.absolute()
    target = destination(root, platform, scope)
    working = root / (".gtg/installer" if scope == "workspace" else ".gemini/gtg-installer")
    safe_path(target)
    safe_path(working)
    with lock(working):
        journal = MoveJournal(root, working)
        recovered = journal.recover()
        if not (target / MANIFEST).is_file():
            raise ValueError("GTG가 설치된 경로가 아닙니다.")
        backup = working / ("removed-" + uuid.uuid4().hex)
        journal.prepare([(target, backup)])
        try:
            journal.apply()
            journal.commit()
        except BaseException:
            journal.recover()
            raise
        return {"ok": True, "removed": str(target), "preserved": str(backup), "recovered_transaction": recovered}


def restore(root: Path, platform: str, scope: str, backup: Path) -> dict:
    root = root.absolute()
    target = destination(root, platform, scope)
    working = root / (".gtg/installer" if scope == "workspace" else ".gemini/gtg-installer")
    backup = backup.absolute()
    for path in (target, working, backup):
        safe_path(path)
    if backup.parent != working or not backup.name.startswith(("backup-", "removed-")):
        raise ValueError("이 설치기가 보존한 복구 경로만 사용할 수 있습니다.")
    with lock(working):
        journal = MoveJournal(root, working)
        recovered = journal.recover()
        metadata = json.loads((backup / MANIFEST).read_text())
        if metadata.get("installed_path") != str(target) or metadata.get("platform") != platform:
            raise ValueError("복구 대상과 원래 설치 경로가 다릅니다.")
        if target.exists() and not (target / MANIFEST).is_file():
            raise ValueError("동일 이름의 사용자 폴더를 덮어쓰지 않습니다.")
        displaced = working / ("backup-" + uuid.uuid4().hex) if target.exists() else None
        moves = [(target, displaced)] if displaced else []
        moves.append((backup, target))
        target.parent.mkdir(parents=True, exist_ok=True)
        journal.prepare(moves)
        try:
            journal.apply()
            journal.commit()
        except BaseException:
            journal.recover()
            raise
        return {"ok": True, "restored": str(target), "backup": str(displaced) if displaced else None,
                "recovered_transaction": recovered}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("install", "doctor", "uninstall", "restore", "restore-legacy"), nargs="?", default="install")
    parser.add_argument("--platform", choices=("antigravity", "gemini-cli"), default="antigravity")
    scopes = parser.add_mutually_exclusive_group()
    scopes.add_argument("--workspace", type=Path)
    scopes.add_argument("--home", type=Path)
    parser.add_argument("--backup", type=Path)
    args = parser.parse_args()
    root = (args.workspace or args.home or Path.home()).expanduser().absolute()
    scope = "workspace" if args.workspace else "global"
    source = Path(__file__).resolve().parents[1]
    try:
        if args.command == "install":
            result = install(source, root, args.platform, scope)
        elif args.command == "uninstall":
            result = uninstall(root, args.platform, scope)
        elif args.command == "restore":
            if args.backup is None:
                raise ValueError("--backup으로 출력된 보존 경로를 지정하세요.")
            result = restore(root, args.platform, scope, args.backup)
        elif args.command == "restore-legacy":
            if scope != "global" or args.platform != "antigravity" or args.backup is None:
                raise ValueError("이전 전역 프로필 복구에는 --backup이 필요합니다.")
            working = root / ".gemini/gtg-installer"
            saved = args.backup.absolute()
            safe_path(saved)
            if saved.parent != working or not saved.name.startswith("legacy-"):
                raise ValueError("이 설치기의 이전 프로필 보존 경로가 아닙니다.")
            with lock(working):
                journal = MoveJournal(root, working)
                journal.recover()
                if destination(root, args.platform, scope).exists():
                    raise ValueError("현재 GTG 플러그인을 uninstall한 뒤 이전 프로필을 복구하세요.")
                journal.prepare(legacy.restore_moves(root, saved))
                try:
                    journal.apply()
                    journal.commit()
                except BaseException:
                    journal.recover()
                    raise
            result = {"ok": True, "restored_legacy": str(saved), "legacy_verified": False}
        else:
            target = destination(root, args.platform, scope)
            safe_path(target)
            working = root / (".gtg/installer" if scope == "workspace" else ".gemini/gtg-installer")
            safe_path(working)
            with lock(working):
                recovered = MoveJournal(root, working).recover()
                result = {**verify(target), "target": str(target), "recovered_transaction": recovered}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
