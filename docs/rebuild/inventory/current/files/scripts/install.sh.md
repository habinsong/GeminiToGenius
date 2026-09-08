# `scripts/install.sh`

- 형식: `100644`
- 바이트: 142
- SHA-256: `7caf933397b9eeae215f2d631d5efcc21683bcee51c9a142aeca82546c3a7258`
- 인코딩: `utf-8`

```
#!/usr/bin/env bash
set -euo pipefail
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
exec python3 "$script_dir/install.py" "$@"
```
