# `evals/fixtures/cross-module-break/receipt.py`

- 형식: `100644`
- 바이트: 228
- SHA-256: `cbbb75a556b39fe1a43696676102b6f3aa02703d57484f4ded83c6780b494304`
- 인코딩: `utf-8`

```
"""영수증 본문을 만듭니다."""

from currency import format_won


def line(name, amount):
    return f"{name}: {format_won(amount)}"


def render(rows):
    return "\n".join(line(name, amount) for name, amount in rows)
```
