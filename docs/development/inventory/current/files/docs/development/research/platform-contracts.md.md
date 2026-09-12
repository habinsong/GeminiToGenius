# `docs/development/research/platform-contracts.md`

- 형식: `100644`
- 바이트: 8520
- SHA-256: `65042e2ac128bd57816a21f3c96392a93eb896f14b82401c1957caa4542e53b1`
- 인코딩: `utf-8`

```
# 플랫폼 계약 및 런타임 인터페이스 조사

확인일: 2026-09-08. 공식 벤더 기술 문서를 직접 열람하여 분석했습니다. 문서상 규격 확인과 실제 런타임 호환성 검증은 명확히 구분하여 다룹니다.

현재 지원 대상 호스트는 3종입니다: Antigravity 데스크톱·IDE(`antigravity`), Antigravity CLI(`antigravity-cli`), Gemini CLI 확장(`gemini-cli`). 앞의 두 호스트는 동일한 내부 하네스를 공유하므로 훅 이벤트 및 입출력 계약이 완전히 같으며 설치 경로만 상이합니다.

| 항목 | Antigravity 계열 | Gemini CLI |
| --- | --- | --- |
| 훅 설정 방식 | 이벤트명 → 개별 핸들러 매핑 | `hooks` → 이벤트 그룹 매핑 |
| 도구 호출 전후 | `PreToolUse`, `PostToolUse` | `BeforeTool`, `AfterTool` |
| 세션 턴 및 모델 호출 | `PreInvocation`, `PostInvocation`, `Stop` | `BeforeAgent`, `AfterAgent`, `BeforeModel` 등 |
| 세션 및 작업 경로 식별 | `conversationId`, `workspacePaths` | `session_id`, `cwd` |
| 도구 호출 인자 스키마 | `toolCall.name`, `toolCall.args` | `tool_name`, `tool_input` |
| 타임아웃 단위 | 초(seconds) | 밀리초(milliseconds) |
| 턴 종료 차단 및 재개 | `Stop` 이벤트에서 `decision: continue` | `AfterAgent` 이벤트에서 `decision: deny` |
| 무한 재귀 방지 플래그 | 종료 사유, 턴 실행 횟수, 자체 상한 | `stop_hook_active`, 자체 상한 |

Antigravity `PostToolUse`는 성공 시 별도의 오류 문자열을 반환하지 않지만, 이 신호만으로 실제 테스트 프로세스의 성공적 완료를 단정하지 않습니다. 비동기 백그라운드 도구 실행 시작과 프로세스 자체의 정상 종료는 본질적으로 다르기 때문입니다. 모든 완료 증거는 로컬 실행기가 직접 채취한 프로세스 종료 코드를 기반으로 삼습니다.

Antigravity `Stop.fullyIdle` 필드는 백그라운드 비동기 작업의 잔여 여부를 나타냅니다. `PostInvocation` 발생 시점에 대한 설명은 호스트별 공식 문서 간에 미세한 차이가 있으므로, 임의의 가정을 기반으로 종료 루프를 설계하지 않습니다. [공통 훅](https://antigravity.google/docs/hooks), [IDE 훅](https://antigravity.google/docs/ide/hooks), [Gemini CLI 훅](https://geminicli.com/docs/hooks/reference/) 문서를 각각 독립적인 기준으로 유지합니다.

Antigravity의 `PreInvocation`은 모델 추론 직전에 호출되며 `ephemeralMessage`를 통해 휘발성 시스템 메시지를 주입합니다. Gemini CLI의 `BeforeAgent.additionalContext`는 현재 사용자 턴에만 적용됩니다. 이전 메시지가 영구 보존될 것으로 가정하고 상태 전송을 생략하지 않습니다. GTG는 매 턴마다 현재 작업공간의 무결성을 재검증하고, 안내 문구 내 중복 경로 설명만 선별적으로 압축합니다. [메시지 크기 비교와 보호 검사](../validation/2026-09-08-context-budget/README.md).

정상 종료 이유를 공식 가이드의 `model_stop` 단 하나로만 제한하면, [실제 운영 환경](https://atamel.dev/posts/2026/07-16_where_agy_hooks/)에서 발행되는 `NO_TOOL_CALL`을 비정상 중단으로 오인하게 됩니다. 따라서 두 종료 코드를 모두 정상 종료 신호로 수용하되, 사용자 명시적 취소나 예외 오류, 불명확한 사유는 자동 재개하지 않습니다. 초기 Antigravity 2.12.2 시험에서는 자동 재개에 실패했으나, [실호스트 재검증](../validation/2026-09-08-native-stop-recheck/README.md)을 통해 1회 재개, 등록 검사 통과, 최종 정상 완료를 온전히 실증했습니다.

Antigravity 플러그인은 `plugin.json`, 선택적인 `hooks.json`, `skills/`, `rules/`, `mcp_config.json`으로 구성됩니다. 작업공간 기준 `.agents/plugins/`, 전역 기준 `~/.gemini/config/plugins/`에서 로드됩니다. 반면 Gemini CLI는 별도의 `gemini-extension.json` 매니페스트와 확장 훅 규약을 따릅니다. [플러그인 규격](https://antigravity.google/docs/plugins), [확장 규격](https://geminicli.com/docs/extensions/reference/).

Antigravity CLI(`agy`)는 동일한 플러그인 컴포넌트를 `~/.gemini/antigravity-cli/plugins/<plugin_name>/` 디렉터리에 배치하고 `import_manifest.json`으로 등록 상태를 추적합니다. `agents/` 하위의 서브에이전트 정의도 지원합니다. [CLI 플러그인 문서](https://antigravity.google/docs/cli/plugins/).

Gemini CLI는 2026-06-18부로 개인 계정 엔드포인트 지원이 중단되었으며, 확장 생태계는 Antigravity 플러그인으로 점진 통합되고 있습니다. GTG는 `gemini-cli` 패키지를 유지하되 자동 감지 대상에서는 제외하고 명시적 옵션(`--platform gemini-cli`) 지정 시에만 설치합니다. [전환 공지](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/).

실제 Antigravity 2.11.0 환경에서 일반적인 이름의 규칙 파일은 로드되지 않았습니다. 공식 내장 가이드에 따라 `rules/AGENTS.md`로 파일명을 고정했을 때 비로소 설정에서 규칙으로 정상 인식되었습니다. [내장 문서와 실제 발견 기록](native-antigravity.md).

패키징 검증 로직은 단순 파일 개수뿐 아니라 필수 라이프사이클 이벤트 2개, 활성화 상태, 실행 인자 유효성을 정밀 검사합니다. Antigravity의 타임아웃은 정수 초 단위이며, Gemini CLI는 밀리초 숫자 단위이므로 실제 검증에도 각 단위를 엄격히 적용합니다. [실패 재현과 수정](../validation/2026-09-08-package/README.md).

레거시 워크플로는 2026-11-01부로 공식 폐기될 예정입니다. 따라서 모든 작업 진입점은 현대적인 Agent Skills 표준으로 구현합니다. [공식 마이그레이션 가이드](https://antigravity.google/docs/migration/workflows-to-skills/).

## 훅 출력 계약 분석 (2026-09-09 확인)

호스트별로 **세션 종료를 허용하면서 동시에 메시지를 전달하는** 인터페이스 경로가 상이합니다.

| 항목 | Antigravity `Stop` | Gemini CLI `AfterAgent` |
| --- | --- | --- |
| 스키마 정의 출력 필드 | `decision`, `reason` | `decision`, `reason`, `continue`, `hookSpecificOutput.clearContext` (+공통 `systemMessage`, `suppressOutput`, `stopReason`) |
| 세션을 차단하지 않고 사용자에게 출력 | 공식 문서상 미기재 | `systemMessage` (대화형 터미널 UI 전용) |
| 세션을 차단하지 않고 모델에 주입 | 공식 문서상 미기재 | 불가 (`additionalContext`는 `BeforeAgent` 전용) |
| 모델 컨텍스트에 주입하기 위한 수단 | `decision: "continue"` (재개 예산 소모) | `decision: "deny"` + `reason` (재시도 강제) |

Antigravity 규격에서 `reason` 필드는 `decision`이 `"continue"`일 때만 동작이 명시되어 있습니다. 반면 종료를 허용하는 응답(`"approve"`)에 함께 실은 `reason`이 모델이나 사용자에게 실제로 전달되는지는 공식 문서에 명확히 정의되어 있지 않아 **실증되지 않은 미검증 영역**으로 분류합니다. GTG는 규격에 맞춰 해당 값을 채워 응답하되 전달 여부를 임의로 단정하지 않습니다. Gemini CLI의 `systemMessage`는 `decision` 값과 무관하게 출력되는 경로를 소스 코드로 확인하여 활용하고 있습니다.

호스트 런타임 역시 2.6.0부터 종료 훅의 무한 재개를 방어하기 위해 자체 상한을 두고 있습니다. GTG의 자체 재개 상한(기본 2회, 최대 8회)은 플랫폼 제한보다 엄격하게 유지됩니다.

서브에이전트 정의 스키마는 [공식 문서](https://antigravity.google/docs/subagents)에 규정되어 있으며 플러그인의 `agents/` 디렉터리가 탐색 대상에 포함됩니다. 다만 실제 호스트 환경에서의 안정적인 동작이 완벽히 실증되기 전까지는 임의 생성을 보류하는 원칙을 유지합니다.

`plugin.json` 규격과 관련하여 벤더 공식 문서 간에 `name` 필드의 필수 여부 및 스킬 디렉터리 배치(단일 `.md` vs 디렉터리+`SKILL.md`)에 차이가 존재합니다. GTG는 더 엄격한 CLI 스키마 표준을 채택하여 `name`을 명시하고 디렉터리+`SKILL.md` 구조로 배치함으로써 모든 호스트 환경에서 완벽히 호환되도록 구성했습니다.


```
