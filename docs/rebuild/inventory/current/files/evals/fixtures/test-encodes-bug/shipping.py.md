# `evals/fixtures/test-encodes-bug/shipping.py`

- 형식: `100644`
- 바이트: 260
- SHA-256: `08786f6e8a5333a4b182ea7cfcfc09ea45dc21cedfbdc9816ee956c066a9e6c0`
- 인코딩: `utf-8`

```
"""배송비 계산입니다."""

BASE_FEE = 3000
PER_KG = 500
FREE_LIMIT = 5


def shipping_fee(weight_kg, express=False):
    extra = max(weight_kg - FREE_LIMIT + 1, 0) * PER_KG
    fee = BASE_FEE + extra
    if express:
        fee = fee * 2
    return fee
```
