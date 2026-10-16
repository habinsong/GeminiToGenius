"""로컬 Python 프로세스의 환경을 관찰하고 명시한 필요조건과 비교합니다."""

from __future__ import annotations

import platform
import re
import shutil


FIELDS = {"system", "machine", "python_version", "python_implementation"}
EXECUTABLE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.+-]{0,79}\Z")


def validate(requirements: dict):
    if (not isinstance(requirements, dict) or not requirements
            or set(requirements) - FIELDS - {"executables"}):
        raise ValueError("환경 조건에는 system, machine, python_version, python_implementation, executables만 지정하세요.")
    for name in FIELDS & requirements.keys():
        value = requirements[name]
        if not isinstance(value, str) or not value.strip() or len(value) > 128:
            raise ValueError("환경 값은 비어 있지 않은 128자 이하 문자열이어야 합니다.")
    if "executables" in requirements:
        names = requirements["executables"]
        if (not isinstance(names, list) or not 1 <= len(names) <= 32
                or any(not isinstance(name, str) or not EXECUTABLE.fullmatch(name) for name in names)):
            raise ValueError("executables에는 인자·경로가 없는 실행 파일 이름을 1~32개 지정하세요.")


def observe(requirements: dict | None = None) -> dict:
    if requirements is not None:
        validate(requirements)
    observed = {"system": platform.system(), "machine": platform.machine(),
                "python_version": platform.python_version(), "python_implementation": platform.python_implementation()}
    mismatches = []
    for name, expected in (requirements or {}).items():
        if name == "executables":
            available = {tool: shutil.which(tool) is not None for tool in sorted(set(expected))}
            observed[name] = available
            mismatches.extend({"field": "executables." + tool, "expected": True, "observed": False}
                              for tool, found in available.items() if not found)
        elif observed[name] != expected:
            mismatches.append({"field": name, "expected": expected, "observed": observed[name]})
    return {"kind": "environment_check", "scope": "local_python_process", "observed": observed,
            "requirements": requirements, "matches": not mismatches if requirements is not None else None,
            "mismatches": mismatches, "target_compatibility_verified": False, "resource_limits_verified": False,
            "limitations": "현재 Python 프로세스의 필요조건만 확인합니다. 원격·컨테이너·기기 동작, API 기능, 자원 예산은 별도 검증이 필요합니다."}
