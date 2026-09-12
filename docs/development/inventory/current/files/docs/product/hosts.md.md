# `docs/product/hosts.md`

- 형식: `100644`
- 바이트: 2813
- SHA-256: `cd46a88001214bda910c9a8867e970ed0c7c88559eea1580355d045f7f87b016`
- 인코딩: `utf-8`

```
# 지원 호스트

세 가지 호스트를 지원합니다. 호스트마다 훅 이벤트 명칭과 식별 필드가 다르므로, 해당 세부 차이는 [`gtg/platforms.py`](../../gtg/platforms.py) 단 한 곳에서 일원화하여 관리합니다.

| 호스트 | 설치 경로 | 훅 이벤트 |
|---|---|---|
| `antigravity` (데스크톱·IDE) | `~/.gemini/config/plugins/geminitogenius/` | `PreInvocation`, `Stop` |
| `antigravity-cli` (`agy`) | `~/.gemini/antigravity-cli/plugins/geminitogenius/` | `PreInvocation`, `Stop` |
| `gemini-cli` | `~/.gemini/extensions/geminitogenius/` | `BeforeAgent`, `AfterAgent` |

작업공간(프로젝트별) 설치는 `antigravity`만 지원하며, 나머지 둘은 전역 경로 설치 동작만 확인했습니다.

## Antigravity CLI (`agy`)

**해당 디렉터리에 파일을 두는 것만으로는 플러그인이 인식되지 않습니다.** `agy plugin install`을 실행해 등록해야 스킬과 훅이 정상 동작합니다. 설치기가 이 과정까지 자동으로 처리하며, `agy`를 찾지 못하더라도 오류로 중단하지 않고 수동 실행 명령을 결과의 `host_registration`에 안내합니다.

헤드리스 모드(`agy -p`)로 실행할 때는 `--add-dir`로 작업공간을 명시해야 합니다. 지정하지 않으면 훅이 전달받는 `workspacePaths`가 빈 배열이 되어 GTG가 검증을 수행하지 않습니다.

플러그인을 `agy plugin disable`로 비활성화했다가 다시 활성화할 때는 주의가 필요합니다. `enable`이나 동일 경로 대상 `install` 재실행으로는 정상 복구되지 않으며, `uninstall` 후 다시 `install`을 실행해야 했습니다. 그 과정에서도 `agy plugin list`는 계속 정상 상태로 표시되므로, 목록 문구가 아닌 실제 동작 여부로 확인해야 합니다.

## Gemini CLI

2026-06-18부로 개인 계정 요청 처리가 종료되었으며 확장 기능은 Antigravity 플러그인 생태계로 통합되었습니다. GTG는 호환 패키지를 유지하되 자동 감지 대상에서는 제외하고, `--platform gemini-cli` 옵션으로 명시할 때만 설치합니다.

이 호스트에서는 훅이 실행 종료를 차단하지 않고 상태를 전달할 수 있는 유일한 수단이 `systemMessage`입니다. 이 메시지는 대화형 터미널에만 출력되며 모델의 대화 컨텍스트에는 포함되지 않습니다.

## 규칙 파일

일반적인 규칙 파일명은 Antigravity에서 인식되지 않았습니다. 공식 가이드에 따라 `rules/AGENTS.md`로 배치해야 환경 설정에서 규칙으로 정상 인식됩니다. 규칙 파일은 호스트 정책상 12,000자를 초과할 수 없으며, 패키지 검증 단계에서 글자 수 한도와 숨겨진 제어 문자를 함께 검사합니다.

```
