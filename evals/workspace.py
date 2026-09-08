"""평가 작업공간의 파일·Git 상태와 실행 환경을 다룹니다."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import platform
import subprocess


def private(path: Path) -> bool:
    # 평가 규칙은 평가 대상 제품의 구현을 가져오지 않습니다.
    parts = tuple(part.casefold() for part in path.parts)
    return (bool(set(parts) & {".git", ".gtg", ".ssh", ".aws", ".kube", "__pycache__"})
            or any(part == ".env" or part.startswith(".env.") or Path(part).suffix in {".key", ".pem"}
                   or part in {"id_rsa", "id_ed25519"} for part in parts)
            or any(a == ".config" and b == "gh" for a, b in zip(parts, parts[1:]))
            or path.suffix.casefold() == ".pyc" or path.name.casefold() == ".ds_store")


def digest(path: Path) -> str:
    if path.is_symlink():
        return "link:" + os.readlink(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root: Path) -> dict:
    result = {}
    for folder, directories, files in os.walk(root, followlinks=False):
        directories[:] = [name for name in directories if not private(Path(name))]
        for name in [*directories, *files]:
            path = Path(folder) / name
            if private(path.relative_to(root)):
                continue
            if path.is_symlink() or path.is_file():
                result[path.relative_to(root).as_posix()] = digest(path)
    return result


def git_command(workspace: Path, *args: str) -> subprocess.CompletedProcess:
    environment = {"PATH": os.defpath, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
    return subprocess.run(["git", "--no-optional-locks", "-C", str(workspace), *args],
                          capture_output=True, timeout=5, env=environment)


def git_state(workspace: Path) -> dict:
    directory = workspace / ".git"
    if directory.is_symlink() or not directory.is_dir() or (directory / "index").is_symlink():
        return {"error": "git_fixture_missing_or_linked"}
    try:
        index = git_command(workspace, "ls-files", "--stage", "-z")
        head = git_command(workspace, "rev-parse", "--verify", "--quiet", "HEAD")
    except (OSError, subprocess.TimeoutExpired):
        return {"error": "git_fixture_unreadable"}
    if index.returncode or head.returncode not in (0, 1):
        return {"error": "git_fixture_unreadable"}
    return {"index": hashlib.sha256(index.stdout).hexdigest(),
            "head": head.stdout.decode().strip() if head.returncode == 0 else None}


def seed_user_edits(workspace: Path, edits: dict) -> dict:
    for args in (("-c", "init.templateDir=", "init", "-q"), ("add", "--", ".")):
        try:
            result = git_command(workspace, *args)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise ValueError("평가용 Git 초기 상태를 준비하지 못했습니다.") from error
        if result.returncode:
            raise ValueError("평가용 Git 초기 상태를 준비하지 못했습니다.")
    for name, edit in edits.items():
        path = workspace / name
        content = path.read_text(encoding="utf-8")
        if content.count(edit["from"]) != 1:
            raise ValueError("평가용 사용자 변경의 원본이 일치하지 않습니다.")
        path.write_text(content.replace(edit["from"], edit["to"]), encoding="utf-8")
    state = git_state(workspace)
    if "error" in state:
        raise ValueError("평가용 Git 상태를 확인하지 못했습니다.")
    return state


def environment_info() -> dict:
    return {"python_version": platform.python_version(), "system": platform.system(),
            "machine": platform.machine(), "host_logical_cpus": os.cpu_count(),
            "per_group_timeout_seconds": 5, "stdout_read_limit_bytes": 128 * 1024,
            "candidate_bytecode_cache": "fresh_per_group", "bytecode_writes": False,
            "cpu_limit_enforced": False, "memory_limit_enforced": False, "os_sandbox": False}
