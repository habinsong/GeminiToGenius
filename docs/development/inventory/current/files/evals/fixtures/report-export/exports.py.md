# `evals/fixtures/report-export/exports.py`

- 형식: `100644`
- 바이트: 97
- SHA-256: `3bb0d265067a84d71eefe4328e0c4f61d00381c13362454ba4dd6942ab280e6d`
- 인코딩: `utf-8`

```
import json


def to_json(records):
    return json.dumps(records, ensure_ascii=False, indent=2)
```
