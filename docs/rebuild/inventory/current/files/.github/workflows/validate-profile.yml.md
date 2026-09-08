# `.github/workflows/validate-profile.yml`

- 형식: `100644`
- 바이트: 1828
- SHA-256: `c99f02f5437a8a7bdc9e8a83740247bed56338a56179f8c89581339bd98ab90e`
- 인코딩: `utf-8`

```
name: 하네스 검증

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  harness:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    env:
      PYTHONDONTWRITEBYTECODE: '1'
    steps:
      - name: 저장소 확인
        uses: actions/checkout@v6

      - name: 실행·훅·설치·실패 복구 검증
        run: |
          bash -n scripts/install.sh
          python3 -m unittest discover -s tests -v

      - name: 공식 진입점으로 격리 설치 검사
        run: |
          bash scripts/install.sh --home "$RUNNER_TEMP/gtg-home"
          bash scripts/install.sh doctor --home "$RUNNER_TEMP/gtg-home"
          bash scripts/install.sh uninstall --home "$RUNNER_TEMP/gtg-home"

      - name: 호스트별 패키지와 감지 설치 검사
        run: |
          for platform in antigravity-cli gemini-cli; do
            bash scripts/install.sh --platform "$platform" --home "$RUNNER_TEMP/gtg-$platform"
            bash scripts/install.sh doctor --platform "$platform" --home "$RUNNER_TEMP/gtg-$platform"
            bash scripts/install.sh uninstall --platform "$platform" --home "$RUNNER_TEMP/gtg-$platform"
          done
          mkdir -p "$RUNNER_TEMP/gtg-detect/.gemini/config" "$RUNNER_TEMP/gtg-detect/.gemini/antigravity-cli"
          echo '{}' > "$RUNNER_TEMP/gtg-detect/.gemini/config/config.json"
          echo '{}' > "$RUNNER_TEMP/gtg-detect/.gemini/antigravity-cli/settings.json"
          bash scripts/install.sh --home "$RUNNER_TEMP/gtg-detect"
          bash scripts/install.sh doctor --home "$RUNNER_TEMP/gtg-detect"
          bash scripts/install.sh uninstall --home "$RUNNER_TEMP/gtg-detect"
      - name: 현재 코드 문서 최신성 검사
        run: python3 scripts/catalog.py --check
```
