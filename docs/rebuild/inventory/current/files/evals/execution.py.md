# `evals/execution.py`

- 형식: `100644`
- 바이트: 5155
- SHA-256: `f279f408aab1dcbebacc8c161dbe55c3a59d953d0d065b3f3544c2a4f6d7ff9b`
- 인코딩: `utf-8`

```
"""준비된 요청을 각 하네스에 그대로 전달하고 실행 관측을 기록합니다.

같은 문자열이 모든 팔에 전달되었음을 사람이 아니라 코드가 보장합니다. 관측은 실행 시간과
종료 상태이며, 모델 사용량이나 비용은 이 도구가 알 수 없습니다.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time

from .workspace import private

PLACEHOLDER = "{prompt}"
OUTPUT_LIMIT = 256 * 1024
# 실행 관측 목록이 보고서를 덮지 않도록 상한을 둡니다.
FILE_LIMIT = 50


def workspace_files(files, workspace: Path) -> list[str]:
    """관측된 실행 파일 중 작업공간 안의 것만 상대 경로로 모읍니다."""
    found = set()
    for path in files:
        try:
            found.add(path.relative_to(workspace).as_posix())
        except ValueError:
            continue
    return sorted(name for name in found if not private(Path(name)))


def terminate(process: subprocess.Popen):
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        process.kill()
    process.wait()


def resolved(command: list[str], prompt: str) -> list[str]:
    if not isinstance(command, list) or not command or any(not isinstance(part, str) for part in command):
        raise ValueError("실행할 하네스 명령이 필요합니다.")
    if not any(PLACEHOLDER in part for part in command):
        raise ValueError(f"명령에 {PLACEHOLDER} 자리를 넣어야 준비된 요청이 그대로 전달됩니다.")
    return [part.replace(PLACEHOLDER, prompt) for part in command]


def run_arm(trial: Path, command: list[str], *, timeout: float = 1800) -> dict:
    trial = Path(trial).absolute()
    manifest = json.loads((trial / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("runtime_observation") is not None:
        raise ValueError("이 시행은 이미 실행됐습니다. 새 시행을 준비하세요.")
    prompt_file = trial / "prompt.txt"
    prompt = prompt_file.read_text(encoding="utf-8")
    if hashlib.sha256(prompt.encode("utf-8")).hexdigest() != manifest["prompt_sha256"]:
        raise ValueError("준비된 평가 요청이 변경되었습니다.")
    argv = resolved(command, prompt.strip())
    workspace = trial / "workspace"
    if not workspace.is_dir():
        raise ValueError("시행 작업공간이 없습니다.")
    started = time.monotonic()
    status, returncode, output = "completed", None, {"stdout_bytes": 0, "stderr_bytes": 0}
    executed: list[str] = []
    process = None
    try:
        # 계측은 실행 단계에서만 필요합니다. 채점 경로가 제품을 import하지 않도록 늦게 불러옵니다.
        from gtg.coverage import collector

        # 모든 팔에 같은 계측을 붙입니다. 하네스의 자기 보고 대신 실제 실행을 관측합니다.
        with collector() as session:
            process = subprocess.Popen(argv, cwd=workspace, stdin=subprocess.DEVNULL,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       env=session.environment(),
                                       start_new_session=os.name == "posix")
            try:
                out, err = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                terminate(process)
                out, err = process.communicate()
                status = "timeout"
            returncode = process.returncode
            output = {"stdout_bytes": len(out or b""), "stderr_bytes": len(err or b"")}
            (trial / "arm-stdout.log").write_bytes((out or b"")[:OUTPUT_LIMIT])
            (trial / "arm-stderr.log").write_bytes((err or b"")[:OUTPUT_LIMIT])
            executed = workspace_files(session.files(), workspace)
    except (ImportError, OSError, ValueError) as error:
        status = "error"
        output["error_type"] = type(error).__name__
    finally:
        if process is not None and process.poll() is None:
            terminate(process)
    observation = {"schema_version": 1, "command": list(command), "argv_length": len(argv),
                   "prompt_sha256": manifest["prompt_sha256"], "status": status, "returncode": returncode,
                   "duration_seconds": round(time.monotonic() - started, 3),
                   # 관측 가능한 런타임에서 실제로 실행된 작업공간 파일입니다. 자기 보고가 아닙니다.
                   "executed_workspace_files": executed[:FILE_LIMIT],
                   "executed_workspace_file_count": len(executed),
                   "observed_at": datetime.now(timezone.utc).isoformat(), **output}
    manifest["runtime_observation"] = observation
    (trial / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"ok": status == "completed" and returncode == 0, "trial": str(trial), **observation}
```
