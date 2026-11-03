"""검증에서 드러난 실수를 근거와 함께 짧은 교훈으로 남기고, 다음 세션이 볼 수 있게 읽어 줍니다."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import time
import unicodedata

from .inspection import workspace_path

try:
    import fcntl
except ImportError:  # Windows는 설치 지원 범위 밖이며 잠금 없이 동작합니다.
    fcntl = None


FILE = Path(".gtg/lessons.jsonl")
MIN_TEXT, MAX_TEXT = 15, 300
MAX_EVIDENCE = 5
MAX_KEEP = 100
URL = re.compile(r"https?://[^\s]{1,500}\Z")
LINE = re.compile(r"(.+?):([1-9][0-9]{0,6})\Z")


def clean(text: str) -> str:
    if not isinstance(text, str):
        raise ValueError("교훈은 문자열이어야 합니다.")
    text = " ".join(text.split())
    if not MIN_TEXT <= len(text) <= MAX_TEXT:
        raise ValueError(f"교훈은 {MIN_TEXT}자 이상 {MAX_TEXT}자 이하의 한 문장으로 쓰세요.")
    if any(unicodedata.category(char) in {"Cc", "Cf"} for char in text):
        raise ValueError("교훈에 제어 문자나 보이지 않는 문자를 넣을 수 없습니다.")
    return text


def evidence_item(root: Path, value: str) -> str:
    """근거는 작업공간의 실제 파일(줄 번호 선택)이나 원문 URL입니다."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("근거가 비어 있습니다.")
    value = value.strip()
    if URL.match(value):
        return value
    match = LINE.match(value)
    name, line = (match.group(1), match.group(2)) if match else (value, None)
    path = workspace_path(root, name)
    target = root / path
    if target.is_symlink() or not target.is_file():
        raise ValueError(f"근거 파일이 작업공간에 없습니다: {path.as_posix()}")
    return path.as_posix() + (f":{line}" if line else "")


def private_folder(root: Path) -> Path:
    """상태 폴더를 만들고 저장소 추적 목록에 나타나지 않게 합니다. 사용자 파일은 덮어쓰지 않습니다."""
    folder = root / FILE.parent
    if any(p.is_symlink() for p in [folder, root / FILE]):
        raise ValueError("교훈 기록 경로에 심볼릭 링크를 사용할 수 없습니다.")
    folder.mkdir(mode=0o700, exist_ok=True)
    ignore = folder / ".gitignore"
    if not ignore.exists() and not ignore.is_symlink():
        ignore.write_text("*\n", encoding="utf-8")
    return root / FILE


def parse(raw: str) -> list[dict]:
    entries = []
    for line in raw.splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(entry, dict) and isinstance(entry.get("text"), str) and isinstance(entry.get("evidence"), list):
            entries.append(entry)
    return entries


def record(root: Path, text: str, evidence: list[str]) -> dict:
    root = root.resolve(strict=True)
    text = clean(text)
    if not isinstance(evidence, list) or not 1 <= len(evidence) <= MAX_EVIDENCE:
        raise ValueError(f"근거를 1~{MAX_EVIDENCE}개 붙이세요. 근거 없는 교훈은 남기지 않습니다.")
    proofs = sorted({evidence_item(root, value) for value in evidence})
    key = hashlib.sha256(text.casefold().encode("utf-8")).hexdigest()[:12]
    path = private_folder(root)
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR | os.O_APPEND, 0o600)
    with os.fdopen(descriptor, "r+", encoding="utf-8") as stream:
        if fcntl is not None:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        stream.seek(0)
        entries = parse(stream.read())
        existing = next((entry for entry in entries if entry.get("id") == key), None)
        if existing:
            return {"recorded": False, "reason": "duplicate", "lesson": existing, "total": len(entries)}
        entry = {"id": key, "text": text, "evidence": proofs, "recorded_at": round(time.time())}
        entries.append(entry)
        if len(entries) > MAX_KEEP:
            entries = entries[-MAX_KEEP:]
            stream.seek(0)
            stream.truncate()
            stream.write("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in entries))
        else:
            stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return {"recorded": True, "lesson": entry, "total": len(entries), "path": str(path)}


def recent(root: Path, limit: int = 5) -> list[dict]:
    """최근 교훈부터 돌려줍니다. 기록이 없거나 읽을 수 없으면 빈 목록입니다."""
    path = root / FILE
    if type(limit) is not int or limit < 1 or path.is_symlink() or not path.is_file():
        return []
    try:
        entries = parse(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return []
    return list(reversed(entries))[:limit]
