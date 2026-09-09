# `evals/definitions.py`

- 형식: `100644`
- 바이트: 1473
- SHA-256: `ce431460233097ed46a0887d683816b51b48b6cf78d73ff2a2cd8071335dd1fa`
- 인코딩: `utf-8`

```
"""평가 사례와 기준 원문의 동일성을 확인합니다."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .workspace import digest, snapshot

ROOT = Path(__file__).resolve().parents[1]
CASES = Path(__file__).with_name("cases.json")
PROBE = Path(__file__).with_name("probe.py")


def definition_digest() -> str:
    data = {"cases": digest(CASES), "fixtures": snapshot(CASES.parent / "fixtures"),
            "modules": {path.name: digest(path) for path in sorted(CASES.parent.glob("*.py"))}}
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def case_by_id(case_id: str) -> dict:
    cases = json.loads(CASES.read_text(encoding="utf-8"))["cases"]
    if case_id not in cases:
        raise ValueError("등록되지 않은 평가 사례입니다.")
    case = dict(cases[case_id])
    oracle = case.pop("oracle_case", None)
    if oracle is not None:
        if oracle == case_id or oracle not in cases or "oracle_case" in cases[oracle]:
            raise ValueError("평가 기준 참조가 올바르지 않습니다.")
        base = cases[oracle]
        if not {"module", "function", "checks"} <= base.keys():
            raise ValueError("재사용할 함수 평가 기준이 없습니다.")
        fields = ("module", "function", "checks", "integrations", "preserve_arguments")
        case = {**{name: base[name] for name in fields if name in base}, **case}
    return case
```
