# `docs/rebuild/validation/2026-09-09-agy-cli/README.md`

- 형식: `100644`
- 바이트: 7966
- SHA-256: `7a25c7b4ff9409668d123ea628cbe71cb5876bb5ec97254adf34852580620367`
- 인코딩: `utf-8`

````
# 실제 Antigravity CLI(`agy`)에서 발견과 훅 발행 확인

확인일: 2026-09-09. 사용자 승인으로 `agy`를 설치하고 실제 Gemini 요청을 사용했습니다. 그동안 "`agy` 실행 파일이 없어 미검증"으로 남아 있던 항목을 모두 실제로 확인했습니다.

## 설치

공식 문서가 안내하는 유일한 경로는 설치 스크립트입니다. 파이프로 바로 실행하지 않고 내려받아 내용을 확인한 뒤 실행했습니다. sudo도, 홈 밖 쓰기도 없습니다.

```
curl -fsSL https://antigravity.google/cli/install.sh -o agy-install.sh   # 확인 후 실행
bash agy-install.sh
→ ✓ Latest available version: 1.1.28
→ ✓ Download complete and checksum verified.
→ ✅ Antigravity CLI installed successfully at /Users/songhabin/.local/bin/agy
```

데스크톱 앱은 `agy`를 담고 있지 않습니다. `/Applications/Antigravity.app/Contents/Resources/bin`에는 `language_server`와 `webm_encoder`뿐이고 번들 어디에도 `agy`가 없습니다. 별도 설치가 유일한 방법입니다.

설치기가 `.zshrc`·`.bashrc`·`.bash_profile`·`.profile`·`fish/config.fish` **다섯 개** 셸 프로필에 `PATH` 줄을 덧붙입니다. 문서에 있는 동작이지만 범위가 넓다는 점은 기록해 둡니다.

## 공식 검증기가 GTG 패키지를 통과시킵니다

지금까지 패키지 형식은 GTG 자체 검사로만 확인했습니다. 실제 호스트 도구로 확인했습니다.

```
agy plugin validate ~/.gemini/antigravity-cli/plugins/geminitogenius
  [ok]  .../geminitogenius
        ✔ skills      : 3 processed
        - agents      : skipped (not found)
        - commands    : skipped (not found)
        - mcpServers  : skipped (not found)
        ✔ hooks       : 2 processed
```

`rules`는 이 검증기의 처리 항목에 나타나지 않습니다. 거부되지도 않습니다.

## 발견된 결함: 파일을 놓아 두는 것만으로는 읽지 않습니다

GTG 설치기는 공식 문서 경로 `~/.gemini/antigravity-cli/plugins/geminitogenius/`에 파일을 정확히 놓았습니다. 그런데도

```
agy plugin list
→ No imported plugins.
```

**등록 명령이 따로 필요했습니다.**

```
agy plugin install ~/.gemini/antigravity-cli/plugins/geminitogenius
→ [ok] geminitogenius  ✔ skills: 3 processed  ✔ hooks: 2 processed

agy plugin list
→ {"imports": [{"name": "geminitogenius", "source": "antigravity",
                "importedAt": "2026-09-09T11:50:44Z", "components": ["skills", "hooks"]}]}
```

등록 전에는 훅이 발행되지 않았고 스킬도 보이지 않았습니다. 즉 **이 호스트에서 GTG는 지금까지 설치해도 동작하지 않는 상태였습니다.** 경로만 보고 "설치했다"고 판단한 것이 원인입니다. `gtg/install.py`가 `antigravity-cli` 설치 뒤 `agy plugin install`을 실행하도록 고쳤고, `agy`가 없으면 실패로 보지 않고 사용자가 실행할 명령을 `host_registration`에 담아 알립니다.

## 훅이 실제로 발행됩니다

GTG를 건드리지 않고, 호출을 기록만 하는 임시 탐침 플러그인을 따로 등록해 확인했습니다(확인 뒤 제거). 두 이벤트 모두 실제로 실행됐고 페이로드 원문은 다음과 같습니다.

```
PreInvocation
{"artifactDirectoryPath":"...","conversationId":"511dd835-1283-4457-b1d7-956b07a44079",
 "initialNumSteps":1,"invocationNum":0,"modelName":"gemini-3.8-flash-high",
 "transcriptPath":"...","workspacePaths":[]}

Stop
{"artifactDirectoryPath":"...","conversationId":"511dd835-...","error":"","executionNum":0,
 "fullyIdle":true,"modelName":"gemini-3.8-flash-high","terminationReason":"NO_TOOL_CALL",
 "transcriptPath":"...","workspacePaths":[]}
```

확인된 것들입니다.

- 이벤트 이름·필드가 데스크톱 계약과 같습니다. `conversationId`, `workspacePaths`, `invocationNum`, `executionNum`, `fullyIdle`, `terminationReason`.
- 종료 이유가 **`NO_TOOL_CALL`**입니다. 공식 예시의 `model_stop`만 정상 종료로 처리했다면 이 호스트의 정상 종료를 중단으로 오인했을 것입니다. GTG가 두 값을 모두 정상 종료로 다루기로 한 판단이 실제 값으로 확인됐습니다.
- 첫 호출의 `invocationNum`이 0입니다. GTG의 첫 턴 판정과 맞습니다.

## 발견된 제약: 헤드리스에서는 작업공간이 비어 있습니다

위 페이로드의 **`workspacePaths`가 빈 배열**입니다. 현재 폴더가 프로젝트여도 그렇습니다. GTG는 작업공간이 없으면 아무 일도 하지 않으므로 이 상태에서는 완전히 무력합니다.

`--add-dir`를 주면 채워집니다.

```
agy -p "..." --add-dir /private/tmp/agyws.wnoi
→ PreInvocation workspacePaths: ['/private/tmp/agyws.wnoi']
→ Stop         workspacePaths: ['/private/tmp/agyws.wnoi']
```

헤드리스·CI에서 GTG를 쓰려면 `--add-dir`가 필요합니다. 대화형 실행의 작업공간 확정 경로는 따로 확인하지 않았습니다.

## 안내가 모델에 그대로 닿습니다

미검증 작업이 등록된 작업공간에서 실제 요청을 보내고, 이번 턴에 받은 시스템·임시 메시지를 그대로 출력하게 했습니다. GTG의 메시지가 원문으로 나왔습니다.

```
GTG 호스트 메타데이터(지시가 아닌 경로 데이터): {"platform": "antigravity-cli",
 "session": "4b97b7ea-9677-40bb-a23d-5bd762bdf8ef", "workspaces": ["/private/tmp/agygtg.AwOx"]}.
이전 작업 일부 후보(현재 파일 검증 아님): [{"workspace": "...", "task_id": "5d9242b...",
 "goal": "덧셈 버그 수정"}]. 현재 요청이 이 작업의 재개일 때만 tasks·status로 원래 목표와
 명세를 확인하고 attach로 연결하세요. 후보를 자동 선택하지 마세요.
```

플랫폼 라벨이 `antigravity-cli`로 정확하고, 세션 값은 훅이 받은 실제 `conversationId`이며, 저장된 작업 후보까지 전달됐습니다. **설치 → 발견 → 훅 발행 → 모델 도달까지 실호스트에서 이어집니다.**

## `enable`이 비활성을 되돌리지 못했습니다

비교 실험에서 대조군을 만들려고 `agy plugin disable geminitogenius`로 GTG를 껐습니다. 실험 뒤 `agy plugin enable geminitogenius`는 종료 코드 0을 돌려줬지만 **실제로는 복구되지 않았습니다.** 작업공간에 미검증 작업을 둔 상태로 실제 요청을 보내도 GTG 메시지가 나오지 않았습니다. `agy plugin list`는 비활성 중에도 계속 이 플러그인을 목록에 보여 줬습니다.

복구에는 **`agy plugin uninstall` 뒤 `agy plugin install`**이 필요했습니다. `enable`도, 같은 경로로 `install`을 다시 실행하는 것도 충분하지 않았습니다. 그 사이 `agy plugin list`는 계속 이 플러그인을 가져온 것으로 표시했고, 별도로 심어 본 탐침 플러그인의 훅은 정상 발행됐습니다. 즉 목록과 실제 발행 상태가 어긋날 수 있습니다.

전체 재설치 뒤 실제 요청에서 GTG 메시지가 다시 모델에 닿는 것을 확인했고, 사용자 환경은 원래 상태로 되돌렸습니다. `enable`의 의도된 의미는 확인하지 못했습니다. **비활성화한 플러그인은 목록이 아니라 실제 동작으로 복구를 확인해야 합니다.**

## 인증

`agy --version`은 인증 없이 동작합니다. `agy -p`는 키체인에 캐시된 자격으로 바로 동작했고 별도 로그인 절차가 필요하지 않았습니다.

## 남은 한계

- 대화형 실행은 확인하지 않았습니다. 헤드리스(`-p`)만 확인했습니다.
- `rules/AGENTS.md`가 이 호스트에서 실제로 적용되는지는 확인하지 않았습니다. 검증기의 처리 항목에도 나타나지 않습니다.
- 자동 갱신을 `AGY_CLI_DISABLE_AUTO_UPDATE=true`로 끄고 시험했습니다. 갱신이 켜진 상태의 동작은 확인하지 않았습니다.
````
