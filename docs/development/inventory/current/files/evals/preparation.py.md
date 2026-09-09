# `evals/preparation.py`

- 형식: `100644`
- 바이트: 2930
- SHA-256: `2c22dccb55d7cf3c4fe106fea010a1fce01f56720f761b006ed53ee5a0ec0f81`
- 인코딩: `utf-8`

```
"""새 평가 폴더와 입력·설치·이전 진행 상태를 준비합니다."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import uuid

from .definitions import ROOT, CASES, case_by_id, definition_digest
from .progress import seed_progress
from .workspace import environment_info, seed_user_edits, snapshot

LABEL = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")


def label(value: str | None, name: str) -> str | None:
    """비교 보고서에 쓰는 사용자 선언 라벨입니다. 실행된 하네스를 확인하지는 않습니다."""
    if value is None:
        return None
    if not isinstance(value, str) or not LABEL.fullmatch(value):
        raise ValueError(f"{name} 라벨은 영숫자와 . _ - 만 사용하는 64자 이내 값이어야 합니다.")
    return value


def prepare(case_id: str, target: Path, profile: str = "baseline", *,
            arm: str | None = None, model: str | None = None) -> dict:
    case = case_by_id(case_id)
    if profile not in {"baseline", "gtg"}:
        raise ValueError("평가 프로필은 baseline 또는 gtg여야 합니다.")
    arm = label(arm, "arm") or profile
    model = label(model, "model")
    target = target.absolute()
    if target.exists() or target.is_symlink() or any(p.is_symlink() for p in target.parents):
        raise ValueError("심볼릭 링크가 없는 새 평가 경로가 필요합니다.")
    target.mkdir(parents=True)
    workspace = target / "workspace"
    fixture = CASES.parent / "fixtures" / case["fixture"]
    shutil.copytree(fixture, workspace, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    git_baseline = seed_user_edits(workspace, case["preexisting_edits"]) if case.get("preexisting_edits") else None
    if profile == "gtg":
        from gtg.install import install
        install(ROOT, workspace, "antigravity", "workspace")
    seeded = seed_progress(workspace, case["prior_progress"]) if profile == "gtg" and case.get("prior_progress") else None
    manifest = {"schema_version": 1, "trial_id": uuid.uuid4().hex, "case_id": case_id,
                "prepared_at": datetime.now(timezone.utc).isoformat(), "profile": profile,
                "arm": arm, "model": model,
                "definition_digest": definition_digest(), "baseline": snapshot(workspace), "git_baseline": git_baseline,
                "prompt_sha256": hashlib.sha256((case["prompt"] + "\n").encode()).hexdigest(),
                "preparation_environment": environment_info(), "seeded_progress": seeded, "runtime_observation": None}
    (target / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (target / "prompt.txt").write_text(case["prompt"] + "\n", encoding="utf-8")
    return {"trial": str(target), "workspace": str(workspace), "prompt": case["prompt"], "model_called": False}
```
