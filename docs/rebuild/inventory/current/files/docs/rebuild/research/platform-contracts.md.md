# `docs/rebuild/research/platform-contracts.md`

- 형식: `100644`
- 바이트: 5535
- SHA-256: `f38f0141965882b8e2b8be0e5cc74684d12aca9b8755c70e57015097bd2e63cb`
- 인코딩: `utf-8`

```
# 플랫폼 계약 조사

확인일: 2026-09-08. 공식 원문을 열어 확인했습니다. 문서 확인과 실환경 테스트는 별도입니다.

| 항목 | Antigravity | Gemini CLI |
| --- | --- | --- |
| 훅 설정 | 이름 → 이벤트별 핸들러 | `hooks` → 이벤트별 그룹 |
| 호출 전후 | `PreToolUse`, `PostToolUse` | `BeforeTool`, `AfterTool` |
| 턴·모델 | `PreInvocation`, `PostInvocation`, `Stop` | `BeforeAgent`, `AfterAgent`, `BeforeModel` 등 |
| 식별·작업 경로 | `conversationId`, `workspacePaths` | `session_id`, `cwd` |
| 도구 호출 | `toolCall.name`, `toolCall.args` | `tool_name`, `tool_input` |
| 시간 제한 단위 | 초 | 밀리초 |
| 종료 재개 | `Stop`의 `decision: continue` | `AfterAgent`의 `decision: deny` |
| 재귀 방지 참고 | 종료 이유·실행 회차·자체 상한 | `stop_hook_active`·자체 상한 |

Antigravity `PostToolUse`는 성공 시 오류 문자열이 없지만 이것만으로 테스트 프로세스의 완료·성공을 추론하지 않습니다. 비동기 `run_command`의 도구 시작 성공과 프로세스 종료 성공은 다릅니다. 완료 증거는 로컬 실행기가 직접 얻은 결과를 사용합니다.

Antigravity `Stop.fullyIdle`은 백그라운드 작업 종료 여부입니다. `PostInvocation` 시점 설명은 제품별 공식 문서가 다르므로 동작을 가정해 종료 루프를 만들지 않습니다. [공통 훅](https://antigravity.google/docs/hooks), [IDE 훅](https://antigravity.google/docs/ide/hooks), [Gemini CLI 훅](https://geminicli.com/docs/hooks/reference/)을 각각 기준으로 둡니다.

정상 종료 이유를 공식 예시의 `model_stop` 하나로 제한하면 [직접 실행 기록](https://atamel.dev/posts/2026/07-16_where_agy_hooks/)의 `NO_TOOL_CALL`을 중단으로 오인합니다. 두 코드를 재생해 처리하되 오류·취소·알 수 없는 이유는 재개하지 않습니다. 자체 Antigravity 2.12.2 시험은 자동 재개에 실패했고 원문 Stop 입력을 보존하지 못했으므로, 해당 시험의 정확한 코드가 같았다고 확정하지 않습니다. [실제 결과와 보완 범위](../validation/2026-09-08-native-stop/README.md).

보완 후 같은 입력의 [실호스트 재검증](../validation/2026-09-08-native-stop-recheck/README.md)에서는 재개 1회·등록 검사 통과·최종 종료를 확인했습니다. 마지막 실제 종료 메타데이터에 `NO_TOOL_CALL`, 실행 번호 1, `fully_idle: true`, 오류 없음이 기록됐습니다. 짧은 연결 시험의 결과로 범위를 제한합니다.

Antigravity 플러그인은 `plugin.json`, 선택적인 `hooks.json`, `skills/`, `rules/`, `mcp_config.json`을 담습니다. 작업공간은 `.agents/plugins/`, 전역은 `~/.gemini/config/plugins/`에서 탐색합니다. Gemini CLI는 별도의 `gemini-extension.json`과 확장 훅 규약을 사용합니다. [플러그인](https://antigravity.google/docs/plugins), [확장](https://geminicli.com/docs/extensions/reference/).

실제 Antigravity 2.11.0에서 일반 이름의 규칙 파일은 로딩되지 않았습니다. 내장 공식 안내에 맞춰 `rules/AGENTS.md`로 생성한 뒤 실제 설정에서 규칙 추가를 확인했습니다. [내장 문서와 실제 발견 기록](native-antigravity.md).

Antigravity IDE 2.5.5에서도 별도 임시 작업공간에 설치한 `rules/AGENTS.md`와 세 스킬을 UI에서 확인했습니다. 모델 요청 없이 발견만 확인했으며, IDE의 실제 훅 발행·자동 선택은 미검증입니다. [관찰과 한계](../validation/2026-09-08-ide/README.md), [IDE 플러그인 문서](https://antigravity.google/docs/ide/plugins).

패키지 검증은 개수뿐 아니라 두 필수 이벤트·활성 여부·실행 인자를 검사합니다. Antigravity의 timeout은 정수 초, Gemini CLI는 밀리초 숫자이며 실제 검사에도 해당 단위를 적용합니다. 검사 자체의 최대 대기는 5초입니다. [실패 재현과 수정](../validation/2026-09-08-package/README.md).

Gemini CLI는 확장과 훅 JSON의 `${extensionPath}` 치환을 문서화합니다. 현재 GTG는 설치 위치별로 인용 처리한 절대 명령을 생성하며, 임의 폴더 이동 호환성은 별도 검증 대상입니다. 공식적으로 확인하지 못한 환경 변수를 가정해 사용하지 않습니다. [확장 변수](https://geminicli.com/docs/extensions/reference/), [공식 확장 작성 예제](https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/writing-extensions.md).

워크플로는 2026-11-01 폐기 예정으로 안내됩니다. 새 작업 진입은 스킬로 구현합니다. [공식 마이그레이션](https://antigravity.google/docs/migration/workflows-to-skills/).

Gemini 3.8 Flash의 공식 모델 ID는 `gemini-3.8-flash`이며 `low`, `medium`, `high` 사고 수준이 문서화되어 있습니다. `minimal`은 지원하지 않는다고 명시되어 있습니다. 설정 지원과 실제 세션에서 선택된 모델은 구분합니다. [모델 문서](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash).

API를 직접 다루게 될 경우 Interactions와 Generate Content의 생각 서명·함수 호출 표현을 혼합하지 않습니다. 호스트 하네스를 확장하는 단계에서 자체 API 호출 경로를 불필요하게 추가하지 않습니다. [Interactions](https://ai.google.dev/gemini-api/docs/interactions-overview), [사고 설정](https://ai.google.dev/gemini-api/docs/thinking).
```
