# 지원 호스트

세 가지 호스트를 지원하며 호스트마다 훅 이벤트 명칭과 식별 필드가 다르므로 세부 차이는 [`gtg/platforms.py`](../../gtg/platforms.py) 한 곳에서 관리합니다.

| 호스트 | 설치 경로 | 훅 이벤트 |
|---|---|---|
| `antigravity` (데스크톱과 IDE) | `~/.gemini/config/plugins/geminitogenius/` | `PreInvocation`, `Stop` |
| `antigravity-cli` (`agy`) | `~/.gemini/antigravity-cli/plugins/geminitogenius/` | `PreInvocation`, `Stop` |
| `gemini-cli` | `~/.gemini/extensions/geminitogenius/` | `BeforeAgent`, `AfterAgent` |

작업공간(프로젝트별) 설치는 `antigravity`만 지원하며 나머지 둘은 전역 경로 설치 동작을 확인했습니다.

## Antigravity CLI (`agy`)

플러그인은 `agy plugin install`로 등록해야 인식되고 스킬과 훅이 동작합니다. 디렉터리에 파일을 넣는 것만으로는 부족하므로 설치 스크립트가 이 등록을 대신 실행하고 `agy`를 찾지 못하면 직접 실행할 명령을 결과의 `host_registration`에 알려 줍니다.

별도 `--home` 경로로 설치하면 실제 사용자 호스트 등록은 변경하지 않고 직접 실행할 명령만 알려 줍니다. 실제 홈에서 등록이 실패하면 설치 결과가 `ok: false`가 되며 검증을 마친 파일과 복구 경로는 보존됩니다. `doctor`의 검사 대상은 파일과 훅, 호스트, 버전입니다.

`agy 1.1.28`은 CLI 패키지를 데스크톱 공용 경로에도 복사하므로 설치기는 기존 공용 패키지를 먼저 보존하고 복사 후 해당 경로를 데스크톱용으로 다시 구성합니다.

헤드리스 모드(`agy -p`)에서는 `--add-dir`로 작업공간을 지정하십시오. 생략하면 훅이 전달받는 `workspacePaths`가 빈 배열이 되어 GTG가 검증하지 않습니다.

명령 실행 권한도 호스트에서 미리 허용해 두십시오. 허용되지 않은 명령이 거부되더라도 CLI가 종료 코드 0을 반환할 수 있으므로 실제 파일 변경 내역과 실행 결과를 직접 대조하십시오. GTG 설치기는 호스트 권한을 그대로 따릅니다.

## Gemini CLI

Gemini CLI 호환 패키지는 `--platform gemini-cli`로 명시할 때 설치합니다. 자동 감지에서 제외된 것은 기본 설치 정책 때문일 뿐 서비스 지원이 끝났다는 뜻이 아닙니다.

`BeforeAgent`의 `additionalContext`로 해당 턴의 맥락을 전달하고, `AfterAgent`의 `decision: "deny"`와 `reason`으로 제한된 재시도를 요청합니다. 예산이 소진되거나 사용자가 중단하면 세션을 끝냅니다.

## 웹 조사 도구

규칙에 따라 외부 문서나 사실을 확인하려면 호스트가 웹 도구를 지원하는 것이 조건입니다. Antigravity SDK 소스는 도구 이름을 `search_web`과 `read_url_content`로 정의하며, Gemini CLI 문서는 `google_web_search`와 `web_fetch`로 안내합니다. 검색 도구의 요약문 대신 원문 페이지를 직접 열어 근거로 삼으십시오.

## 규칙 파일

GTG는 Antigravity 규칙을 `rules/AGENTS.md`에 배치하며, 공식 한도는 파일별 24,000바이트와 활성 규칙 합계 20,000토큰입니다. GTG는 이 24,000바이트 한도와 함께 기존 패키지 호환 정책인 12,000자도 검사합니다.
