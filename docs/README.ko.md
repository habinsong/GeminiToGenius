# GeminiToGenius

> Gemini 를 덜 멍청하게 만드는 하네스입니다.

[English](../README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

Gemini 3.7 Flash (High)를 Antigravity와 Antigravity IDE에서 쓰기 위한 전역 규칙·훅·스킬 묶음입니다.

## 처음 설치

macOS에서 아래 한 줄만 실행합니다.

```bash
git clone https://github.com/habinsong/GeminiToGenius.git && bash GeminiToGenius/scripts/install.sh
```

스크립트가 순서대로 처리합니다.

1. `git pull --ff-only`로 저장소를 최신화합니다.
2. 기존 Gemini 프로필을 날짜가 붙은 폴더로 옮깁니다.
3. 현재 프로필(v2.12.0)을 설치합니다.
4. 프로필과 훅을 검증합니다.

`curl | sh`는 쓰지 않습니다. 먼저 저장소를 받은 뒤 그 안의 스크립트를 실행합니다.

필수 명령은 `git`, `python3`, `rsync`입니다. `/GTG` UI 검증에는 이미 설치된 Google Chrome 또는 Chromium도 필요합니다. `Installed agy-focus v2.12.0`가 보이면 Antigravity 또는 Antigravity IDE를 다시 실행합니다.

## 설치되는 것

| 항목 | 현재값 (v2.12.0) |
| --- | --- |
| 대상 모델 | Gemini 3.7 Flash (High) 하이브리드 추론 |
| 전역 엔지니어링 규칙 | 22개 완전 규칙 (GEMINI.md 100% 매핑) |
| 아키텍처 가드레일 | 500줄 제한 규칙 (500-Line Limit Rule) |
| 디버깅 파이프라인 | 7단계 디버깅 및 4대 필수 보고 포맷 |
| UI/UX 디자인 시스템 | Windows 11 & WinUI 3 Fluent Design System 2.0 |
| 수명 주기 훅 | 14개 |
| 집중 스킬 | 11개 |
| 외부 플러그인 | 없음 |
| MCP | 접속 자체가 작업 목적일 때만 |

일반 요청은 자동으로 분류합니다. 저장소·UI 작업을 엄격 모드로 진행할 때는 `/GTG`로 시작합니다.

```text
/GTG "habinsong/GeminiToGenius" 를 설명하는 웹페이지 만들어줘
```

`/GTG`는 요청이 끝날 때까지 복명복창, 코드 우선 탐색, 파일 전체 읽기, 500줄 제한 준수, 외과수술식 최소 변경, 320px·768px·데스크톱 브라우저 렌더, 쓰기 후 직접 검증을 유지합니다.

## `GEMINI.md`를 항상 두는 이유

- Antigravity는 `~/.gemini/GEMINI.md`를 [전역 규칙](https://antigravity.google/docs/ide/rules)으로 읽습니다.
- v2.12.0 진입점은 복명복창, 단일 책임 원칙, 500줄 제한, 7단계 디버깅 및 엄격 검증 게이트를 포함한 22개 전역 엔지니어링 표준을 확립합니다.
- 코드·아키텍처·UI·카피·조사 절차는 관련 작업에서만 [집중 스킬](https://antigravity.google/docs/skills?app=antigravity-ide)로 불러옵니다.
- [훅](https://antigravity.google/docs/hooks)이 고위험 경계를 검사하므로 모든 프롬프트에 전체 절차를 넣지 않습니다.
- 무관한 저장소 이력과 작업별 문서는 기본 주입하지 않습니다.

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
"hooks": 14
"skills": 11
hook runner tests passed
```

## 버전 변경

현재 버전과 과거 버전 모두 설치 스크립트로 바꿉니다. 최신화 → 백업 → 설치 → 검증 순서는 같습니다.

```bash
bash scripts/install.sh --version v2.12.0
bash scripts/install.sh --help
```

`bash scripts/install.sh`를 실행하면 다시 최신 버전으로 돌아옵니다.

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

## UI·구현 규칙

- **Zero AI Slop**: 모호한 AI 마케팅 카피, 요술봉 아이콘, 가짜 지표, 장식용 3D 요소를 철저히 배제합니다.
- **Windows 11 & WinUI 3 디자인 시스템**: 정통 Mica/Acrylic 서피스, Settings Cards, ToggleSwitch, Windows Terminal을 적용합니다.
- **500줄 제한 규칙 (500-Line Limit Rule)**: 단일 파일 500줄을 초과하지 않으며 SRP 기반 하위 모듈 분해를 원칙으로 합니다.
- **풀뷰 소스 탐색**: 1줄부터 끝까지 연속 탐색하며 부분 snippet 및 임의 환각을 금지합니다.
- **Chrome 3단 시각 계측**: `verify_ui_render.py`를 통해 320px·768px·1280px 수평 잘림 제로를 검증합니다.
- **5대 표준 응답 포맷**: 변경 요약, 수정 파일, 실행 명령, 검증 결과, 남은 리스크 5대 필드로 완결 보고합니다.

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
