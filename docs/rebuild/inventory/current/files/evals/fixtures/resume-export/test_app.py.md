# `evals/fixtures/resume-export/test_app.py`

- 형식: `100644`
- 바이트: 758
- SHA-256: `4389b90434e47e8ff8ee100b4c08826b5a563c13c60ec153ac10d82da1a0ae0a`
- 인코딩: `utf-8`

```
import unittest

from app import DOWNLOAD_STEM, download


class DownloadTests(unittest.TestCase):
    def test_existing_json_download(self):
        result = download([])
        self.assertEqual(result, {"filename": DOWNLOAD_STEM + ".json",
                                 "media_type": "application/json; charset=utf-8", "content": "[]"})

    def test_csv_download(self):
        result = download([], format="csv")
        self.assertEqual(result, {"filename": DOWNLOAD_STEM + ".csv",
                                 "media_type": "text/csv; charset=utf-8", "content": "id,name,note\r\n"})

    def test_unknown_format(self):
        with self.assertRaises(ValueError):
            download([], "xml")


if __name__ == "__main__":
    unittest.main()
```
