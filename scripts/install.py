#!/usr/bin/env python3
"""작업공간을 바꾸지 않고 checkout의 설치기를 실행합니다."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gtg.install import main

raise SystemExit(main())
