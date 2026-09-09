# `evals/fixtures/resume-export/app.py`

- 형식: `100644`
- 바이트: 307
- SHA-256: `2906dc64761ec0dafc14dc248fe30f57f726aa506152e5aa595dd7723dc9dc2d`
- 인코딩: `utf-8`

```
from exports import to_json


DOWNLOAD_STEM = "records"


def download(records, format="json"):
    if format != "json":
        raise ValueError("unsupported format")
    return {"filename": DOWNLOAD_STEM + ".json",
            "media_type": "application/json; charset=utf-8", "content": to_json(records)}
```
