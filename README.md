<div align="center">

<h1>GeminiToGenius</h1>

<p>Gemini를 조금 더 똑똑하게(덜 멍청하게) 만드는 플러그인입니다.</p>

<p>한국어 · <a href="docs/README.en.md">English</a></p>

<p><a href="https://github.com/habinsong/GeminiToGenius/releases">릴리즈</a> · <a href="docs/product/getting-started.md">설치 안내</a> · <a href="docs/verification/README.md">검증 기록과 한계</a> · <a href="CHANGELOG.md">변경 기록</a></p>

<p>GTG 3.3.0은 Antigravity 데스크톱·IDE, Antigravity CLI, Gemini CLI를 지원합니다.</p>

</div>

## 하는 일

- 작업을 등록할 때 완료 조건과 검증 명령을 먼저 고정합니다. 등록한 뒤에는 통과하기 쉬운 명령으로 임의 변경할 수 없습니다.
- `verify`는 등록된 명령을 실제로 실행하며 종료 코드, 소요 시간, 검사 대상 파일 목록을 기록합니다. 검사 대상 파일이 변경되면 이전 성공 기록은 효력을 잃습니다.
- `certify`는 완료 주장과 실행 근거를 단일 파일에 묶습니다. `replay`는 별도 상태 DB 없이 해당 파일과 현재 작업공간만으로 결과를 다시 검증합니다.
- 검사가 실행하지 못한 파일과 판단할 수 없었던 범위도 결과에 있는 그대로 명시합니다. 비어 있는 목록을 '모두 확인 완료'로 포장하지 않습니다.
- 세션이 끊겨도 등록된 작업과 검사 결과, 기록 메모는 보존됩니다. 새 세션에서는 `tasks`로 검색해 `attach`로 작업을 이어갈 수 있습니다.
- 코드를 바꾼 뒤에는 `structure` 검사가 이번 변경의 빈 함수와 새 TODO, 큰 파일에 쌓인 기능, 계속 불어나는 클래스를 막고, 구현이 하나뿐인 추상화나 인자만 넘기는 래퍼, 부르는 곳 없는 새 정의를 검토 신호로 알립니다.
- 문서를 쓴 뒤에는 `prose` 검사가 한국어·영어 상투구와 과장, 번역투가 몰린 문단, 대구, 뚝뚝 끊기는 문장을 줄 번호와 함께 찾고 0~100점으로 환산합니다. 논문·일상 글·문학처럼 글의 갈래를 고를 수 있고, 파일로 저장하지 않은 글은 표준 입력으로 검사합니다.
- 윤문한 글은 원문과 견줘, 수치·인용·URL·코드가 바뀌었는지와 바뀐 단어의 비율을 확인합니다.
- 검증에서 드러난 저장소별 실수(예: 없는 함수 이름)를 근거 파일과 함께 교훈으로 남기면, 다음 세션 첫 턴에 그 기록을 보여 줍니다.

## 설치

macOS 또는 Linux, Python 3.10 이상, Git이 필요합니다. 외부 Python 패키지는 요구하지 않습니다.

```bash
git clone https://github.com/habinsong/GeminiToGenius.git
cd GeminiToGenius
bash scripts/install.sh
```

설치기는 홈 디렉터리에서 지원 호스트를 자동으로 찾아 설치하며, 설치 전에 별도 임시 디렉터리에서 패키지 무결성을 검증합니다. 감지된 호스트가 없으면 Antigravity 전역 플러그인으로 설치합니다. 설치 후에는 해당 호스트를 재시작하세요.

| 호스트 | 설치 방식 |
| --- | --- |
| Antigravity 데스크톱·IDE | 자동 감지 또는 프로젝트별 설치 |
| Antigravity CLI (`agy`) | 자동 감지 후 `agy plugin install`까지 실행 |
| Gemini CLI | `--platform gemini-cli`를 지정해 직접 설치 |

특정 프로젝트에만 적용하려면 다음과 같이 실행합니다.

```bash
bash scripts/install.sh --workspace /absolute/path/to/project
```

설치 상태 확인과 제거는 아래 명령을 사용합니다.

```bash
python3 scripts/install.py doctor
python3 scripts/install.py uninstall
```

## 쓰는 법

설치 후에는 평소처럼 자연어로 요청하면 됩니다. 슬래시 명령이나 별도 명세 파일을 작성할 필요가 없습니다.

```
로그인하면 500이 납니다. 원인 찾아서 고쳐 주세요.
```

코드 동작·타입·호출 관계를 바꾸는 작업은 단일 파일이어도 빌드와 필수 시험을 완료 계약에 연결하도록 안내합니다. PRD가 있으면 요구별 검사를 연결하며, 문답·문구·포맷 수정은 관련 검사로 끝냅니다.

3.1.0은 결과물을 직접 읽는 구조·문체 검사와 교훈 기록을 더하고, 상시 규칙을 "기억보다 원문, 끝내기 전에 스스로 반박하기" 중심으로 다시 썼습니다. 3.2.0은 한국어 윤문을 갈래별 스킬 세 개로 나누고 문체 점수를 붙였으며, 3.3.0은 표준 입력과 윤문 전후 비교를 더하고 긴 문서에서 경고가 쏟아지던 문제를 고쳤습니다. 각 버전에서 무엇을 확인했고 무엇을 확인하지 못했는지는 [3.1.0](docs/verification/3.1.0.md), [3.2.0](docs/verification/3.2.0.md), [3.3.0](docs/verification/3.3.0.md) 검증 기록에 있습니다.

### 한국어 글을 쓰거나 다듬을 때

```
이 보고서 문단 AI 티 안 나게 고쳐 줘.
```

스킬 이름을 부를 필요는 없습니다. 스킬 설명에 `자연스럽게`, `번역투 빼 줘`, `답장 써 줘`, `소설처럼` 같은 거친 말을 적어 두었고, 논문·보고서는 `gtg-korean-academic`, 카톡·메일·후기는 `gtg-korean-everyday`, 소설·수필·시는 `gtg-korean-literary`, 그 밖의 글은 `gtg-writing`이 맡습니다. 호스트가 요청에 맞는 스킬을 실제로 여는지는 확인하지 못했습니다.

윤문 스킬은 원문의 수치·인용·주장 강도를 바꾸지 않게 하고 끝내기 전에 `prose` 검사를 돌리게 합니다. 에이전트는 턴 시작 안내에 담긴 실행기 경로로 이 검사를 부르며, 저장소에서 직접 돌려 볼 수도 있습니다.

```bash
python3 -m gtg prose --register academic paper.md
python3 -m gtg prose --register everyday --original draft.md reply.md
python3 -m gtg prose --register everyday - <<'EOF'
내일 3시에 봐요. 늦으면 연락 줘요.
EOF
```

| 옵션 | 하는 일 |
| --- | --- |
| `--register` | `general`(기본), `academic`(논문·보고서), `everyday`(대화·메시지·후기), `literary`(소설·수필·시) 가운데 고릅니다. 같은 `~라고 볼 수 있다`도 논문에서는 관례이고 대화에서는 어색하므로 갈래마다 규칙을 끄고 완화하고 더합니다. |
| `-` 또는 `--text` | 파일로 저장하지 않은 글(채팅 답변 등)을 표준 입력이나 명령줄로 받아 검사합니다. |
| `--original` | 윤문본을 원문과 견줍니다. 수치·인용·URL·코드가 바뀌었으면 종료 코드 1이고, 바뀐 단어 비율도 알려 줍니다. |
| `--min-score` | 점수가 이 값(0~100)보다 낮은 문서가 있으면 종료 코드 1입니다. |

점수는 찾은 신호를 글 분량(문장 10개 단위)으로 나눈 밀도이고 A(90점 이상), B(75점), C(60점), D 등급으로 나뉩니다. AI가 썼을 확률이 아닙니다. 사람이 쓴 에세이의 8%도 90점에 못 미쳤으므로 낮은 점수만으로 AI가 썼다고 판단하면 안 됩니다.

## 대상 모델

3.1.0의 지침은 Gemini 4 Argon(2026-10-13 공개)과 Gemini 3.8 Flash(2026-09-02 공개)를 염두에 두고 썼습니다. 두 모델은 벤치마크 점수에 비해 실제 저장소 작업에서 코드 동작을 지어내거나, 미완성 코드를 완료라고 하거나, 지키겠다고 한 제약을 바로 어긴다는 사용자 보고가 있습니다. 그래서 GTG는 모델의 자기 보고 대신 검사 결과와 다시 연 원문을 근거로 삼게 하고, Google의 Gemini 프롬프트 지침대로 금지 사항은 규칙 끝에 구체적으로 모았습니다.

실행 코어는 모델 이름으로 갈라지지 않으며 호스트가 정한 모델과 사고 수준을 바꾸지 않습니다. Google 문서는 두 모델 모두 기본 사고 수준을 medium으로 둡니다. Argon 문서는 여러 파일에 걸친 소프트웨어 작업에 high를 권하고, 3.8 Flash 문서는 복잡한 코드와 에이전트 작업에 medium을, 까다로운 다단계 추론에 high를 권하므로 사고 수준은 작업에 맞춰 호스트에서 고르면 됩니다. 2026-10-28에 발표된 Gemini 4 Carbon은 아직 일반 공개 전이라 사양을 가정하지 않았습니다. 이 지침이 실제로 환각과 과장을 줄이는지는 아직 측정하지 않았습니다.

## 확인한 것

| 항목 | 확인한 결과 |
| --- | --- |
| Antigravity 2.12.2 | 다단계 요청에서 작업 등록, 검사 실행, `certify`, `replay` 동작을 확인했습니다. |
| Antigravity CLI 1.1.28 | 공식 패키지 검증을 통과했고 2개 훅이 정상 발행됐습니다. |
| 완료 증명서 | 검사 대상 파일의 한 줄을 바꾸면 재현 검증이 실패하고, 되돌리면 다시 통과함을 확인했습니다. |
| 동일 모델 비교 | GTG 사용 여부와 무관하게 모두 14/14 통과했습니다. 이 결과는 제품 간 우열이나 단일 턴 작업의 품질 개선을 의미하지 않습니다. |
| 3.3.0 오프라인 시험 | 전체 513개 시험이 통과했습니다. 문체 검사를 일부러 망가뜨린 변형 56개를 시험이 모두 잡는지 확인했고(`scripts/mutation_check.py`), 스킬 문서의 고친 예시 21개를 검사기에 다시 대 보았습니다. 실제 Gemini 호출은 하지 않았습니다. |
| 문체 점수 | 사람·LLM 한국어 글(KatFish)에서 사람 글과 LLM 글을 가르는 확인용 AUC는 에세이 0.945, 초록 0.798, 시 0.669입니다. 사람이 쓴 논문 본문 100편은 A 98편, B 2편이었습니다. Gemini가 쓴 글로는 재지 않았습니다. |

구체적인 수치, 실행 환경, 미확인 항목은 [검증 기록](docs/verification/README.md)에 가감 없이 정리했습니다.

## 아직 확인하지 못한 것

- Windows 환경 설치 및 네트워크 파일 시스템에서의 실행 잠금 동작
- 실제 전원 차단 후 복구, 다일 간의 장기 작업, 다양한 모델에서의 반복 시험
- Go·Rust와 컴파일하여 실행하는 TypeScript의 실행 범위 관측
- 토큰 사용량 및 비용 측정
- 3.1.0 지침과 구조·문체 검사, 교훈 기록이 실제 Gemini 4 Argon·Gemini 3.8 Flash의 환각과 미완성 보고를 줄이는지
- Gemini가 쓴 한국어의 문체 점수. 점수는 사람 글과 2024년 LLM 글로만 맞췄습니다. 고정 프롬프트 26개로 직접 재는 절차는 [evals/prose](evals/prose/README.md)에 있습니다.
- 한국어 윤문 스킬이 실제 Gemini의 윤문을 낫게 하는지, 모호한 요청에 맞는 스킬이 저절로 열리는지
- 일상 글·소설·수필·영어에서 점수의 판별력(정답이 붙은 자료가 없어 시험 문장과 문서 예시로만 확인했습니다)
- 데스크톱 Antigravity의 웹 도구 이름(SDK 소스의 `search_web`, `read_url_content`와 같은지)

## 문서

| 문서 | 내용 |
| --- | --- |
| [설치와 첫 사용](docs/product/getting-started.md) | 설치, 호스트 선택, 제거 방법 |
| [동작 방식](docs/product/how-it-works.md) | 작업 등록부터 검증과 재확인까지의 실행 흐름 |
| [명령 목록](docs/reference/cli.md) | 에이전트가 사용하는 CLI 명령과 종료 코드 |
| [완료 증명서](docs/reference/certificate.md) | 증명서 규격과 `replay` 판정 기준 |
| [검증 기록과 한계](docs/verification/README.md) | 실호스트 검증, 하네스 비교, 미확인 범위 |
| [문체 점수 실측 절차](evals/prose/README.md) | 모델이 쓴 글을 같은 잣대로 재는 고정 프롬프트와 절차 |
| [전체 문서](docs/README.md) | 제품·참조·구조 문서 전체 색인 |

## 개발

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
python3 scripts/catalog.py --check
```

현재 작업 기록과 파일별 원문 목록은 저장소에 올리지 않는 `docs/development/` 폴더에 둡니다. 문체 검사를 다시 맞추거나 변형 시험으로 시험의 빈틈을 찾는 방법은 [3.3.0 검증 기록](docs/verification/3.3.0.md)과 `scripts/prose_calibration.py`, `scripts/mutation_check.py`의 도움말에 있습니다.

## 라이선스

MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE)를 참고하세요. Google, Antigravity, Gemini와 공식 제휴나 후원 관계가 아니며, 제품명은 호환 대상을 안내하기 위한 용도로만 사용합니다.
