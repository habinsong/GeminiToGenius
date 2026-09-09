# `evals/fixtures/dead-code/dashboard.py`

- 형식: `100644`
- 바이트: 370
- SHA-256: `f91b2030a632cb313de04c9ed9d5873f7e576ebe2a48e4410bab5d8b4cb82912`
- 인코딩: `utf-8`

```
"""보고서를 화면용으로 조립합니다."""

import reporting


def render(rows, kind):
    # 이름으로 찾아 부르므로 grep으로는 호출이 보이지 않습니다.
    label = getattr(reporting, "build_" + "label")(kind)
    summary = reporting.summarize(rows)
    return f"{label} {summary['count']}건 {reporting.format_currency(summary['total'])}"
```
