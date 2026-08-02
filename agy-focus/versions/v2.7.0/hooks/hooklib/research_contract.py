from __future__ import annotations

import re
from urllib.parse import urlsplit

from .config import OFFICIAL_UI_SOURCE_RE
from .payloads import latest_request_records, record_tool_calls


REQUIRED_SOURCE_COUNT = 4
REQUIRED_HOST_COUNT = 3
REQUIRED_CATEGORY_COUNT = 3

SOURCE_CATEGORIES = (
    "platform-adaptive",
    "accessibility",
    "performance",
    "human-centered",
)


def canonical_url(value: str) -> str:
    return value.strip().rstrip(".,;:)]}>")


def _read_results(payload: dict) -> list[tuple[str, str]]:
    pending: list[str] = []
    results: list[tuple[str, str]] = []
    for record in latest_request_records(payload):
        for call in record_tool_calls(record):
            if not isinstance(call, dict) or str(call.get("name", "")).lower() != "read_url_content":
                continue
            args = call.get("args")
            if not isinstance(args, dict):
                continue
            for key in ("Url", "url", "URL"):
                if isinstance(args.get(key), str):
                    pending.append(canonical_url(args[key]))
                    break
        if record.get("type") != "READ_URL_CONTENT" or not pending:
            continue
        url = pending.pop(0)
        content = str(record.get("content", ""))
        if record.get("status") == "DONE" and content.strip() and not re.search(
            r"(?:\b404\b|not found|찾을 수 없|页面不存在)", content, re.IGNORECASE
        ):
            results.append((url, content))
    return results


def source_categories(url: str) -> set[str]:
    parsed = urlsplit(url.lower())
    host = parsed.netloc
    path = parsed.path
    categories: set[str] = set()
    if host in {"developer.apple.com", "developer.android.com"}:
        if re.search(r"accessib|wcag|keyboard|focus", path):
            categories.add("accessibility")
        else:
            categories.add("platform-adaptive")
    if host == "developer.chrome.com":
        if re.search(r"performance|long-animation|web-vitals|inp|render|animation", path):
            categories.add("performance")
        else:
            categories.add("platform-adaptive")
    if host == "web.dev":
        if re.search(r"performance|vitals|inp|render|accessib", path):
            categories.add("performance")
        else:
            categories.add("accessibility")
    if host in {"w3.org", "www.w3.org"}:
        categories.add("accessibility")
    if host in {"research.google", "design.google", "chi2026.acm.org", "arxiv.org", "www.arxiv.org"}:
        categories.add("human-centered")
    return categories & set(SOURCE_CATEGORIES)


def _report_text(payload: dict) -> str:
    return "\n".join(
        str(record.get("content", ""))
        for record in latest_request_records(payload)
        if record.get("source") == "MODEL" and isinstance(record.get("content"), str)
    )


def _status(urls: list[str], report: str) -> dict:
    unique_urls = list(dict.fromkeys(canonical_url(url) for url in urls if url))
    official_urls = [url for url in unique_urls if OFFICIAL_UI_SOURCE_RE.search(url)]
    hosts = sorted({urlsplit(url).netloc.lower() for url in official_urls if urlsplit(url).netloc})
    categories = sorted({category for url in official_urls for category in source_categories(url)})
    cited_urls = [url for url in official_urls if url in report]
    failures: list[str] = []
    if len(official_urls) < REQUIRED_SOURCE_COUNT:
        failures.append(f"official-sources:{len(official_urls)}/{REQUIRED_SOURCE_COUNT}")
    if len(hosts) < REQUIRED_HOST_COUNT:
        failures.append(f"official-hosts:{len(hosts)}/{REQUIRED_HOST_COUNT}")
    if len(categories) < REQUIRED_CATEGORY_COUNT:
        failures.append(f"evidence-categories:{len(categories)}/{REQUIRED_CATEGORY_COUNT}")
    if len(cited_urls) < REQUIRED_SOURCE_COUNT:
        failures.append(f"report-citations:{len(cited_urls)}/{REQUIRED_SOURCE_COUNT}")
    return {
        "ok": not failures,
        "officialUrls": official_urls,
        "hosts": hosts,
        "categories": categories,
        "citedUrls": cited_urls,
        "failures": failures,
    }


def ui_research_status(payload: dict) -> dict:
    records = latest_request_records(payload)
    result_types = {record.get("type") for record in records if record.get("status") == "DONE"}
    read_results = _read_results(payload)
    status = _status([url for url, _ in read_results], _report_text(payload))
    status.update(
        {
            "searchDone": "SEARCH_WEB" in result_types,
            "readDone": "READ_URL_CONTENT" in result_types,
            "readCount": len(read_results),
        }
    )
    if not status["searchDone"]:
        status["failures"].append("search-web:missing")
    if not status["readDone"]:
        status["failures"].append("read-url-content:missing")
    status["ok"] = not status["failures"]
    return status


def plan_evidence_status(text: str) -> dict:
    urls = [canonical_url(match.group(0)) for match in re.finditer(r"https?://[^\s)\]>}]+", text, re.IGNORECASE)]
    status = _status(urls, text)
    status["searchDone"] = True
    status["readDone"] = True
    status["readCount"] = len(status["officialUrls"])
    return status
