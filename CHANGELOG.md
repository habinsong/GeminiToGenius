# 3.3.3 (2026-11-23)

엔진 강화 릴리즈입니다. GTG에 있던 문체 검사(`gtg prose`)를 없애고, 별도 저장소로 만들어 둔 AI 냄새 측정기를 원본 그대로 가져와 윤문 엔진으로 삼았습니다. 같은 저자의 지침 저장소에서 Gemini 계열 지침과 한국어 윤문 문서도 옮겼습니다.

- **기존 문체 검사 삭제**: `gtg prose` 명령과 `gtg/prose*.py` 7개, 시험 9개, 점수 보정 스크립트(`scripts/prose_calibration.py`), 변형 시험(`scripts/mutation_check.py`), `evals/prose`를 지웠습니다. 문서 윤문의 측정, 교정, 대조는 이식한 측정기 하나로 합쳤습니다. `docs/verification/3.1.0~3.3.0`은 삭제 전 측정 기록으로 남겼습니다.
- **AI 냄새 측정기 이식**: 규칙 485개(영어 160, 한국어 312, 공통 13)와 분석기 22가지로 점수를 내는 `ai-smell-polish` 스킬을 `profile/skills/ai-smell-polish`에 두었습니다. `analyze`로 측정하고, `polish`로 뜻이 바뀌지 않는 항목만 고치며, `verify`로 수치, 주소, 코드, 인용이 남았는지 대조합니다. 스킬 머리말만 GTG 패키지 규격(이름과 설명 두 줄)에 맞췄고 엔진 소스는 고치지 않았습니다.
- **에이전트와 시험 이식**: Claude Code, Codex, Gemini용 에이전트 정의는 `profile/agents`에, 시험 230개와 설계, 근거, 한계 문서와 평가 도구는 `vendor/ai-smell-meter`에 두었습니다. 스킬과 에이전트 폴더는 심볼릭 링크로 이어 한 벌만 유지합니다.
- **'절' 낱말 규칙 추가**: 문서의 부분을 `이 절에서는`, `있는 절은`처럼 학술 용어로 가리키는 말을 AI 슬롭 낱말로 보고 측정기에 `ko.tic.section-word`로 넣었습니다. 절차, 절반, 사찰의 절은 걸리지 않습니다.
- **상위 저장소 자료 이식**: `K-Fable-Opus-Claude-Astra-Sol-GPT-md`에서 Gemini 4 계열 8개 모델 지침(`md/03-gemini`)과 조사 기록(`docs/03-gemini`), 한국어 윤문 공통 문서, 한국어 문체 측정 스크립트 `ko_style_probe.py`와 시험 19개를 `vendor/k-fable-md`에 옮겼습니다.
- **README 모델 표기**: 권장 모델에 Gemini 4 Neon과 Carbon을 Argon과 함께, 사용 금지 모델에 Gemini 4 Hydrogen을 Gemini 3.8 Flash와 함께 적었습니다.
- **문서 윤문**: 프로젝트 Markdown 44개를 측정기로 측정하고 `ai-smell-polisher` 에이전트가 구조 문제까지 다시 썼습니다. 평균 점수는 14.8에서 3.9로, 점수 20점 이상(SLOP)인 문서는 13개에서 0개로, 10점 이상인 문서는 36개에서 2개로 줄었고 `verify`는 FAIL 없이 통과했습니다. 점수는 문체 패턴이 걸린 빈도이고 AI가 썼을 확률이 아닙니다.
- **용어 통일**: 문서와 오류 메시지의 "작업 계약"을 "작업 명세"로 바꿨습니다. 호스트 훅과 API 계약처럼 다른 뜻의 "계약"은 그대로입니다.
- **시험**: GTG 단위 시험 399개와 측정기 시험 230개, `ko_style_probe` 시험 19개가 통과합니다.

# 3.3.2 (2026-11-04)

고도 AI 특유의 구조적 글쓰기 습관(3항 나열, 기계적 문단 균일성)과 AI 슬롭의 대표적 징후인 em dash(`—`) 삽입구 남발을 검출하도록 문체 검사기를 고도화하고, README를 군더더기 없이 정돈한 릴리즈입니다.

- 3항 병렬 나열(Tricolon) 강박을 감지하는 `en-list-of-three`, `ko-list-of-three` 규칙을 추가했습니다. 문장 내에서 3개 항목이 `A, B, and C`(한국어 `A, B, 그리고 C`) 형태로 병렬 나열되는 구문이 문서 전체에서 3회 이상 반복될 때 감지합니다. 한국어 규칙은 쉼표 2개 또는 명시적 접속사(`그리고`, `및`)가 동반된 경우만 엄격하게 매칭하여 2항 나열을 잘못 잡는 일을 막습니다.
- 기계적 문단 균일성을 감지하는 `rhythm-uniform-paragraphs` 규칙을 추가했습니다. 산문 문단이 4개 이상이고 총 문장이 10개 이상인 글에서, 모든 문단이 2~6문장 안팎의 좁은 구간에 갇혀 있고 문단별 문장 수 변동계수가 0.5 미만이며 단문 문단(1문장)이나 심층 문단(7문장 이상)이 없는 기계적 균등 구성을 감지합니다.
- em dash(`—`) 슬롭을 차단하도록 규칙을 강화했습니다. 문장 중간에 대시 쌍(`—aside—`)을 끼워 넣는 삽입구 습관을 1회만 나와도 즉시 잡는 `format-em-dash-pair`를 추가하고, 본문 긴 대시 감지 임계값을 기존 4회에서 2회(`minimum: 2`)로 강화했습니다.
- Gemini 3.8 Flash가 추론 강도(Thinking Effort)와 무관하게 시스템 규칙을 무시하고 인간 흉내를 낸답시고 원문에 없는 사물, 배경과 사연을 날조(Fabrication)하는 치명적 결함을 실측으로 확인해 문서에 공식 명시하고 실사용 비권장을 안내했습니다.
- README에서 사람 흉내를 내는 인위적 예문과 버전별 장황한 과거 나열을 걷어내고, 핵심 기능과 CLI 명령 중심으로 짧고 명쾌하게 재정비했습니다.
- 에이전트가 작은 일에도 프로젝트 전체 폴더와 파일을 훑으며 토큰과 시간을 소모하던 과다 탐색 문제를 규칙과 매 턴 주입 문구에서 억제했습니다. 읽기 범위를 고칠 곳 주변으로 좁히고, 불가능하다는 증거가 확인되면 멈춰 보고하며, 승인 없는 우회 탐색을 하지 않도록 했습니다. 규칙과 스킬 문서는 측정기로 윤문했습니다.

# 3.3.1 (2026-11-03)

영문 AI 상투구 감지 및 교정 기능을 보강하고, 저장소 내 모든 안내와 참조 Markdown 문서를 정중하고 자연스러운 경어체("~니다" 합쇼체)로 전면 윤문한 릴리즈입니다.

- 영문 AI 상투구 감지 규칙을 확장했습니다. 지수, 밀도, 더하다와 자동화 표현(`exponential`, `density`, `add to`, `automatically`), 짝과 쌍 표현(`pair with`, `couple with`, `go hand in hand with`), 신호 표현(`signal that`, `serve as a signal of`), 상투적 동작 표현(`embed into`, `bake into`, `measure progress against`, `propagate through`) 등 주요 영문 클리셰 10가지 개념군을 `gtg/prose_patterns.py` 및 외부 윤문 엔진에 체계적으로 반영했습니다.
- 영문 및 한국어 작문 지침(`profile/skills/gtg-writing/references/korean.md`, `references/english.md`)을 보강하여, 영문 작성 시에도 과장되거나 관용화된 AI 특유의 연결 어구를 배제하고 명확한 인과와 능동적 주어를 사용하도록 안내했습니다.
- `README.md`, `docs/`, `evals/`, `CONTRIBUTING.md`, `SUPPORT.md`를 비롯한 프로젝트 내 20여 개 설명 문서의 어조를 기존의 거칠거나 번역투였던 문맥에서 정중하고 일관된 "~니다" 체로 전면 재정비했습니다.
- 모든 문서에 대해 문체 검사(`prose`)를 수행하여 97~100점(A등급)을 획득하도록 문맥과 호흡을 다듬었습니다.

# 3.3.0 (2026-11-03)

한국어 윤문 검사를 채팅 답변, 윤문 전후 비교, 긴 문서에 맞게 고치고, 3.2.0이 근거가 약한 채 정해 둔 감점 결정을 측정값으로 다시 정한 릴리즈입니다. Gemini가 쓴 글로는 측정하지 않았습니다. 개발 환경에 Gemini CLI와 API 키가 없어, 대신 모아 둔 출력을 오프라인으로 측정하는 도구와 절차를 넣었습니다.

- `prose`가 파일 없이 글을 받습니다. `-`는 표준 입력을, `--text`는 명령줄의 글을 문서 하나로 검사합니다. 빈 글, UTF-8이 아닌 입력, 1MB를 넘는 입력은 실패로 처리합니다. 내용 없는 파일도 100점으로 통과시키지 않습니다.
- `prose --original 원문`이 윤문 전후를 비교합니다. 수치(퍼센트, 소수와 세 자리 이상), 8자 이상 따옴표 인용, URL, 코드가 바뀌면 차단하고 한두 자리 수와 영문 표기는 검토로 알립니다. 바뀐 단어 비율은 30%를 넘으면 검토, 50%를 넘으면 지운 문장을 보고하라는 검토, 80%를 넘으면 차단합니다. 이 발견은 문체 점수에 넣지 않습니다.
- 문서 전체와 문단 안 횟수 기준을 글 분량에 비례하게 바꿨습니다. 사람이 쓴 논문 본문 100편(평균 79문장)에서 번역투 경고가 97%에서 26%로, 연결어미 뒤 쉼표 경고가 79%에서 27%로 줄고 등급이 A 92편, B 8편에서 A 98편, B 2편이 됐습니다(번호 줄을 문단 경계로 계산하는 수정과 길이 비례가 함께 낸 효과이며 분해한 표는 검증 기록에 있습니다). 시는 분량 단위가 행이라, 차단 규칙은 가장 엄격하게 막기로 한 신호를 긴 문단에서 놓치지 않으려고 비례시키지 않습니다.
- 접어 쓴 산문의 분량을 문장 수로 계산합니다. 3.2.0은 줄 수로 계산해 점수가 후하게 나왔습니다.
- 짧은 문장 4연속과 같은 첫머리 3연속을 일반과 학술 갈래에서 감점합니다. 3.2.0은 사람이 쓴 글에 더 많다는 이유로 뺐으나 표본이 에세이 5편 대 4편이었고 초록에서는 사람 0편, LLM 12편으로 반대였습니다. 시와 일상 글에서는 알리기만 합니다.
- `~라고 볼 수 있다`를 차단에서 두 번 이상 반복될 때만 알리는 검토로 내렸습니다. 에세이에서 사람 5.5%, LLM 7.1%로 구분되지 않았습니다.
- 일반 갈래 규칙 3개(문장 첫머리 `이는`, `이러한·이와 같은`, `다양한`), 맞춤법 규칙(24가지, 점수 제외), 일상 갈래의 반말 공감 문구와 `전달드리도록 하겠습니다`를 더했습니다. 에세이 확인용 AUC는 0.937에서 0.945, 사람 에세이의 A 등급은 83%에서 91%가 됐습니다.
- `scripts/prose_calibration.py`에 `--outputs`(모델 출력 채점), `--export-prompts`, `--rules`, `--bodies`를 더하고 고정 프롬프트 26개와 수집 절차를 `evals/prose`에 뒀습니다. 이 스크립트에 처음으로 시험을 붙였습니다.
- 저장소 밖에만 있던 변형 시험을 `scripts/mutation_check.py`로 옮겼습니다. 변형 56개를 시험이 모두 잡고, 각 변형이 지키는 불변식을 `--list`로 봅니다. 처음 53개를 돌렸을 때 살아남은 3개는 시험을 더해 잡았고, 이후 더한 변형 3개도 모두 잡힙니다.
- `gtg-build`의 작업 명세 참조에 `prose` 검사를 등록하는 방법을, 영어 글쓰기 참조에 검사 방법과 점수가 영어에서 맞춰지지 않았다는 한계를 적었습니다. 한국어와 영문 README와 동작 방식과 명령 목록을 3.2.0, 3.3.0 기능에 맞췄습니다.
- 3.2.0 변경 기록의 "(미발행)"(태그와 릴리즈가 나간 뒤에도 남아 있었음)과 3.2.0 검증 문서의 수치 두 곳(`이 논문은` 20%, `등 다양한` 10~36%)을 바로잡았습니다. README의 버전 표기와 `.gitignore` 대상인 개발 문서로 가던 깨진 링크도 고쳤습니다.

시험은 443개에서 513개가 됐고, 작업 명세와 증명서 형식은 바뀌지 않았습니다. 자세한 내용은 [검증 범위와 남은 위험](docs/verification/3.3.0.md)에 있습니다.

# 3.2.0 (2026-11-03)

한국어 윤문을 글 갈래별로 나누고, 문체 검사에 점수를 붙인 릴리즈입니다. 점수는 사람과 LLM이 쓴 공개 한국어 자료로 측정했고, Gemini가 쓴 글로는 측정하지 않았습니다.

- 한국어 윤문 스킬 세 개를 추가했습니다. `gtg-korean-academic`은 논문과 보고서, `gtg-korean-everyday`는 메시지, 메일과 후기 같은 일상 글, `gtg-korean-literary`는 소설, 수필과 시를 맡고, 공통 기준은 `gtg-writing`의 한국어 참조로 다시 썼습니다.
- `prose --register`로 갈래마다 규칙을 끄고 완화하고 더합니다. 논문의 관례적 완곡, 구어의 도치, 소설의 단문은 문제 삼지 않고 영어식 피동, 공감 상투구, 사물 존대, 감정 상투구, 시행 끝 쉼표 같은 갈래별 버릇을 봅니다.
- 대구(`A가 아니라 B`의 연쇄, 짝 질문, `X, 그것은 Y`), 도치, 예고와 반전 문장, 번역투(`~할 것이다`, `변화를 가져온다`, `~적` 추상어, `해당`), 쉼표 습관, 높임 혼용과 한 가지 어미만 이어지는 경어체를 찾는 규칙을 더했습니다.
- `prose` 결과에 0~100점과 A~D 등급, 감점 내역을 넣고 `--min-score` 기준을 추가했습니다. KatFish 자료의 확인용 절반에서 사람이 쓴 글과 LLM이 쓴 글을 구분하는 AUC는 에세이 0.937, 초록 0.784, 시 0.669였습니다.
- 문장을 닫는 따옴표 뒤에서도 끊어, 대사와 서술의 높임을 따로 셉니다.

# 3.1.0 (2026-11-03)

Gemini 4 Argon과 Gemini 3.8 Flash가 벤치마크보다 실제 저장소 작업에서 자주 틀린다는 보고를 염두에 두고, 모델의 자기 보고 대신 결과물을 직접 읽는 검사와 근거 중심 규칙을 더한 릴리즈입니다. 실제 Gemini에서 품질이 나아졌는지는 측정하지 않았습니다.

- `structure` 검사를 추가했습니다. 이번에 바뀐 코드의 TODO, FIXME, 본문이 빈 함수, 기준(400줄)을 넘어 커진 파일, 메서드(20개)가 늘어난 클래스, 구문 오류를 차단하고, 구현이 하나뿐인 추상 클래스와 래퍼 클래스와 단순 전달 함수와 부르는 곳 없는 새 정의와 긴 함수는 검토 신호로 알립니다.
- `prose` 검사를 추가했습니다. 한국어와 영어 상투구를 차단하고, 과장 표현과 번역투 연결의 밀집, 같은 어미 반복, 짧은 문장 연쇄, 단조로운 문장 길이를 검토 신호로 알립니다. 코드와 URL과 머리말은 검사 대상에서 제외합니다.
- 검증에서 확인된 저장소별 사실을 근거 파일과 URL과 함께 기록하는 `lesson`, `lessons`를 추가했습니다. 턴 시작 훅이 최근 교훈 다섯 개를 기록 데이터로 붙입니다.
- 턴 시작 안내에 설치된 실행기 경로(`runner`)를 넣어, 스킬을 열지 않아도 검사 명령을 쓸 수 있게 했습니다.
- 상시 규칙을 다시 썼습니다. 기억보다 원문을 확인하고(검색 요약은 근거가 아님), 버그는 먼저 재현하고, 구현이 하나뿐인 추상화를 만들지 않고, 끝내기 전에 핵심 주장을 외부 근거로 반박해 보게 합니다. Google의 Gemini 프롬프트 지침에 맞춰 금지 사항은 끝에 모았습니다.
- 글쓰기 스킬 `gtg-writing`과 한국어와 영어 참조를 추가했습니다. 조사 스킬은 검색할 때와 원문 열기와 출처 기록과 멈출 때를 중심으로 다시 썼고, 코드 설계 참조와 반박 절차 중심의 검토 참조를 더했습니다.
- root로 실행하면 PID 1 전제가 깨져 실패하던 런타임 시험이 다른 사용자 PID의 권한 거부를 직접 재현하도록 고쳤습니다. 보호하는 동작은 같습니다.
- 영문 README에 남아 있던 Gemini CLI 계정 엔드포인트 중단 설명과, 작업 미등록을 의도된 동작으로 표현한 문장을 실제 기록에 맞게 고쳤습니다. 구조 문서의 전원 차단 복구 서술도 시험한 범위로 줄였습니다.

작업 명세와 증명서 형식은 바뀌지 않았습니다. 자세한 내용은 [검증 범위와 조사 출처](docs/verification/3.1.0.md)에 있습니다.

# 3.0.1 (2026-10-16)

비판적 검토와 코드 완료 검증을 보강한 릴리즈입니다. 환각, 과장과 무조건적 긍정과 없는 API 참조와 실사용 조건 불일치를 다루되 실제 모델 품질 개선을 입증했다고 주장하지 않습니다.

- 코드 동작, 타입과 호출 관계 변경에 빌드와 필수 시험과 PRD 요구를 연결하는 `code_contract`를 추가했습니다. 선행 빌드 실패와 입력과 PRD 변경, 빌드 재실행 뒤 이전 시험 성공의 재사용을 차단합니다.
- Python 필수 시험 실행기가 실제 성공한 시험 ID를 확인합니다. 실행 0개, 전부 skip, 필수 시험 누락, skip, expectedFailure, 조기 종료와 오래된 캐시와 손상된 관측을 통과시키지 않습니다.
- `environment`로 로컬 Python 프로세스의 필요조건을 비교합니다. 원격 환경과 자원 집행과 제품 호환성은 별도 확인 범위입니다.
- 평가 비교에서 실행기와 채점 조건 누락과 불일치, 사람 검토 대기를 차단합니다. 비판적 검토 9사례와 빌드, PRD, SDK 참조 사례를 추가했습니다.
- `replay`의 검사 중 파일 변경과 잔여 자식 프로세스와 타임아웃 정리를 보강하고, 중복 감시 경로를 예산에 두 번 계산하던 결함을 수정했습니다.
- 별도 홈 설치가 실제 사용자 호스트 등록을 건드리지 않도록 했습니다. 실제 CLI 등록 실패와 설치 경로/호스트 불일치를 성공으로 보고하지 않습니다.
- 실제 `agy 1.1.28`의 CLI 등록이 데스크톱 경로를 덮는 동작에 대응해 기존 패키지를 보존하고 호스트에 맞게 복구합니다.
- 규칙의 24,000바이트 상한을 검사하고 기존 12,000자는 GTG 호환 정책으로 구분했습니다. 현재 공식 안내와 어긋난 Gemini CLI 계정과 훅 설명을 바로잡았습니다.

기존 작업 명세와 schema_version 3 증명서를 유지합니다. 새 코드 완료 보호는 해당 계약을 등록한 작업에 적용합니다. [검증 결과와 한계](docs/verification/3.0.1.md).

# 3.0.0 (2026-09-09)

기존 2.x 프롬프트 프로필 아키텍처를 순수 Python 로컬 실행 코어로 전면 개편한 릴리즈입니다. 세 차례의 알파 버전을 거쳐 실제 호스트 환경에서 동작을 실증한 후 배포합니다.

## 주요 추가 기능

- 완료 조건을 사전에 고정하고 등록된 명령을 실제로 실행합니다. 프로세스 종료 코드, 실행 시간, 검사 대상 파일 해시를 기록하며, 대상 파일이 변경되면 이전 성공 기록은 즉시 무효화됩니다.
- `certify`가 완료 주장과 실행 명령, 종료 코드, 파일 지문을 결합하고, `replay`가 상태 DB 없이 해당 문서만으로 결과를 독립 재현합니다. 판정 결과는 `pass`, `invalid`, `inconclusive`이며 종료 코드는 각각 0, 1, 2입니다.
- 검사 과정에서 실제로 실행된 소스 파일을 관측하여, 검사는 통과했으나 호출되지 않은 대상 파일을 있는 그대로 보고합니다. 관측할 수 없는 런타임 언어가 포함된 경우 미실행으로 단정하지 않고 판단을 유보한 원인을 명시합니다.
- Antigravity 데스크톱과 IDE, Antigravity CLI(`agy`), Gemini CLI 3개 호스트를 지원하며, 플랫폼별 세부 차이는 `gtg/platforms.py` 단 한 곳에서 일원화하여 관리합니다.
- 세션이 끊겨도 작업 데이터가 보존됩니다. 새 세션에서 `tasks`로 검색해 `attach`하면 목표, 검사 결과, 진행 메모를 그대로 이어받습니다.
- 설치기가 호스트 환경을 자동 감지해 단일 명령으로 설치와 무결성 진단과 제거를 수행합니다. 파일 이동 저널을 사전 기록하여 설치 중 프로세스가 중단되더라도 안전하게 정리합니다.

## 주요 수정 사항

- 시스템 재부팅 후 PID 재사용으로 인해 `recover`가 계속 거부되어 작업이 교착되던 문제를 해결했습니다. 프로세스 수명 중에만 유지되는 OS 파일 잠금 방식으로 판별 기준을 변경했습니다. 자식 검사 프로세스가 잠금을 상속받으므로 부모 프로세스만 종료된 경우도 동일하게 감지됩니다.
- 검사가 백그라운드에서 실행 중일 때 종료 훅이 작업 완료를 잘못 승인하던 결함을 수정했습니다. 재개 예산을 불필요하게 소진하지 않으면서 잔여 검사와 프로세스 복구 방법을 안내하도록 개선했습니다.
- 관측 범위에 단 하나의 셸 스크립트만 포함되어도 미실행 범위 보고 전체가 `null`이 되던 문제를 수정했습니다. 판단을 가로막은 원인을 `unobservable_watch`에 명확히 밝힙니다.
- Antigravity CLI에서 패키지 파일만 배치하고 `agy plugin install`을 호출하지 않아 훅이 발행되지 않던 문제를 수정했습니다. 설치기가 CLI 등록 단계까지 자동으로 처리합니다.
- 평가 도구가 작업공간에 임시 설치된 GTG 자체 모듈의 실행까지 테스트 코드 실행으로 집계하여 GTG에 유리하게 편향되던 계측 오류를 바로잡았습니다.

## 호환성 안내

- 완료 증명서 스키마 버전이 v3으로 갱신되었습니다. 이전 버전 증명서는 인식되지 않으므로 `certify`로 다시 생성해야 합니다.
- 개발 문서 디렉터리 경로가 `docs/rebuild`에서 `docs/development`로 변경되었습니다.

## 참고 사항

동일한 기반 모델 환경에서 GTG 활성화 여부를 비교한 64회 시험 결과, 단일 턴 수준의 짧은 작업에서는 최종 산출물 차이가 없었습니다. GTG의 실질적 가치는 한 턴에 끝나지 않는 다단계 복합 작업에서 발휘됩니다. 구체적인 수치와 미확인 항목은 [확인한 것과 확인하지 못한 것](docs/verification/README.md) 문서를 참고하세요.


# 3.0.0-alpha.3 (2026-09-09, 개발 중, 미발행)

- 검사가 실제로 실행한 Python 파일을 관찰해 `unexecuted_watch`, `unverified_scope`로 검증하지 못한 범위를 밝힙니다.
- 증명서에 `coverage_complete`를 넣어 확인하지 못한 범위를 전부 검증으로 읽지 않게 했습니다.
- 증명서 스키마가 판 2로 바뀌어 호환되지 않습니다. 이전 판 증명서는 거부되므로 `certify`로 다시 만드세요.
- `replay` 판정이 `pass`, `invalid`, `inconclusive` 세 값이며 종료 코드는 각각 0, 1, 2입니다.
- 준비된 요청을 그대로 전달하는 `evals.harness run`과 팔별 실행 시간 집계를 추가했습니다.
- 배포 지시문의 제어, 양방향과 폭 없는 문자를 거부하고 `plugin.json`을 공식 CLI 스키마에 맞췄습니다.
- 안내 문서의 실행 예시가 실제 CLI 계약과 어긋나면 검사가 실패합니다.
- 설치물과 `.gtg`가 자기 자신을 무시해 사용자 저장소의 변경 목록을 오염시키지 않습니다.
- 재사용된 PID의 프로세스 그룹에 신호를 보내던 간헐적 실패를 고쳤습니다.

# 3.0.0-alpha.2 (2026-09-08, 개발 중, 미발행)

- Antigravity CLI(`agy`) 호스트를 공식 플러그인 경로에 설치하고 훅 두 개를 실제 실행해 검증합니다.
- 호스트별 이벤트와 설치 경로와 감지 표식을 `gtg/platforms.py` 한 곳으로 모았습니다.
- 설치기가 호스트 설정 파일을 감지해 한 명령으로 설치, 검사와 제거하며 부분 실패를 함께 보고합니다.
- 완료 주장을 명령과 종료 코드와 파일 지문에 연결하는 `certify`와 상태 DB 없이 재실행하는 `replay`를 추가했습니다.
- 같은 사례, 요청과 채점 기준을 공유할 때만 결과를 모으는 `evals.harness compare`를 추가했습니다.
- 긴 작업의 자동 재개 예산을 작업 명세의 `max_resumes`로 정합니다. 기본 2, 상한 8입니다.
- 모든 작업 명령이 `--workspace`를 받고, 조회 명령은 상태 없는 폴더에 새 DB를 만들지 않습니다.
- 규칙 파일 12,000자 한도와 스킬 메타데이터의 꺾쇠 금지를 패키지 검증에 넣었습니다.
- `.gtg` 상태 폴더가 자기 자신을 무시하고, 결과를 만들지 않는 명령은 새 작업에 등록되지 않습니다.

# 3.0.0-alpha.1 (2026-09-08, 사전 릴리즈)

- Python 실행 코어와 현재 파일 해시 기반 증거와 재시작 상태를 구현했습니다.
- Antigravity와 Gemini CLI 훅과 패키징을 분리하고 검증 후 설치, 백업과 복구를 추가했습니다.
- 특정 모델과 슬래시 명령을 요구하는 프로필을 작업별 스킬로 대체했습니다.
- 기존 작업 조회와 새 세션 연결과 검증 및 메모 보존 경로를 추가했습니다.
- 기존 113개 경로의 원문을 보존하고 중복 프로필 86개 경로를 제거했습니다.
- 실제 오류 수정과 종료 후 재개와 새 세션 연결을 제한된 사례에서 확인했습니다. 다른 모델과 경쟁 환경 대비 성능은 미검증입니다.
- 상태 안내를 축약하고 생략 정보와 현재 파일 재검증을 유지했습니다.

# Changelog

## Unreleased

## v2.15.0 (2026-09-03)

- updates harness target model from Gemini 3.7 Flash (High) to **Gemini 3.8 Flash (High)** (`gemini-3.8-flash`)
- renames focused skill and directory from `gemini-37-flash-high` to `gemini-38-flash-high`
- updates profile integrity checks, verification contracts, and manifests for Gemini 3.8 Flash
- updates all multi-language documentation and landing pages

## v2.14.0 (2026-08-24)

- completely removed all hooks, hook runner code, tests, and CI hook steps
- added documentation website to docs/ for GitHub Pages deployment
- enforced complete sentence endings and banned AI Slop UI patterns

- adds explicit prohibition against "AI-style narrative text" and "AI technical exposition text" across harness rules and human-copy skills
- strictly bans short-answers (unless essential for compact UI labels) and enforces natural, complete sentence endings (~합니다, ~해요)
- enforces friendly, non-technical explanations accessible to non-developers without technical jargon
- upgrades website presentation to **Apple Liquid Glass UI** with visionOS/macOS materials, SF Pro typography, and Apple.com minimalist layout
- synchronizes versioning and entrypoint assembly to v2.13.0

## v2.12.0 (2026-08-23)

- completely ports all 22 global engineering rules (0. Communication to 21. Hard Prohibitions) from `GEMINI.md` without omission, truncation, or invention
- introduces the **500-Line Limit Rule (500 LOC)** preventing single-file bloat and enforcing single-responsibility component decomposition
- embeds the 7-step debugging pipeline and 4-field blocker reporting format (`Tested`, `Failed`, `Ruled out`, `Next cause`)
- integrates strict security gates covering 9 sensitive files and dangerous command execution bans
- completely redesigns the presentation site with **Microsoft Windows 11 & WinUI 3 Fluent Design System 2.0** (Mica surfaces, Settings Cards, Windows Terminal, TitleBar)
- synchronizes versioning across all components to v2.12.0

## v2.11.3 (2026-08-23)

- establishes repository root `VERSION` as the single source of truth for version management
- adds `scripts/sync_version.py` to synchronize profile versions, manifests, entrypoint assembly, and cleanup in one step
- adds automated dynamic pruning in `scripts/install.sh` to remove non-active version directories without hardcoding
- resolves scattered version strings and prevents legacy version accumulation across updates

## v2.11.2 (2026-08-23)

- fixes step type recognition (`GENERIC`, `SYSTEM_MESSAGE`) in `verification_after_last_write` and helper verifiers
- prevents false Stop hook blocks and infinite continue loops across Antigravity IDE step reporting formats
- recognizes case-insensitive completion statuses (`DONE`, `SUCCESS`, `COMPLETED`) across command runners

## v2.11.1 (2026-08-17)

- fixes Stop hook infinite loops by allowing clean turn completion instead of perpetual continue blocks
- resolves exploration and tool deadlocks in scope-read gates by permitting list_dir, grep_search, and essential tool calls
- improves read-only request heuristics for error reports, questions, and inquiry prompts
- maintains strict quality standards while eliminating agent stall loops and token exhaustion

## v2.11.0 (2026-08-17)

- updates model target and system prompt optimizations for Gemini 3.8 Flash (High) with hybrid reasoning and thinking token budget allocation
- adds zero AI Slop intent orchestration and removes conversational filler, repetitive narrative phrasing, and speculative over-engineering
- strengthens single responsibility principle (SRP) architectural boundaries against God Objects in backend, frontend, and coordination layers
- establishes human-crafted UI/UX microcopy standards with concrete action verbs, empathetic error recovery, and clear hierarchy
- installs and verifies the v2.11.0 global profile while maintaining the entrypoint strictly under 6,000 characters (5,998 chars)

## v2.10.1 (2026-08-03)

- aligns the strict research message in the Stop hook and `/GTG` skill with the four-category v2.10 contract, including design-system evidence
- keeps v2.10.0 immutable as the previous release and points the current profile at the corrected patch release

## v2.10.0 (2026-08-03)

- adds a post-render Computer Use/vision observation gate for every strict UI task
- requires `search_web` followed by an official UI `read_url_content` after the visual observation
- adds Microsoft Fluent 2, Atlassian Design, Adobe Spectrum 2, IBM Carbon, and Shopify Polaris to the design-system evidence category
- raises the strict UI research contract from three to four evidence categories while keeping the always-on entrypoint below 6,000 characters

## v2.9.0 (2026-08-03)

- adds a machine-checked design decision ledger linking user outcome, rationale, implementation location, and verification method
- requires explicit recovery, retry, or undo paths in strict UI plans
- tightens `/GTG` intake wording so file lists and document summaries cannot substitute for contiguous, file-by-file source, configuration, and related-test reads
- replaces the blanket blur ban with a context gate: decorative content-surface blur and repeated material effects are blocked; functional navigation/control material remains possible when fallback is verified
- refreshes the adaptive-window, Apple materials, Design Theater, FlowEval, semantic-guidance, and GUIDE evidence set

## v2.8.0 (2026-08-03)

- Require every official UI source in a plan to carry a local finding, implementation impact or decision, and verification gate in the same evidence-matrix row or block.
- Extend Chrome rendering checks with actual CSS/DOM motion detection and `prefers-reduced-motion` emulation at every viewport.
- Connect the 2026 Antigravity Hooks, Chrome, WCAG 2.2, and Google HCI references to planning decisions and runtime verification.

## v2.7.0 (2026-08-03)

- removes the Stop-gate retry-limit escape hatch: incomplete source intake or required research keeps the execution loop running
- counts only successful transcript tool records as `view_file`/write evidence, so failed or errored calls cannot satisfy full-read gates
- aligns PreToolUse confirmation responses with the canonical Antigravity `ask` decision value

## v2.6.0 (2026-08-03)

- requires contiguous `view_file` reads of affected source, configuration, and tests before README/docs/search results, writes, or exploration can guide a change; the official `list_dir` summary is not a source read
- requires `/GTG` UI research to read at least four official URLs across three hosts and three evidence categories, then cite every URL in the report
- adds adaptive `reflow`/`reveal`/`presentation`, compact-transition, WAI-ARIA keyboard-pattern, and evidence-matrix contracts to UI plans
- compares planned files, routes, and flow traces with the actual implementation and browser evidence before completion
- refreshes the working evidence set against Apple HIG, Android adaptive guidance, Chrome I/O 2026, WCAG/APG, and Google GUIDE/HCI research

## v2.5.0 (2026-08-02)

- defaults website, webpage, landing-page, and static-page work to two or more route contracts instead of letting a single-page plan pass
- requires `/GTG` UI plans to compare at least two official sources and record the decision, implementation impact, motion budget, and verification gate
- blocks completion when restrained/expressive motion choice, trigger, timing, budget, or reduced-motion fallback is missing
- blocks shell workspace inventory (`find`, `ls`, `tree`, `fd`, `rg --files`, `git ls-files`) before source intake, in addition to IDE-native exploration
- keeps research and planning responsibilities split in a dedicated module; hook modules remain at or below 260 lines

## v2.4.0 (2026-08-02)

- blocks shell-based README, docs, Markdown reads before source intake, including `cat`, `sed`, `rg`, `git show`, and common script readers
- blocks IDE-native `analyze`, `inspect`, and `explore` reads of README/docs before source intake
- keeps strict `/GTG` review and diagnosis tasks running at `Stop` until the discovered implementation sources and related tests have full-read evidence
- blocks workspace/folder/file-tree exploration before source intake; directory summaries never count as a complete source read
- denies unknown analysis/exploration tools before source intake when Antigravity exposes them through the hook payload
- requires a successful post-write verification result instead of accepting a verification-shaped command alone
- keeps the source-order guard in its own module so the hook runner does not become a God Object
- refreshes the official Antigravity hook contract and 2026 UI evidence references used by the profile

## v2.3.0 (2026-08-02)

- extends Chrome UI rendering to 320px, 768px, and 1280px so the intermediate responsive state is measured instead of inferred
- requires UI plans to record visual direction, product rationale, rejected alternatives, and trade-offs without forcing one visual style
- requires verification plans to cover the medium viewport and real state transitions
- adds source-first call/state/data-path wording to the Gemini 3.6 Flash (High) skill so filenames, README, and docs cannot substitute for complete implementation reads
- aligns the UI planning, implementation, and review evidence with Apple 2026 HIG, Material 3 Expressive, Chrome Long Animation Frames/View Transitions, and WCAG 2.2

## v2.2.0 (2026-08-02)

- extends Chrome UI rendering with document metadata, semantic landmarks, image alt, accessible names, 24 CSS px control targets, keyboard focus, CLS, and Long Animation Frames diagnostics
- rejects duplicate route titles/headings and reduced-motion declarations that do not actually override animation or transition properties
- requires plan substance for motion purpose/timing, measurement, accessibility, and target-size checks
- refreshes 2026 Apple, Android Material 3, Chrome, W3C, and Google Research interface evidence

## v2.1.0 (2026-08-02)

- adds design, implementation, and verification plan gates before `/GTG` UI source writes
- requires route-aware multi-page plans and all-route Chrome renders when a website has multiple user flows
- adds deterministic plan and multi-page verifiers for route links, semantic structure, 320px/1280px render, overflow, reduced motion, and visible focus
- adds 2026 Apple, Chrome, web.dev, W3C, and Google Research references for interface planning
- updates the profile to 11 focused skills while keeping the hook responsibilities split

## v2.0.0 (2026-08-02)

- adds explicit `/GTG` strict mode for repository and UI work while keeping ordinary-request routing
- blocks writes until affected source files and a related test have been read from first line to last; README, docs, plans, comments, search summaries, and partial reads do not count
- requires separate first-party repository overview and implementation evidence when a page describes an external `owner/repository`
- blocks generic dark developer templates, Tailwind Slate inversions, centered documentation shells, repeated boxed sections, fake dashboards, repeated cards, vague copy, and decorative interaction
- requires post-write full-file rereads, project verification, dependency-free Chrome renders at 320px and 1280px, horizontal-overflow metrics, and direct screenshot inspection
- splits repository evidence and UI quality checks from the hook runner; every hook module stays at or below 260 lines
- adds direct God Object responsibility checks and the `architecture-boundaries` skill
- updates the 12 rules, 14 hooks, 10 skills, installer examples, checked installation snapshots, and four-language documentation

## v1.17.0 (2026-08-02)

- adds `scripts/install.sh`: update a clean checkout, back up the installed profile, install the current profile, and verify it in one run
- adds `--version vX.Y.Z`, `--skip-update`, `--help`, isolated install testing, and strict version validation
- replaces path-ordered whole-workspace reading with repository mapping plus full reads of affected source, call/data/state paths, and tests
- prevents README, plans, comments, search snippets, and summaries from counting as implementation evidence
- splits the former hook-runner God Object into focused state, payload, anchor, gate, and configuration modules
- adds an architecture-boundaries skill to separate UI state, domain decisions, I/O, persistence, network, and external-process responsibilities without file-count refactors
- strengthens UI implementation and review with product evidence, non-generic hierarchy, mobile-first reflow, accessibility states, reduced motion, and measured performance gates
- extends AI Slop checks for fake dashboards, glass/glow, nested cards, repeated radius/spacing, decorative 3D, vague copy, and purposeless interaction
- updates first-install, update, version-switch, removal, restore, UI, support, citation, issue, and social-preview surfaces

## v1.16.0 (2026-08-02)

- keeps the always-on entrypoint under 6,000 characters; detailed guidance now loads through focused skills and hooks
- adds an automatic workspace-intake skill for complete, path-ordered reading before changes
- adds PreInvocation anchors for scope intake, UI context, and product copy
- adds a write gate for native edits and common shell write paths until safe workspace text files have been read in full
- splits UI implementation from UI evidence review and extends human-copy checks for labels, links, and recovery text

## v1.15.0 (2026-08-02)

- 9th lifecycle hook: one-time UI evidence anchor after relevant invocations
- 2 focused skills: UI evidence review and human product copy
- focused automatic skill descriptions; no `@` mention or slash command required
- deterministic hook test added to local and CI validation

## v1.14.2 (2026-08-02)

- 모델이 생성한 UI를 정답으로 승인하지 않고 실제 렌더링과 제품 문맥, 접근성과 사용 흐름을 검증하도록 가드레일 강화
- Gemini 최신 모델의 시각 스타일 한계에 대응하는 결과 확인 기준 추가

## v1.14.1 (2026-08-01)

- 공식 Antigravity 문서에 없는 앱 버전 숫자 표기를 제거하고 전역 customization 경로 기준으로 정리
- Antigravity와 Antigravity IDE 모두 `~/.gemini/GEMINI.md`, `~/.gemini/config/` 기준으로 설명

## v1.14.0 (2026-08-01)

- Gemini 3.6 Flash 공식 모델 ID와 최신 Thinking 안내 반영
- 근거 없는 우주, 로봇과 관제 화면과 가짜 지표와 범용 AI 화면 패턴 차단
- 특정 시각 스타일을 기본값으로 강제하던 UI 지침 제거
- 레이아웃과 반응형 규칙을 콘텐츠와 기존 디자인 시스템과 접근성 근거 중심으로 조정
- 키보드 포커스와 색상 의존과 불필요한 상호작용 움직임을 UI 검증 항목에 추가

## v1.13.0 (2026-08-01)

- Gemini 3.6 Flash (High) targeting
- Antigravity and Antigravity IDE compatibility metadata
- 12 instruction files
- 8 lifecycle hooks
- 4 focused skills
- anti-AI-Slop UI and responsive-layout guardrails
- versioned profile history from `v1.0.0`
