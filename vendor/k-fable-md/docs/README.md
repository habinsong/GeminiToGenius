# docs

사람이 읽는 조사 기록입니다. AI에게 읽히는 지침은 [`universal/`](../universal/README.md)과 [`md/`](../md/README.md)에 있고, 사양과 가격, 벤치마크, 출처는 여기에만 있습니다. 모델마다 `docs/계열/모델/` 폴더가 하나씩 있습니다.

## 폴더 구조

```text
docs/
├── README.md                         이 문서
├── _common/                          계열과 모델에 공통인 조사 기록
│   ├── domain-rules/분야.md          분야별 규칙의 근거 수준 (행 단위 대조 표, 8개 분야)
│   ├── generic-notes.md              모델 전용 2절이 없을 때 쓰는 범용 2절의 근거
│   └── korean-writing/               한국어 문체 조사 기록 (측정 도구, 실측, 문장 원리, 서지)
└── 계열/모델/
    ├── README.md                     해당 모델 조사 기록의 색인
    ├── overview.md                   모델의 위치, 연혁, 사양, 라이선스
    ├── performance.md                성능 근거 (벤더 자체 수치와 독립 평가 해석)
    ├── operations.md                 실제 운용 (행동 특성, API와 하네스와 로컬 구동, 데이터 정책)
    ├── critique.md                   비판적 평가와 맞는 상황, 맞지 않는 상황
    ├── sources.md                    출처 주소, 확인 수준, 조사상 한계
    ├── xcheck.md                     공식 문서 외 복수 출처와의 교차 검증 결과
    ├── domains/분야.md               웹, 앱, 하드웨어 같은 분야별 운용 조사와 출처
    └── korean-writing.md             한국어 윤문 세 분야의 모델별 조사 기록 (주요 네 계열)
```

내용이 없는 파일은 만들지 않았습니다. 성능 근거를 확인하지 못한 모델에는 `performance.md`가 없습니다.

## md 지침 문서와의 대응

| `md/계열/모델/`의 지침 문서 | `docs/계열/모델/`의 조사 문서 |
|---|---|
| 전역 지침(`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) | `overview.md`, `performance.md`, `operations.md`, `critique.md`, `sources.md`, `xcheck.md` |
| `web.md`, `app.md`, `native.md`, `hardware.md`, `firmware.md`, `web-research.md`, `research.md`, `tech-research.md` | `domains/` 안의 같은 이름 파일 |
| `ko-academic.md`, `ko-everyday.md`, `ko-literary.md` | `korean-writing.md` (세 분야의 조사를 하나로 통합) |

`domains/` 문서의 절 번호는 지침 문서와 같습니다. 1절은 분야 규칙, 2절은 이 모델의 분야 운용입니다. 복명복창과 보고 형식, 작업 원칙은 전역 지침이 맡습니다. 지침 문서의 2절은 이 폴더의 2절에서 근거 표기와 수치를 걷어 낸 것이고, 걷어 낸 내용은 이 폴더에만 남습니다.

## 지원하는 계열과 모델

| 폴더 | 개발사 | 모델 |
|---|---|---|
| `01-gpt/` | OpenAI | `gpt-6-astra`, `gpt-6-luna`, `gpt-6.1-sol`, `gpt-6.1-terra`, `gpt-6.2-astra`, `gpt-6.2-sol` |
| `02-claude/` | Anthropic | `fable-5.1`, `fable-5.2`, `fable-5.5`, `haiku-4.5`, `haiku-5.5`, `opus-5.5`, `sonnet-5.5` |
| `03-gemini/` | Google | `gemini-3.8-flash`, `gemini-4-argon`, `gemini-4-carbon`, `gemini-4-hydrogen`, `gemini-4-krypton`, `gemini-4-neon`, `gemini-4-oxygen`, `gemini-4-sodium` |
| `04-grok/` | xAI | `grok-4.7`, `grok-4.8`, `grok-5` |
| `05-deepseek/` | DeepSeek | `v4.1-flash-1017` |
| `06-qwen/` | Alibaba | `qwen3.6-27b`, `qwen3.6-35b-a3b`, `qwen3.7-max`, `qwen3.8-2.4t-a95b`, `qwen3.8-27b`, `qwen3.8-flash-next`, `qwen3.8-max`, `qwen4-27b`, `qwen4-max` |
| `07-kimi/` | Moonshot | `kimi-k3.1` |
| `08-glm/` | Z.ai (Zhipu) | `glm-5.3`, `glm-5.3-flash`, `glm-5.5` |
| `09-gemma/` | Google (로컬) | `gemma-4-12b`, `gemma-4-26b-a4b`, `gemma-4-31b`, `gemma-4-e2b`, `gemma-4-e4b` |
| `10-muse/` | Meta | `muse-ember`, `muse-glimmer`, `muse-spark`, `muse-wonder` |
| `11-minimax/` | MiniMax | `minimax-m3`, `minimax-m3.1-flash` |
| `12-mistral/` | Mistral AI | `mistral-large-4` |
| `13-microsoft/` | Microsoft AI | `mai-code-2`, `mai-code-2-flash` |
| `14-nvidia/` | NVIDIA | `nemotron-3.5-bolt-74b-a9b`, `nemotron-3.5-super-vl` |
| `15-tencent/` | Tencent | `hy4`, `hy4-flash` |
| `16-baidu/` | Baidu | `ernie-5.5-flash-preview` |
| `17-thinking-machines/` | Thinking Machines Lab | `inkling-2-small` |
| `18-lg/` | LG AI Research | `exaone-4.5`, `k-exaone-2.0`, `k-exaone-2.5` |
| `19-sk-telecom/` | SK Telecom | `a.x-k1`, `a.x-k2` |
| `20-upstage/` | Upstage | `solar-mini-4`, `solar-open-2`, `solar-pro-4` |
| `21-motif/` | Motif Technologies | `motif-3` |
| `22-naver/` | Naver Cloud | `hyperclova-x-seed-32b-think`, `hyperclova-x-seed-8b-omni` |
| `23-kakao/` | Kakao | `kanana-2`, `kanana-2.5` |
| `24-kt/` | KT | `midm-k-2.5-pro` |
| `25-krafton/` | Krafton | `raon-1-mini` |
| `26-xiaomi/` | Xiaomi | `mimo-v2.6-flash` |

## 근거 수준 표기

- `[확인]`은 공식 기술 문서, API 명세, 소스 코드 같은 1차 출처를 직접 열람하여 교차 확인을 마친 내용입니다.
- `[부분]`은 검색 결과 요약문, 2차 인용 기사, 벤더 자체 주장, 집계 사이트로만 파악한 내용입니다.
- `[미확인]`은 조사 환경에서 확인하지 못했거나 출처 간 내용이 서로 충돌하는 항목입니다.
- `[추정]`은 검증된 사실을 바탕으로 논리적으로 이끌어낸 추론입니다.

모델 개발사가 직접 발표한 벤치마크는 객관적 사실로 보지 않고 일방의 주장으로만 다루며, 독립 평가 지표의 버전이 서로 다를 때는 억지로 값을 비교하지 않고 충돌 항목으로 따로 분류했습니다.

## 한계

조사는 2026년 9월 말부터 11월 중순까지 모은 공개 자료가 중심이고, 새로 넣거나 고친 모델은 2026-11-19 기준입니다. 그 뒤에 나온 변경은 들어 있지 않을 수 있습니다.

공식 사이트에 들어가지 못한 항목은 `[부분]`으로 남아 있습니다. 중요한 결정에 쓸 때는 공식 1차 출처를 한 번 더 보세요.
