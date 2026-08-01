# GeminiToGenius

Gemini 3.6 Flash (High)용 집중 유지 하네스입니다.
Antigravity와 Antigravity IDE의 전역 설정을 버전별로 관리합니다.

## 구성

- 전역 지침 12개
- 훅 8개
- 스킬 4개
- `v1.0.0`부터 `v1.13.0`까지의 버전 기록
- 외부 플러그인 없음
- MCP는 필요한 작업에서만 연결

## 설치

macOS 기준입니다. 기존 Gemini 설정을 먼저 백업합니다.

### 1. 저장소 받기

```bash
git clone https://github.com/habinsong/GeminiToGenius.git
cd GeminiToGenius
```

### 2. 기존 설정 백업

```bash
BACKUP_DIR="$HOME/.gemini-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR" "$HOME/.gemini/config"

if [ -e "$HOME/.gemini/config/agy-focus" ] || [ -L "$HOME/.gemini/config/agy-focus" ]; then
  mv "$HOME/.gemini/config/agy-focus" "$BACKUP_DIR/agy-focus"
fi

if [ -e "$HOME/.gemini/GEMINI.md" ] || [ -L "$HOME/.gemini/GEMINI.md" ]; then
  mv "$HOME/.gemini/GEMINI.md" "$BACKUP_DIR/GEMINI.md"
fi

if [ -e "$HOME/.gemini/config/hooks.json" ] || [ -L "$HOME/.gemini/config/hooks.json" ]; then
  mv "$HOME/.gemini/config/hooks.json" "$BACKUP_DIR/hooks.json"
fi

if [ -e "$HOME/.gemini/config/skills" ] || [ -L "$HOME/.gemini/config/skills" ]; then
  mv "$HOME/.gemini/config/skills" "$BACKUP_DIR/skills"
fi

printf '%s\n' "$BACKUP_DIR"
```

마지막에 출력된 경로가 백업 위치입니다.

### 3. 프로필 설치

```bash
cp -a agy-focus "$HOME/.gemini/config/agy-focus"

ln -sfn versions/v1.13.0 \
  "$HOME/.gemini/config/agy-focus/current"
ln -sfn config/agy-focus/current/GEMINI.md \
  "$HOME/.gemini/GEMINI.md"
ln -sfn agy-focus/current/hooks/hooks.json \
  "$HOME/.gemini/config/hooks.json"
ln -sfn agy-focus/current/skills \
  "$HOME/.gemini/config/skills"
```

### 4. 설치 확인

```bash
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
```

정상 결과의 기준:

```text
"ok": true
"rules": 12
"hooks": 8
"target": "Gemini 3.6 Flash (High)"
```

Antigravity 또는 Antigravity IDE를 다시 열어 적용 여부를 확인합니다.

## 업데이트

저장소에서 최신 파일을 받습니다.

```bash
cd GeminiToGenius
git pull --ff-only
```

프로필을 다시 설치하려면 `설치`의 2~4단계를 실행합니다.

## 버전 변경

설치된 버전 목록:

```bash
find "$HOME/.gemini/config/agy-focus/versions" \
  -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort -V
```

예를 들어 `v1.12.0`으로 바꾸려면:

```bash
ln -sfn versions/v1.12.0 \
  "$HOME/.gemini/config/agy-focus/current"
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
```

## 디렉터리

- `agy-focus/versions/` — 버전별 지침·훅·스킬 원본
- `agy-focus/current` — 현재 선택된 버전을 가리키는 심볼릭 링크
- `agy-focus/state/` — 공개용 런타임 스냅샷
- `installed/` — 현재 전역 설치 파일 복사본
- `legacy/` — 이전 전역 지침 보관본

실행 중 생성되는 `__pycache__`, `*.pyc`, `.DS_Store`는 저장하지 않습니다.

## UI 작업 규칙

- AI Slop 금지
- 모호한 헤드라인과 추상 아이콘 금지
- 목적 없는 호버·애니메이션 금지
- 카드 중첩과 기계적인 대칭 레이아웃 금지
- `Inter`·`Roboto` 기본 사용 금지
- 보라색·파란색 네온 그라데이션 남용 금지
- `width: 100%`·`flex-grow: 1` 남용 금지
- `fit-content`·`min-content`·`clamp()` 우선 검토
- 모바일 우선 반응형 구성

## 삭제

설치된 프로필과 링크를 비활성화합니다. 삭제 전용 폴더로 옮기므로 복구할 수 있습니다.

```bash
REMOVED_DIR="$HOME/.gemini-removed-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$REMOVED_DIR"

if [ -L "$HOME/.gemini/GEMINI.md" ]; then
  unlink "$HOME/.gemini/GEMINI.md"
fi

if [ -L "$HOME/.gemini/config/hooks.json" ]; then
  unlink "$HOME/.gemini/config/hooks.json"
fi

if [ -L "$HOME/.gemini/config/skills" ]; then
  unlink "$HOME/.gemini/config/skills"
fi

if [ -d "$HOME/.gemini/config/agy-focus" ]; then
  mv "$HOME/.gemini/config/agy-focus" "$REMOVED_DIR/agy-focus"
fi
```

삭제 전용 폴더까지 지우려면 경로를 확인한 뒤 실행합니다.

```bash
printf '%s\n' "$REMOVED_DIR"
rm -rf "$REMOVED_DIR"
```

설치 전 백업을 복원하려면 백업 폴더를 지정하고 실행합니다.

```bash
BACKUP_DIR="$HOME/.gemini-backup-YYYYMMDD-HHMMSS"
mv "$BACKUP_DIR/agy-focus" "$HOME/.gemini/config/agy-focus"
mv "$BACKUP_DIR/GEMINI.md" "$HOME/.gemini/GEMINI.md"
mv "$BACKUP_DIR/hooks.json" "$HOME/.gemini/config/hooks.json"
mv "$BACKUP_DIR/skills" "$HOME/.gemini/config/skills"
```

## 라이선스

현재 별도 라이선스를 선언하지 않았습니다.
