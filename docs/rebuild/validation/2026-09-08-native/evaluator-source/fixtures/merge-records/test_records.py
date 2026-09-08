import unittest

from app import summarize


class RecordTests(unittest.TestCase):
    def test_single_record(self):
        self.assertEqual(summarize([{"id": "a"}]), {"items": [{"id": "a"}]})


if __name__ == "__main__":
    unittest.main()
