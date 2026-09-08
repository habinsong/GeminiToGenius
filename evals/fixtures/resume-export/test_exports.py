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
