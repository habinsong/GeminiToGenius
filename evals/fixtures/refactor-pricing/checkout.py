"""공개 호출자입니다. 이 파일의 호출 방식은 유지되어야 합니다."""

from pricing import guest_total, member_total, staff_total


def receipt(items, kind, rate=0.1):
    if kind == "member":
        return {"kind": kind, "total": member_total(items, rate)}
    if kind == "staff":
        return {"kind": kind, "total": staff_total(items)}
    return {"kind": kind, "total": guest_total(items)}
