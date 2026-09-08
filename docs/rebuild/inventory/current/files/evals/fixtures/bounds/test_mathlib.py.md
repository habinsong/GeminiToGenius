# `evals/fixtures/bounds/test_mathlib.py`

- 형식: `100644`
- 바이트: 213
- SHA-256: `80ec21f265da49a2efbd25efea1ab54fad017d7ddd9856745101fcbb6e63f5c6`
- 인코딩: `utf-8`

```
import unittest

from mathlib import clamp


class ClampTests(unittest.TestCase):
    def test_upper_boundary(self):
        self.assertEqual(clamp(12, 0, 10), 10)


if __name__ == "__main__":
    unittest.main()
```
