# GeminiToGenius

> Gemini를 더욱 똑똑하고 안전하게 만드는 AI 코딩 보조 하네스입니다.

[English](../README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

Gemini 3.7 Flash (High)를 Antigravity 및 Antigravity IDE에서 사용하기 위한 전역 규칙·훅·스킬 묶음입니다.

## 처음 설치하기

macOS 터미널에서 아래 한 줄의 명령어를 실행해 주세요.

```bash
git clone https://github.com/habinsong/GeminiToGenius.git && bash GeminiToGenius/scripts/install.sh
```

설치 스크립트가 다음 순서대로 안전하게 처리합니다.

1. `git pull --ff-only`로 최신 변경사항을 가져옵니다.
2. 기존에 설치되어 있던 Gemini 프로필을 날짜가 적힌 백업 폴더로 안전하게 옮깁니다.
3. 최신 프로필(v2.13.0)을 새롭게 설치합니다.
4. 설치된 프로필과 검증 훅이 정상적으로 동작하는지 확인합니다.

`curl | sh` 방식은 사용하지 않으며, 먼저 저장소를 내려받은 뒤 스크립트를 직접 실행합니다.

필요한 프로그램은 `git`, `python3`, `rsync`입니다. 화면 디자인 검증을 진행할 때는 이미 설치된 Google Chrome 또는 Chromium이 함께 사용됩니다. 설치가 끝나고 `Installed agy-focus v2.13.0` 메시지가 보이면 Antigravity 또는 Antigravity IDE를 다시 시작해 주세요.

## 설치되는 항목 안내

| 항목 | 현재 설정값 (v2.13.0) |
| --- | --- |
| 대상 AI 모델 | Gemini 3.7 Flash (High) 하이브리드 추론 |
| 전역 엔지니어링 규칙 | 22가지 핵심 원칙 (GEMINI.md 원문 100% 반영) |
| 파일 크기 제한 규칙 | 500줄 제한 규율 (파일 하나당 최대 500줄로 나누기) |
| 오류 해결 과정 | 7단계 디버깅 및 막힌 부분 솔직 보고 양식 |
| UI/UX 품질 기준 | 사용자 과업 중심 & Zero AI Slop UI 검증 |
| 자동 보호 훅 | 14개 |
| 역할별 전담 스킬 | 11개 |
| 불필요한 플러그인 | 없음 |
| 외부 서버 연결 | 사용자가 명시적으로 요청했을 때만 연결 |

일반적인 요청은 자동으로 알맞게 처리됩니다. 코드를 깊이 있게 수정하거나 웹 화면을 꼼꼼하게 만들고 싶으실 때는 `/GTG`를 입력하여 시작해 주세요.

```text
/GTG "habinsong/GeminiToGenius" 를 설명하는 웹페이지 만들어줘
```

`/GTG` 모드가 켜지면 작업이 완전히 끝날 때까지 사용자의 지시를 다시 확인하고, 파일을 처음부터 끝까지 빠짐없이 읽으며, 문제가 있는 부분만 조심스럽게 고친 뒤 브라우저 화면 검증까지 꼼꼼하게 진행합니다.

## `GEMINI.md`를 전역 규칙으로 두는 이유

- Antigravity는 `~/.gemini/GEMINI.md` 파일을 [전역 규칙](https://antigravity.google/docs/ide/rules)으로 읽어 들입니다.
- v2.13.0 진입점은 지시 사항 확인, 파일 분리, 500줄 제한, 7단계 디버깅 등 22가지 핵심 엔지니어링 표준을 항상 기억하도록 돕습니다.
- 복잡한 세부 절차는 필요할 때만 [전담 스킬](https://antigravity.google/docs/skills?app=antigravity-ide)을 통해 알맞게 불러옵니다.
- [보호 훅](https://antigravity.google/docs/hooks)이 위험한 행동을 미리 막아주므로, 매번 긴 프롬프트를 일일이 적지 않아도 안전하게 작업할 수 있습니다.

## 기존 사용자 업데이트 방법

이전에 내려받았던 폴더에서 아래 명령어를 실행해 주세요.

```bash
cd /path/to/GeminiToGenius
bash scripts/install.sh
```

설치 스크립트가 저장소를 먼저 최신으로 업데이트하므로, 이전 버전이 자동으로 최신 버전으로 갱신됩니다. 만약 작업 중이던 변경사항이 있다면 먼저 커밋하거나 정리한 뒤에 실행해 주세요.

실행할 때마다 아래와 같은 복구용 백업 경로가 안내됩니다.

```text
/Users/you/.gemini-backup-YYYYMMDD-HHMMSS
```

## 정상 설치 여부 확인하기

```bash
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
python3 "$HOME/.gemini/config/agy-focus/current/scripts/test_hook_runner.py"
```

아래와 같은 결과가 나오면 정상적으로 설치된 것입니다.

```text
"ok": true
"rules": 12
"hooks": 14
"skills": 11
hook runner tests passed
```

## 버전 변경하기

원하는 버전으로 언제든지 쉽게 전환하실 수 있습니다.

```bash
bash scripts/install.sh --version v2.13.0
bash scripts/install.sh --help
```

## 삭제하는 방법

연결된 링크를 해제하고 프로필을 날짜가 적힌 폴더로 안전하게 옮깁니다. 폴더는 임의로 삭제되지 않습니다.

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

## 이전 백업으로 되돌리기

설치 스크립트가 화면에 보여주었던 실제 백업 경로를 입력해 주세요.

```bash
BACKUP_DIR="$HOME/.gemini-backup-YYYYMMDD-HHMMSS"
mv "$BACKUP_DIR/config/agy-focus" "$HOME/.gemini/config/agy-focus"
mv "$BACKUP_DIR/GEMINI.md" "$HOME/.gemini/GEMINI.md"
mv "$BACKUP_DIR/config/hooks.json" "$HOME/.gemini/config/hooks.json"
mv "$BACKUP_DIR/config/skills" "$HOME/.gemini/config/skills"
```

## 주요 핵심 규칙 안내

- **AI 특유의 서술 텍스트 배제**: 모호한 과장 광고 문구, 가짜 지표, 불필요한 AI 해설조 말투를 일절 사용하지 않습니다.
- **제품 근거 기반의 UI/UX 디자인**: 실제 제품과 사용자 과업에 필요한 직관적인 화면 구조와 명확한 계층을 적용합니다.
- **사람이 작성한 친절한 설명**: 비전공자도 쉽게 이해할 수 있는 일상적인 표현과 온전한 문장형 종결어미(~합니다, ~해요)로 서술합니다.
- **파일 500줄 제한 규칙**: 파일 하나가 너무 커지지 않도록 역할을 깔끔하게 나누어 유지보수를 쉽게 합니다.
- **전체 파일 꼼꼼히 읽기**: 1번째 줄부터 마지막 줄까지 틈 없이 읽은 뒤 수정하며, 대충 넘겨짚지 않습니다.
- **브라우저 화면 정밀 측정**: 모바일(320px), 태블릿(768px), PC(1280px) 전 화면에서 글자가 잘리지 않는지 측정합니다.

## 라이선스

MIT 라이선스에 따라 자유롭게 사용하고 수정하실 수 있습니다. 상세한 내용은 [LICENSE](../LICENSE) 파일을 참고해 주세요.
