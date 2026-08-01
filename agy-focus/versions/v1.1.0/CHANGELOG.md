# agy-focus 변경 기록

## 1.1.0 — 2026-08-01

- 범용 `agy-one-tap` 작업 라우터 스킬을 추가했습니다.
- Gemini 3.6 Flash의 직접적·구조화된 지시, 선행 검사, 도구·턴 절감 특성에 맞춰 실행 루프를 정리했습니다.
- 공식 훅 계약에 맞춰 `Stop`이 항상 `decision`을 반환하도록 고쳤습니다.
- 훅 실행 경로를 workspace 의존 상대경로에서 사용자 전역 설정 경로로 바꿨습니다.
- 이전 훅 실패를 다음 invocation의 짧은 재집중 앵커로 전달합니다.
- `rm -rf`, `git reset --hard`, 외부 설치·네트워크 명령 판별을 보강했습니다.
- 전역 프로필을 한 번에 점검하는 읽기 전용 `scripts/verify_profile.py`를 추가했습니다.
- `/agy-one-tap`으로 호출하는 글로벌 Workflow를 추가했습니다.

## 1.0.0 — 2026-08-01

- 12개 전역 규칙, 8개 lifecycle 훅, `focus-session`, `gemini-36-flash-high` 스킬을 구성했습니다.
- 공통 지침 복구 기준본은 `~/.gemini/GEMINI.legacy-2026-08-01.md`에 보존했습니다.
