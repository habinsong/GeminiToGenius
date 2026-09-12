# `CHANGELOG.md`

- 형식: `100644`
- 바이트: 22234
- SHA-256: `8108652c67c637b3d06030ae5da315956419e766b12121358f9f81f4be594c06`
- 인코딩: `utf-8`

```
# 3.0.0 — 2026-09-09

기존 2.x 프롬프트 프로필 아키텍처를 순수 Python 로컬 실행 코어로 전면 개편한 릴리스입니다. 세 차례의 알파 버전을 거쳐 실제 호스트 환경에서 동작을 실증한 후 배포합니다.

## 주요 추가 기능

- 완료 조건을 사전에 고정하고 등록된 명령을 실제로 실행합니다. 프로세스 종료 코드, 실행 시간, 검사 대상 파일 해시를 기록하며, 대상 파일이 변경되면 이전 성공 기록은 즉시 무효화됩니다.
- `certify`가 완료 주장과 실행 명령, 종료 코드, 파일 지문을 결합하고, `replay`가 상태 DB 없이 해당 문서만으로 결과를 독립 재현합니다. 판정 결과는 `pass`, `invalid`, `inconclusive`이며 종료 코드는 각각 0, 1, 2입니다.
- 검사 과정에서 실제로 실행된 소스 파일을 관측하여, 검사는 통과했으나 호출되지 않은 대상 파일을 있는 그대로 보고합니다. 관측할 수 없는 런타임 언어가 포함된 경우 미실행으로 단정하지 않고 판단을 유보한 원인을 명시합니다.
- Antigravity 데스크톱·IDE, Antigravity CLI(`agy`), Gemini CLI 3개 호스트를 지원하며, 플랫폼별 세부 차이는 `gtg/platforms.py` 단 한 곳에서 일원화하여 관리합니다.
- 세션이 끊겨도 작업 데이터가 보존됩니다. 새 세션에서 `tasks`로 검색해 `attach`하면 목표, 검사 결과, 진행 메모를 그대로 이어받습니다.
- 설치기가 호스트 환경을 자동 감지해 단일 명령으로 설치, 무결성 진단, 제거를 수행합니다. 파일 이동 저널을 사전 기록하여 설치 중 프로세스가 중단되더라도 안전하게 정리합니다.

## 주요 수정 사항

- 시스템 재부팅 후 PID 재사용으로 인해 `recover`가 계속 거부되어 작업이 교착되던 문제를 해결했습니다. 프로세스 수명 중에만 유지되는 OS 파일 잠금 방식으로 판별 기준을 변경했습니다. 자식 검사 프로세스가 잠금을 상속받으므로 부모 프로세스만 종료된 경우도 동일하게 감지됩니다.
- 검사가 백그라운드에서 실행 중일 때 종료 훅이 작업 완료를 잘못 승인하던 결함을 수정했습니다. 재개 예산을 불필요하게 소진하지 않으면서 잔여 검사와 프로세스 복구 방법을 안내하도록 개선했습니다.
- 관측 범위에 단 하나의 셸 스크립트만 포함되어도 미실행 범위 보고 전체가 `null`이 되던 문제를 수정했습니다. 판단을 가로막은 원인을 `unobservable_watch`에 명확히 밝힙니다.
- Antigravity CLI에서 패키지 파일만 배치하고 `agy plugin install`을 호출하지 않아 훅이 발행되지 않던 문제를 수정했습니다. 설치기가 CLI 등록 단계까지 자동으로 처리합니다.
- 평가 도구가 작업공간에 임시 설치된 GTG 자체 모듈의 실행까지 테스트 코드 실행으로 집계하여 GTG에 유리하게 편향되던 계측 오류를 바로잡았습니다.

## 호환성 안내

- 완료 증명서 스키마 버전이 v3으로 갱신되었습니다. 이전 버전 증명서는 인식되지 않으므로 `certify`로 다시 생성해야 합니다.
- 개발 문서 디렉터리 경로가 `docs/rebuild`에서 `docs/development`로 변경되었습니다.

## 참고 사항

동일한 기반 모델 환경에서 GTG 활성화 여부를 비교한 64회 시험 결과, 단일 턴 수준의 짧은 작업에서는 최종 산출물 차이가 없었습니다. GTG의 실질적 가치는 한 턴에 끝나지 않는 다단계 복합 작업에서 발휘됩니다. 구체적인 측정치와 미확인 항목은 [확인한 것과 확인하지 못한 것](docs/verification/README.md) 문서를 참고하세요.


# 3.0.0-alpha.3 — 2026-09-09 (개발 중, 미발행)

- 검사가 실제로 실행한 Python 파일을 관찰해 `unexecuted_watch`·`unverified_scope`로 검증하지 못한 범위를 밝힙니다.
- 증명서에 `coverage_complete`를 넣어 확인하지 못한 범위를 전부 검증으로 읽지 않게 했습니다.
- **호환성 변경**: 증명서 스키마가 판 2입니다. 이전 판 증명서는 거부되므로 `certify`로 다시 만드세요.
- `replay` 판정이 `pass`·`invalid`·`inconclusive` 세 값이며 종료 코드는 각각 0·1·2입니다.
- 준비된 요청을 그대로 전달하는 `evals.harness run`과 팔별 실행 시간 집계를 추가했습니다.
- 배포 지시문의 제어·양방향·폭 없는 문자를 거부하고 `plugin.json`을 공식 CLI 스키마에 맞췄습니다.
- 안내 문서의 실행 예시가 실제 CLI 계약과 어긋나면 검사가 실패합니다.
- 설치물과 `.gtg`가 자기 자신을 무시해 사용자 저장소의 변경 목록을 오염시키지 않습니다.
- 재사용된 PID의 프로세스 그룹에 신호를 보내던 간헐적 실패를 고쳤습니다.

# 3.0.0-alpha.2 — 2026-09-08 (개발 중, 미발행)

- Antigravity CLI(`agy`) 호스트를 공식 플러그인 경로에 설치하고 훅 두 개를 실제 실행해 검증합니다.
- 호스트별 이벤트·설치 경로·감지 표식을 `gtg/platforms.py` 한 곳으로 모았습니다.
- 설치기가 호스트 설정 파일을 감지해 한 명령으로 설치·검사·제거하며 부분 실패를 함께 보고합니다.
- 완료 주장을 명령·종료 코드·파일 지문에 묶는 `certify`와 상태 DB 없이 재실행하는 `replay`를 추가했습니다.
- 같은 사례·요청·채점 기준을 공유할 때만 결과를 모으는 `evals.harness compare`를 추가했습니다.
- 긴 작업의 자동 재개 예산을 작업 명세의 `max_resumes`로 정합니다. 기본 2, 상한 8입니다.
- 모든 작업 명령이 `--workspace`를 받고, 조회 명령은 상태 없는 폴더에 새 DB를 만들지 않습니다.
- 규칙 파일 12,000자 한도와 스킬 메타데이터의 꺾쇠 금지를 패키지 검증에 넣었습니다.
- `.gtg` 상태 폴더가 자기 자신을 무시하고, 결과를 만들지 않는 명령은 새 작업에 등록되지 않습니다.

# 3.0.0-alpha.1 — 2026-09-08 (사전 릴리스)

- Python 실행 코어·현재 파일 해시 기반 증거·재시작 상태를 구현했습니다.
- Antigravity와 Gemini CLI 훅·패키징을 분리하고 검증 후 설치·백업·복구를 추가했습니다.
- 특정 모델과 슬래시 명령을 요구하는 프로필을 작업별 스킬로 대체했습니다.
- 기존 작업 조회·새 세션 연결·검증 및 메모 보존 경로를 추가했습니다.
- 기존 113개 경로의 원문을 보존하고 중복 프로필 86개 경로를 제거했습니다.
- 실제 오류 수정·종료 후 재개·새 세션 연결을 제한된 사례에서 확인했습니다. 다른 모델과 경쟁 환경 대비 성능은 미검증입니다.
- 상태 안내를 축약하고 생략 정보와 현재 파일 재검증을 유지했습니다.

# Changelog

## Unreleased

## v2.15.0 — 2026-09-03

- updates harness target model from Gemini 3.7 Flash (High) to **Gemini 3.8 Flash (High)** (`gemini-3.8-flash`)
- renames focused skill and directory from `gemini-37-flash-high` to `gemini-38-flash-high`
- updates profile integrity checks, verification contracts, and manifests for Gemini 3.8 Flash
- updates all multi-language documentation and landing pages

## v2.14.0 — 2026-08-24

- completely removed all hooks, hook runner code, tests, and CI hook steps
- added documentation website to docs/ for GitHub Pages deployment
- enforced complete sentence endings and banned AI Slop UI patterns

- adds explicit prohibition against "AI-style narrative text" and "AI technical exposition text" across harness rules and human-copy skills
- strictly bans short-answers (unless essential for compact UI labels) and enforces natural, complete sentence endings (~합니다, ~해요)
- enforces friendly, non-technical explanations accessible to non-developers without technical jargon
- upgrades website presentation to **Apple Liquid Glass UI** with visionOS/macOS materials, SF Pro typography, and Apple.com minimalist layout
- synchronizes versioning and entrypoint assembly to v2.13.0

## v2.12.0 — 2026-08-23

- completely ports all 22 global engineering rules (0. Communication to 21. Hard Prohibitions) from `GEMINI.md` without omission, truncation, or invention
- introduces the **500-Line Limit Rule (500 LOC)** preventing single-file bloat and enforcing single-responsibility component decomposition
- embeds the 7-step debugging pipeline and 4-field blocker reporting format (`Tested`, `Failed`, `Ruled out`, `Next cause`)
- integrates strict security gates covering 9 sensitive files and dangerous command execution bans
- completely redesigns the presentation site with **Microsoft Windows 11 & WinUI 3 Fluent Design System 2.0** (Mica surfaces, Settings Cards, Windows Terminal, TitleBar)
- synchronizes versioning across all components to v2.12.0

## v2.11.3 — 2026-08-23

- establishes repository root `VERSION` as the single source of truth for version management
- adds `scripts/sync_version.py` to synchronize profile versions, manifests, entrypoint assembly, and cleanup in one step
- adds automated dynamic pruning in `scripts/install.sh` to remove non-active version directories without hardcoding
- resolves scattered version strings and prevents legacy version accumulation across updates

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

- updates model target and system prompt optimizations for Gemini 3.8 Flash (High) with hybrid reasoning and thinking token budget allocation
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
```
