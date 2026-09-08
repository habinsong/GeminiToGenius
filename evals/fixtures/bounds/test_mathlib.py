import unittest

from mathlib import clamp


class ClampTests(unittest.TestCase):
    def test_upper_boundary(self):
        self.assertEqual(clamp(12, 0, 10), 10)


if __name__ == "__main__":
    unittest.main()
