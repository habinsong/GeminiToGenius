<div align="center">

<h1>GeminiToGenius</h1>

<p>Gemini를 조금 더 똑똑하게(덜 멍청하게) 만드는 플러그인입니다.</p>

<p>한국어 · <a href="docs/README.en.md">English</a></p>

<p><a href="https://github.com/habinsong/GeminiToGenius/releases">릴리즈</a> · <a href="docs/product/getting-started.md">설치 안내</a> · <a href="docs/verification/README.md">검증 기록과 한계</a> · <a href="CHANGELOG.md">변경 기록</a></p>

<p>GTG 3.1.0은 Antigravity 데스크톱·IDE, Antigravity CLI, Gemini CLI를 지원합니다.</p>

</div>

## 하는 일

- 작업을 등록할 때 완료 조건과 검증 명령을 먼저 고정합니다. 등록한 뒤에는 통과하기 쉬운 명령으로 임의 변경할 수 없습니다.
- `verify`는 등록된 명령을 실제로 실행하며 종료 코드, 소요 시간, 검사 대상 파일 목록을 기록합니다. 검사 대상 파일이 변경되면 이전 성공 기록은 효력을 잃습니다.
- `certify`는 완료 주장과 실행 근거를 단일 파일에 묶습니다. `replay`는 별도 상태 DB 없이 해당 파일과 현재 작업공간만으로 결과를 다시 검증합니다.
- 검사가 실행하지 못한 파일과 판단할 수 없었던 범위도 결과에 있는 그대로 명시합니다. 비어 있는 목록을 '모두 확인 완료'로 포장하지 않습니다.
- 세션이 끊겨도 등록된 작업과 검사 결과, 기록 메모는 보존됩니다. 새 세션에서는 `tasks`로 검색해 `attach`로 작업을 이어갈 수 있습니다.
- 코드를 바꾼 뒤에는 `structure` 검사가 이번 변경의 빈 함수와 새 TODO, 큰 파일에 쌓인 기능, 계속 불어나는 클래스를 막고, 구현이 하나뿐인 추상화나 인자만 넘기는 래퍼, 부르는 곳 없는 새 정의를 검토 신호로 알립니다.
- 문서를 쓴 뒤에는 `prose` 검사가 한국어·영어 상투구와 과장, 번역투가 몰린 문단, 뚝뚝 끊기는 문장을 줄 번호와 함께 찾습니다.
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

3.1.0은 결과물을 직접 읽는 구조·문체 검사와 교훈 기록을 더하고, 상시 규칙을 "기억보다 원문, 끝내기 전에 스스로 반박하기" 중심으로 다시 썼습니다. [검증 범위와 조사 출처](docs/verification/3.1.0.md)에 무엇을 확인했고 무엇을 확인하지 못했는지 적어 두었습니다.

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
| 3.1.0 오프라인 시험 | 전체 411개 시험이 통과했습니다. 구조·문체 검사는 걸려야 할 사례와 걸리면 안 되는 사례를 함께 시험했고, 구현을 일부러 망가뜨려 시험이 잡는지도 확인했습니다. 실제 Gemini 호출은 하지 않았습니다. |

구체적인 수치, 실행 환경, 미확인 항목은 [검증 기록](docs/verification/README.md)에 가감 없이 정리했습니다.

## 아직 확인하지 못한 것

- Windows 환경 설치 및 네트워크 파일 시스템에서의 실행 잠금 동작
- 실제 전원 차단 후 복구, 다일 간의 장기 작업, 다양한 모델에서의 반복 시험
- Go·Rust와 컴파일하여 실행하는 TypeScript의 실행 범위 관측
- 토큰 사용량 및 비용 측정
- 3.1.0 지침과 구조·문체 검사, 교훈 기록이 실제 Gemini 4 Argon·Gemini 3.8 Flash의 환각과 미완성 보고를 줄이는지
- 데스크톱 Antigravity의 웹 도구 이름(SDK 소스의 `search_web`, `read_url_content`와 같은지)

## 문서

| 문서 | 내용 |
| --- | --- |
| [설치와 첫 사용](docs/product/getting-started.md) | 설치, 호스트 선택, 제거 방법 |
| [동작 방식](docs/product/how-it-works.md) | 작업 등록부터 검증과 재확인까지의 실행 흐름 |
| [명령 목록](docs/reference/cli.md) | 에이전트가 사용하는 CLI 명령과 종료 코드 |
| [완료 증명서](docs/reference/certificate.md) | 증명서 규격과 `replay` 판정 기준 |
| [검증 기록과 한계](docs/verification/README.md) | 실호스트 검증, 하네스 비교, 미확인 범위 |
| [전체 문서](docs/README.md) | 제품·참조·구조 문서 전체 색인 |

## 개발

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
python3 scripts/catalog.py --check
```

현재 작업과 남은 과제는 [개발 기록](docs/development/current-work.md)에, 파일별 원문과 해시는 [현재 목록](docs/development/inventory/current/README.md)에 정리되어 있습니다.

## 라이선스

MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE)를 참고하세요. Google, Antigravity, Gemini와 공식 제휴나 후원 관계가 아니며, 제품명은 호환 대상을 안내하기 위한 용도로만 사용합니다.
