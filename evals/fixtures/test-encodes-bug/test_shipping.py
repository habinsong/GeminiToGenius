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
