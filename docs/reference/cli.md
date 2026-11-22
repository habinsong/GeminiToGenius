# 명령 목록

설치된 패키지 디렉터리의 `run.py`가 전체 CLI의 진입점이며 모델이 명령을 직접 호출하므로 사용자가 터미널에서 입력할 필요는 없습니다. 아래 예시의 `$GTG`는 설치된 `run.py`의 절대 경로입니다.

```bash
GTG=~/.gemini/config/plugins/geminitogenius/run.py
```

모든 작업 관리 명령은 `--workspace` 옵션을 지원하며 생략하면 현재 디렉터리를 작업공간으로 삼습니다. 상태 데이터베이스 경로는 전역 옵션 `--state`로 직접 지정할 수 있으며 두 옵션을 함께 전달하면 `--state`가 우선 적용됩니다.

## 작업 관리

| 명령 | 역할 |
|---|---|
| `start --spec <파일>` | 완료 조건이 고정된 새 작업을 생성하며 `--platform`, `--session`을 지정하면 해당 세션에도 연결합니다. |
| `tasks` | 저장된 작업 목록, 메모, 세션 연결 후보를 읽기 전용으로 조회하며 기록된 상태가 없으면 빈 목록을 반환합니다. |
| `attach <작업ID> --platform <호스트> --session <세션>` | 기존 작업을 현재 활성 세션으로 전환하여 연결하며 이전 검사 결과와 메모는 보존됩니다. |
| `status <작업ID>` | 지정된 작업의 검사 결과, 작업 명세, 진행 메모를 조회합니다. |
| `checkpoint <작업ID> --note <파일>` | 작업 재개용 메모를 저장하며 검사 통과 여부는 메모와 별개로 `verify` 결과로 판단합니다. |

## 검증 실행

| 명령 | 역할 |
|---|---|
| `verify <작업ID>` | 등록된 검증 명령들을 순차 실행하며 첫 번째 실패가 발생하면 즉시 중단합니다. |
| `verify <작업ID> --all` | 일부 검사가 실패하더라도 등록된 모든 검증을 끝까지 실행합니다. |
| `verify <작업ID> --check <검사ID>` | 지정한 검사만 골라 실행하며 결과는 `requested_verified` 필드에 표시됩니다. |
| `recover <작업ID>` | 중단된 검사의 잔여 실행 기록을 정리하며 검사 프로세스가 동작 중이면 정리를 거부합니다. |

## 완료 증명서와 replay

| 명령 | 역할 |
|---|---|
| `certify <작업ID> --output <파일>` | 완료 주장과 실제 실행 명령, 종료 코드, 파일 지문을 단일 증명서 파일로 패키징하며 미검증 상태이면 종료 코드 1을 반환합니다. |
| `replay --certificate <파일>` | 증명서 파일만 읽어 로컬 상태 데이터베이스 없이 검증 명령을 다시 실행합니다. |

`replay`의 종료 코드는 증명서 판정 결과와 일치하여 `0`은 `pass`(재실행 성공 및 범위 완전), `1`은 `invalid`(재실행 실패 또는 불일치), `2`는 `inconclusive`(재실행은 성공했으나 미확인 범위 잔존)입니다.

## 기타 유틸리티

| 명령 | 역할 |
|---|---|
| `inspect <경로...>` | 여러 텍스트 파일을 한 번에 읽고 라인 범위, 잘림 여부, 파일 해시를 반환합니다. |
| `environment [--expect <파일>]` | 로컬 Python 프로세스의 실행 환경(OS, 아키텍처, 런타임)과 실행 파일 존재를 관찰하고 조건과 비교합니다. 불일치는 종료 코드 1을 반환합니다. |
| `unittest [--start-directory <폴더>] [--pattern <패턴>] [--require <시험ID>]` | Python unittest를 별도 프로세스에서 실행하고 필수 시험 ID의 성공을 확인합니다. 실패나 누락, 필수 skip이 있으면 종료 코드 1로 끝납니다. |
| `pause --platform <호스트> --session <세션> --reason <사유>` | 사용자의 확인 대기나 외부 리소스 한도로 인해 작업을 일시 정지합니다. |
| `resume --platform <호스트> --session <세션>` | 일시 정지된 세션 연결을 다시 활성화합니다. |

## 환경 조건 비교

```bash
python3 "$GTG" environment
python3 "$GTG" environment --expect verification-environment.json
```

조건 파일은 작업 요구사항에 따라 에이전트가 직접 작성합니다. `system`, `machine`, `python_version`, `python_implementation`은 문자열을 정확히 비교하며 `executables`는 PATH에서 찾을 실행 파일 이름 목록입니다. 잘못된 필드나 빈 조건은 거부합니다.

관찰 범위는 현재 Python 프로세스에 한정되며 컨테이너나 원격 환경의 실행 조건은 관찰 대상 밖입니다. `target_compatibility_verified`와 `resource_limits_verified`는 항상 `false`입니다.

## Python 필수 시험

```bash
python3 "$GTG" unittest --workspace . --start-directory tests
```

`--require`에는 발견된 실제 전체 시험 ID를 지정하며 실행 결과가 0개이거나 필수 시험이 누락 또는 skip된 경우는 실패로 처리합니다.

프로젝트 인터프리터를 사용하고 제한 시간은 작업 명세의 `timeout_seconds`를 따릅니다. 관측 JSON은 최대 256KiB이며 용량 초과나 조기 종료는 실패로 처리합니다.

## 결과물 검사

| 명령 | 역할 |
|---|---|
| `structure [경로...] [--base <리비전>] [--max-lines <줄>] [--max-methods <개수>]` | `--base` 리비전(기본 HEAD)과 작업 트리를 비교해 변경된 코드만 검사하고 새로 작성한 줄의 TODO, 본문이 빈 함수, 초과 크기 파일, 한도를 넘는 클래스 메서드, 구문 오류가 있으면 종료 코드 1을 반환합니다. |

```bash
python3 "$GTG" structure --workspace . --base START_COMMIT
```

`structure` 결과의 `findings`에는 `block`(차단)과 `review`(검토) 항목이 나뉘어 담기고, 종료 코드는 차단 항목에 따라서만 결정됩니다.

`structure`의 기본값은 파일 400줄 및 클래스 메서드 20개이며, 이미 한도를 초과한 대형 파일은 30줄을 넘겨 더 커지거나 새 최상위 정의가 생길 때만 차단하므로 기존 레거시 코드의 단순 버그 수정은 그대로 진행할 수 있습니다.

문서 문체의 측정과 윤문은 `gtg` 명령이 아니라 `ai-smell-polish` 스킬의 `scripts/ai-smell`(`analyze`, `polish`, `verify`)이 맡습니다. 사용법은 [`vendor/ai-smell-meter`](../../vendor/ai-smell-meter/README.md)에 있습니다.

## 교훈 기록

| 명령 | 역할 |
|---|---|
| `lesson --text <문장> --evidence <근거>` | 검증에서 확인된 저장소 사실을 `.gtg/lessons.jsonl`에 저장합니다. 근거는 작업공간의 실제 파일이나 URL을 기록합니다. 중복 문장은 한 번만 저장하고 최근 100개까지 유지합니다. |
| `lessons [--limit <개수>]` | 저장된 교훈을 최근 순으로 조회합니다. |

턴 시작 훅은 최근 교훈 다섯 개를 참고 기록으로 모델 안내에 덧붙입니다.

## 플랫폼 훅

호스트 환경이 `hook <호스트> <이벤트>` 규격으로 호출하며 표준 입력으로 호스트 이벤트 페이로드를 전달받고 표준 출력으로 처리 결과 JSON을 응답합니다. 세부 계약은 [훅 계약](hooks.md) 문서를 참고해 주십시오.
