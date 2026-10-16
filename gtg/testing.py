"""시험 수와 필수 시험 ID의 실제 성공을 확인합니다. 언어 전체의 API 검사기는 아닙니다."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

from .spec import relative, sensitive


def run_unittest(workspace: Path, start_directory: str = ".", pattern: str = "test*.py", required=()) -> dict:
    workspace = Path(workspace).resolve(strict=True)
    directory = workspace / relative(start_directory)
    if (sensitive(workspace) or not directory.is_dir()
            or any(p.is_symlink() for p in [directory, *directory.parents])):
        raise ValueError("시험 탐색에는 링크 없는 작업공간 내부의 비민감 폴더가 필요합니다.")
    if (not isinstance(pattern, str) or not pattern or len(pattern) > 128
            or any(char in pattern for char in ("/", "\\", "\0"))):
        raise ValueError("시험 패턴은 경로 없는 파일명 패턴이어야 합니다.")
    if (not isinstance(required, (list, tuple))
            or any(not isinstance(name, str) or not name.strip() or len(name) > 512
                   or any(char in name for char in ("\0", "\n", "\r")) for name in required)):
        raise ValueError("필수 시험은 실제 unittest 시험 ID 목록이어야 합니다.")
    request = {"workspace": str(workspace), "start_directory": str(directory), "pattern": pattern}
    # 기존 실행기의 프로세스 그룹·시간 제한·실행 관측을 상속합니다. 테스트 코드는 OS 격리가 아닙니다.
    with tempfile.TemporaryDirectory() as cache, tempfile.TemporaryFile() as output:
        process = subprocess.run([sys.executable, "-B", "-X", f"pycache_prefix={cache}",
                                  str(Path(__file__).with_name("unittest_probe.py"))],
                                 input=json.dumps(request).encode(), stdout=output, cwd=workspace)
        output.seek(0)
        raw = output.read(256 * 1024 + 1)
    report = {"kind": "required_unittest", "passed": False, "required_tests": sorted(set(required)),
              "returncode": process.returncode, "scope": "discovered_unittest_cases"}
    try:
        observation = json.loads(raw) if len(raw) <= 256 * 1024 else None
    except (ValueError, UnicodeError):
        observation = None
    if (not isinstance(observation, dict) or observation.get("kind") != "unittest_observation"
            or type(observation.get("tests_run")) is not int or observation["tests_run"] < 0
            or not isinstance(observation.get("successful_tests"), list)
            or any(not isinstance(name, str) for name in observation["successful_tests"])):
        return {**report, "reason": "missing_or_invalid_observation"}
    succeeded = set(observation["successful_tests"])
    missing = sorted(set(required) - succeeded)
    return {**report, "observation": observation, "required_not_passed": missing,
            "passed": process.returncode == 0 and observation.get("successful") is True
                      and observation["tests_run"] > 0 and bool(succeeded) and not missing}
