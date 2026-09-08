# `gtg/platforms.py`

- 형식: `100644`
- 바이트: 1652
- SHA-256: `dd1a71be7ad3f56cb80ffa55005f8d78a22669720278fe59c2fd92be06d4be6f`
- 인코딩: `utf-8`

```
"""호스트별 계약 차이를 한 곳에서 정의합니다. 다른 모듈은 이 값을 참조합니다."""

from __future__ import annotations

# Antigravity Desktop·IDE와 Antigravity CLI는 같은 하네스를 사용하므로 훅 계약이 같습니다.
# 설치 위치만 다릅니다. Gemini CLI 확장은 별도 계약을 유지합니다.
ANTIGRAVITY = ("antigravity", "antigravity-cli")
PLATFORMS = (*ANTIGRAVITY, "gemini-cli")

EVENTS = {**{name: ("PreInvocation", "Stop") for name in ANTIGRAVITY},
          "gemini-cli": ("BeforeAgent", "AfterAgent")}

NAME = "geminitogenius"

# 설치기가 관리하는 호스트·범위별 상위 폴더입니다. 이동 기록도 이 목록만 허용합니다.
INSTALL_ROOTS = {("antigravity", "workspace"): ".agents/plugins",
                 ("antigravity", "global"): ".gemini/config/plugins",
                 ("antigravity-cli", "global"): ".gemini/antigravity-cli/plugins",
                 ("gemini-cli", "global"): ".gemini/extensions"}

# 호스트가 스스로 만드는 설정 파일입니다. 자동 감지는 이 근거만 사용합니다.
# Gemini CLI는 개인 계정 서비스가 종료됐고 고유한 표식을 확인하지 못해 자동 감지 대상이 아닙니다.
HOST_MARKERS = {"antigravity": ".gemini/config/config.json",
                "antigravity-cli": ".gemini/antigravity-cli/settings.json"}


def antigravity(platform: str) -> bool:
    """Antigravity 계열이면 참입니다. 지원하지 않는 이름은 거부합니다."""
    if platform not in PLATFORMS:
        raise ValueError("지원하지 않는 호스트입니다.")
    return platform in ANTIGRAVITY
```
