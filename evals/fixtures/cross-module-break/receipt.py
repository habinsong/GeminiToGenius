"""영수증 본문을 만듭니다."""

from currency import format_won


def line(name, amount):
    return f"{name}: {format_won(amount)}"


def render(rows):
    return "\n".join(line(name, amount) for name, amount in rows)
