# `evals/fixtures/refactor-pricing/pricing.py`

- 형식: `100644`
- 바이트: 1200
- SHA-256: `e60f9db76de3a73bb2e8279294352177d6a9ad25ef1aaff1a882cb0aab67b694`
- 인코딩: `utf-8`

```
"""주문 금액을 계산합니다. 공개 함수 세 개의 동작은 다른 모듈이 의존합니다."""


def member_total(items, rate):
    total = 0
    for item in items:
        price = item["price"]
        count = item["count"]
        if count < 0:
            raise ValueError("수량은 음수일 수 없습니다.")
        total += price * count
    discounted = total - total * rate
    if discounted < 0:
        discounted = 0
    return round(discounted, 2)


def guest_total(items):
    total = 0
    for item in items:
        price = item["price"]
        count = item["count"]
        if count < 0:
            raise ValueError("수량은 음수일 수 없습니다.")
        total += price * count
    discounted = total - total * 0.0
    if discounted < 0:
        discounted = 0
    return round(discounted, 2)


def staff_total(items):
    total = 0
    for item in items:
        price = item["price"]
        count = item["count"]
        if count < 0:
            raise ValueError("수량은 음수일 수 없습니다.")
        total += price * count
    discounted = total - total * 0.3
    if discounted < 0:
        discounted = 0
    return round(discounted, 2)
```
