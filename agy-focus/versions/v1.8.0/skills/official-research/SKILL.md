---
name: official-research
description: Verifies current, obscure, or official Antigravity and Gemini facts through real web search and primary-source pages. Use automatically for 최신, 공식, 최신 문서, 검색, 찾아, 확인, verify, latest, docs, or source requests without an @mention, slash action, or manual skill selection.
---

# 공식 최신 조사

최신성·공식성·불확실성이 요청에 포함되면 기억이나 내장 가이드만으로 답하지 말고 실제 검색으로 확인합니다.

1. `search_web`로 현재 연도(2026)를 포함해 검색합니다.
2. 검색 결과 중 공식 1차 출처를 `read_url_content`로 열어 핵심 문장을 확인합니다.
3. 확인된 사실, 추론, 확인하지 못한 항목을 분리하고 공식 URL을 함께 보고합니다.
4. Antigravity와 Antigravity IDE의 경로·동작은 한 제품으로 합치지 말고 각각 확인합니다.
5. 현재 공식 문서의 글로벌 스킬 경로는 `~/.gemini/config/skills`, workspace 스킬 경로는 `.agents/skills`로 취급합니다. `.gemini/skills`는 현재 공식 근거가 없으면 보고하지 않습니다.
6. 검색·URL 읽기 외의 MCP·플러그인·설치·파일 변경은 요청 범위에 없으면 하지 않습니다.

검색 도구를 실제로 사용할 수 없으면 검색했다고 쓰지 말고, 미검증 상태를 짧게 밝힙니다. 일반 요청에서 사용자에게 `@멘션`, `/액션`, `/learn` 또는 수동 스킬 선택을 요구하지 않습니다.
