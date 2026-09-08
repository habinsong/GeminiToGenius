# `evals/fixtures/resume-export/exports.py`

- 형식: `100644`
- 바이트: 393
- SHA-256: `b95c91ff1457f5cec1bc47c6eeef66e56e62155b2d84a4b66d909938ae479bd4`
- 인코딩: `utf-8`

```
import csv
import io
import json


def to_json(records):
    return json.dumps(records, ensure_ascii=False, indent=2)


def to_csv(records):
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["id", "name", "note"])
    for record in records:
        writer.writerow([record.get(name, "") for name in ("id", "name", "note")])
    return output.getvalue()
```
