import unittest

from exporter import export


class ExportTests(unittest.TestCase):
    def test_text_and_dimensions(self):
        self.assertEqual(export("사진, A", 640, 480), {"text": "사진, A", "width": 640, "height": 480})

    def test_invalid_dimensions(self):
        with self.assertRaises(ValueError):
            export("sample", 0, 1)

    def test_startup(self):
        from startup import preview
        self.assertEqual(preview(), {"text": "sample", "width": 1, "height": 1})
