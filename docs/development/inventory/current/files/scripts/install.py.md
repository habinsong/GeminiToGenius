# `scripts/install.py`

- 형식: `100644`
- 바이트: 257
- SHA-256: `cca22a44e7cc79ccfc07fd62b6ca0fa97c3ebdcf5fecaabb6ee79cb080d0295d`
- 인코딩: `utf-8`

```
#!/usr/bin/env python3
"""작업공간을 바꾸지 않고 checkout의 설치기를 실행합니다."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gtg.install import main

raise SystemExit(main())
```
