#!/usr/bin/env python3
"""Build the always-on GEMINI.md entrypoint from the versioned rule files."""

from __future__ import annotations

import sys
from pathlib import Path


RULE_COUNT = 12
MAX_CHARS = 6_000


def render_profile(profile: Path) -> str:
    version = (profile / "VERSION").read_text(encoding="utf-8").strip()
    rules = sorted((profile / "rules").glob("*.md"))
    if len(rules) != RULE_COUNT:
        raise ValueError(f"expected {RULE_COUNT} rule files, found {len(rules)}")

    header = (
        "# 전역 작업 계약\n\n"
        f"이 파일은 `agy-focus` v{version}의 생성된 전역 진입점입니다. "
        "일반 자연어 프롬프트만으로 작업 유형을 자동 라우팅하고, "
        "현재 사용자 지시·활성 작업창·관련 파일·검증 가능한 결과에만 집중합니다. "
        "관련 없는 정리·플러그인·MCP 연결은 자의로 시작하지 않습니다."
    )
    text = header + "\n\n" + "\n\n".join(
        path.read_text(encoding="utf-8").strip() for path in rules
    )
    text = text.rstrip() + "\n"
    if len(text) >= MAX_CHARS:
        raise ValueError(f"GEMINI.md exceeds {MAX_CHARS} characters")
    return text


def main() -> int:
    profile = Path(__file__).resolve().parents[1]
    output = profile / "GEMINI.md"
    output.write_text(render_profile(profile), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
