# `docs/development/validation/2026-09-09-real-comparison/claude-code-mathlib.py`

- 형식: `100644`
- 바이트: 179
- SHA-256: `2ed45c162e80ffa23c5c359aef6e9a83fda522c9ae6b02ae326e7614c21d789a`
- 인코딩: `utf-8`

```
def clamp(value, lower, upper):
    if lower > upper:
        raise ValueError(f"lower({lower}) must not be greater than upper({upper})")
    return min(max(value, lower), upper)
```
