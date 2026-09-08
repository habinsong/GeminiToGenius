# `evals/fixtures/resume-export/test_exports.py`

- 형식: `100644`
- 바이트: 630
- SHA-256: `13130aa76779508e04722a1c5feddb15df276f12eef7e6736ff57e3414225c27`
- 인코딩: `utf-8`

```
import unittest

from exports import to_csv


class CSVTests(unittest.TestCase):
    def test_empty_rows_keep_header(self):
        self.assertEqual(to_csv([]), "id,name,note\r\n")

    def test_quotes_and_newlines_are_preserved(self):
        value = to_csv([{"id": 0, "name": "첫, 항목", "note": '메모\n"끝"'}])
        self.assertEqual(value, 'id,name,note\r\n0,"첫, 항목","메모\n""끝"""\r\n')

    def test_input_is_unchanged(self):
        rows = [{"id": "x", "name": "항목"}]
        to_csv(rows)
        self.assertEqual(rows, [{"id": "x", "name": "항목"}])


if __name__ == "__main__":
    unittest.main()
```
