# `gtg/spec.py`

- 형식: `100644`
- 바이트: 5961
- SHA-256: `0a4084ca04f998703dc5a0f496829821ce5628f521fa7557f510a8a39456240f`
- 인코딩: `utf-8`

```
"""작업 계약과 검증 대상의 내용을 다룹니다."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import stat


ID = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}\Z")
PRIVATE_DIRS = {".git", ".gtg", ".ssh", ".aws", ".kube", "__pycache__"}
# 자동 재개는 사용자 쿼터를 사용합니다. 긴 작업도 이 상한을 넘지 않습니다.
DEFAULT_RESUMES = 2
MAX_RESUMES = 8
# 이 명령들은 항상 성공하거나 입력을 그대로 출력하므로 어떤 요구도 검증하지 못합니다.
# 셸을 거친 우회까지 막지는 못하며, 실제 방어는 증명서의 독립 재실행입니다.
NO_EVIDENCE = {"true", ":", "echo", "printf", "yes", "test", "[", "sleep", "cat"}


def sensitive(path: Path) -> bool:
    parts = tuple(part.casefold() for part in path.parts)
    return (bool(set(parts) & {".ssh", ".aws", ".kube"})
            or any(part == ".env" or part.startswith(".env.") or Path(part).suffix in {".key", ".pem"}
                   or part in {"id_rsa", "id_ed25519"} for part in parts)
            or any(a == ".config" and b == "gh" for a, b in zip(parts, parts[1:])))


def private(path: Path) -> bool:
    return (sensitive(path) or bool({part.casefold() for part in path.parts} & PRIVATE_DIRS)
            or path.suffix.casefold() == ".pyc" or path.name.casefold() == ".ds_store")


def relative(value: str) -> Path:
    if not isinstance(value, str) or not value or "\0" in value:
        raise ValueError("검증 경로가 비어 있거나 올바르지 않습니다.")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or private(path):
        raise ValueError("검증 경로는 작업공간 내부의 비민감 경로여야 합니다.")
    return path


def validate(spec: dict) -> dict:
    if not isinstance(spec, dict) or type(spec.get("schema_version")) is not int or spec["schema_version"] != 1:
        raise ValueError("schema_version 1 작업 계약이 필요합니다.")
    if not isinstance(spec.get("goal"), str) or not spec["goal"].strip():
        raise ValueError("구체적인 목표가 필요합니다.")
    resumes = spec.get("max_resumes", DEFAULT_RESUMES)
    if type(resumes) is not int or not 1 <= resumes <= MAX_RESUMES:
        raise ValueError(f"자동 재개 예산은 1 이상 {MAX_RESUMES} 이하의 정수여야 합니다.")
    spec = {**spec, "max_resumes": resumes}
    checks = spec.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError("하나 이상의 완료 조건과 검증 명령이 필요합니다.")
    seen = set()
    for check in checks:
        if not isinstance(check, dict) or not isinstance(check.get("id"), str) or not ID.fullmatch(check["id"]):
            raise ValueError("검사 식별자가 올바르지 않습니다.")
        if check["id"] in seen:
            raise ValueError("검사 식별자가 중복됩니다.")
        seen.add(check["id"])
        if not isinstance(check.get("criterion"), str) or not check["criterion"].strip():
            raise ValueError("검사마다 사용자 요구와 연결된 완료 조건이 필요합니다.")
        command = check.get("argv")
        if not isinstance(command, list) or not command or any(
                not isinstance(arg, str) or "\0" in arg for arg in command) or not command[0]:
            raise ValueError("검증 명령은 비어 있지 않은 argv 배열이어야 합니다.")
        timeout = check.get("timeout_seconds", 120)
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or not 0 < timeout <= 3600:
            raise ValueError("명령 시간 제한은 0초 초과 3600초 이하여야 합니다.")
        watch = check.get("watch")
        if not isinstance(watch, list) or not watch:
            raise ValueError("검증 근거에 포함할 파일 또는 폴더가 필요합니다.")
        for name in watch:
            relative(name)
    return json.loads(json.dumps(spec, allow_nan=False))


def evidential(spec: dict) -> dict:
    """새 작업 등록에만 적용합니다. 저장된 기존 명세는 그대로 읽습니다."""
    for check in spec["checks"]:
        if PurePosixPath(check["argv"][0]).name.casefold() in NO_EVIDENCE:
            raise ValueError("결과를 만들지 않는 명령은 완료 증거가 될 수 없습니다. 실제 테스트·빌드·결과 검사를 등록하세요.")
    return spec


def fingerprint(root: Path, watched: list[str]) -> str:
    """파일 내용·모드·삭제를 비교합니다. 제외 경로의 내용은 읽지 않습니다."""
    root = root.resolve(strict=True)
    records = {}

    def add(path: Path):
        name = path.relative_to(root).as_posix()
        if private(Path(name)):
            return
        for parent in [path, *path.parents]:
            if parent == root:
                break
            if parent.is_symlink():
                raise ValueError("검증 대상의 심볼릭 링크는 지원하지 않습니다.")
        try:
            info = path.lstat()
        except FileNotFoundError:
            records[name] = "missing"
            return
        if stat.S_ISDIR(info.st_mode):
            records[name] = "directory"
            for child in sorted(path.iterdir()):
                add(child)
        elif stat.S_ISREG(info.st_mode):
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            records[name] = f"{stat.S_IMODE(info.st_mode):o}:{digest.hexdigest()}"
        else:
            raise ValueError("검증 대상에 일반 파일이 아닌 항목이 있습니다.")

    for name in watched:
        add(root / relative(name))
    return hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()
```
