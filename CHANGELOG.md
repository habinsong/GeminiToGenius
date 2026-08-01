# Changelog

## v1.16.0 — 2026-08-02

- keeps the always-on entrypoint under 6,000 characters; detailed guidance now loads through focused skills and hooks
- adds an automatic workspace-intake skill for complete, path-ordered reading before changes
- adds PreInvocation anchors for scope intake, UI context, and product copy
- adds a write gate for native edits and common shell write paths until safe workspace text files have been read in full
- splits UI implementation from UI evidence review and extends human-copy checks for labels, links, and recovery text

## v1.15.0 — 2026-08-02

- 9th lifecycle hook: one-time UI evidence anchor after relevant invocations
- 2 focused skills: UI evidence review and human product copy
- focused automatic skill descriptions; no `@` mention or slash command required
- deterministic hook test added to local and CI validation

## v1.14.2 — 2026-08-02

- 모델이 생성한 UI를 정답으로 승인하지 않고 실제 렌더링·제품 문맥·접근성·사용 흐름을 검증하도록 가드레일 강화
- Gemini 최신 모델의 시각 스타일 한계에 대응하는 결과 확인 기준 추가

## v1.14.1 — 2026-08-01

- 공식 Antigravity 문서에 없는 앱 버전 숫자 표기를 제거하고 전역 customization 경로 기준으로 정리
- Antigravity와 Antigravity IDE 모두 `~/.gemini/GEMINI.md`, `~/.gemini/config/` 기준으로 설명

## v1.14.0 — 2026-08-01

- Gemini 3.6 Flash 공식 모델 ID와 최신 Thinking 안내 반영
- 근거 없는 우주·로봇·관제 화면·가짜 지표·범용 AI 화면 패턴 차단
- 특정 시각 스타일을 기본값으로 강제하던 UI 지침 제거
- 레이아웃과 반응형 규칙을 콘텐츠·기존 디자인 시스템·접근성 근거 중심으로 조정
- 키보드 포커스·색상 의존·불필요한 상호작용 움직임을 UI 검증 항목에 추가

## v1.13.0 — 2026-08-01

- Gemini 3.6 Flash (High) targeting
- Antigravity and Antigravity IDE compatibility metadata
- 12 instruction files
- 8 lifecycle hooks
- 4 focused skills
- anti-AI-Slop UI and responsive-layout guardrails
- versioned profile history from `v1.0.0`
