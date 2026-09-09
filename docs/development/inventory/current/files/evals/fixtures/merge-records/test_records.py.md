# `evals/fixtures/merge-records/test_records.py`

- 형식: `100644`
- 바이트: 243
- SHA-256: `74fbc53df867e6b252feba5d35de30663a622dd7d6ca5c42d5170d97e52aa27b`
- 인코딩: `utf-8`

```
import unittest

from app import summarize


class RecordTests(unittest.TestCase):
    def test_single_record(self):
        self.assertEqual(summarize([{"id": "a"}]), {"items": [{"id": "a"}]})


if __name__ == "__main__":
    unittest.main()
```
