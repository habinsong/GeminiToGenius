# 설치와 첫 사용

macOS 또는 Linux, Python 3.10 이상, Git만 있으면 되며 외부 Python 패키지는 필요 없습니다.

```bash
git clone https://github.com/habinsong/GeminiToGenius.git
bash GeminiToGenius/scripts/install.sh
```

설치기는 홈 디렉터리의 호스트 설정 파일로 호스트를 감지해 각각에 플러그인을 설치합니다. 감지된 호스트가 없으면 Antigravity 전역 경로가 기본 대상이며, 호스트별 설치 상태는 실행 결과의 `hosts` 항목에서 확인할 수 있습니다.

설치 후에는 해당 호스트를 재시작해 주십시오. 모델과 추론 수준은 호스트 설정을 그대로 따릅니다.

## 특정 프로젝트에만 설치할 때

```bash
bash scripts/install.sh --workspace /absolute/path/to/project
```

## 대상 호스트를 직접 지정할 때

```bash
bash scripts/install.sh --platform antigravity-cli
```

지원 대상은 `antigravity`, `antigravity-cli`, `gemini-cli`입니다. 호스트별 세부 사항은 [지원 호스트](hosts.md) 문서를 참고해 주십시오.

## 설치기 동작 원리

패키지를 임시 디렉터리에서 검증한 뒤 대상 경로로 복사하고, 기존 GTG 설치본이 있으면 백업 경로로 이동해 보존합니다. 이전 v2 설치기가 만든 심볼릭 링크만 정리하고, 기존 전역 규칙과 타사 플러그인은 정리 대상이 아닙니다.

현재 체크아웃된 소스 코드를 그대로 설치하며, 임의로 `git pull`을 수행하지는 않습니다.

설치 도중 프로세스가 중단되더라도 다음 실행 시 잔여 임시 파일을 정리합니다. 설치 상태는 다음 명령으로 확인하실 수 있습니다.

```bash
python3 scripts/install.py doctor
```

## 첫 사용

설치 후에는 일반 자연어로 작업을 요청하시면 됩니다. 별도의 슬래시 명령어나 명세 파일 작성은 필요 없습니다. 버그 수정, 기능 구현, 문서 작성 등 작업 의도를 전달하시면 모델과 훅이 검증 흐름을 수행합니다.

세부 흐름은 [동작 방식](how-it-works.md) 문서에서 확인하실 수 있습니다.

## 제거

```bash
python3 scripts/install.py uninstall
```

백업 경로에 보존된 이전 설치본은 `restore` 명령으로 복원하실 수 있습니다.
