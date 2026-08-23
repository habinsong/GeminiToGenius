from __future__ import annotations

import re

from .arguments import clean_text_argument
from .payloads import (
    latest_request_records,
    latest_user_prompt,
    workspace_roots,
)
from .ui_quality import is_strict_gtg, is_ui_task


GITHUB_SLUG_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])([A-Za-z0-9](?:[A-Za-z0-9_.-]{0,38}))"
    r"/([A-Za-z0-9_.-]{2,100})(?![A-Za-z0-9_.-])"
)


def referenced_github_slug(payload: dict) -> str | None:
    for match in GITHUB_SLUG_RE.finditer(latest_user_prompt(payload)):
        owner, repository = match.groups()
        if owner.lower() in {"windows", "macos", "linux", "http", "https"}:
            continue
        return f"{owner}/{repository}".rstrip(".,;:!?")
    return None


def _read_categories(slug: str, url: str) -> set[str]:
    normalized = clean_text_argument(url).casefold().split("?", 1)[0].rstrip("/")
    slug_lower = slug.casefold()
    if slug_lower not in normalized:
        return set()
    categories: set[str] = set()
    if normalized.endswith(slug_lower) or re.search(r"/(?:readme(?:\.[a-z0-9]+)?)$", normalized):
        categories.add("overview")
    if re.search(
        r"/(?:install(?:\.[a-z0-9]+)?|manifest\.json|version|hooks\.json)$"
        r"|/(?:scripts|hooks|hooklib|skills|rules|src|lib)/",
        normalized,
    ):
        categories.add("implementation")
    return categories


def _successful_read_categories(payload: dict, slug: str) -> set[str]:
    pending: list[str] = []
    categories: set[str] = set()
    for record in latest_request_records(payload):
        for call in record.get("tool_calls", record.get("toolCalls", [])):
            if not isinstance(call, dict) or str(call.get("name", "")).lower() != "read_url_content":
                continue
            args = call.get("args")
            if isinstance(args, dict):
                pending.append(str(args.get("Url", args.get("url", ""))))
        if record.get("type") != "READ_URL_CONTENT" or not pending:
            continue
        url = pending.pop(0)
        content = str(record.get("content", ""))
        if record.get("status") == "DONE" and content and not re.search(
            r"(?:\b404\b|not found|찾을 수 없)", content, re.IGNORECASE
        ):
            categories.update(_read_categories(slug, url))
    return categories


def _successful_command_categories(payload: dict, slug: str) -> set[str]:
    pending: list[str] = []
    categories: set[str] = set()
    for record in latest_request_records(payload):
        for call in record.get("tool_calls", record.get("toolCalls", [])):
            if not isinstance(call, dict) or str(call.get("name", "")).lower() != "run_command":
                continue
            args = call.get("args")
            if isinstance(args, dict):
                pending.append(str(args))
        if record.get("type") not in {"RUN_COMMAND", "GENERIC", "SYSTEM_MESSAGE"} or not pending:
            continue
        command = pending.pop(0)
        if str(record.get("status", "")).upper() in {"DONE", "SUCCESS", "COMPLETED"} and re.search(
            rf"(?:github\.com/|repos/|gh\s+(?:repo\s+view|api)\s+)[^\n]*{re.escape(slug)}",
            command,
            re.IGNORECASE,
        ):
            categories.update(_read_categories(slug, command))
    return categories


def repository_reference_evidence_present(payload: dict) -> bool:
    slug = referenced_github_slug(payload)
    if not slug:
        return True
    repository = slug.split("/", 1)[1]
    if any(root.name.casefold() == repository.casefold() for root in workspace_roots(payload)):
        return True

    categories = _successful_read_categories(payload, slug)
    categories.update(_successful_command_categories(payload, slug))
    return {"overview", "implementation"}.issubset(categories)


def repository_reference_gate(payload: dict) -> dict:
    if not is_strict_gtg(payload) or not is_ui_task(payload):
        return {"decision": "allow"}
    slug = referenced_github_slug(payload)
    if not slug or repository_reference_evidence_present(payload):
        return {"decision": "allow"}
    return {
        "decision": "deny",
        "reason": f"{slug} 저장소를 설명하는 1차 근거가 부족합니다. 검색 요약은 근거가 아닙니다. "
        f"https://github.com/{slug}의 README/저장소 개요와 별도로 설치 스크립트·manifest·실제 소스 중 "
        "하나를 read_url_content나 gh/curl로 끝까지 직접 확인한 뒤 버전·개수·명령을 작성하세요.",
    }
