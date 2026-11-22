# md

모델마다 따로 다듬은 지침입니다. 모델 하나에 폴더 하나(`md/계열/모델/`)가 있고, 폴더 안의 파일 이름은 어느 모델이든 거의 같습니다. 쓰는 모델이 목록에 없으면 [`universal/`](../universal/README.md)을 보세요.

## 전역 지침

폴더마다 `AGENTS.md`가 있고, Claude 계열은 `CLAUDE.md`, Gemini 계열은 `GEMINI.md`입니다. AI 도구가 이 이름으로 찾아 읽습니다. 프로젝트 루트에 넣으면 그 프로젝트에서만, `~/.codex`나 `~/.claude`, `~/.gemini`에 넣으면 모든 프로젝트에서 적용됩니다.

## 분야 문서

전역 지침 위에 하는 일에 맞는 파일을 프로젝트에 더하세요. 분야 문서에는 전역 지침과 겹치는 규칙이 없고, 그 분야의 규칙(1절)과 이 모델이 그 분야에서 지킬 점(2절)만 들어 있습니다. 모델 전용 2절을 쓸 만한 근거가 없는 모델과 분야에는 어떤 모델이든 쓸 수 있는 범용 2절("어떤 모델이든 지킬 점")을 넣었습니다. 분야가 정해지지 않았으면 전역 지침만 쓰면 됩니다. 붙이는 방법은 [`universal/README.md`](../universal/README.md)에 있습니다.

| 파일 | 쓰는 일 |
|---|---|
| `web.md` | 웹 프런트엔드, 백엔드 API, 풀스택 |
| `app.md` | iOS와 Android 앱, 크로스플랫폼 앱 |
| `native.md` | 데스크톱 프로그램, CLI, 드라이버 같은 컴파일하는 소프트웨어 |
| `hardware.md` | 회로와 PCB 설계, 부품 선정, FPGA용 HDL |
| `firmware.md` | MCU와 SoC 펌웨어, RTOS, 부트로더 |
| `web-research.md` | 최신 정보 조사, 사실 확인, 출처 수집 |
| `research.md` | 논문, 실험, 데이터 분석 |
| `tech-research.md` | 기술 선정, 도입 타당성, 특허와 라이선스 조사 |
| `ko-academic.md` | 논문, 초록, 기술 보고서 같은 한국어 학술 글의 윤문 |
| `ko-everyday.md` | 메신저, 이메일, 블로그 같은 한국어 일상 글의 윤문 |
| `ko-literary.md` | 소설, 수필, 칼럼 같은 한국어 문학 글의 윤문 |

한국어 윤문 문서 세 개는 GPT, Claude, Google(Gemini와 Gemma) 계열에만 있습니다.

사양, 가격, 벤치마크와 출처는 [`docs/`](../docs/README.md)에 있습니다.
