# `docs/development/validation/2026-09-09-real-comparison/gtg-mathlib.py`

- 형식: `100644`
- 바이트: 159
- SHA-256: `d9a109c6c055fb8d29006a6b9021cb65bff5a446f971dd738307f09b6a57e1c7`
- 인코딩: `utf-8`

```
def clamp(value, lower, upper):
    if lower > upper:
        raise ValueError("lower cannot be greater than upper")
    return max(lower, min(value, upper))

```
