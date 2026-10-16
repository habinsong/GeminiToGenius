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

별도 `--home` 경로의 설치는 실제 사용자 호스트의 등록을 건드리지 않고 수동 명령만 안내합니다. 실제 홈에서 등록 명령이 실행됐으나 실패하면 설치 결과는 `ok: false`이며 검증된 파일과 복구 경로는 보존합니다. `doctor`는 파일·훅·호스트·버전을 검사하며 실제 모델의 플러그인 채택까지 증명하지 않습니다.

`agy 1.1.28`은 CLI 패키지를 데스크톱 공용 경로에도 복사합니다. 설치기는 기존 공용 패키지를 먼저 보존하고, 복사가 확인되면 해당 경로를 데스크톱용으로 다시 구성합니다. 결과의 `shared_host_backup`과 `shared_host_repair`로 이 처리를 확인할 수 있습니다.

헤드리스 모드(`agy -p`)로 실행할 때는 `--add-dir`로 작업공간을 명시해야 합니다. 지정하지 않으면 훅이 전달받는 `workspacePaths`가 빈 배열이 되어 GTG가 검증을 수행하지 않습니다.

명령 실행 권한도 호스트에서 허용되어야 합니다. 3.0.1 실호스트 시험에서 허용되지 않은 `RunCommand`가 거부됐는데도 CLI는 종료 코드 0과 `status: "SUCCESS"`를 반환했습니다. `denied_actions`, 실제 변경과 실행 결과를 함께 확인해야 합니다. GTG 설치기는 전역 권한을 허용하거나 검사를 우회하지 않습니다.

2026-09-09에 확인한 `agy 1.1.28`에서는 비활성화한 플러그인을 `enable`이나 같은 경로의 `install`만으로 복구하지 못했고 `uninstall` 후 재설치가 필요했습니다. 당시 목록 표시는 정상이었습니다. 다른 버전에도 같은 결함이 있다고 단정하지 말고 실제 로딩을 확인합니다.

## Gemini CLI

GTG는 Gemini CLI 호환 패키지를 유지하며 `--platform gemini-cli`로 명시할 때 설치합니다. 자동 감지에서 제외한 것은 GTG 설치 정책이며 서비스 종료를 뜻하지 않습니다. 계정 지원과 인증 방식은 [현재 공식 안내](https://geminicli.com/docs/get-started/authentication/)에서 확인합니다.

`BeforeAgent`의 `additionalContext`로 해당 턴의 맥락을 전달하고, `AfterAgent`의 `decision: "deny"`와 `reason`으로 제한된 재시도를 요청합니다. 예산 소진이나 사용자 중단은 세션을 멈춥니다. [공식 훅 계약](https://geminicli.com/docs/hooks/reference/).

## 규칙 파일

GTG는 Antigravity 규칙을 `rules/AGENTS.md`에 배치합니다. [현재 공식 한도](https://antigravity.google/docs/rules)는 포함 확장 뒤 파일별 24,000바이트, 활성 규칙 합계 20,000토큰입니다. GTG는 24,000바이트와 기존 패키지 호환 정책인 12,000자를 함께 검사합니다. 사용자 전체 규칙의 토큰 합계나 외부 포함 확장까지 측정하지는 않습니다.

