# `evals/fixtures/dead-code/test_reporting.py`

- 형식: `100644`
- 바이트: 430
- SHA-256: `9c8717cba2514a2f518629e9973bc5a9cf754b56d7bc58767060118c4c408989`
- 인코딩: `utf-8`

```
import unittest

import reporting
from dashboard import render


class ReportingTests(unittest.TestCase):
    def test_render(self):
        rows = [{"amount": 1000}, {"amount": 2500}]
        self.assertEqual(render(rows, "월간"), "[월간] 2건 3,500.00원")

    def test_to_json(self):
        self.assertEqual(reporting.to_json([{"amount": 5}]), '{"count": 1, "total": 5}')


if __name__ == "__main__":
    unittest.main()
```
