from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone

from .config import ONE_TIME_STATE_KEYS, STATE_FILE, STATE_ROOT, VERSION_FILE


def read_state() -> dict:
    try:
        value = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def profile_version() -> str:
    try:
        return VERSION_FILE.read_text(encoding="utf-8").strip() or "unknown"
    except OSError:
        return "unknown"


def is_target_model(model_name: str) -> bool:
    normalized = model_name.lower()
    return (
        "gemini" in normalized
        and ("3.7" in normalized or "3-7" in normalized)
        and "flash" in normalized
        and "high" in normalized
    )


def save_state(
    event: str,
    payload: dict,
    *,
    failed: bool = False,
    extra: dict | None = None,
) -> None:
    """Store lifecycle metadata only; never copy transcript or tool arguments."""
    try:
        STATE_ROOT.mkdir(parents=True, exist_ok=True)
        state = {
            "event": event,
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "profileVersion": profile_version(),
            "modelName": payload.get("modelName", ""),
            "workspacePaths": payload.get("workspacePaths", []),
            "stepIdx": payload.get("stepIdx"),
            "invocationNum": payload.get("invocationNum"),
            "failed": failed,
        }
        previous = read_state()
        conversation_id = str(payload.get("conversationId", ""))
        for prefix in ("researchGate", "scopeGate"):
            key = f"{prefix}ConversationId"
            attempts_key = f"{prefix}Attempts"
            if conversation_id and previous.get(key) == conversation_id:
                state[key] = conversation_id
                state[attempts_key] = previous.get(attempts_key, 0)
        for key in ONE_TIME_STATE_KEYS:
            if conversation_id and previous.get(key) == conversation_id:
                state[key] = conversation_id
        if extra:
            state.update(extra)
        fd, temp_name = tempfile.mkstemp(prefix="last_state.", dir=STATE_ROOT)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(state, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temp_name, STATE_FILE)
    except OSError:
        pass
