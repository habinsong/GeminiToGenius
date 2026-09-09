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
