# `docs/product/getting-started.md`

- 형식: `100644`
- 바이트: 2059
- SHA-256: `a898610e4e45fe59df5b7b20dc9e505dd920fbb4b3536fa05ea988d9aa0193e6`
- 인코딩: `utf-8`

````
# 설치와 첫 사용

macOS 또는 Linux, Python 3.10 이상, Git이 필요합니다. 외부 Python 패키지는 설치하지 않습니다.

```bash
git clone https://github.com/habinsong/GeminiToGenius.git
bash GeminiToGenius/scripts/install.sh
```

설치기가 홈 폴더에서 호스트가 직접 만든 설정 파일을 찾아, 감지한 호스트마다 설치합니다. 감지된 호스트가 없으면 Antigravity 전역 플러그인 하나만 넣습니다. 결과의 `hosts`에 호스트별 성공 여부가 나옵니다.

설치 후 호스트를 다시 시작합니다. 모델은 호스트에서 고른 설정을 그대로 씁니다. GTG가 특정 Flash 버전이나 사고 수준을 강제하지 않습니다.

## 특정 프로젝트에만

```bash
bash scripts/install.sh --workspace /absolute/path/to/project
```

## 호스트를 직접 고를 때

```bash
bash scripts/install.sh --platform antigravity-cli
```

`antigravity`, `antigravity-cli`, `gemini-cli` 중 하나입니다. 호스트별 경로와 주의점은 [지원 호스트](hosts.md)에 있습니다.

## 설치기가 하는 일

패키지를 별도 폴더에서 검증한 뒤 옮깁니다. 기존 GTG가 있으면 지우지 않고 보존 경로로 옮깁니다. 이전 v2 설치기가 만든 것으로 확인되는 링크만 따로 풀고, 사용자 전역 규칙과 다른 플러그인은 건드리지 않습니다.

현재 checkout을 설치합니다. `git pull`을 대신 실행하지 않습니다.

옮기는 도중에 프로세스가 죽어도 다음 실행이 이어서 정리합니다. 상태를 확인하려면 이렇게 합니다.

```bash
python3 scripts/install.py doctor
```

## 첫 사용

평소처럼 요청하면 됩니다. 슬래시 명령도, 명세 파일도 필요 없습니다.

```
로그인하면 500 나는데 고쳐줘
```

무슨 일이 일어나는지는 [동작 방식](how-it-works.md)에 있습니다.

## 지우기

```bash
python3 scripts/install.py uninstall
```

보존 경로에 남은 이전 설치본은 `restore`로 되돌릴 수 있습니다.
````
