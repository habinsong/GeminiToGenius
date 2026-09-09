# `docs/development/validation/2026-09-08-native-stop/input/records.py`

- 형식: `100644`
- 바이트: 355
- SHA-256: `4ef8ba3cc13e11e8a78d01454f2e944805a3e3e5f032b06515862d653b822714`
- 인코딩: `utf-8`

```
def merge_records(records):
    by_id = {}
    for record in records:
        if "id" not in record:
            raise ValueError("Record missing 'id'")
        rec_id = record["id"]
        if rec_id in by_id:
            by_id[rec_id] = {**by_id[rec_id], **record}
        else:
            by_id[rec_id] = dict(record)
    return list(by_id.values())

```
