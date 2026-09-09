# `docs/product/hosts.md`

- 형식: `100644`
- 바이트: 2487
- SHA-256: `da4a1ac71ee0af354ef7d3c2c0a75527d5eec9f2621cda4cab657bbcd4923568`
- 인코딩: `utf-8`

```
# 지원 호스트

세 호스트를 지원합니다. 훅 이벤트 이름과 식별 필드가 달라서, 그 차이는 [`gtg/platforms.py`](../../gtg/platforms.py) 한 곳에만 적혀 있습니다.

| 호스트 | 설치 경로 | 훅 이벤트 |
|---|---|---|
| `antigravity` (데스크톱·IDE) | `~/.gemini/config/plugins/geminitogenius/` | `PreInvocation`, `Stop` |
| `antigravity-cli` (`agy`) | `~/.gemini/antigravity-cli/plugins/geminitogenius/` | `PreInvocation`, `Stop` |
| `gemini-cli` | `~/.gemini/extensions/geminitogenius/` | `BeforeAgent`, `AfterAgent` |

작업공간 설치는 `antigravity`만 지원합니다. 나머지 둘은 전역 경로만 확인했습니다.

## Antigravity CLI (`agy`)

**파일을 경로에 놓는 것만으로는 읽히지 않습니다.** `agy plugin install`로 가져오기 목록에 올려야 스킬과 훅이 동작합니다. 설치기가 이 단계까지 실행하며, `agy`를 못 찾으면 실패로 보지 않고 사용자가 실행할 명령을 결과의 `host_registration`에 담아 알립니다.

헤드리스(`agy -p`)로 쓸 때는 `--add-dir`로 작업공간을 지정해야 합니다. 지정하지 않으면 훅이 받는 `workspacePaths`가 빈 배열이라 GTG가 아무 일도 하지 않습니다.

플러그인을 `agy plugin disable`로 껐다가 되돌릴 때는 주의해야 합니다. `enable`이나 같은 경로로 `install`을 다시 실행하는 것으로는 복구되지 않았고, `uninstall` 뒤 `install`이 필요했습니다. 그 사이 `agy plugin list`는 계속 정상으로 표시합니다. 목록이 아니라 실제 동작으로 확인하세요.

## Gemini CLI

2026-06-18에 개인 계정 요청 처리가 끝났고 확장은 Antigravity 플러그인으로 옮겨 갑니다. GTG는 이 패키지를 남겨 두되 자동 감지 대상에서 빼고, `--platform gemini-cli`로 직접 지정할 때만 설치합니다.

이 호스트에서는 훅이 종료를 막지 않으면서 사실을 전달하는 방법이 `systemMessage` 하나입니다. 대화형 터미널에만 보이고 모델 컨텍스트에는 들어가지 않습니다.

## 규칙 파일

일반적인 이름의 규칙 파일은 Antigravity에서 로딩되지 않았습니다. 내장 안내에 맞춰 `rules/AGENTS.md`로 만든 뒤에야 실제 설정에서 규칙으로 잡혔습니다. 규칙 파일은 호스트 한도인 12,000자를 넘을 수 없고, 패키지 검증이 이 한도와 보이지 않는 문자를 함께 확인합니다.
```
