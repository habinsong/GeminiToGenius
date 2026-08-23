# 저장소 표준 및 지침 우선순위 (Repository Standards)

이 문서는 GEMINI.md의 지침 우선순위, 저장소 개요/구조/스택 템플릿 및 문서화 규칙을 원문 그대로 정의합니다.

---

## 0.1 Instruction Priority

When instructions conflict, follow this order:

1. Explicit user instruction in the current task.
2. Repository-specific instructions in this AGENTS.md.
3. More specific instructions in nested AGENTS.md files.
4. User global memory.
5. General best practices.

Do not treat placeholders like [PROJECT_NAME], [SHORT_DESCRIPTION], [GOAL_1], or example commands as facts.
Replace placeholders with repository-specific information before acting.
Do not run placeholder commands literally.

---

## 7. Repository Overview

[PROJECT_NAME] is a [SHORT_DESCRIPTION].

Primary goals:

* [GOAL_1]
* [GOAL_2]
* [GOAL_3]

Non-goals:

* Do not introduce cloud dependencies unless explicitly requested.
* Do not rewrite stable working code for style-only reasons.
* Do not create speculative abstractions.
* Do not change package manager, build system, or design system without explicit instruction.

---

## 8. Repository Map

Update this section when the repository structure changes.

```text
.
├── src/                 # Main source code
├── tests/               # Tests
├── docs/                # Architecture, design, and project documentation
├── scripts/             # Local automation scripts
├── README.md            # Human-facing overview
└── AGENTS.md            # Agent-facing rules
```

Important files:

* README.md: human-facing overview.
* AGENTS.md: agent-facing operating contract.
* docs/: durable project decisions.
* PROJECT_NOTES.md: optional local project notes. Do not commit unless intentionally shared.

---

## 9. Tech Stack

Replace this section with actual project details.

* Language: [TypeScript / Swift / Rust / Python / Kotlin / etc.]
* Runtime: [Node / Bun / Deno / SwiftPM / Cargo / etc.]
* Framework: [React / Tauri / Next.js / SwiftUI / etc.]
* Package manager: [pnpm / npm / bun / yarn / etc.]
* Test runner: [Vitest / Jest / Playwright / XCTest / cargo test / pytest / etc.]
* Lint/format: [ESLint / Biome / Prettier / SwiftFormat / ruff / etc.]

Use the repository’s existing conventions.

---

## 18. Documentation Rules

Update documentation when behavior, setup, commands, or architecture changes.

Good documentation is:

* Short.
* Specific.
* Close to the code it explains.
* Focused on durable facts.

Do not create large docs unless requested.
