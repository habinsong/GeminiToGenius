---
name: official-research
description: Verifies time-sensitive, obscure, or official Antigravity and Gemini facts through primary-source pages before answering. Use automatically for 최신, 공식 문서, 출처, 업데이트, 검색, Antigravity 문서, Gemini 문서, latest, official docs, source, or migration requests without requiring @mentions or slash commands.
---

# 공식 최신 조사

최신성·공식성·불확실성이 요청에 포함되면 기억이나 내장 가이드만으로 답하지 말고 실제 검색으로 확인합니다.

1. `search_web`로 현재 날짜와 `site:` 공식 도메인을 포함해 검색합니다.
2. Antigravity 문서는 `https://antigravity.google/docs/` 아래 URL만 1차 출처로 인정합니다. Gemini 문서는 `https://ai.google.dev/` 공식 문서 URL만 인정합니다. 도메인 루트, PyPI, GitHub, 블로그, 검색 요약은 문서 근거로 읽지 않습니다.
3. 일치하는 공식 문서 URL이 없으면 해당 주제로 다시 검색하고, 루트 페이지를 문서 대신 읽지 않습니다. 일치 URL을 `read_url_content`로 열어 핵심 문장을 확인합니다.
4. 확인된 사실, 추론, 확인하지 못한 항목을 분리하고 실제 읽은 문서의 정확한 URL을 함께 보고합니다.
5. 읽은 페이지에 직접 나타나지 않은 분류명·기능명·명세를 보태지 않습니다. 근거가 없으면 미확인으로 표시합니다.
6. Antigravity와 Antigravity IDE의 경로·동작은 한 제품으로 합치지 말고 각각 확인합니다.
7. Antigravity Hooks를 조사할 때는 검색 결과의 `/docs/plugins/hooks` 같은 대체 경로를 공식 Hooks 본문으로 간주하지 말고, `https://antigravity.google/docs/hooks`의 실제 내용을 기준으로 삼습니다. 이 페이지에 없는 `Inspect/Decide/Transform` 분류, Python SDK, `ask_user`, `before_tool_call`, `after_model_call`, `continue_on_error`, `event:`를 만들지 말고, 실제 문서의 `hooks.json`, `enabled`, `PreToolUse`, `PostToolUse`, `PreInvocation`, `PostInvocation`, `Stop`, `type`, `command`, `timeout`만 보고합니다.
8. 현재 공식 문서의 글로벌 스킬 경로는 `~/.gemini/config/skills`, workspace 스킬 경로는 `.agents/skills`로 취급합니다. `.gemini/skills`는 현재 공식 근거가 없으면 보고하지 않습니다.
9. 검색·URL 읽기 외의 MCP·플러그인·설치·파일 변경은 요청 범위에 없으면 하지 않습니다.

검색 도구를 실제로 사용할 수 없으면 검색했다고 쓰지 말고, 미검증 상태를 짧게 밝힙니다. 일반 요청에서 사용자에게 `@멘션`, `/액션`, `/learn` 또는 수동 스킬 선택을 요구하지 않습니다.
