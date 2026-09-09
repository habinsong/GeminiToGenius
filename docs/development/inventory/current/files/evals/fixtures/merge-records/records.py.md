# `evals/fixtures/merge-records/records.py`

- 형식: `100644`
- 바이트: 139
- SHA-256: `4a81a71f72cc545f1d0e0408a3f144ffb6cb0629346388b6cb8cc22a83c14a9d`
- 인코딩: `utf-8`

```
def merge_records(records):
    by_id = {}
    for record in records:
        by_id[record["id"]] = record
    return list(by_id.values())
```
