from __future__ import annotations

import re
from urllib.parse import urlsplit

from .config import (
    ANTIGRAVITY_DOC_URL_RE,
    GEMINI_DOC_URL_RE,
    GTG_TRIGGER_RE,
    OFFICIAL_UI_SOURCE_RE,
    RESEARCH_TRIGGER_RE,
    UNSUPPORTED_OFFICIAL_CLAIM_RE,
    URL_RE,
)
from .payloads import latest_request_records, latest_user_prompt, record_tool_calls
from .research_contract import ui_research_status
from .ui_quality import is_strict_gtg, is_ui_task


def research_gate_required(payload: dict) -> bool:
    prompt = latest_user_prompt(payload)
    return bool(RESEARCH_TRIGGER_RE.search(prompt) or (is_strict_gtg(payload) and is_ui_task(payload)))


def expected_official_url_re(prompt: str):
    if re.search(r"antigravity", prompt, re.IGNORECASE):
        return ANTIGRAVITY_DOC_URL_RE
    if re.search(r"gemini", prompt, re.IGNORECASE):
        return GEMINI_DOC_URL_RE
    if is_ui_prompt(prompt):
        return OFFICIAL_UI_SOURCE_RE
    return URL_RE


def is_ui_prompt(prompt: str) -> bool:
    return bool(
        re.search(
            r"(?:\b(?:ui|ux|css|html|react|frontend|website|webpage|responsive|layout|motion|animation|accessibility)\b|"
            r"디자인|화면|웹\s*페이지|반응형|레이아웃|모션|애니메이션|접근성)",
            prompt,
            re.IGNORECASE,
        )
    )


def _read_urls(records: list[dict]) -> list[str]:
    urls: list[str] = []
    for record in records:
        for call in record_tool_calls(record):
            if not isinstance(call, dict) or str(call.get("name", "")).lower() != "read_url_content":
                continue
            args = call.get("args")
            if not isinstance(args, dict):
                continue
            for key in ("Url", "url", "URL"):
                if isinstance(args.get(key), str):
                    urls.append(args[key])
                    break
    return urls


def _distinct_hosts(urls: list[str]) -> set[str]:
    return {urlsplit(url).netloc.lower() for url in urls if urlsplit(url).netloc}


def research_evidence_present(payload: dict) -> bool:
    records = latest_request_records(payload)
    prompt = "\n".join(
        record.get("content", "")
        for record in records
        if record.get("type") == "USER_INPUT" and isinstance(record.get("content"), str)
    )
    assistant_text = "\n".join(
        record.get("content", "")
        for record in records
        if record.get("source") == "MODEL" and isinstance(record.get("content"), str)
    )
    expected_url = expected_official_url_re(prompt)
    ui_required = is_ui_prompt(prompt) and is_strict_prompt(prompt)
    if ui_required:
        status = ui_research_status(payload)
        source_ok = status["ok"]
        report_ok = all(url in assistant_text for url in status["officialUrls"])
    else:
        result_types = {record.get("type") for record in records if record.get("status") == "DONE"}
        read_urls = _read_urls(records)
        source_ok = any(expected_url.search(url) for url in read_urls)
        report_ok = bool(expected_url.search(assistant_text))
    return (
        (source_ok if ui_required else {"SEARCH_WEB", "READ_URL_CONTENT"}.issubset(result_types))
        and source_ok
        and report_ok
        and not UNSUPPORTED_OFFICIAL_CLAIM_RE.search(assistant_text)
    )


def is_strict_prompt(prompt: str) -> bool:
    return bool(GTG_TRIGGER_RE.search(prompt))
