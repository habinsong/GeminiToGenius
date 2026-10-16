"""코드 작업의 빌드 선행 조건과 명시한 PRD 요구의 검사 연결을 다룹니다."""

from pathlib import Path


def normalize(spec: dict, relative) -> dict:
    if "code_contract" not in spec:
        return spec
    contract = spec["code_contract"]
    if not isinstance(contract, dict) or set(contract) - {"build_check", "test_checks", "requirements"}:
        raise ValueError("code_contract에는 build_check, test_checks, requirements만 지정하세요.")
    ids = [check["id"] for check in spec["checks"]]
    build, tests = contract.get("build_check"), contract.get("test_checks")
    if (not isinstance(build, str) or build not in ids or not isinstance(tests, list) or not tests
            or any(not isinstance(name, str) or name not in ids or name == build for name in tests)
            or len(set(tests)) != len(tests)):
        raise ValueError("실제 빌드 검사 하나와 별도의 필수 시험 검사를 연결하세요.")
    if any(ids.index(build) > ids.index(name) for name in tests):
        raise ValueError("빌드 검사는 필수 시험보다 먼저 등록하세요.")
    requirements = contract.get("requirements", [])
    if not isinstance(requirements, list):
        raise ValueError("PRD 요구 연결은 목록이어야 합니다.")
    seen, sources = set(), set()
    for item in requirements:
        if (not isinstance(item, dict) or set(item) != {"id", "source", "checks"}
                or not isinstance(item["id"], str) or not item["id"].strip() or len(item["id"]) > 120
                or item["id"] in seen):
            raise ValueError("PRD 요구마다 고유 id, 기존 source, 연결할 checks가 필요합니다.")
        seen.add(item["id"])
        sources.add(relative(item["source"]).as_posix())
        refs = item["checks"]
        if (not isinstance(refs, list) or not refs
                or any(not isinstance(name, str) or name not in [build, *tests] for name in refs)
                or len(set(refs)) != len(refs)):
            raise ValueError("각 PRD 요구를 빌드 또는 필수 시험 검사에 연결하세요.")
    # 빌드·시험 입력과 PRD가 달라지면 이전 성공을 함께 무효화합니다.
    watched = sorted(sources | {name for check in spec["checks"] for name in check["watch"]})
    return {**spec, "checks": [{**check, "watch": watched} for check in spec["checks"]]}


def ensure_sources(workspace: Path, spec: dict):
    for item in spec.get("code_contract", {}).get("requirements", []):
        path = workspace / item["source"]
        if not path.is_file() or any(p.is_symlink() for p in [path, *path.parents]):
            raise ValueError("PRD 근거는 작업공간의 실제 일반 파일이어야 합니다.")


def dependencies(spec: dict, check_id: str) -> list[str]:
    contract = spec.get("code_contract", {})
    return [contract["build_check"]] if check_id in contract.get("test_checks", []) else []


def summarize(spec: dict, checks: list[dict], latest: dict) -> dict:
    states = {check["id"]: check for check in checks}
    for check in checks:
        if check["status"] != "passed":
            continue
        for name in dependencies(spec, check["id"]):
            result = latest[check["id"]]["result"]
            if states[name]["status"] != "passed":
                check.update(status="blocked", blocked_by=[name])
            elif result.get("prerequisite_runs", {}).get(name) != latest[name]["run_id"]:
                check.update(status="stale", blocked_by=[name])
            if check["status"] != "passed":
                for field in ("executed_watch", "unexecuted_watch", "unobservable_watch"):
                    check[field] = None
    return {"code_contract_enforced": "code_contract" in spec,
            "requirements": [{**item, "verified": all(states[name]["status"] == "passed" for name in item["checks"])}
                             for item in spec.get("code_contract", {}).get("requirements", [])]}
