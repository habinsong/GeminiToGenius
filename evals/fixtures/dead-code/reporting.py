"""보고서 유틸리티입니다."""

import json


def format_currency(amount):
    return f"{amount:,.2f}원"


def summarize(rows):
    return {"count": len(rows), "total": sum(row["amount"] for row in rows)}


def to_json(rows):
    return json.dumps(summarize(rows), ensure_ascii=False, sort_keys=True)


def legacy_csv_header():
    """예전 내보내기 형식입니다. 지금은 어디서도 부르지 않습니다."""
    return "name,amount"


def build_label(kind):
    """이름으로 찾아 부르는 경로가 있어 직접 호출은 보이지 않습니다."""
    return f"[{kind}]"
