import unittest

from inventory import low_stock, restock


class InventoryTests(unittest.TestCase):
    def test_restock_raises_low_counts(self):
        self.assertEqual(restock([("볼트", 2), ("너트", 7)], 5), [("볼트", 5), ("너트", 7)])

    def test_restock_keeps_input(self):
        original = [("볼트", 2)]
        restock(original, 5)
        self.assertEqual(original, [("볼트", 2)])

    def test_low_stock_lists_names(self):
        self.assertEqual(low_stock([("볼트", 2), ("너트", 7)], 5), ["볼트"])


if __name__ == "__main__":
    unittest.main()
