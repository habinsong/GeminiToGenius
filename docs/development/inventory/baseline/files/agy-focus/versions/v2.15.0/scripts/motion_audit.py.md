# `agy-focus/versions/v2.15.0/scripts/motion_audit.py`

- 형식: `100644`
- 바이트: 872
- SHA-256: `62dc3b23b1b0051d4ff2b5fa65d93c17ecd1f2ddb769674b9e20c52e2b2c11a7`
- 인코딩: `utf-8`

```
"""Run the reduced-motion branch of the browser render audit."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ui_render_audit import MOTION_SCRIPT


def reduced_motion_audit(
    client: Any,
    evaluate: Callable[[Any, str], dict],
    wait_for_page: Callable[[Any], None],
) -> dict:
    """Emulate reduced motion, measure it, and restore the default media state."""

    client.call(
        "Emulation.setEmulatedMedia",
        {"features": [{"name": "prefers-reduced-motion", "value": "reduce"}]},
    )
    client.call("Page.reload", {"ignoreCache": True})
    wait_for_page(client)
    reduced_motion = evaluate(client, MOTION_SCRIPT)
    client.call("Emulation.setEmulatedMedia", {"features": []})
    client.call("Page.reload", {"ignoreCache": True})
    wait_for_page(client)
    return reduced_motion
```
