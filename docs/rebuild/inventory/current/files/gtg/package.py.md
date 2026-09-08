# `gtg/package.py`

- 형식: `100644`
- 바이트: 11145
- SHA-256: `56f9da5254498e6ba008f9c024c56d13fbd9564e83d6e73b3f726f1be92638bd`
- 인코딩: `utf-8`

```
"""단일 소스에서 호스트별 패키지를 생성하고 실제 진입점을 검사합니다."""

from __future__ import annotations

import ast
import hashlib
import json
import math
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import re

from .inspection import open_regular
from .platforms import EVENTS, NAME, PLATFORMS, antigravity
from .spec import sensitive

MANIFEST = "gtg-manifest.json"


def validate_source(path: Path):
    if sensitive(path):
        raise ValueError("민감 경로는 패키지 원본에 포함할 수 없습니다.")
    if any(item.is_symlink() for item in [path, *path.parents]):
        raise ValueError("패키지 원본에 심볼릭 링크가 있습니다.")


def read_source(root: Path, name: str) -> bytes:
    path = root / name
    validate_source(path)
    with open_regular(root, Path(name)) as stream:
        return stream.read()


def copy_file(root: Path, relative: Path, target: Path):
    validate_source(root / relative)
    with open_regular(root, relative) as source:
        with target.open("wb") as output:
            shutil.copyfileobj(source, output)


def copy_source(root: Path, name: str, target: Path):
    source = root / name
    validate_source(source)
    if not source.is_dir():
        raise ValueError("패키지 원본 폴더가 없습니다.")
    for path in sorted(source.rglob("*")):
        parts = {part.casefold() for part in path.relative_to(source).parts}
        if (parts & {"__pycache__", ".git", ".gtg"}
                or path.suffix.casefold() == ".pyc" or path.name.casefold() == ".ds_store"):
            continue
        validate_source(path)
        if path.is_file():
            dest = target / path.relative_to(source)
            dest.parent.mkdir(parents=True, exist_ok=True)
            copy_file(root, path.relative_to(root), dest)
        elif not path.is_dir():
            raise ValueError("패키지 원본에 일반 파일이 아닌 항목이 있습니다.")


def build(source: Path, target: Path, installed: Path, platform: str) -> dict:
    if platform not in PLATFORMS:
        raise ValueError("지원하지 않는 패키지 호스트입니다.")
    source = source.absolute()
    validate_source(source)
    if target.exists() and any(target.iterdir()):
        raise ValueError("패키지 생성 대상은 비어 있어야 합니다.")
    target.mkdir(parents=True, exist_ok=True)
    copy_source(source, "gtg", target / "gtg")
    copy_source(source, "profile/skills", target / "skills")
    copy_file(source, Path("scripts/gtg_runner.py"), target / "run.py")
    rules = read_source(source, "profile/rules/gtg.md")
    version = read_source(source, "VERSION").decode("utf-8").strip()
    command = "python3 " + shlex.quote(str(installed / "run.py")) + " hook " + platform + " "
    if antigravity(platform):
        (target / "rules").mkdir()
        (target / "rules/AGENTS.md").write_bytes(rules)
        (target / "plugin.json").write_text(json.dumps({"name": NAME}) + "\n")
        hooks = {"gtg-context": {"PreInvocation": [{"type": "command", "command": command + "PreInvocation", "timeout": 5}]},
                 "gtg-completion": {"Stop": [{"type": "command", "command": command + "Stop", "timeout": 5}]}}
        hook_file = target / "hooks.json"
    else:
        (target / "GEMINI.md").write_bytes(rules)
        (target / "gemini-extension.json").write_text(json.dumps({"name": NAME, "version": version, "contextFileName": "GEMINI.md"}) + "\n")
        hooks = {"hooks": {event: [{"hooks": [{"type": "command", "name": "gtg-" + event.lower(),
                                               "command": command + event, "timeout": 5000}]}]
                           for event in ("BeforeAgent", "AfterAgent")}}
        hook_file = target / "hooks/hooks.json"
        hook_file.parent.mkdir()
    hook_file.write_text(json.dumps(hooks, indent=2) + "\n")
    files = {path.relative_to(target).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in sorted(target.rglob("*")) if path.is_file()}
    manifest = {"schema_version": 1, "name": NAME, "platform": platform,
                "version": version, "installed_path": str(installed), "files": files}
    (target / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def validated_hooks(hooks: dict, platform: str, installed: Path) -> list:
    """GTG가 생성하는 두 필수 훅의 구조와 실행 인자를 검사합니다."""
    required = {name: set(events) for name, events in EVENTS.items()}
    if platform not in required or not isinstance(hooks, dict):
        raise ValueError("패키지 훅 형식이 올바르지 않습니다.")
    entries = []
    if antigravity(platform):
        for named in hooks.values():
            if (not isinstance(named, dict) or named.get("enabled", True) is not True
                    or set(named) - required[platform] - {"enabled"}):
                raise ValueError("필수 훅이 비활성화됐거나 형식이 올바르지 않습니다.")
            for event, handlers in named.items():
                if event == "enabled":
                    continue
                if not isinstance(handlers, list):
                    raise ValueError("훅 핸들러는 배열이어야 합니다.")
                entries.extend((event, handler) for handler in handlers)
    else:
        if set(hooks) != {"hooks"} or not isinstance(hooks["hooks"], dict):
            raise ValueError("확장 훅 형식이 올바르지 않습니다.")
        for event, groups in hooks["hooks"].items():
            if not isinstance(groups, list):
                raise ValueError("훅 그룹은 배열이어야 합니다.")
            for group in groups:
                if (not isinstance(group, dict) or set(group) != {"hooks"}
                        or not isinstance(group["hooks"], list)):
                    raise ValueError("필수 훅 그룹 형식이 올바르지 않습니다.")
                entries.extend((event, handler) for handler in group["hooks"])
    if len(entries) != 2 or {event for event, _ in entries} != required[platform]:
        raise ValueError("필수 컨텍스트·완료 훅이 누락되거나 중복됐습니다.")
    result = []
    for event, handler in entries:
        if (not isinstance(handler, dict) or handler.get("type") != "command"
                or set(handler) - {"type", "name", "command", "timeout"}
                or not isinstance(handler.get("command"), str)):
            raise ValueError("필수 훅 명령 형식이 올바르지 않습니다.")
        argv = shlex.split(handler["command"])
        if argv != ["python3", str(installed / "run.py"), "hook", platform, event]:
            raise ValueError("훅 실행 경로·호스트·이벤트가 패키지 계약과 다릅니다.")
        timeout = handler.get("timeout")
        if type(timeout) not in {int, float} or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("훅 시간 제한은 양의 유한 수여야 합니다.")
        if antigravity(platform) and type(timeout) is not int:
            raise ValueError("Antigravity 훅 시간 제한은 정수 초여야 합니다.")
        seconds = timeout / 1000 if platform == "gemini-cli" else timeout
        result.append((event, argv, min(seconds, 5)))
    return result


def verify(target: Path, execute_hooks: bool = True, *, installed: Path | None = None) -> dict:
    manifest = json.loads((target / MANIFEST).read_text())
    declared = Path(manifest["installed_path"])
    if not declared.is_absolute() or declared != (installed or target).absolute():
        raise ValueError("설치 위치가 바뀌었습니다. 현재 경로에 다시 설치하세요.")
    expected = manifest["files"]
    if antigravity(manifest["platform"]) and "rules/AGENTS.md" not in expected:
        raise ValueError("호스트가 읽는 기본 규칙 진입점이 없습니다.")
    actual = {path.relative_to(target).as_posix(): path for path in target.rglob("*")
              if path.is_file() and path.name != MANIFEST and "__pycache__" not in path.parts and path.suffix != ".pyc"}
    if set(actual) != set(expected):
        raise ValueError("패키지 파일 목록이 manifest와 다릅니다.")
    for name, path in actual.items():
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected[name]:
            raise ValueError(f"패키지 원문이 변경되었습니다: {name}")
        if path.suffix == ".py":
            ast.parse(path.read_text(encoding="utf-8"))
        if path.name == "SKILL.md":
            text = path.read_text(encoding="utf-8")
            match = re.match(r"\A---\nname: ([a-z0-9]+(?:-[a-z0-9]+)*)\ndescription: ([^\n]+)\n---\n", text)
            if not match or match[1] != path.parent.name or len(match[1]) > 64 or len(match[2]) > 1024:
                raise ValueError(f"스킬 메타데이터가 올바르지 않습니다: {name}")
    platform = manifest["platform"]
    hooks = json.loads((target / ("hooks.json" if antigravity(platform) else "hooks/hooks.json")).read_text())
    entries = validated_hooks(hooks, platform, declared)
    if not execute_hooks:
        return {"ok": True, "files": len(actual), "hooks_executed": 0}
    count = 0
    for event, argv, timeout in entries:
        # 설치 전에는 동일한 진입점을 staging 경로에서 실행합니다.
        argv[1] = str(target / "run.py")
        payload = ({"conversationId": "package-check", "workspacePaths": [str(target)], "invocationNum": 0,
                    "executionNum": 0, "fullyIdle": True, "terminationReason": "model_stop"}
                   if antigravity(platform) else
                   {"session_id": "package-check", "cwd": str(target), "hook_event_name": event, "stop_hook_active": False})
        try:
            process = subprocess.run(argv, input=json.dumps(payload), text=True, capture_output=True, timeout=timeout,
                                     env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        except subprocess.TimeoutExpired as error:
            raise ValueError("패키지 훅이 시간 제한 안에 끝나지 않았습니다.") from error
        if process.returncode or process.stderr.strip():
            raise ValueError("패키지 훅 실행이 실패했습니다.")
        output = json.loads(process.stdout)
        if not isinstance(output, dict):
            raise ValueError("훅 출력이 JSON 객체가 아닙니다.")
        if event == "Stop" and output.get("decision") != "stop":
            raise ValueError("작업 없는 종료 훅이 종료를 허용하지 않습니다.")
        if event == "PreInvocation" and not output.get("injectSteps"):
            raise ValueError("첫 호출의 세션 정보가 없습니다.")
        if event == "BeforeAgent" and not output.get("hookSpecificOutput", {}).get("additionalContext"):
            raise ValueError("첫 요청의 세션 정보가 없습니다.")
        count += 1
    return {"ok": True, "files": len(actual), "hooks_executed": count, "platform": platform}
```
