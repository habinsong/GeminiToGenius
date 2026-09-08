# `.github/workflows/validate-profile.yml`

- 형식: `100644`
- 바이트: 888
- SHA-256: `ba2a49a7220bcfb668bdd80d68a48d122ce8b0e65a747853012ec3c5e1ea0e41`
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
      - name: 현재 코드 문서 최신성 검사
        run: python3 scripts/catalog.py --check
```
