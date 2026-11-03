# 설치와 첫 사용

macOS 또는 Linux 환경, Python 3.10 이상, Git이 필요합니다. 외부 Python 패키지는 요구하지 않습니다.

```bash
git clone https://github.com/habinsong/GeminiToGenius.git
bash GeminiToGenius/scripts/install.sh
```

설치기는 사용자 홈 디렉터리에서 호스트 설정 파일을 탐색하여 감지된 각 호스트에 플러그인을 설치하며 만약 감지된 호스트가 없으면 Antigravity 전역 플러그인 경로에 기본으로 설치합니다. 실행 결과의 `hosts` 항목을 살펴보시면 호스트별 설치 상태를 투명하게 확인하실 수 있습니다.

설치를 마친 뒤에는 해당 호스트를 재시작해 주십시오. 모델은 호스트에 미리 설정된 모델과 추론(Thinking) 수준을 그대로 유지하므로 GTG가 특정 버전이나 파라미터를 강제하지는 않습니다.

## 특정 프로젝트에만 설치할 때

```bash
bash scripts/install.sh --workspace /absolute/path/to/project
```

## 대상 호스트를 직접 지정할 때

```bash
bash scripts/install.sh --platform antigravity-cli
```

지원 대상은 `antigravity`, `antigravity-cli`, `gemini-cli`입니다. 호스트별 세부 경로와 주의사항은 [지원 호스트](hosts.md) 문서를 참고해 주십시오.

## 설치기 동작 원리

패키지를 별도의 임시 디렉터리에서 사전 검증한 뒤 대상 경로로 안전하게 복사합니다. 기존 GTG 설치본이 발견되면 바로 삭제하지 않고 백업 경로로 이동하여 보존합니다. 이전 v2 설치기가 생성한 것으로 확인된 심볼릭 링크만 선별적으로 정리하며, 사용자의 기존 전역 규칙이나 타사 플러그인은 변경하지 않습니다.

현재 체크아웃된 소스 코드를 설치하며, 백그라운드에서 임의로 `git pull`을 수행하지 않습니다.

설치 도중 예기치 않게 프로세스가 종료되더라도 다음 실행 시 잔여 임시 파일을 정리합니다. 설치 무결성 상태는 다음 명령으로 언제든 점검하실 수 있습니다.

```bash
python3 scripts/install.py doctor
```

## 첫 사용

설치를 마친 후에는 평소처럼 자연어로 편안하게 요청하시면 됩니다. 슬래시 명령어나 별도의 명세 파일을 번거롭게 작성하실 필요가 없습니다.

```
로그인하면 500 나는데 고쳐줘
```

작업 진행 과정과 세부 흐름은 [동작 방식](how-it-works.md) 문서에서 상세히 확인하실 수 있습니다.

## 제거

```bash
python3 scripts/install.py uninstall
```

백업 경로에 보존된 이전 설치본은 `restore` 명령으로 언제든 안전하게 복원하실 수 있습니다.
