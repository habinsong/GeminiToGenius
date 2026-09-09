# GeminiToGenius

Gemini가 스스로 검증하고 끝냈다고 말하게 만드는 로컬 하네스입니다.

한국어 · [English](docs/README.en.md)

[문서](docs/README.md) · [확인한 것과 확인하지 못한 것](docs/verification/README.md) · [변경 기록](CHANGELOG.md)

GTG는 Antigravity와 Gemini CLI에 설치하는 플러그인입니다. 사용자가 요청을 보내면, 여러 턴에 걸칠 만한 작업에 대해 모델이 완료 조건을 먼저 고정하고, 그 조건을 실제 명령으로 실행해 통과시킨 뒤에야 끝났다고 보고합니다. 끝났다는 말에는 실행한 명령과 종료 코드와 파일 지문을 묶은 증명서가 따라옵니다. 받는 쪽은 그 파일 하나로 다시 확인할 수 있습니다.

슬래시 명령도, 명세 입력도 없습니다. 평소처럼 요청하면 됩니다.

## 왜 만들었나

에이전트가 "다 고쳤습니다"라고 말하는 것과 실제로 고쳐진 것은 다릅니다. 테스트를 한 번도 돌리지 않고 완료를 보고하는 일이 흔하고, 돌렸다고 말해도 그게 사실인지 확인할 방법이 사용자에게 없습니다.

GTG 2.x는 이 문제를 프롬프트로 다뤘습니다. 목표와 검증 결과를 다루는 실행 파일이 없었고, 구조 검사는 비어 있는 훅 설정도 정상으로 봤습니다. 3.0.0은 그 부분을 전부 걷어내고 Python 실행 코어로 다시 만들었습니다.

핵심은 하나입니다. **완료 조건을 미리 고정하고, 그 조건을 실제로 실행하고, 실행한 사실을 재현 가능한 형태로 남깁니다.** 나중에 통과하기 쉬운 쪽으로 조건을 옮길 수 없고, 실행하지 않은 검사를 통과로 만들 방법이 없습니다.

## 무엇을 하나

| | |
|---|---|
| 완료 조건 고정 | 등록한 뒤에는 검증 명령을 바꿀 수 없습니다. `echo`나 `true` 같은 명령은 애초에 등록되지 않습니다. |
| 실제 실행 | 등록한 명령을 그대로 돌리고 종료 코드·시간·파일 해시를 남깁니다. 대상 파일이 바뀌면 이전 성공은 무효가 됩니다. |
| 완료 증명서 | 주장과 근거를 한 파일로 묶습니다. 상태 DB 없이 `replay` 하나로 재현합니다. 판정은 `pass`·`invalid`·`inconclusive` 셋이고 미확정을 통과로 바꾸지 않습니다. |
| 미검증 범위 공개 | 통과한 검사가 한 번도 실행하지 않은 파일을 그대로 보고합니다. 관찰할 수 없는 언어가 섞이면 미실행을 주장하지 않고 무엇이 판단을 막았는지 밝힙니다. |
| 세션을 넘는 작업 | 세션이 끊겨도 목표·검사 결과·메모가 남습니다. 새 세션에서 같은 작업에 이어 붙입니다. |
| 중단 복구 | 실행 중인지 여부를 PID가 아니라 파일 잠금으로 판단합니다. 재부팅이나 강제 종료 뒤에도 작업이 교착되지 않습니다. |

훅 안에서 모델을 부르거나 테스트를 자동으로 돌리지 않습니다. 자동 재개는 사용자 쿼터를 쓰므로 기본 2회입니다.

## 설치

macOS 또는 Linux, Python 3.10 이상, Git이 필요합니다. 외부 Python 패키지는 쓰지 않습니다.

```bash
git clone https://github.com/habinsong/GeminiToGenius.git
bash GeminiToGenius/scripts/install.sh
```

홈 폴더에서 호스트가 만든 설정 파일을 찾아 감지한 호스트마다 설치합니다. 설치 후 호스트를 다시 시작하면 됩니다.

| 호스트 | 설치 경로 |
|---|---|
| Antigravity 데스크톱·IDE | `~/.gemini/config/plugins/geminitogenius/` |
| Antigravity CLI (`agy`) | `~/.gemini/antigravity-cli/plugins/geminitogenius/` |
| Gemini CLI | `~/.gemini/extensions/geminitogenius/` |

Antigravity CLI는 파일을 경로에 놓는 것만으로 읽지 않습니다. 설치기가 `agy plugin install`까지 실행합니다. `agy`를 못 찾으면 설치를 실패로 보지 않고 실행할 명령을 알려 줍니다.

Gemini CLI는 2026-06-18에 개인 계정 요청 처리가 끝나 자동 감지 대상이 아닙니다. `--platform gemini-cli`로 직접 지정할 때만 설치합니다.

자세한 것은 [설치와 첫 사용](docs/product/getting-started.md)에 있습니다.

## 확인한 것

실제 호스트에서 돌린 결과만 적습니다.

Antigravity 2.12.2에서 모델이 스스로 작업을 등록하고 검증하고 증명서를 만든 뒤 재실행까지 했습니다. 검증 대상 파일을 한 줄 바꾸자 재현이 깨졌고, 되돌리니 다시 재현됐습니다. Antigravity CLI 1.1.28에서는 공식 검증기가 패키지를 통과시켰고 훅 두 개가 실제로 발행됐습니다.

같은 사례·같은 요청·같은 채점기로 네 하네스를 64회 돌렸습니다.

| 팔 | 자동 채점 | 통과 | 매번 통과 |
|---|---|---|---|
| `agy` + GTG (Gemini 3.8 Flash High) | 14 | 14 | 7/7 |
| `agy` GTG 없음 (같은 모델) | 14 | 14 | 7/7 |
| Claude Code (Sonnet 5) | 14 | 12 | 6/7 |
| Codex CLI (gpt-5.6-terra) | 14 | 13 | 6/7 |

**같은 모델에서 GTG를 켜고 끈 결과가 같습니다. 짧은 작업에서 GTG의 산출물 이점은 확인되지 않았습니다.** 모델이 16회 중 5회만 작업을 등록했기 때문이고, 등록하지 않는 편이 그 작업들에서는 맞는 판단이었습니다. 파일 두세 개 고치는 요청에 완료 조건과 증명서를 붙이면 비용만 늘어납니다.

등록한 5회는 모두 검사를 실행하고 증명서를 남겼습니다. 이전 세션의 진행 상태를 이어받는 사례에서는 매번 등록했고, 작업 두 개를 연결하고 메모까지 남겼습니다. GTG가 값을 하는 지점은 한 턴에 끝나지 않는 작업입니다.

Claude Code와 Codex는 모델이 다르므로 이 표로 제품 우열을 말할 수 없습니다. 측정하지 않은 것은 [확인하지 못한 것](docs/verification/README.md#아직-확인하지-못한-것)에 적어 두었습니다.

## 문서

| 문서 | 언제 보나 |
|---|---|
| [설치와 첫 사용](docs/product/getting-started.md) | 설치하고 바로 써 볼 때 |
| [동작 방식](docs/product/how-it-works.md) | 요청 하나가 등록·검증·증명서로 이어지는 흐름을 볼 때 |
| [명령 목록](docs/reference/cli.md) | `run.py`가 받는 명령과 종료 코드 |
| [완료 증명서](docs/reference/certificate.md) | 증명서 형식과 `replay` 판정 |
| [구조](docs/architecture/overview.md) | 훅과 실행 코어의 경계 |
| [전체 문서](docs/README.md) | 위에 없는 것 |

## 개발

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
python3 scripts/catalog.py --check
```

검사 317개입니다. 조사 근거는 [출처 원장](docs/development/research/sources.json) 94건에 있고, 구현된 파일의 전체 원문은 [현재 원본 전체](docs/development/inventory/current/README.md)에 있습니다. 작업 규칙은 [CONTRIBUTING.md](CONTRIBUTING.md)에 있습니다.

## 라이선스

MIT. [LICENSE](LICENSE)를 보세요. Google, Antigravity, Gemini와 제휴하거나 후원받는 관계가 아닙니다. 제품 이름은 무엇과 함께 동작하는지 가리키는 데만 씁니다.
