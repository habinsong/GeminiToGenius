# `evals/fixtures/report-export/test_app.py`

- 형식: `100644`
- 바이트: 504
- SHA-256: `525cae662a4a5b5ce52c103e826dde4b0eb6f5808bf1afebea5a17a73eb832a5`
- 인코딩: `utf-8`

```
import unittest

from app import DOWNLOAD_STEM, download


class DownloadTests(unittest.TestCase):
    def test_existing_json_download(self):
        result = download([])
        self.assertEqual(result, {"filename": DOWNLOAD_STEM + ".json",
                                 "media_type": "application/json; charset=utf-8", "content": "[]"})

    def test_unknown_format(self):
        with self.assertRaises(ValueError):
            download([], "xml")


if __name__ == "__main__":
    unittest.main()
```
