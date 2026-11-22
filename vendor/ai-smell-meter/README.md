# AI 냄새 측정기 (ai-smell-meter)

한국어와 영어 글(연결 단절 검사는 일본어, 중국어, 스페인어, 프랑스어, 독일어, 포르투갈어, 이탈리아어, 러시아어 포함)에서 **AI 냄새**(챗봇, 의미 부풀리기, 구라, 개소리, 헛소리, 올려치기, 번역말투)를 비교 검토하고, **교정된 글을 출력**하는 윤문 도구입니다. 단일 코드베이스로 세 가지 형태를 지원합니다.

- **윤문 엔진**: `python3` 표준 라이브러리만 사용하는 경량 명령줄 도구입니다. 외부 네트워크나 API 키가 필요 없습니다.
- **윤문 스킬**: Agent Skills 규격을 따르는 `ai-smell-polish`입니다. Claude Code, Codex CLI, Gemini CLI 같은 에이전트 도구가 읽고 실행합니다.
- **윤문 에이전트**: Claude Code 전용 서브에이전트 정의와 Codex, Gemini용 연계 설정, 터미널 없는 웹 채팅 환경용 프롬프트를 함께 제공합니다.

> **본 도구는 AI 탐지기가 아닙니다.** 점수는 문체 패턴이 걸린 빈도이고 AI가 작성했을 확률과는 다릅니다. 사람이 쓴 글이 높은 점수를 받을 수 있고 AI가 쓴 글이 낮은 점수를 받을 수도 있어서, 저자 판정이나 인사 평가, 징계의 근거로 쓰지 않습니다. 탐지기 우회 기능은 일절 제공하지 않습니다. 자세한 한계는 [`docs/limits.md`](docs/limits.md)에, 공개된 자료로 확인한 오탐지율과 검출 비율은 [`docs/evaluation.md`](docs/evaluation.md)에 있습니다.

## AI 에이전트 연계 방법

AI 에이전트 환경에서는 다음처럼 요청하시면 됩니다.

```text
AI 냄새 측정기/ai-smell-meter 를 설치하고 실행한뒤 결과를 알려 주고 수정 방향 제시해봐
```

에이전트는 [`AGENTS.md`](AGENTS.md) 지침에 따라 설치하고 실행한 뒤 결과를 알려 주고, 수정 방향을 제시합니다.

## 직접 실행하기

저장소 루트에서 다음 명령어를 실행합니다 (경로에 한글과 공백이 포함되어 있으므로 따옴표로 감쌉니다. Windows 환경은 `python3` 대신 `py -3`을 사용합니다):

```bash
cd "AI 냄새 측정기/ai-smell-meter"
python3 install.py                                  # 점검 + 설치 + 시험 + 시연
python3 bin/ai-smell analyze 글.md                  # 점수와 검출 패턴 목록
python3 bin/ai-smell polish 글.md > 글.교정.md      # 교정문은 표준 출력, 요약은 표준 오류로 전송
python3 bin/ai-smell prompt 글.md --target claude   # 남은 어색한 표현을 LLM이 다듬을 지시문
python3 bin/ai-smell verify 글.md 글.최종.md        # 사실 보존, 변경률, 신규 결함 대조 검증
```

| 명령 | 주요 기능 |
|---|---|
| `analyze` | 점수(0~100), 범주별 검출 항목, 문단별 점수 출력. `--format json`, `--genre academic\|everyday\|literary\|technical` |
| `polish` | 교정문 출력. `--tier safe\|standard\|strong`, `--out`, `--in-place`(.bak 백업 생성), `--diff`, `--format json` |
| `prompt` | 남은 표현을 고칠 LLM 프롬프트 생성. `--target generic\|claude\|gpt\|gemini`, `--chat ko\|en`(웹 채팅용) |
| `verify` | 숫자, 주소, 코드, 인용, 영문 고유명사 보존 여부, 변경률, 신규 결함 검증. PASS/WARN/CONFIRM/FAIL |
| `rules` | 규칙 목록 확인 (등급 및 교정 단계 안내). 전체 명세는 [`docs/rules.md`](docs/rules.md) |
| `selftest`, `doctor` | 설치 상태 및 환경 점검 |
| `install` | 스킬 및 에이전트 설치. `--scope user\|project\|both`, `--agents`, `--dry-run`, `--uninstall` |

작성자 금지어는 `--ban "구절"`, `--ban-file 목록.txt` 옵션으로 전달합니다. 코드 블록, 인라인 코드, URL, 인용 블록(`>`), 그리고 `<!-- ai-smell:ignore-start -->`와 `<!-- ai-smell:ignore-end -->` 구간은 검사 및 수정 대상에서 제외합니다.

## 실제 교정 출력 예시

점수가 80 이상이면 AI 핵폐기물, 55~79면 디지털 쓰레기입니다. 같은 점수 구간의 영어 표본과 한국어 표본을 하나씩 윤문해 점수를 한 자리 수로 낮췄습니다.

### AI 핵폐기물

영어 표본 (95/100):

```text
Certainly! In today's fast-paced digital world, AI plays a crucial role in shaping how teams work. It's not just a tool, it's a game-changer. Experts agree that organizations can leverage its robust capabilities to unlock their full potential. In order to get started, utilize the free tier. I hope this helps!
```

윤문 후: (0/100)

```text
AI shapes how teams work, and organizations can use its capabilities to reach their goals. To get started, use the free tier.
```

한국어 표본 (87/100):

```text
물론입니다! 급변하는 AI 시대에 인공지능은 단순한 도구가 아니라 패러다임의 전환을 의미한다. 이는 다양한 측면에서 시사하는 바가 크다. 분석을 진행한 결과, 비용이 감소되어진 것으로 나타났다. 도움이 되었기를 바랍니다.
```

윤문 후: (0/100)

```text
인공지능이 업무 방식을 크게 바꾸고 있다. 분석 결과 비용이 줄어든 것이 확인됐다.
```

### 디지털 쓰레기

영어 표본 (77/100):

```text
In today's fast-paced digital world, our platform provides a comprehensive solution that plays a vital role in improving team productivity. It's not just a tool, it's a game-changer. It offers a wide range of features and responds in 0.8 seconds on average. Moreover, 20,000 users rely on it. In conclusion, it is a valuable tool for businesses.
```

윤문 후: (0/100)

```text
The platform responds in 0.8 seconds on average and is built to improve team productivity. It has 20,000 users, and businesses rely on it.
```

한국어 표본 (67/100):

```text
급변하는 디지털 시대에 이 서비스는 사용자 경험을 향상시키는 데 중요한 역할을 합니다. 단순한 도구가 아니라 업무 방식의 패러다임을 바꾸는 솔루션입니다. 다양한 측면에서 효율성을 높이는 데 도움이 되며, 응답 시간은 평균 0.8초이고 사용자는 2만 명입니다. 결론적으로 많은 기업에게 큰 가치를 제공한다고 할 수 있습니다.
```

윤문 후: (0/100)

```text
이 서비스는 팀의 업무 효율을 높이려고 만들었고 평균 응답 시간은 0.8초입니다. 사용자는 2만 명이며 많은 기업이 사용합니다.
```

## 무엇을 잡는지

규칙은 크게 네 가지를 찾습니다. 챗봇 특유의 말투, 사람이 잘 쓰지 않는 낱말, 문장 구조, 앞뒤 문맥을 봐야 알 수 있는 표현입니다.

| 종류 | 예 |
|---|---|
| 챗봇 말투 | `물론입니다!`, `도움이 되었기를 바랍니다` |
| 낱말 | `갈린다`, `나뉘었고`, `신호`, `밀도` |
| 문장 구조 | `A가 아니라 B`, 한 문장에서 부정 둘을 맞세운 면책 문구 |
| 문맥 | 숫자가 없는 `근삿값`, 앞에서 설명하지 않은 `흔적` |

## 동작 원리

1. **원문 보호**: 소스 코드, URL, 인용 블록, 명시적 무시 구간을 먼저 차폐합니다.
2. **패턴 검출**: 485개 규칙(영어 160, 한국어 312, 공통 13)과 22가지 분석기가 어색한 패턴을 검출합니다. 규칙마다 근거 등급(A/B/C)이 지정되어 가중치에 반영됩니다.
3. **점수 계산**: 범주별 상한을 둔 빈도 점수와 챗봇 잔재 점수를 합산합니다. 문장 길이 변동 자체는 글의 고유한 호흡일 수 있어 점수 계산에서 제외하지만, 짧은 문장이 접속어, 지시어, 되받는 말 없이 이어지는 **연결 단절**은 따로 반영합니다(접속어를 지우고 문장을 쪼개는 방향으로 점수가 내려가는 것을 막기 위해서입니다).
4. **단계별 교정**: `safe`(오탈자 수준), `standard`(군더더기, 챗봇 잔재, 이중 피동 등 의미 왜곡이 없는 항목), `strong`(문맥에 따른 의미 변화 가능성이 있는 항목). 거대 구조 습관은 기계적으로 바꾸지 않습니다.
5. **대조 검증**: 교정본에서 숫자, 주소, 코드, 인용이 훼손되면 FAIL, 변경률이 50%를 초과하면 CONFIRM, 새로운 결함이 감지되면 WARN을 보고합니다.

아키텍처 설계는 [`docs/design.md`](docs/design.md), 각 규칙의 근거와 학술 출처는 [`docs/research.md`](docs/research.md)에 상세히 수록되어 있습니다.

## 평가

Gemini, Claude, GPT, DeepSeek, GLM의 2026년 모델 답변으로 직접 평가했습니다. 일상, 회화, 코딩 및 개발, 뉴스 및 이슈 질문에 각각 200번이 넘게 답하게 했고, 코딩 및 개발 문서는 약 3,000번 만들었습니다. 결과는 `docs/evaluation.md`에 있습니다.

## 도구별 설치 위치

| 도구 | 사용자 범위 (전역) | 프로젝트 범위 (로컬) |
|---|---|---|
| Claude Code | `~/.claude/skills/ai-smell-polish`, `~/.claude/agents/ai-smell-polisher.md` | `.claude/skills/...`, `.claude/agents/...` |
| 공통 (Codex, Gemini CLI 등) | `~/.agents/skills/ai-smell-polish` | `.agents/skills/ai-smell-polish` |
| Gemini CLI | `~/.gemini/skills/ai-smell-polish` | `.gemini/skills/ai-smell-polish` |
| Codex (구 경로) | `~/.codex/skills/ai-smell-polish` | |

**각 CLI 도구가 해당 경로를 실제로 읽어들이는지는 개별 런타임 환경에 따라 다를 수 있습니다.** 설치 후 도구의 스킬 목록에 `ai-smell-polish`가 정상 등록되었는지 확인해 주시기 바랍니다.

## 모델에 독립적인 운용

윤문 엔진은 LLM API를 호출하지 않는 독립 프로그램이므로 모델 종류에 구애받지 않고 일관되게 동작합니다. 구조적 윤문 단계만 에이전트 모델이 수행하며, 지시문은 마크다운 형식(GPT, Gemini 등 범용)과 XML 태그 형식(Claude)으로 나누어 생성합니다(`prompt --target`). 터미널 접근이 불가능한 웹 채팅 환경에서는 [`chat-prompts.md`](skills/ai-smell-polish/references/chat-prompts.md)의 프롬프트를 복사하여 활용하시면 됩니다.

## 디렉터리 구성

```text
install.py   bin/ai-smell   AGENTS.md
skills/ai-smell-polish/{SKILL.md, scripts/, references/}   스킬 = 엔진 + 지침
agents/{claude, codex, gemini}/                             에이전트 정의 및 안내 설정
docs/{design, research, limits, rules}.md                   설계, 연구 근거, 한계, 규칙 명세
tests/                                                      단위 테스트 및 회귀 시험 모음
```

## English Summary

`ai-smell-meter` measures and removes "AI smell" (chatbot residue, importance inflation, negative parallelism, translationese, filler) in **Korean and English** text and outputs polished text. It uses Python 3.9+ standard library only, ships as an Agent Skill (`ai-smell-polish`) alongside agent definitions, and can be installed directly by autonomous coding agents via `AGENTS.md`. It is **not an AI detector**: the score represents pattern frequency rather than authorship probability, and contains no detection-evasion features. Fixes are tiered (`safe`/`standard`/`strong`), while structural edits are guided by `prompt` and strictly audited by `verify` (preserving factual accuracy, change ratios, and preventing regressions). Detailed limits: [`docs/limits.md`](docs/limits.md).

```bash
python3 install.py            # doctor + install + selftest + demo
python3 bin/ai-smell polish draft.md > draft.polished.md
```

## 라이선스

본 도구는 [MIT 라이선스](LICENSE)를 따릅니다. 참고한 오픈소스 프로젝트의 아이디어를 독자적인 클린룸 방식으로 구현했으며 외부 코드를 직접 포함하지 않았습니다.
