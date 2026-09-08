# `README.md`

- 형식: `100644`
- 바이트: 7164
- SHA-256: `942bdfedd6b2c6cab35968c279ef6598d9bb5aaa0aba274654c52484499a376d`
- 인코딩: `utf-8`

````
# GeminiToGenius

Gemini가 자연어 요청을 조사·구현·검증으로 이어가도록 돕는 로컬 하네스입니다. `/GTG` 같은 명령 없이 현재 파일과 오류 맥락을 확인해 작업하도록 구성합니다.

현재 버전은 **3.0.0-alpha.1**입니다. 기존 프롬프트 프로필을 Python 실행 코어·호스트별 훅·작업별 스킬로 재개발하고 있습니다. 로컬 실행과 Antigravity의 발견·초기 훅·자동 스킬 선택을 확인했으며, Gemini 3.8 Flash High로 선택된 단일 오류 수정 사례가 독립 검사를 통과했습니다. 다른 모델과 다양한 작업, 경쟁 도구 대비 품질은 아직 검증하지 않았습니다.

Antigravity 2.12.2의 종료 후 자동 재개 실패를 보완한 뒤, 같은 입력의 실호스트 재검증에서 재개 1회와 등록 검사 6개 통과를 확인했습니다. 짧은 연결 시험이며 장기 작업이나 모델 전체 품질을 보장하지 않습니다. [재검증 결과와 한계](docs/rebuild/validation/2026-09-08-native-stop-recheck/README.md).

## 설치

macOS 또는 Linux에서 Python 3.10 이상과 Git이 필요합니다. 외부 Python 패키지는 설치하지 않습니다.

```bash
git clone https://github.com/habinsong/GeminiToGenius.git
bash GeminiToGenius/scripts/install.sh
```

기본 설치는 Antigravity 전역 플러그인입니다. 패키지를 별도 폴더에서 검증한 뒤 설치하며, 기존 GTG는 보존 경로로 옮깁니다. 기존 v2 설치기가 만든 것으로 확인되는 링크만 따로 보존·해제합니다. 사용자 전역 규칙과 다른 플러그인은 그대로 둡니다. 현재 checkout을 설치하며 자동 `git pull`은 하지 않습니다.

특정 프로젝트에만 설치하려면 다음처럼 실행합니다.

```bash
bash scripts/install.sh --workspace /absolute/path/to/project
```

Gemini CLI의 확장 형식은 별도로 생성합니다.

```bash
bash scripts/install.sh --platform gemini-cli
```

설치 후 호스트를 다시 시작합니다. 모델은 호스트에서 선택한 설정을 유지합니다. 특정 Flash 버전이나 사고 수준을 강제하지 않으며, 출시 전 모델의 호환성을 가정하지 않습니다.

## 사용

평소처럼 요청합니다. 짧거나 불완전한 요청도 현재 코드·오류·화면을 먼저 확인하도록 지시합니다. 결과나 데이터 안전에 영향을 주는 정보만 질문합니다.

관련 텍스트 파일은 호스트의 다중 읽기 도구나 `inspect` 명령으로 함께 확인할 수 있습니다. 전체 파일과 요청한 줄 범위의 완료 여부를 구분하며, 출력이 잘렸거나 조회 중 파일이 바뀌면 이를 명시합니다.

```text
이거 왜 안 됨 고쳐줘
이 화면 좀 불편한데 고쳐봐
이어서 해. 테스트 실패한 데부터
원인만 찾아. 수정은 하지 마
```

복잡한 작업에서는 에이전트가 목표·완료 조건·검증 명령을 등록합니다. 실행기는 명령을 직접 실행해 종료 코드와 파일 해시를 기록합니다. 검사 후 코드가 바뀌면 이전 성공을 무효화합니다. 상태는 프로젝트의 `.gtg/`에 저장되므로 로컬 ignore에 추가하는 것을 권장합니다.

긴 작업은 진행 메모와 다음 행동을 별도로 저장합니다. 재개할 때 메모의 기준 파일이 달라졌는지 확인하며, 메모를 테스트 성공으로 취급하지 않습니다. 같은 호스트 세션의 동일한 시작 요청을 다시 보내도 작업을 중복 생성하지 않습니다.

새 세션에서 이어가려면 에이전트가 저장된 작업 후보와 원래 명세를 확인한 뒤 같은 작업에 연결합니다. 목표·검증 결과·메모와 현재 파일을 유지하며, 과거의 성공을 현재 검증으로 혼동하지 않습니다. 작업 조회·연결은 현재 로컬 및 이벤트 재생으로 검증하는 기능입니다. 기존 호스트의 종료나 동시 파일 편집 제어는 호스트에서 확인해야 합니다.

훅은 연결된 작업의 미검증 상태를 알리고 자연 종료를 최대 두 번 재개하도록 구현했습니다. 사용자 중단·오류·백그라운드 작업을 무시하고 계속 호출하지 않습니다. 훅에서 LLM을 추가 호출하지 않습니다.

재개 상한에 도달하면 완료 대신 중단 상태와 이유를 남깁니다. 검증 CLI는 `SIGTERM`과 키보드 중단에 하위 프로세스도 종료하며, 부모만 종료되고 하위 프로세스가 남은 명령은 성공으로 인정하지 않습니다.

`status`의 `continuation[].last_stop`에서 마지막으로 받은 종료 코드·조건을 확인할 수 있습니다. 원본 프롬프트와 오류 본문은 저장하지 않습니다. 이전 버전에서 이미 끝난 이벤트의 정보는 복원하지 않습니다.

## 설치 검사와 제거

```bash
bash scripts/install.sh doctor
bash scripts/install.sh uninstall
```

프로젝트 설치라면 두 명령에도 같은 `--workspace`를 전달합니다. Gemini CLI라면 같은 `--platform gemini-cli`를 전달합니다. 제거는 삭제 대신 보존 폴더로 이동합니다.

`doctor`는 미완료 설치 기록이 있으면 먼저 이전 파일 배치를 복구한 뒤 검사합니다. 새 사용자 파일과 충돌하면 덮어쓰지 않고 중단합니다.

프로젝트 폴더를 옮겼다면 새 경로로 다시 설치합니다. 훅 명령은 설치 위치에 맞춰 생성되며 `doctor`는 이전 위치를 가리키는 설치를 실패로 표시합니다.

복구하려면 설치·제거 결과의 실제 `backup` 또는 `preserved` 경로를 지정합니다.

```bash
bash scripts/install.sh restore --backup /absolute/path/printed/by/installer
```

이전 v2 링크로 돌아가려면 먼저 새 플러그인을 제거한 뒤 실제 `legacy_backup` 경로로 `restore-legacy --backup`을 실행합니다. 이전 프로필의 결함까지 수정하는 명령은 아닙니다.

## 개발 및 검증

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/catalog.py
python3 scripts/catalog.py --check
```

- [재개발 문서](docs/rebuild/README.md): 계획·현재 상태·설계 판단입니다.
- [기존 원본 전체](docs/rebuild/inventory/baseline/README.md): 기존 113개 경로의 전체 코드와 해시입니다.
- [현재 원본 전체](docs/rebuild/inventory/current/README.md): 현재 구현을 파일별로 기록합니다.
- [연구 근거](docs/rebuild/research/sources.json): 공식 문서·논문·오픈소스 원장입니다.
- [자연어 평가 사례](evals/README.md): 슬래시 없는 요청의 후속 평가 기준입니다.
- [실제 단일 평가](docs/rebuild/validation/2026-09-08-native/README.md): 사용량·산출물·재현 자료와 검증 한계입니다.

등록한 검사가 통과해도 모든 사용자 요구가 충족됐다는 뜻은 아닙니다. UI·제품 품질·자연어 해석은 별도 결과 평가가 필요합니다. 여러 작업공간에 같은 호스트 세션으로 등록한 검사는 함께 확인합니다.

MIT. [라이선스](LICENSE).
````
