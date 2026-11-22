# 구조 개요

GTG는 호스트가 턴마다 호출하는 **플랫폼 훅**과, 훅과 에이전트가 함께 사용하는 **로컬 실행 코어**로 나뉩니다. 코어는 모델 API나 외부 네트워크를 부르지 않고 Python 표준 라이브러리만으로 작업 상태, 완료 조건, 실행 증명서, 복구 과정을 다룹니다.

```
호스트(Antigravity / agy / Gemini CLI)
   │  훅 이벤트
   ▼
gtg/hooks.py ──▶ gtg/sessions.py ──▶ gtg/store.py  (SQLite + 파일 기반 실행 잠금)
   │                                      ▲
   ├── 안내 문구 gtg/context_message.py    │
   └── 교훈 기록 gtg/lessons.py            │
                                          │
모델이 부르는 명령 ──▶ gtg/runner.py ──────┘
   │                      ├─ gtg/spec.py       계약 검증, 파일 지문, 감시 범위 예산
   │                      ├─ gtg/coverage.py   실제 실행 파일 관측
   │                      └─ gtg/certificate.py 증명서 생성과 재실행
   │
   ├──▶ gtg/structure.py ──▶ gtg/changes.py (Git 변경 범위), gtg/code_shape.py (AST 측정)
   └──▶ gtg/prose.py ──▶ gtg/prose_registers.py (글 갈래별 규칙) ──▶ gtg/prose_patterns.py (표현 목록)
                     ├─▶ gtg/prose_rhythm.py (문장 리듬과 높임, 분량)
                     ├─▶ gtg/prose_score.py (신호 밀도를 점수로)
                     ├─▶ gtg/prose_fidelity.py (윤문 전후 비교)
                     └─▶ gtg/prose_input.py (파일·표준 입력 읽기)
```

## 경계 구분

사용자 인증, 모델 호출, 샌드박스 보안은 호스트가 전담하며 GTG는 여기에 직접 개입하지 않습니다. 호스트별 차이점인 이벤트 이름, 세션 식별 필드, 설치 경로, 제한 시간 단위는 [`gtg/platforms.py`](../../gtg/platforms.py)에 모아 관리합니다.

평가와 채점 코드는 제품 코드를 import하지 않고 표준 라이브러리만 사용합니다. 제품 코드를 수정하더라도 채점 기준이 임의로 바뀌지 않도록 방지하기 위함입니다.

내부 로직은 특정 모델 식별자로 분기하지 않으며 호스트에 설정된 모델을 그대로 활용합니다. 구조 및 문체 검사 역시 모델 종류와 무관하게 동일한 기준을 적용합니다.

문체 검사는 글 갈래에 따라 분리하여 [`gtg/prose_registers.py`](../../gtg/prose_registers.py)의 데이터로 관리합니다. 점수 계산은 [`gtg/prose_score.py`](../../gtg/prose_score.py)가 독립적으로 담당하며 충실도 검사는 [`gtg/prose_fidelity.py`](../../gtg/prose_fidelity.py)가 맡습니다.

## 모듈별 책임

모듈 하나가 여러 책임을 떠안지 않도록 역할을 아래 표에 한 문장으로 명시합니다. 실제 소스 파일과 이 표가 어긋나면 아키텍처 단위 시험이 실패합니다.

| 모듈 | 책임 |
| --- | --- |
| `gtg/platforms.py` | 호스트별 훅 이벤트와 설치 경로와 감지 표식의 단일 정의 |
| `gtg/spec.py` | 작업 계약 검증, 검증 대상의 지문과 범위 예산 |
| `gtg/code_contract.py` | 코드 작업의 빌드 선행 조건과 PRD 요구의 검사 연결 |
| `gtg/store.py` | 작업, 실행과 메모의 SQLite 상태와 실행 중 여부를 알리는 파일 잠금 |
| `gtg/runner.py` | 검증 명령 실행과 현재 상태 조회 |
| `gtg/coverage.py` | 검사가 실제로 실행한 코드 파일 관찰 |
| `gtg/certificate.py` | 완료 증명서 생성과 상태 DB 없는 재실행 |
| `gtg/checkpoints.py` | 검증과 분리된 재개용 메모 |
| `gtg/sessions.py` | 호스트 세션 연결과 재개 예산과 중단 |
| `gtg/hooks.py` | 호스트 이벤트를 로컬 증거와 연결 |
| `gtg/context_message.py` | 훅 안내의 표현. IO 없음 |
| `gtg/lessons.py` | 검증에서 드러난 교훈의 근거 확인, 저장과 최근 목록 조회 |
| `gtg/discovery.py` | 읽기 전용 작업 후보 조회 |
| `gtg/inspection.py` | 작업공간 텍스트 파일의 안전한 읽기와 범위 조회 |
| `gtg/environment.py` | 로컬 실행 환경 관찰과 명시한 필요조건 비교 |
| `gtg/testing.py` | Python 시험 관측의 유효성과 필수 시험 성공 확인 |
| `gtg/unittest_probe.py` | 별도 프로세스에서 unittest 실행과 시험별 성공 관측 |
| `gtg/changes.py` | Git 기준 리비전과 작업 트리의 변경 파일과 추가된 줄 조회 |
| `gtg/code_shape.py` | Python 소스 하나의 정의, 복잡도, 응집도와 빈 본문 측정. IO 없음 |
| `gtg/structure.py` | 변경 코드에 구조 기준을 적용한 차단과 검토 신호 |
| `gtg/prose.py` | 표현과 리듬 신호를 줄 번호와 함께 모아 문서별 결과로 취합하기 |
| `gtg/prose_input.py` | 검사할 글을 파일이나 표준 입력에서 읽고 읽지 못한 이유를 상태로 적기 |
| `gtg/prose_patterns.py` | 문체 검사가 찾는 공통 표현 목록. 로직 없음 |
| `gtg/prose_registers.py` | 학술, 일상과 문학 갈래별로 규칙을 끄고 완화하고 더하기 |
| `gtg/prose_rhythm.py` | 문장 길이, 어미, 첫머리, 쉼표와 높임 등급과 글 분량 측정 |
| `gtg/prose_score.py` | 찾은 신호의 밀도를 0~100점과 A~D 등급으로 환산 |
| `gtg/prose_fidelity.py` | 윤문 전후를 견줘 수치, 인용, URL, 코드가 남았는지와 바뀐 분량 재기 |
| `gtg/package.py` | 호스트별 패키지 생성과 원문과 훅 검증 |
| `gtg/install.py` | 호스트 감지, 설치, 검사, 제거와 복구 |
| `gtg/install_journal.py` | 파일 이동의 사전 기록과 되돌리기 |
| `gtg/legacy.py` | 구형 프로필 링크의 보존과 복구 |
| `gtg/__main__.py` | 에이전트가 쓰는 CLI 진입점 |

평가 프레임워크 구조는 [평가 문서](../../evals/README.md)에 기술되어 있으며 채점 로직은 제품 코드를 import하지 않습니다.

## 상태 저장소와 격리

상태는 작업공간 내 `.gtg/state.sqlite3` 파일에 보관합니다. 폴더는 `0700`, 파일은 `0600` 권한으로 생성하고 내부에 `.gitignore`를 배치하여 Git 추적에서 제외합니다. 교훈 기록 파일인 `.gtg/lessons.jsonl`도 동일한 폴더를 사용합니다.

동시에 실행되는 검사는 단 하나여야 하며 데이터베이스 유니크 인덱스로 통제합니다. 실행 중 여부는 OS 파일 잠금으로 판정합니다.

## 패키징과 설치

호스트별 패키지는 단일 원본 소스에서 빌드합니다. 설치 전 임시 폴더에서 패키지를 검증하고 파일 이동 기록을 남긴 뒤 실제 설치를 진행하므로, 중단되더라도 다음 실행 시 잔여 파일을 안전하게 되돌립니다. 배포 패키지에는 모든 파일의 SHA-256 목록이 포함되어 파일 변조를 감지합니다.
