# GeminiToGenius

Gemini를 천재로 만들지는 않습니다.
딴짓을 줄이고, 지시를 끝까지 보게 합니다.

## 정체

운영 하네스라고 불러도 됩니다.

- 전역 지침 12개
- 훅 8개
- 스킬 4개
- `v1.0.0` → `v1.13.0` 버전 기록
- 외부 플러그인 0개
- MCP는 연결이 목적일 때만
- 대상: Antigravity / Antigravity IDE
- 모델 기준: Gemini 3.6 Flash (High)

핵심은 화려한 프롬프트가 아닙니다. 볼 것만 남기는 것입니다.

## 들어있는 것

- `agy-focus/versions/` — 버전별 원본
- `agy-focus/current` — 현재 프로필
- `agy-focus/hooks/` — 8개 훅과 훅 설정
- `agy-focus/skills/` — 집중 유지용 스킬
- `agy-focus/state/` — 공개용 런타임 스냅샷
- `installed/` — 전역 설치 상태의 현재 스냅샷
- `legacy/` — 원본 지침 보관본

`.pyc`, `__pycache__`, `.DS_Store`는 넣지 않았습니다. 실행 흔적이지 설정이 아니기 때문입니다.

## 설치

기존 설정을 먼저 백업한 뒤 실행합니다.

```bash
mkdir -p "$HOME/.gemini/config"
mkdir -p "$HOME/.gemini/config/agy-focus"
cp -a agy-focus/. "$HOME/.gemini/config/agy-focus/"
ln -sfn versions/v1.13.0 "$HOME/.gemini/config/agy-focus/current"
ln -sfn config/agy-focus/current/GEMINI.md "$HOME/.gemini/GEMINI.md"
ln -sfn agy-focus/current/hooks/hooks.json "$HOME/.gemini/config/hooks.json"
ln -sfn agy-focus/current/skills "$HOME/.gemini/config/skills"
```

설치 후 검증:

```bash
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
```

버전 변경은 `current` 링크만 바꾸면 됩니다.

```bash
ln -sfn versions/v1.12.0 "$HOME/.gemini/config/agy-focus/current"
```

## 운영 원칙

- 자연어 지침은 짧게 쪼갭니다.
- 모델에게 현재 작업과 창 상태만 보게 합니다.
- AI Slop, 목적 없는 효과, 모호한 카피, 카드 중첩, 기계적 반응형 레이아웃을 막습니다.
- UI는 기능이 먼저입니다. 보라-파랑 그라데이션과 요술봉은 쉬어도 됩니다.

## 라이선스

필요한 라이선스를 정하기 전까지는 별도 라이선스를 선언하지 않습니다.
