# 언어별 검증 명령어 규율 (Verification Commands)

이 문서는 GEMINI.md의 언어 및 프레임워크별 표준 검증 명령어와 실행 원칙을 원문 그대로 정의합니다.

---

## 11. Verification Commands

Replace with commands that actually work in this repository.

Use only the commands that match this repository.
Before running a command, confirm the relevant tool exists through package files, lockfiles, or project structure.
Do not run commands for languages or frameworks that are not present in the project.

JavaScript / TypeScript

```bash
pnpm typecheck
pnpm lint
pnpm test
pnpm build
```

Python

```bash
python -m pytest
python -m ruff check .
python -m pyright
```

Rust

```bash
cargo fmt --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test
cargo build
```

Swift / macOS

```bash
swift build
swift test
```

Only run expensive commands when necessary.
Prefer targeted tests while iterating, then full checks before final response.

If verification cannot be run, explain exactly why it was not run and provide the closest manual or static check performed instead.
