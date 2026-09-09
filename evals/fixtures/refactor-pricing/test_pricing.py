import unittest

from pricing import guest_total, member_total, staff_total


class PricingTests(unittest.TestCase):
    def test_member_discount(self):
        self.assertEqual(member_total([{"price": 100, "count": 2}], 0.1), 180.0)

    def test_guest_has_no_discount(self):
        self.assertEqual(guest_total([{"price": 100, "count": 2}]), 200.0)

    def test_staff_discount(self):
        self.assertEqual(staff_total([{"price": 100, "count": 1}]), 70.0)

    def test_negative_count_is_rejected(self):
        with self.assertRaises(ValueError):
            guest_total([{"price": 10, "count": -1}])


if __name__ == "__main__":
    unittest.main()
