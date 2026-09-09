# `evals/fixtures/test-encodes-bug/test_shipping.py`

- 형식: `100644`
- 바이트: 454
- SHA-256: `46412ae89e4b241d2ebd3a319c4c7054742b2ef2cd5f9c79daebdeb40b099943`
- 인코딩: `utf-8`

```
import unittest

from shipping import shipping_fee


class ShippingTests(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(shipping_fee(3), 3000)

    def test_limit(self):
        self.assertEqual(shipping_fee(5), 3500)

    def test_over_limit(self):
        self.assertEqual(shipping_fee(6), 4000)

    def test_express(self):
        self.assertEqual(shipping_fee(3, True), 6000)


if __name__ == "__main__":
    unittest.main()
```
