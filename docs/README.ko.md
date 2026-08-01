# GeminiToGenius

Gemini 3.6 Flash (High)를 Antigravity와 Antigravity IDE에서 쓰기 위한 버전 관리형 집중 유지 하네스입니다.

[English](../README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

현재 지시, 활성 작업창, 관련 파일, 검증 가능한 결과에만 집중하도록 전역 지침과 실행 경계를 관리합니다.

## 구성

- 항상 주입되는 지침 12개
- 수명 주기 훅 8개
- 집중 유지 스킬 4개
- `v1.0.0`부터 `v1.14.2`까지의 버전 기록
- 외부 플러그인 없음
- MCP는 연결이 필요한 작업에서만 사용

## 만든 이유

항상 주입되는 지침이 길면 잘리거나 영향이 약해집니다. 규칙을 짧은 파일로 나누고, 하나의 진입점으로 생성하며, 모든 변경을 버전으로 남깁니다.

## 설치

macOS 기준입니다. 순서는 `clone → update → backup → install → verify`입니다. 저장소 업데이트가 백업보다 먼저입니다.

```bash
git clone https://github.com/habinsong/GeminiToGenius.git
cd GeminiToGenius
```

새로 받은 저장소는 최신 상태입니다. 기존 저장소를 다시 사용할 때만 업데이트합니다. 이 단계를 끝낸 뒤 현재 프로필을 백업합니다.

```bash
cd GeminiToGenius && git pull --ff-only
```

프로필을 덮어쓰기 전에 백업합니다.

```bash
BACKUP_DIR="$HOME/.gemini-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR" "$HOME/.gemini/config"
if [ -e "$HOME/.gemini/config/agy-focus" ] || [ -L "$HOME/.gemini/config/agy-focus" ]; then mv "$HOME/.gemini/config/agy-focus" "$BACKUP_DIR/agy-focus"; fi
if [ -e "$HOME/.gemini/GEMINI.md" ] || [ -L "$HOME/.gemini/GEMINI.md" ]; then mv "$HOME/.gemini/GEMINI.md" "$BACKUP_DIR/GEMINI.md"; fi
if [ -e "$HOME/.gemini/config/hooks.json" ] || [ -L "$HOME/.gemini/config/hooks.json" ]; then mv "$HOME/.gemini/config/hooks.json" "$BACKUP_DIR/hooks.json"; fi
if [ -e "$HOME/.gemini/config/skills" ] || [ -L "$HOME/.gemini/config/skills" ]; then mv "$HOME/.gemini/config/skills" "$BACKUP_DIR/skills"; fi
printf '%s\n' "$BACKUP_DIR"
```

출력된 경로가 복원 지점입니다. 백업 뒤 프로필을 설치합니다.

```bash
cp -a agy-focus "$HOME/.gemini/config/agy-focus"
ln -sfn versions/v1.14.2 "$HOME/.gemini/config/agy-focus/current"
ln -sfn config/agy-focus/current/GEMINI.md "$HOME/.gemini/GEMINI.md"
ln -sfn agy-focus/current/hooks/hooks.json "$HOME/.gemini/config/hooks.json"
ln -sfn agy-focus/current/skills "$HOME/.gemini/config/skills"
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
```

정상 기준은 `"ok": true`, `"rules": 12`, `"hooks": 8`, `"target": "Gemini 3.6 Flash (High)"`입니다. 설치 후 Antigravity 또는 Antigravity IDE를 다시 실행합니다.

## 업데이트

```bash
cd GeminiToGenius && git pull --ff-only
```

`git pull --ff-only`를 먼저 끝내고, 그 다음 백업→설치→검증 순서로 다시 실행합니다.

## 버전 변경

```bash
find "$HOME/.gemini/config/agy-focus/versions" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort -V
ln -sfn versions/v1.12.0 "$HOME/.gemini/config/agy-focus/current"
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
```

## 삭제 및 복원

```bash
REMOVED_DIR="$HOME/.gemini-removed-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$REMOVED_DIR"
if [ -L "$HOME/.gemini/GEMINI.md" ]; then unlink "$HOME/.gemini/GEMINI.md"; fi
if [ -L "$HOME/.gemini/config/hooks.json" ]; then unlink "$HOME/.gemini/config/hooks.json"; fi
if [ -L "$HOME/.gemini/config/skills" ]; then unlink "$HOME/.gemini/config/skills"; fi
if [ -d "$HOME/.gemini/config/agy-focus" ]; then mv "$HOME/.gemini/config/agy-focus" "$REMOVED_DIR/agy-focus"; fi
printf '%s\n' "$REMOVED_DIR"
```

경로를 확인한 뒤 완전히 삭제합니다.

```bash
rm -rf "$REMOVED_DIR"
```

백업 복원:

```bash
BACKUP_DIR="$HOME/.gemini-backup-YYYYMMDD-HHMMSS"
mv "$BACKUP_DIR/agy-focus" "$HOME/.gemini/config/agy-focus"
mv "$BACKUP_DIR/GEMINI.md" "$HOME/.gemini/GEMINI.md"
mv "$BACKUP_DIR/hooks.json" "$HOME/.gemini/config/hooks.json"
mv "$BACKUP_DIR/skills" "$HOME/.gemini/config/skills"
```

## UI 규칙

- AI Slop 문구, 모호한 헤드라인, 추상적인 요술봉 아이콘 금지
- 목적 없는 호버 효과와 마이크로 인터랙션 금지
- 반복되는 둥근 카드와 기계적인 대칭 레이아웃 금지
- `Inter`·`Roboto` 습관적 사용 금지
- 보라색-파란색 네온 그라데이션 남용 금지
- 내재적 크기, 유체 타이포그래피, 비대칭 배치, 모바일 우선 반응형 우선 검토

## 라이선스

MIT 라이선스입니다. [LICENSE](../LICENSE)를 확인하십시오.
