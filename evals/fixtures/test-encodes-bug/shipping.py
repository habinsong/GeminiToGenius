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
