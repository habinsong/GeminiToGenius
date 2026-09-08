# `docs/rebuild/validation/2026-09-08-native/evaluator-source/fixtures/merge-records/app.py`

- 형식: `100644`
- 바이트: 105
- SHA-256: `b3cda19c426317b623565a34d3c52beb90778d9145f15b32caca7980118588ca`
- 인코딩: `utf-8`

```
from records import merge_records


def summarize(records):
    return {"items": merge_records(records)}
```
