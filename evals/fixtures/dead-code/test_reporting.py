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
