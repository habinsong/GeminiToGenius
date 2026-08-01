# GeminiToGenius

> Gemini가 실제 작업에서 점점 멍청해져서 만들었습니다. Gemini를 덜 멍청하게 만드는 하네스입니다.

[English](../README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

Gemini 3.6 Flash (High)를 Antigravity와 Antigravity IDE에서 쓰기 위한 전역 규칙·훅·스킬 묶음입니다.

## 처음 설치

macOS에서 아래 한 줄만 실행합니다.

```bash
git clone https://github.com/habinsong/GeminiToGenius.git && bash GeminiToGenius/scripts/install.sh
```

스크립트가 순서대로 처리합니다.

1. `git pull --ff-only`로 저장소를 최신화합니다.
2. 기존 Gemini 프로필을 날짜가 붙은 폴더로 옮깁니다.
3. 현재 프로필을 설치합니다.
4. 프로필과 훅을 검증합니다.

`curl | sh`는 쓰지 않습니다. 먼저 저장소를 받은 뒤 그 안의 스크립트를 실행합니다.

필수 명령은 `git`, `python3`, `rsync`입니다. `Installed agy-focus v...`가 보이면 Antigravity 또는 Antigravity IDE를 다시 실행합니다.

## 설치되는 것

| 항목 | 현재값 |
| --- | --- |
| 대상 모델 | Gemini 3.6 Flash (High) |
| 항상 주입되는 규칙 | 12개 |
| 수명 주기 훅 | 13개 |
| 자동 스킬 | 8개 |
| 외부 플러그인 | 없음 |
| MCP | 접속 자체가 작업 목적일 때만 |

일반 자연어 요청으로 자동 동작합니다. `/`나 `@`는 필요 없습니다.

## 기존 사용자 업데이트

예전 clone에서 아래만 실행합니다.

```bash
cd /path/to/GeminiToGenius
bash scripts/install.sh
```

스크립트가 먼저 저장소를 최신화하므로 예전 프로필도 현재 버전으로 바뀝니다. tracked 변경이 있으면 `git pull` 전에 멈춥니다. 그때는 커밋·stash·정리 중 하나를 먼저 하시면 됩니다.

실행할 때마다 다음과 같은 백업 경로가 출력됩니다.

```text
/Users/you/.gemini-backup-YYYYMMDD-HHMMSS
```

## 설치 확인

```bash
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
python3 "$HOME/.gemini/config/agy-focus/current/scripts/test_hook_runner.py"
```

아래가 보이면 됩니다.

```text
"ok": true
"rules": 12
"hooks": 13
hook runner tests passed
```

## 버전 변경

설치 스크립트는 항상 현재 버전으로 돌아옵니다. 예전 동작을 재현할 때만 직접 바꾸면 됩니다.

```bash
find "$HOME/.gemini/config/agy-focus/versions" \
  -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort -V

ln -sfn versions/v1.12.0 "$HOME/.gemini/config/agy-focus/current"
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
```

나중에 `bash scripts/install.sh`를 실행하면 다시 최신 버전으로 돌아옵니다.

## 삭제

아래 명령은 링크를 끊고 프로필을 날짜 폴더로 옮깁니다. 그 폴더는 지우지 않습니다.

```bash
REMOVED_DIR="$HOME/.gemini-removed-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$REMOVED_DIR/config"

if [ -L "$HOME/.gemini/GEMINI.md" ]; then unlink "$HOME/.gemini/GEMINI.md"; fi
if [ -L "$HOME/.gemini/config/hooks.json" ]; then unlink "$HOME/.gemini/config/hooks.json"; fi
if [ -L "$HOME/.gemini/config/skills" ]; then unlink "$HOME/.gemini/config/skills"; fi
if [ -e "$HOME/.gemini/config/agy-focus" ] || [ -L "$HOME/.gemini/config/agy-focus" ]; then
  mv "$HOME/.gemini/config/agy-focus" "$REMOVED_DIR/config/agy-focus"
fi

printf '%s\n' "$REMOVED_DIR"
```

출력된 경로를 확인한 뒤에만 완전히 지웁니다.

```bash
rm -rf "$REMOVED_DIR"
```

## 백업 복원

설치 스크립트가 출력한 실제 경로를 넣습니다.

```bash
BACKUP_DIR="$HOME/.gemini-backup-YYYYMMDD-HHMMSS"
mv "$BACKUP_DIR/config/agy-focus" "$HOME/.gemini/config/agy-focus"
mv "$BACKUP_DIR/GEMINI.md" "$HOME/.gemini/GEMINI.md"
mv "$BACKUP_DIR/config/hooks.json" "$HOME/.gemini/config/hooks.json"
mv "$BACKUP_DIR/config/skills" "$HOME/.gemini/config/skills"
```

## UI 규칙

- 모호한 AI 카피, 미래 타령, 요술봉 아이콘, 가짜 지표, 장식용 3D 이미지를 넣지 않습니다.
- 보라·파랑 기본 그라데이션, 반복 둥근 카드, 이유 없는 애니메이션을 쓰지 않습니다.
- 실제 작업, 기존 시스템, 정보 위계, 접근성에서 화면을 만듭니다.
- 코드 변경 전 안전한 텍스트 파일을 전부 읽습니다. 검색 결과나 일부 줄은 전체 읽기가 아닙니다.

## 구성

- `agy-focus/versions/` — 버전별 프로필
- `agy-focus/current` — 현재 프로필 링크
- `scripts/install.sh` — 최신화·백업·설치·검증
- `installed/` — 현재 설치 표면 복사본

## 도움말과 기여

- [도움말](../SUPPORT.md)
- [보안](../SECURITY.md)
- [기여](../CONTRIBUTING.md)
- [변경 기록](../CHANGELOG.md)

MIT 라이선스입니다. [LICENSE](../LICENSE)를 확인하세요.
