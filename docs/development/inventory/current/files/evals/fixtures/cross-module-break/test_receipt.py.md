# `evals/fixtures/cross-module-break/test_receipt.py`

- 형식: `100644`
- 바이트: 358
- SHA-256: `3bffbd8565cf1b847f997c7c060f2a666abde309d9d747401c8be5ff77fcd3f1`
- 인코딩: `utf-8`

```
import unittest

from receipt import render


class RenderTests(unittest.TestCase):
    def test_two_rows(self):
        self.assertEqual(render([("커피", 4500), ("빵", 12000)]),
                         "커피: 4500원\n빵: 12000원")

    def test_empty(self):
        self.assertEqual(render([]), "")


if __name__ == "__main__":
    unittest.main()
```
