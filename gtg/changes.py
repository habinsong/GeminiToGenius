"""Git 기준 리비전과 작업 트리를 비교해 변경된 텍스트 파일과 추가된 줄을 읽습니다."""

from __future__ import annotations

import difflib
import io
import os
from pathlib import Path
import subprocess

from .inspection import ChangedDuringRead, read_text, workspace_path
from .spec import private


MAX_FILE_BYTES = 1024 * 1024
MAX_SELECTED = 2000
# 커밋이 하나도 없는 저장소의 기준입니다. 모든 파일을 새 파일로 봅니다.
EMPTY = "empty"
# 저장소 설정이 외부 diff·파일 감시 프로그램을 부르지 않게 하고, 조회가 인덱스를 다시 쓰지 않게 합니다.
GIT_ENV = {"GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0"}
# 기준 없이 폴더를 훑을 때 건너뛰는 의존성·생성물 폴더입니다.
SKIP_DIRS = {"node_modules", ".venv", "venv", "site-packages", "build", "dist", ".tox", ".mypy_cache", ".pytest_cache"}


def git(root: Path, *args: str) -> bytes:
    try:
        process = subprocess.run(["git", "-c", "core.fsmonitor=false", "-C", str(root), *args],
                                 capture_output=True, timeout=60, env={**os.environ, **GIT_ENV})
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ValueError("git을 실행하지 못했습니다.") from error
    if process.returncode:
        raise ValueError("git 조회가 실패했습니다: " + " ".join(args[:2]))
    return process.stdout


def names(root: Path, *args: str) -> list[str]:
    return sorted({os.fsdecode(name) for name in git(root, *args).split(b"\0") if name})


def inside_git(root: Path) -> bool:
    try:
        return git(root, "rev-parse", "--is-inside-work-tree").strip() == b"true"
    except ValueError:
        return False


def baseline(root: Path, base: str | None, in_git: bool) -> str | None:
    """비교할 커밋 ID입니다. none이면 기준 없음(None), 커밋이 없는 저장소는 EMPTY입니다."""
    if base == "none":
        return None
    if not in_git:
        if base:
            raise ValueError("Git 저장소가 아니어서 기준 리비전을 읽을 수 없습니다. --base none과 경로를 지정하세요.")
        return None
    if base is not None and (not base.strip() or base.startswith("-")):
        raise ValueError("기준 리비전 이름이 올바르지 않습니다.")
    try:
        return git(root, "rev-parse", "--verify", "--quiet", (base or "HEAD") + "^{commit}").decode().strip()
    except ValueError:
        if base:
            raise ValueError("기준 리비전을 찾을 수 없습니다.") from None
        return EMPTY


def changed(root: Path, base: str) -> list[str]:
    """기준과 다른 추적 파일과 무시되지 않은 새 파일입니다. 삭제된 파일은 뺍니다."""
    untracked = names(root, "ls-files", "-z", "--others", "--exclude-standard")
    if base == EMPTY:
        return sorted(set(untracked) | set(names(root, "ls-files", "-z", "--cached")))
    modified = names(root, "diff", "--name-only", "--relative", "--no-renames", "--no-ext-diff",
                     "-z", "--diff-filter=AM", base, "--")
    return sorted(set(modified) | set(untracked))


def normalized(root: Path, value: str) -> str:
    name = workspace_path(root, value).as_posix()
    return "" if name == "." else name


def walk(root: Path, start: str) -> list[str]:
    found = []
    for directory, folders, files in os.walk(root / start):
        folders[:] = sorted(f for f in folders if f not in SKIP_DIRS and not private(Path(f)))
        for name in sorted(files):
            path = Path(directory, name)
            if not path.is_symlink():
                found.append(path.relative_to(root).as_posix())
            if len(found) > MAX_SELECTED:
                raise ValueError(f"검사할 파일이 {MAX_SELECTED}개를 넘습니다. 경로를 좁히세요.")
    return found


def expand(root: Path, wanted: list[str]) -> set[str]:
    """기준이 없을 때 쓰는 목록입니다. 지정한 파일과, 지정한 폴더 안의 파일을 모읍니다."""
    if not wanted:
        raise ValueError("기준 리비전이 없으면 검사할 파일이나 폴더를 지정하세요.")
    chosen = set()
    for name in wanted:
        target = root / name
        chosen.update(walk(root, name) if target.is_dir() and not target.is_symlink() else [name])
    return chosen


def within(candidates: list[str], wanted: list[str]) -> set[str]:
    """바뀐 파일 가운데 지정한 범위에 든 것입니다. 범위를 주지 않으면 전부입니다."""
    if not wanted:
        return set(candidates)
    return {c for c in candidates for w in wanted if not w or c == w or c.startswith(w + "/")}


def select(root: Path, base: str | None, paths: list[str]) -> list[str]:
    """검사할 파일 목록입니다. 경로를 주면 그 범위로 좁히고, 이름을 직접 준 파일은 바뀌지 않았어도 넣습니다."""
    wanted = [normalized(root, value) for value in paths]
    if base is None:
        chosen = expand(root, wanted)
    else:
        chosen = within(changed(root, base), wanted)
        chosen.update(w for w in wanted if w and (root / w).is_file())
    if len(chosen) > MAX_SELECTED:
        raise ValueError(f"변경 파일이 {MAX_SELECTED}개를 넘습니다. 경로를 좁히세요.")
    return sorted(n for n in chosen if not private(Path(n)))


def base_text(root: Path, base: str | None, name: str) -> str | None:
    if base in (None, EMPTY):
        return None
    try:
        data = git(root, "show", f"{base}:./{name}")
    except ValueError:
        return None
    if len(data) > MAX_FILE_BYTES or b"\0" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def added_lines(before: str | None, after: str) -> set[int]:
    """작업 트리 본문에서 기준에 없던 줄 번호(1부터)입니다."""
    lines = after.splitlines()
    if before is None:
        return set(range(1, len(lines) + 1))
    matcher = difflib.SequenceMatcher(None, before.splitlines(), lines, autojunk=False)
    added = set()
    for tag, _, _, start, end in matcher.get_opcodes():
        if tag in {"insert", "replace"}:
            added.update(range(start + 1, end + 1))
    return added


def collect(root: Path, base: str | None, paths: list[str], suffixes: set[str] | None = None) -> dict:
    """변경 파일마다 기준 본문·현재 본문·추가된 줄을 돌려줍니다. 읽지 못한 파일은 이유와 함께 따로 둡니다."""
    root = root.resolve(strict=True)
    if not root.is_dir() or private(root):
        raise ValueError("비민감 작업공간 폴더가 필요합니다.")
    in_git = inside_git(root)
    resolved = baseline(root, base, in_git)
    files, skipped = [], []
    for name in select(root, resolved, paths):
        if suffixes is not None and Path(name).suffix.casefold() not in suffixes:
            continue
        try:
            text = read_text(root, Path(name), MAX_FILE_BYTES)
        except FileNotFoundError:
            skipped.append({"path": name, "reason": "missing"})
            continue
        except ChangedDuringRead:
            skipped.append({"path": name, "reason": "changed_during_read"})
            continue
        except io.UnsupportedOperation:
            skipped.append({"path": name, "reason": "not_regular"})
            continue
        except NotImplementedError:
            skipped.append({"path": name, "reason": "unsupported_platform"})
            continue
        except OSError:
            skipped.append({"path": name, "reason": "denied"})
            continue
        if text is None:
            skipped.append({"path": name, "reason": "binary_or_large"})
            continue
        before = base_text(root, resolved, name)
        files.append({"path": name, "before": before, "after": text, "added": added_lines(before, text)})
    return {"root": root, "git": in_git, "base": resolved, "files": files, "skipped": skipped}


def workspace_texts(root: Path, in_git: bool, suffix: str, *, max_files: int = 5000,
                    max_bytes: int = 32 * 1024 * 1024) -> dict[str, str] | None:
    """참조 검색에 쓸 작업공간 파일 본문입니다. 상한을 넘으면 None을 돌려 판단을 유보하게 합니다."""
    if in_git:
        listed = [n for n in names(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
                  if n.endswith(suffix)]
    else:
        try:
            listed = [n for n in walk(root, "") if n.endswith(suffix)]
        except ValueError:
            return None
    if len(listed) > max_files:
        return None
    texts, total = {}, 0
    for name in listed:
        if private(Path(name)):
            continue
        try:
            text = read_text(root, Path(name), MAX_FILE_BYTES)
        except (OSError, NotImplementedError):
            continue
        if text is None:
            continue
        total += len(text)
        if total > max_bytes:
            return None
        texts[name] = text
    return texts
