# `.github/workflows/validate-profile.yml`

- 형식: `100644`
- 바이트: 636
- SHA-256: `01bd5e6f1a57beb16c5a8394c56fa89f1b23b206acaa37bf6962bc12b8c4771a`
- 인코딩: `utf-8`

```
name: Validate profile

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  profile:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v6

      - name: Install profile with the supported installer
        run: |
          bash -n scripts/install.sh
          AGY_INSTALL_HOME="$RUNNER_TEMP/gemini-home" bash scripts/install.sh --skip-update

      - name: Verify installed profile
        run: |
          AGY_INSTALL_HOME="$RUNNER_TEMP/gemini-home" python3 "$RUNNER_TEMP/gemini-home/.gemini/config/agy-focus/current/scripts/verify_profile.py"
```
