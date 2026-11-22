# 구조 개요

GTG는 **플랫폼 훅**(호스트가 턴마다 호출)과 **로컬 실행 코어**(훅과 에이전트가 함께 사용)로 이루어집니다. 코어는 모델 API나 외부 네트워크를 호출하지 않고 Python 표준 라이브러리만으로 작업 상태, 완료 조건, 실행 증명서, 복구 과정을 처리합니다.

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
   └──▶ gtg/structure.py ──▶ gtg/changes.py (Git 변경 범위), gtg/code_shape.py (AST 측정)
```

## 경계 구분

사용자 인증, 모델 호출, 샌드박스 보안은 호스트가 전담하며 GTG가 직접 개입하는 부분은 없습니다. 호스트별 차이점인 이벤트 이름, 세션 식별 필드, 설치 경로, 제한 시간 단위는 [`gtg/platforms.py`](../../gtg/platforms.py)에 모여 있습니다.

평가와 채점 코드는 제품 코드를 import하지 않고 표준 라이브러리만 사용합니다. 제품 코드를 수정해도 채점 기준이 따라 바뀌는 일을 막으려는 설계입니다.

내부 로직은 특정 모델 식별자로 분기하지 않으며 호스트에 설정된 모델을 그대로 씁니다. 구조 검사 역시 모델 종류와 무관하게 동일한 기준을 적용합니다.

문서 문체 측정은 [`profile/skills/ai-smell-polish`](../../profile/skills/ai-smell-polish/SKILL.md)의 독립 엔진이 맡습니다. `gtg` 코어는 이 엔진을 import하지 않고, 스킬로 설치되어 호스트가 명령줄로 실행합니다.

## 모듈별 책임

모듈 하나가 여러 책임을 떠안지 않도록 역할을 아래 표에 한 문장으로 정리했습니다. 실제 소스 파일과 이 표가 어긋나면 아키텍처 단위 시험이 실패합니다.

| 모듈 | 책임 |
| --- | --- |
| `gtg/platforms.py` | 호스트별 훅 이벤트와 설치 경로와 감지 표식의 단일 정의 |
| `gtg/spec.py` | 작업 명세 검증, 검증 대상의 지문과 범위 예산 |
| `gtg/code_contract.py` | 코드 작업의 빌드 선행 조건과 PRD 요구의 검사 연결 |
| `gtg/store.py` | 작업, 실행과 메모의 SQLite 상태와 실행 중 여부를 알리는 파일 잠금 |
| `gtg/runner.py` | 검증 명령 실행과 현재 상태 조회 |
| `gtg/coverage.py` | 검사가 실제로 실행한 코드 파일 관찰 |
| `gtg/certificate.py` | 완료 증명서 생성과 상태 DB 없는 재실행 |
| `gtg/checkpoints.py` | 검증과 분리된 재개용 메모 |
| `gtg/sessions.py` | 호스트 세션 연결과 재개 예산과 중단 |
| `gtg/hooks.py` | 호스트 이벤트를 로컬 증거와 연결 |
| `gtg/context_message.py` | 훅 안내의 표현. IO 없음 |
| `gtg/lessons.py` | 검증에서 확인된 교훈의 근거 확인, 저장과 최근 목록 조회 |
| `gtg/discovery.py` | 읽기 전용 작업 후보 조회 |
| `gtg/inspection.py` | 작업공간 텍스트 파일의 안전한 읽기와 범위 조회 |
| `gtg/environment.py` | 로컬 실행 환경 관찰과 명시한 필요조건 비교 |
| `gtg/testing.py` | Python 시험 관측의 유효성과 필수 시험 성공 확인 |
| `gtg/unittest_probe.py` | 별도 프로세스에서 unittest 실행과 시험별 성공 관측 |
| `gtg/changes.py` | Git 기준 리비전과 작업 트리의 변경 파일과 추가된 줄 조회 |
| `gtg/code_shape.py` | Python 소스 하나의 정의, 복잡도, 응집도와 빈 본문 측정. IO 없음 |
| `gtg/structure.py` | 변경 코드에 구조 기준을 적용한 차단과 검토 대상 표시 |
| `gtg/package.py` | 호스트별 패키지 생성과 원문과 훅 검증 |
| `gtg/install.py` | 호스트 감지, 설치, 검사, 제거와 복구 |
| `gtg/install_journal.py` | 파일 이동의 사전 기록과 되돌리기 |
| `gtg/legacy.py` | 구형 프로필 링크의 보존과 복구 |
| `gtg/__main__.py` | 에이전트가 쓰는 CLI 진입점 |

평가 프레임워크의 구조는 [평가 문서](../../evals/README.md)에 기술되어 있습니다.

## 상태 저장소와 격리

상태는 작업공간 내 `.gtg/state.sqlite3` 파일에 들어 있습니다. 폴더는 `0700`, 파일은 `0600` 권한으로 생성하고 내부에 `.gitignore`를 배치하여 Git 추적에서 제외합니다. 교훈 기록 파일인 `.gtg/lessons.jsonl`도 같은 폴더 안에 있습니다.

동시에 실행할 수 있는 검사는 데이터베이스 유니크 인덱스에 따라 하나뿐입니다. 실행 중 여부는 OS 파일 잠금으로 판정합니다.

## 패키징과 설치

호스트별 패키지는 단일 원본 소스를 바탕으로 만듭니다. 설치 전 임시 폴더에서 패키지를 검증하고 파일 이동 기록을 남긴 뒤 실제 설치를 진행하므로, 중단되더라도 다음 실행 시 잔여 파일을 되돌립니다. 배포 패키지에는 모든 파일의 SHA-256 목록이 포함되어 파일 변조를 감지합니다.
