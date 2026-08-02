# GeminiToGenius

> Gemini 를 덜 멍청하게 만드는 하네스입니다.

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

필수 명령은 `git`, `python3`, `rsync`입니다. `/GTG` UI 검증에는 이미 설치된 Google Chrome 또는 Chromium도 필요합니다. `Installed agy-focus v...`가 보이면 Antigravity 또는 Antigravity IDE를 다시 실행합니다.

## 설치되는 것

| 항목 | 현재값 |
| --- | --- |
| 대상 모델 | Gemini 3.6 Flash (High) |
| 항상 주입되는 규칙 | 12개 |
| 수명 주기 훅 | 14개 |
| 집중 스킬 | 11개 |
| 외부 플러그인 | 없음 |
| MCP | 접속 자체가 작업 목적일 때만 |

일반 요청은 자동으로 분류합니다. 저장소·UI 작업을 엄격 모드로 진행할 때는 `/GTG`로 시작합니다.

```text
/GTG "habinsong/GeminiToGenius" 를 설명하는 웹페이지 만들어줘
```

`/GTG`는 요청이 끝날 때까지 코드 우선 탐색, 파일 전체 읽기, 원격 저장소 1차 근거, UI 소스 쓰기 전 계획, 공식 UI 출처 4개·호스트 3개·근거 분야 3개, 웹페이지·랜딩·정적 페이지의 2개 이상 경로, 320px·768px·데스크톱 브라우저 렌더, 계획-구현 대조와 쓰기 후 검증을 유지합니다.

## `GEMINI.md`를 항상 두는 이유

- Antigravity는 `~/.gemini/GEMINI.md`를 [전역 규칙](https://antigravity.google/docs/ide/rules)으로 읽습니다.
- v2.6.0 진입점은 5,992자입니다. 소스 우선 라우팅·안전·근거·계획·완료·UI 감사 게이트만 둡니다.
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
bash scripts/install.sh --version v2.6.0
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

- IDE-native `analyze`·`inspect`·`explore`로 README·docs·workspace 폴더·파일 트리를 먼저 분석하는 경로도 같은 소스 인테이크 게이트에서 차단합니다. 디렉터리 요약은 소스 읽기로 세지 않습니다.
- 훅 payload로 들어오는 미등록 분석·탐색 도구도 소스 인테이크 전에는 기본 거부합니다. `view_file`과 등록된 검증 명령만 명시적 경로로 남깁니다.

- 모호한 AI 카피, 미래 타령, 요술봉 아이콘, 가짜 지표·대시보드, 장식용 3D 이미지를 넣지 않습니다.
- 보라·파랑 기본 그라데이션, 유리·글로우, 중첩 둥근 카드, 동일 여백·반경 반복, 이유 없는 애니메이션을 쓰지 않습니다.
- 실제 제품·사용자 작업·데이터·상태·정보 위계·기존 디자인 시스템·접근성을 근거로 화면을 만듭니다.
- 모바일 우선, 320 CSS px 리플로우, 768px 중간 폭 전환, 보이는 포커스, 움직임 감소 설정, 측정된 성능 근거를 확인합니다.
- 기본 제공 `verify_ui_render.py`로 설치된 Chrome의 320px·768px·1280px 수평 잘림과 문서·접근성 계약을 계측하고 모든 폭의 스크린샷을 만듭니다. Playwright를 설치하지 않습니다.
- `/GTG` UI 소스 변경 전 `docs/plans/design-plan.md`, `implementation-plan.md`, `verification-plan.md`를 작성하고 `verify_plan.py --require-multi-page --require-ui-evidence`를 실행합니다. 웹페이지·랜딩·정적 페이지는 기본 2개 이상 경로로 만들고 `verify_multi_page.py`로 모든 경로를 확인합니다.
- UI 방향은 공식 출처 4개 이상을 서로 다른 호스트 3개·근거 분야 3개로 대조한 뒤 evidence matrix에 발견·결정·구현 영향·검증 기준을 남깁니다.
- 저장소 구조를 먼저 잡고 영향 범위의 실제 코드·호출 경로·상태·데이터·테스트를 끝까지 읽습니다. README와 검색 조각은 구현 근거가 아닙니다. `cat`, `sed`, `rg`, `find`, `ls`, `tree`, `fd`, `git show`, `git ls-files` 같은 shell 읽기·목록 명령은 소스 인테이크가 끝날 때까지 차단하며, 마지막 검증은 실제 성공 결과가 있어야 인정합니다.
- `/GTG` 읽기·검토·진단 작업도 `Stop`에서 소스와 관련 테스트 전체 읽기를 확인합니다. 변경하지 않는다는 이유로 README·docs만 읽고 완료하는 경로는 허용하지 않습니다.
- 다른 GitHub 저장소를 설명할 때는 README·저장소 개요와 별도의 설치 스크립트·manifest·실제 소스 중 하나를 직접 읽습니다. 검색 요약은 근거로 세지 않습니다.
- UI 상태·도메인 판단·입출력·영속화·외부 프로세스를 한 God Object에 몰아넣지 않습니다.

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
