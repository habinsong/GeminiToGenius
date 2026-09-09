import unittest

from app import summarize


class RecordTests(unittest.TestCase):
    def test_single_record(self):
        self.assertEqual(summarize([{"id": "a"}]), {"items": [{"id": "a"}]})

    def test_merge_duplicate_records_preserves_fields(self):
        records = [
            {"id": "a", "name": "first", "score": 10},
            {"id": "a", "score": 20, "status": "active"},
        ]
        result = summarize(records)
        self.assertEqual(
            result,
            {"items": [{"id": "a", "name": "first", "score": 20, "status": "active"}]},
        )

    def test_preserves_order_of_first_appearance(self):
        records = [
            {"id": "b", "val": 1},
            {"id": "a", "val": 2},
            {"id": "b", "val": 3},
            {"id": "c", "val": 4},
            {"id": "a", "extra": 5},
        ]
        result = summarize(records)
        self.assertEqual(
            result,
            {
                "items": [
                    {"id": "b", "val": 3},
                    {"id": "a", "val": 2, "extra": 5},
                    {"id": "c", "val": 4},
                ]
            },
        )

    def test_does_not_mutate_input_records(self):
        item1 = {"id": "x", "val": 1}
        item2 = {"id": "x", "val": 2}
        records = [item1, item2]
        summarize(records)
        self.assertEqual(item1, {"id": "x", "val": 1})
        self.assertEqual(item2, {"id": "x", "val": 2})
        self.assertEqual(records, [item1, item2])

    def test_zero_is_valid_id(self):
        records = [{"id": 0, "val": 1}, {"id": 0, "status": "ok"}]
        result = summarize(records)
        self.assertEqual(result, {"items": [{"id": 0, "val": 1, "status": "ok"}]})

    def test_missing_id_raises_value_error(self):
        records = [{"name": "no-id"}]
        with self.assertRaises(ValueError):
            summarize(records)


if __name__ == "__main__":
    unittest.main()

