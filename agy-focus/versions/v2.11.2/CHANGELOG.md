# Changelog

## Unreleased

## v2.11.2 — 2026-08-23

- fixes step type recognition (`GENERIC`, `SYSTEM_MESSAGE`) in `verification_after_last_write` and helper verifiers
- prevents false Stop hook blocks and infinite continue loops across Antigravity IDE step reporting formats
- recognizes case-insensitive completion statuses (`DONE`, `SUCCESS`, `COMPLETED`) across command runners

## v2.11.1 — 2026-08-17

- fixes Stop hook infinite loops by allowing clean turn completion instead of perpetual continue blocks
- resolves exploration and tool deadlocks in scope-read gates by permitting list_dir, grep_search, and essential tool calls
- improves read-only request heuristics for error reports, questions, and inquiry prompts
- maintains strict quality standards while eliminating agent stall loops and token exhaustion

## v2.11.0 — 2026-08-17

- updates model target and system prompt optimizations for Gemini 3.7 Flash (High) with hybrid reasoning and thinking token budget allocation
- adds zero AI Slop intent orchestration and removes conversational filler, repetitive narrative phrasing, and speculative over-engineering
- strengthens single responsibility principle (SRP) architectural boundaries against God Objects in backend, frontend, and coordination layers
- establishes human-crafted UI/UX microcopy standards with concrete action verbs, empathetic error recovery, and clear hierarchy
- installs and verifies the v2.11.0 global profile while maintaining the entrypoint strictly under 6,000 characters (5,998 chars)

## v2.10.1 — 2026-08-03

- aligns the strict research message in the Stop hook and `/GTG` skill with the four-category v2.10 contract, including design-system evidence
- keeps v2.10.0 immutable as the previous release and points the current profile at the corrected patch release

## v2.10.0 — 2026-08-03

- adds a post-render Computer Use/vision observation gate for every strict UI task
- requires `search_web` followed by an official UI `read_url_content` after the visual observation
- adds Microsoft Fluent 2, Atlassian Design, Adobe Spectrum 2, IBM Carbon, and Shopify Polaris to the design-system evidence category
- raises the strict UI research contract from three to four evidence categories while keeping the always-on entrypoint below 6,000 characters

## v2.9.0 — 2026-08-03

- adds a machine-checked design decision ledger linking user outcome, rationale, implementation location, and verification method
- requires explicit recovery, retry, or undo paths in strict UI plans
- tightens `/GTG` intake wording so file lists and document summaries cannot substitute for contiguous, file-by-file source, configuration, and related-test reads
- replaces the blanket blur ban with a context gate: decorative content-surface blur and repeated material effects are blocked; functional navigation/control material remains possible when fallback is verified
- refreshes the adaptive-window, Apple materials, Design Theater, FlowEval, semantic-guidance, and GUIDE evidence set

## v2.8.0 — 2026-08-03

- Require every official UI source in a plan to carry a local finding, implementation impact or decision, and verification gate in the same evidence-matrix row or block.
- Extend Chrome rendering checks with actual CSS/DOM motion detection and `prefers-reduced-motion` emulation at every viewport.
- Connect the 2026 Antigravity Hooks, Chrome, WCAG 2.2, and Google HCI references to planning decisions and runtime verification.

## v2.7.0 — 2026-08-03

- removes the Stop-gate retry-limit escape hatch: incomplete source intake or required research keeps the execution loop running
- counts only successful transcript tool records as `view_file`/write evidence, so failed or errored calls cannot satisfy full-read gates
- aligns PreToolUse confirmation responses with the canonical Antigravity `ask` decision value

## v2.6.0 — 2026-08-03

- requires contiguous `view_file` reads of affected source, configuration, and tests before README/docs/search results, writes, or exploration can guide a change; the official `list_dir` summary is not a source read
- requires `/GTG` UI research to read at least four official URLs across three hosts and three evidence categories, then cite every URL in the report
- adds adaptive `reflow`/`reveal`/`presentation`, compact-transition, WAI-ARIA keyboard-pattern, and evidence-matrix contracts to UI plans
- compares planned files, routes, and flow traces with the actual implementation and browser evidence before completion
- refreshes the working evidence set against Apple HIG, Android adaptive guidance, Chrome I/O 2026, WCAG/APG, and Google GUIDE/HCI research

## v2.5.0 — 2026-08-02

- defaults website, webpage, landing-page, and static-page work to two or more route contracts instead of letting a single-page plan pass
- requires `/GTG` UI plans to compare at least two official sources and record the decision, implementation impact, motion budget, and verification gate
- blocks completion when restrained/expressive motion choice, trigger, timing, budget, or reduced-motion fallback is missing
- blocks shell workspace inventory (`find`, `ls`, `tree`, `fd`, `rg --files`, `git ls-files`) before source intake, in addition to IDE-native exploration
- keeps research and planning responsibilities split in a dedicated module; hook modules remain at or below 260 lines

## v2.4.0 — 2026-08-02

- blocks shell-based README·docs·Markdown reads before source intake, including `cat`, `sed`, `rg`, `git show`, and common script readers
- blocks IDE-native `analyze`, `inspect`, and `explore` reads of README/docs before source intake
- keeps strict `/GTG` review and diagnosis tasks running at `Stop` until the discovered implementation sources and related tests have full-read evidence
- blocks workspace/folder/file-tree exploration before source intake; directory summaries never count as a complete source read
- denies unknown analysis/exploration tools before source intake when Antigravity exposes them through the hook payload
- requires a successful post-write verification result instead of accepting a verification-shaped command alone
- keeps the source-order guard in its own module so the hook runner does not become a God Object
- refreshes the official Antigravity hook contract and 2026 UI evidence references used by the profile

## v2.3.0 — 2026-08-02

- extends Chrome UI rendering to 320px, 768px, and 1280px so the intermediate responsive state is measured instead of inferred
- requires UI plans to record visual direction, product rationale, rejected alternatives, and trade-offs without forcing one visual style
- requires verification plans to cover the medium viewport and real state transitions
- adds source-first call/state/data-path wording to the Gemini 3.6 Flash (High) skill so filenames, README, and docs cannot substitute for complete implementation reads
- aligns the UI planning, implementation, and review evidence with Apple 2026 HIG, Material 3 Expressive, Chrome Long Animation Frames/View Transitions, and WCAG 2.2

## v2.2.0 — 2026-08-02

- extends Chrome UI rendering with document metadata, semantic landmarks, image alt, accessible names, 24 CSS px control targets, keyboard focus, CLS, and Long Animation Frames diagnostics
- rejects duplicate route titles/headings and reduced-motion declarations that do not actually override animation or transition properties
- requires plan substance for motion purpose/timing, measurement, accessibility, and target-size checks
- refreshes 2026 Apple, Android Material 3, Chrome, W3C, and Google Research interface evidence

## v2.1.0 — 2026-08-02

- adds design, implementation, and verification plan gates before `/GTG` UI source writes
- requires route-aware multi-page plans and all-route Chrome renders when a website has multiple user flows
- adds deterministic plan and multi-page verifiers for route links, semantic structure, 320px/1280px render, overflow, reduced motion, and visible focus
- adds 2026 Apple, Chrome, web.dev, W3C, and Google Research references for interface planning
- updates the profile to 11 focused skills while keeping the hook responsibilities split

## v2.0.0 — 2026-08-02

- adds explicit `/GTG` strict mode for repository and UI work while keeping ordinary-request routing
- blocks writes until affected source files and a related test have been read from first line to last; README, docs, plans, comments, search summaries, and partial reads do not count
- requires separate first-party repository overview and implementation evidence when a page describes an external `owner/repository`
- blocks generic dark developer templates, Tailwind Slate inversions, centered documentation shells, repeated boxed sections, fake dashboards, repeated cards, vague copy, and decorative interaction
- requires post-write full-file rereads, project verification, dependency-free Chrome renders at 320px and 1280px, horizontal-overflow metrics, and direct screenshot inspection
- splits repository evidence and UI quality checks from the hook runner; every hook module stays at or below 260 lines
- adds direct God Object responsibility checks and the `architecture-boundaries` skill
- updates the 12 rules, 14 hooks, 10 skills, installer examples, checked installation snapshots, and four-language documentation

## v1.17.0 — 2026-08-02

- adds `scripts/install.sh`: update a clean checkout, back up the installed profile, install the current profile, and verify it in one run
- adds `--version vX.Y.Z`, `--skip-update`, `--help`, isolated install testing, and strict version validation
- replaces path-ordered whole-workspace reading with repository mapping plus full reads of affected source, call/data/state paths, and tests
- prevents README, plans, comments, search snippets, and summaries from counting as implementation evidence
- splits the former hook-runner God Object into focused state, payload, anchor, gate, and configuration modules
- adds an architecture-boundaries skill to separate UI state, domain decisions, I/O, persistence, network, and external-process responsibilities without file-count refactors
- strengthens UI implementation and review with product evidence, non-generic hierarchy, mobile-first reflow, accessibility states, reduced motion, and measured performance gates
- extends AI Slop checks for fake dashboards, glass/glow, nested cards, repeated radius/spacing, decorative 3D, vague copy, and purposeless interaction
- updates first-install, update, version-switch, removal, restore, UI, support, citation, issue, and social-preview surfaces

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
