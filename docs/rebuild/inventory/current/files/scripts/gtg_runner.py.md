# `scripts/gtg_runner.py`

- 형식: `100644`
- 바이트: 293
- SHA-256: `df6f8577c5c1d224cf6d20b21f301baeea5b508ad6c3f87385d41a0175cf9a83`
- 인코딩: `utf-8`

```
#!/usr/bin/env python3
"""설치된 패키지에서 현재 작업공간을 유지하며 GTG를 실행합니다."""

import sys

if len(sys.argv) > 1 and sys.argv[1] == "hook":
    from gtg.hooks import main
    del sys.argv[1]
else:
    from gtg.__main__ import main

raise SystemExit(main())
```
