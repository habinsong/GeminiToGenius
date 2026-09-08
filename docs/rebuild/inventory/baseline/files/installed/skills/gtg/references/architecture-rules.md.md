# `installed/skills/gtg/references/architecture-rules.md`

- 형식: `100644`
- 바이트: 2096
- SHA-256: `016b6c8956913364f304d6eebd1ed37fbc5006039c305c7e79b8874bfeb43d12`
- 인코딩: `utf-8`

```
# 아키텍처 및 단순성 원칙 (Architecture & Simplicity)

이 문서는 GEMINI.md의 단순성 우선 원칙과 500줄 제한(500-Line Limit Rule)을 포함한 아키텍처 설계 규율을 원문 그대로 정의합니다.

---

## 3. Simplicity First

Minimum code that solves the problem. Nothing speculative.

* No features beyond what was asked.
* No abstractions for single-use code.
* No “flexibility” or “configurability” that was not requested.
* No new framework unless explicitly required.
* No new dependency if existing code or standard library can solve it.
* No error handling for impossible scenarios.
* No premature plugin/hook/agent/skill system unless repeated use is clear.
* If a solution becomes much larger than the problem, simplify before finalizing.

Ask internally: “Would a senior engineer say this is overcomplicated?”
If yes, rewrite smaller.

---

## 15. Architecture Rules

* Prefer boring, explicit code over clever abstractions.
* Keep boundaries clear.
* Prevent God Objects: do not concentrate unrelated state, behavior, orchestration, and I/O in one type or file.
* 500-Line Limit Rule: No single file should exceed 500 lines of code (LOC) without a compelling, documented justification. When a file approaches or exceeds this limit, decompose it into cohesive sub-modules across dedicated directories and files based on clear responsibilities (e.g., UI state, domain logic, persistence/IO, external processes, presentation) rather than performing superficial line splits. Maintain high cohesion and low coupling so that each component remains independently maintainable.
* Avoid global mutable state unless already established.
* Avoid hidden side effects in utility functions.
* Keep UI state, domain logic, and IO separate when practical.
* Preserve existing architecture unless the task is explicitly architectural.
* Do not introduce speculative interfaces, adapters, registries, or factories.

When proposing architecture changes, include:

* Current problem.
* Proposed structure.
* Migration path.
* Tradeoffs.
* Verification plan.
```
