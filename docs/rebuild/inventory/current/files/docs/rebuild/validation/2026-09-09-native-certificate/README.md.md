# `docs/rebuild/validation/2026-09-09-native-certificate/README.md`

- 형식: `100644`
- 바이트: 4633
- SHA-256: `e9a1b70d6135255db152dd6fe6d23c63c379c7d3bccc690f3eccd9e0c916cfe4`
- 인코딩: `utf-8`

```
# 실제 Antigravity 시험: 자동 스킬·작업 등록·완료 증명서

확인일: 2026-09-09. Antigravity 2.12.2, 표시 모델 `Gemini 3.8 Flash High`. 실제 요청 2회를 보냈습니다. 전체 목표에서 보낸 실제 시험 요청은 누적 6회입니다.

시험 폴더는 기존 프로젝트가 가리키던 경로를 다시 만들어 사용했습니다. Antigravity 설정은 바꾸지 않았습니다. 시작 전 새로고침한 잔여 한도는 주간 100%·5시간 100%였고, 두 요청 뒤에는 주간 99%·5시간 98%였습니다. 정확한 토큰 사용량은 아닙니다.

## 먼저 발견해 고친 결함

설치 직후 사용자 저장소의 `git status`에 설치물 28개 경로와 `.gtg/installer/install.lock`이 나타났습니다. 실제 사용에서만 드러난 문제입니다.

패키지에 자기 자신을 무시하는 `.gitignore`를 포함하고, 설치기가 `.gtg`를 만들 때도 같은 파일을 씁니다. 다른 플러그인과 사용자 규칙 파일은 계속 보입니다. 재설치 후 `git status`가 비었습니다.

## 요청 1: 짧은 자연어 오류 수정

입력은 `재고 올리는 게 안 되는데 고쳐줘` 한 문장이며 슬래시 명령이 없습니다.

- 모델의 **첫 도구 호출이 `.agents/plugins/geminitogenius/skills/gtg-build/SKILL.md` 읽기**였습니다. 이어서 `references/task-contract.md`를 읽었습니다. 자동 스킬 선택과 점진적 로딩이 실제로 동작했습니다.
- 21단계에서 `python3 .agents/plugins/geminitogenius/run.py tasks --workspace .`를 한 번에 성공했습니다. 이전 시험에서 관찰한 실행기 경로 탐색과 잘못된 `--workspace` 호출이 사라졌습니다.
- 작업을 등록하지 않고 직접 고쳤습니다. 규칙의 "일상 답변과 단순 수정은 직접 처리합니다"와 일치합니다.
- `inventory.py` 한 파일만 바꿨고 `python3 check_inventory.py`가 통과했습니다. 최종 답변은 규칙이 요구한 **변경 사항·실행한 검증·미검증 범위** 구조 그대로였습니다. 1분 걸렸습니다.

## 요청 2: 여러 단계 기능 구현

입력은 `README에 적어둔 재고 보고서 기능 구현해줘. 기존 거 깨지면 안 돼` 한 문장입니다.

- 모델이 **스스로 작업을 등록했습니다.** 목표와 검사 2개를 만들었고 각 검사의 `watch` 범위를 나눠 지정했습니다.
  - `regression`: `python3 check_inventory.py`, watch `inventory.py`, `check_inventory.py`
  - `report`: `python3 check_report.py`, watch `report.py`, `inventory.py`, `check_report.py`
- 두 검사 모두 실제 실행에서 종료 코드 0으로 통과했습니다. [상태 스냅샷](state-snapshot.json).
- **`certify`로 증명서를 만들고 `replay`로 스스로 독립 재실행까지 했습니다.** 안내한 적 없는 새 기능을 스스로 채택했습니다. 최종 답변에 `verified: true`, `reconstructed: true`, 증명서 경로를 함께 적었습니다.
- 종료 훅 기록은 `NO_TOOL_CALL`, `fully_idle: true`, 오류 없음이며 재개 횟수는 0입니다. 모든 검사가 통과해 훅이 정상 종료를 허용했습니다. 자동 재개 경로는 이번에 발동하지 않았습니다.

## 증명서 독립 검증

- [증명서](certificate.json)는 검사마다 명령·종료 코드·검증 대상 파일 지문을 담습니다.
- 같은 폴더에서 `replay`를 실행해 [재현 성공](replay-clean.json)을 확인했습니다.
- 반증 시험으로 `report.py`에 주석 한 줄을 추가하자 `reconstructed: false`, 해당 검사만 `reason: "fingerprint"`가 됐고 `status`는 `stale`, 전체 `verified`는 거짓이 됐습니다. 원상 복구 후 다시 재현됐습니다.

## 발견과 예산

Antigravity 설정의 Customizations에서 `gtg-build`·`gtg-interface`·`gtg-research` 세 스킬이 모두 `Plugin: geminitogenius`로 표시됐습니다. 규칙 572토큰 2.9%, 스킬 319토큰 1.6%이며 커스터마이제이션 예산의 95.5%가 남아 있습니다. 이 값은 전체 커스터마이제이션 합계이며 GTG만의 값이 아닙니다.

## 한계

두 번의 요청이며 통계가 아닙니다. 자동 재개·일시 중단·여러 작업공간 경로는 이번 시험에서 발동하지 않았습니다. 다른 모델과 경쟁 도구 대비 우월성은 이 기록으로 주장하지 않습니다. `agy` 실행 파일은 여전히 이 컴퓨터에 없으므로 Antigravity CLI의 실제 발견은 미검증입니다. 사용자의 전역 설치는 이전 alpha.1 빌드였고, 이번 시험은 작업공간에 설치한 현재 빌드를 사용했습니다.
```
