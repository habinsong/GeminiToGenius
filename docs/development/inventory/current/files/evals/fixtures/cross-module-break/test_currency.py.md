# `evals/fixtures/cross-module-break/test_currency.py`

- 형식: `100644`
- 바이트: 211
- SHA-256: `a18a25f9a90e0ce2e8e1e98ab08d11ca27136835f0d5c4c4eda9d6a8151e2283`
- 인코딩: `utf-8`

```
import unittest

from currency import format_won


class FormatTests(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(format_won(0), "0원")


if __name__ == "__main__":
    unittest.main()
```
