# `docs/development/validation/2026-09-08-resume-eval/capture_native.py`

- 형식: `100644`
- 바이트: 3729
- SHA-256: `29478bc0a28bf4cab51703a2fda0c3e7345ce8e5d0a48cc8da5446c9c51a0047`
- 인코딩: `utf-8`

```
"""이번 네이티브 대화의 도구 인자와 시각만 읽습니다. 응답·사고 본문은 읽지 않습니다."""

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3


def varint(data, offset):
    value = shift = 0
    while offset < len(data) and shift <= 63:
        byte = data[offset]
        offset += 1
        value |= (byte & 127) << shift
        if byte < 128:
            return value, offset
        shift += 7
    raise ValueError("잘못된 varint")


def fields(data):
    offset = 0
    while offset < len(data):
        tag, offset = varint(data, offset)
        number, kind = tag >> 3, tag & 7
        if kind == 0:
            value, offset = varint(data, offset)
        elif kind in (1, 2, 5):
            if kind == 2:
                length, offset = varint(data, offset)
            else:
                length = 8 if kind == 1 else 4
            value = data[offset:offset + length]
            offset += length
            if len(value) != length:
                raise ValueError("잘린 필드")
        else:
            raise ValueError("미지원 wire type")
        yield number, kind, value


def created_at(metadata):
    # 이 버전에서 확인한 step metadata의 첫 Timestamp 필드만 사용합니다.
    stamp = next(value for number, kind, value in fields(metadata) if number == 1 and kind == 2)
    values = {number: value for number, kind, value in fields(stamp) if kind == 0}
    return datetime.fromtimestamp(values[1] + values.get(2, 0) / 1e9, timezone.utc).isoformat()


def main():
    folder = Path(__file__).resolve().parent
    prep = json.loads((folder / "preparation.json").read_text())
    conversation = prep["conversation_id"]
    path = Path.home() / ".gemini/antigravity/conversations" / (conversation + ".db")
    db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    counts = dict(db.execute("SELECT step_type, count(*) FROM steps GROUP BY step_type"))
    times = []
    # 도구가 아닌 응답 payload는 SELECT하지 않습니다. metadata는 시각만 추출합니다.
    for idx, metadata in db.execute("SELECT idx, metadata FROM steps ORDER BY idx"):
        times.append({"step": idx, "created_at": created_at(metadata)})
    tools = []
    allowed = {"CommandLine", "Cwd", "AbsolutePath", "File", "TargetFile", "toolSummary", "toolAction"}
    for idx, payload in db.execute("SELECT idx, step_payload FROM steps WHERE step_type=132 ORDER BY idx"):
        tool = {"step": idx, "arguments": {}}
        for number, kind, value in fields(payload):
            if number != 140 or kind != 2:
                continue
            for entry, wire, encoded in fields(value):
                if entry != 1 or wire != 2:
                    continue
                pair = {n: v.decode("utf-8") for n, k, v in fields(encoded) if k == 2}
                if pair.get(1) in allowed:
                    tool["arguments"][pair[1]] = pair.get(2, "")
        tools.append(tool)
    db.close()
    output = {"conversation_id": conversation, "native_database": str(path),
              "response_content_copied": False, "thinking_content_copied": False,
              "step_type_counts": counts, "times": times, "tools": tools,
              "tool_action_counts": dict(Counter(t["arguments"].get("toolAction", "unknown") for t in tools))}
    (folder / "native-tools.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"steps": sum(counts.values()), "tools": len(tools),
                      "commands": [t for t in tools if "CommandLine" in t["arguments"]]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```
