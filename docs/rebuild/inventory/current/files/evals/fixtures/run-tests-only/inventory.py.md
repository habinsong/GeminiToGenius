# `evals/fixtures/run-tests-only/inventory.py`

- 형식: `100644`
- 바이트: 280
- SHA-256: `87162af2134ad536f3259a125134520d1bdd7a043810239f7bd92ab2b2a6adb0`
- 인코딩: `utf-8`

```
"""재고 수량을 다룹니다. 이 파일은 이미 올바르게 동작합니다."""


def restock(items, minimum):
    return [(name, max(count, minimum)) for name, count in items]


def low_stock(items, minimum):
    return [name for name, count in items if count < minimum]
```
