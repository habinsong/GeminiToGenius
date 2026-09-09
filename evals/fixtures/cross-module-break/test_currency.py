import unittest

from currency import format_won


class FormatTests(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(format_won(0), "0원")


if __name__ == "__main__":
    unittest.main()
