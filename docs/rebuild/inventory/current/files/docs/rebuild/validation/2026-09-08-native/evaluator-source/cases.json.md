# `docs/rebuild/validation/2026-09-08-native/evaluator-source/cases.json`

- 형식: `100644`
- 바이트: 2126
- SHA-256: `aac833c12183f12c23f4a58e088713130cfc9ce599be1902dfe05256e41a015d`
- 인코딩: `utf-8`

```
{
  "schema_version": 1,
  "cases": {
    "bounds": {
      "prompt": "범위 밖 값이 제대로 안 잡히는데 고쳐봐.",
      "fixture": "bounds",
      "module": "mathlib.py",
      "function": "clamp",
      "allowed_edits": ["mathlib.py", "test_mathlib.py"],
      "checks": [
        {"args": [-3, 0, 10], "expected": 0},
        {"args": [15, 0, 10], "expected": 10},
        {"args": [5, 0, 10], "expected": 5},
        {"args": [-1.5, -1, 2], "expected": -1},
        {"args": [3, 3, 3], "expected": 3},
        {"args": [0, 10, 1], "error": "ValueError"}
      ]
    },
    "merge-records": {
      "prompt": "중복된 항목 합치면 값이 자꾸 사라짐. 고쳐줘.",
      "fixture": "merge-records",
      "module": "records.py",
      "function": "merge_records",
      "allowed_edits": ["records.py", "test_records.py", "app.py"],
      "checks": [
        {"args": [[{"id": "a", "name": "사진"}, {"id": "a", "count": 2}]], "expected": [{"id": "a", "name": "사진", "count": 2}]},
        {"args": [[{"id": "a", "count": 1}, {"id": "b", "count": 5}, {"id": "a", "count": 3}]], "expected": [{"id": "a", "count": 3}, {"id": "b", "count": 5}]},
        {"args": [[]], "expected": []},
        {"args": [[{"id": 0, "name": "영"}, {"id": 0, "count": 1}]], "expected": [{"id": 0, "name": "영", "count": 1}]},
        {"args": [[{"name": "ID 없음"}]], "error": "ValueError"}
      ],
      "preserve_arguments": true,
      "integrations": [
        {
          "module": "app.py",
          "function": "summarize",
          "preserve_arguments": true,
          "checks": [
            {"args": [[{"id": "a", "name": "사진"}, {"id": "a", "count": 2}]], "expected": {"items": [{"id": "a", "name": "사진", "count": 2}]}},
            {"args": [[]], "expected": {"items": []}},
            {"args": [[{"name": "ID 없음"}]], "error": "ValueError"}
          ]
        }
      ]
    },
    "inspect-only": {
      "prompt": "왜 음수가 그대로 나옴? 원인만 찾아. 수정 ㄴㄴ.",
      "fixture": "bounds",
      "allowed_edits": [],
      "requires_human_review": true
    }
  }
}
```
