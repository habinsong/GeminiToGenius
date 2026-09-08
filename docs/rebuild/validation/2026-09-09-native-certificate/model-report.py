"""재고 보고서를 생성합니다."""

import csv
import io
from inventory import restock


def low_stock(items, minimum):
    """수량이 minimum 미만인 항목 이름만 원래 순서로 담은 목록을 돌려줍니다."""
    return [name for name, count in items if count < minimum]


def to_csv(items):
    """헤더 name,count로 시작하고 각 줄이 \r\n으로 끝나는 CSV 문자열을 돌려줍니다."""
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\r\n")
    writer.writerow(["name", "count"])
    for name, count in items:
        writer.writerow([name, count])
    return output.getvalue()


def report(items, minimum):
    """보충 목록, 부족 이름 목록, 보충 목록의 CSV 문자열을 담은 사전을 돌려줍니다."""
    restocked = restock(items, minimum)
    low = low_stock(items, minimum)
    csv_str = to_csv(restocked)
    return {
        "restocked": restocked,
        "low": low,
        "csv": csv_str,
    }
