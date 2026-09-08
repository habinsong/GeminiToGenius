#!/usr/bin/env python3
"""설치된 패키지에서 현재 작업공간을 유지하며 GTG를 실행합니다."""

import sys

if len(sys.argv) > 1 and sys.argv[1] == "hook":
    from gtg.hooks import main
    del sys.argv[1]
else:
    from gtg.__main__ import main

raise SystemExit(main())
