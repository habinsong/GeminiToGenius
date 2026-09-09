# GeminiToGenius

작업이 끝났다고 말하기 전에, 정해 둔 검사를 실제로 실행하고 그 기록을 남기는 로컬 플러그인입니다.

한국어 · [English](docs/README.en.md)

[릴리즈](https://github.com/habinsong/GeminiToGenius/releases) · [설치 안내](docs/product/getting-started.md) · [검증 기록과 한계](docs/verification/README.md) · [변경 기록](CHANGELOG.md)

GTG 3.0.0은 Antigravity 데스크톱·IDE, Antigravity CLI(`agy`), Gemini CLI에 설치합니다.

## 먼저 확인할 것

GTG가 모델의 코딩 실력을 올려 주는 것은 아닙니다. 같은 사례와 채점기로 64회 비교했을 때, 같은 모델에서 GTG를 켠 쪽과 끈 쪽은 모두 14/14를 통과했습니다. 짧은 작업에서 산출물 이점은 확인되지 않았습니다.

이 도구는 여러 단계로 이어지는 작업에서 검사한 내용과 완료 근거를 남길 때 씁니다. 모든 요청에 작업을 붙이지 않으며, 짧은 수정에는 개입하지 않는 편이 맞습니다.

## 하는 일

- 작업을 등록할 때 완료 조건과 검증 명령을 먼저 정합니다. 등록 뒤에는 통과하기 쉬운 명령으로 바꿀 수 없습니다.
- `verify`는 등록된 명령을 실행하고 종료 코드, 걸린 시간, 검사한 파일을 기록합니다. 그 파일이 바뀌면 이전 성공은 더 이상 현재 상태의 근거가 아닙니다.
- `certify`는 완료 주장과 실행 기록을 한 파일에 묶습니다. `replay`는 상태 DB 없이 그 파일과 현재 작업공간으로 다시 확인합니다.
- 검사가 실행하지 못한 파일과 판단할 수 없었던 범위도 결과에 남깁니다. 빈 목록을 전부 확인했다는 뜻으로 바꾸지 않습니다.
- 세션이 끊겨도 작업, 검사 결과, 메모는 남습니다. 새 세션에서는 `tasks`로 찾고 `attach`로 이어갑니다.

## 설치

macOS 또는 Linux, Python 3.10 이상, Git이 필요합니다. 외부 Python 패키지는 설치하지 않습니다.

```bash
git clone https://github.com/habinsong/GeminiToGenius.git
cd GeminiToGenius
bash scripts/install.sh
```

설치기는 홈 폴더에서 찾은 호스트에 넣고, 설치 전에 패키지를 별도 폴더에서 검사합니다. 감지된 호스트가 없으면 Antigravity 전역 플러그인 하나를 설치합니다. 설치 뒤에는 해당 호스트를 다시 시작하세요.

| 호스트 | 설치 방식 |
| --- | --- |
| Antigravity 데스크톱·IDE | 자동 감지 또는 프로젝트별 설치 |
| Antigravity CLI (`agy`) | 자동 감지 후 `agy plugin install`까지 실행 |
| Gemini CLI | `--platform gemini-cli`를 지정해 직접 설치 |

프로젝트 하나에만 넣으려면 다음처럼 실행합니다.

```bash
bash scripts/install.sh --workspace /absolute/path/to/project
```

설치 상태 확인과 제거는 아래 명령을 씁니다.

```bash
python3 scripts/install.py doctor
python3 scripts/install.py uninstall
```

## 쓰는 법

설치 뒤에는 평소처럼 요청하면 됩니다. 슬래시 명령이나 명세 파일을 사용자가 만들 필요는 없습니다.

```
로그인하면 500이 납니다. 원인 찾아서 고쳐 주세요.
```

여러 단계가 필요한 작업으로 판단되면 모델이 완료 조건을 등록하고 검사를 실행합니다. 등록하지 않은 짧은 작업에는 GTG가 억지로 증명서를 붙이지 않습니다.

## 확인한 것

| 항목 | 확인한 결과 |
| --- | --- |
| Antigravity 2.12.2 | 다단계 요청에서 작업 등록, 검사 실행, `certify`, `replay`를 확인했습니다. |
| Antigravity CLI 1.1.28 | 공식 패키지 검증을 통과했고 두 훅이 발행됐습니다. |
| 완료 증명서 | 검사 대상 파일 한 줄을 바꾸면 재확인이 깨지고, 되돌리면 다시 통과했습니다. |
| 같은 모델 비교 | GTG 사용·미사용 모두 14/14였습니다. 이 결과는 제품 우열이나 짧은 작업의 품질 향상을 뜻하지 않습니다. |

숫자, 실행 환경, 빠진 항목은 [검증 기록](docs/verification/README.md)에 그대로 적어 두었습니다.

## 아직 확인하지 못한 것

- Windows 설치와 네트워크 파일 시스템에서의 실행 잠금
- 실제 전원 차단 뒤 복구, 여러 날에 걸친 장기 작업, 다른 모델의 반복 시험
- Go·Rust와 컴파일해서 실행하는 TypeScript의 실행 범위 관찰
- 토큰 사용량과 비용

## 문서

| 문서 | 내용 |
| --- | --- |
| [설치와 첫 사용](docs/product/getting-started.md) | 설치, 호스트 선택, 제거 |
| [동작 방식](docs/product/how-it-works.md) | 작업 등록부터 검사와 재확인까지의 흐름 |
| [명령 목록](docs/reference/cli.md) | 에이전트가 쓰는 명령과 종료 코드 |
| [완료 증명서](docs/reference/certificate.md) | 증명서와 `replay` 판정 |
| [검증 기록과 한계](docs/verification/README.md) | 실호스트 확인, 비교, 미확인 범위 |
| [전체 문서](docs/README.md) | 제품·참조·구조 문서 목록 |

## 개발

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
python3 scripts/catalog.py --check
```

현재 작업과 남은 과제는 [개발 기록](docs/development/current-work.md)에, 파일별 원문과 해시는 [현재 목록](docs/development/inventory/current/README.md)에 있습니다.

## 라이선스

MIT 라이선스입니다. [LICENSE](LICENSE)를 보세요. Google, Antigravity, Gemini와 제휴하거나 후원받는 관계가 아니며, 제품 이름은 호환 대상을 가리키는 데만 씁니다.
