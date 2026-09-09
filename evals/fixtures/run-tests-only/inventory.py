"""재고 수량을 다룹니다. 이 파일은 이미 올바르게 동작합니다."""


def restock(items, minimum):
    return [(name, max(count, minimum)) for name, count in items]


def low_stock(items, minimum):
    return [name for name, count in items if count < minimum]
