from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from .config import OFFICIAL_UI_SOURCE_RE


VISION_TOOL_RE = re.compile(r"(?:computer(?:[_-]use)?|vision|screenshot|view[_-]?image)", re.IGNORECASE)
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def _name(call: dict) -> str:
    return str(call.get("name", "")).lower()


def _args_text(call: dict) -> str:
    return json.dumps(call.get("args", {}), ensure_ascii=False)


def is_vision_observation(call: dict) -> bool:
    """Recognize a real screen/image observation, not a render command alone."""

    name = _name(call)
    if name == "view_file":
        args = call.get("args", {})
        if isinstance(args, dict):
            values = [value for value in args.values() if isinstance(value, str)]
            return any(Path(value).suffix.lower() in IMAGE_SUFFIXES for value in values)
        return False
    return bool(VISION_TOOL_RE.search(name))


def post_visual_web_research(calls: list[dict], visual_index: int) -> tuple[bool, str]:
    """Require web search and a first-party UI page after visual inspection."""

    later = calls[visual_index + 1 :]
    search_indexes = [index for index, call in enumerate(later) if _name(call) == "search_web"]
    searched = bool(search_indexes)
    official_reads = []
    for index, call in enumerate(later):
        if _name(call) != "read_url_content":
            continue
        if search_indexes and index < min(search_indexes):
            continue
        args = call.get("args", {})
        if not isinstance(args, dict):
            continue
        for value in args.values():
            if isinstance(value, str) and OFFICIAL_UI_SOURCE_RE.search(value):
                official_reads.append(value)
    if not searched:
        return False, "실제 화면을 본 뒤 `search_web`로 외부 UI 근거를 다시 대조한 기록이 없습니다."
    if not official_reads:
        return False, "화면 관찰 뒤 `search_web` 결과를 바탕으로 공식 UI 페이지를 `read_url_content`로 읽은 기록이 없습니다."
    hosts = {urlsplit(value).netloc.lower() for value in official_reads if urlsplit(value).netloc}
    if not hosts:
        return False, "화면 관찰 뒤 읽은 공식 UI URL의 호스트를 확인할 수 없습니다."
    return True, ""
