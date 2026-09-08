# `docs/rebuild/validation/2026-09-08-native-stop/input/task.json`

- 형식: `100644`
- 바이트: 502
- SHA-256: `38240d7daf072cf52e5bf7d9abd9f22eb7f51a2d73b067606976cbf10083569e`
- 인코딩: `utf-8`

```
{
  "schema_version": 1,
  "goal": "현재 호스트의 종료 훅 재개를 받은 뒤 등록된 레코드 회귀 검사를 실행합니다.",
  "checks": [
    {
      "id": "records-regression",
      "criterion": "필드 병합·순서·입력 보존·ID 0·누락 ID를 포함한 기존 회귀 검사 6개가 통과합니다.",
      "argv": ["python3", "-B", "-m", "unittest", "discover", "-v"],
      "watch": ["records.py", "app.py", "test_records.py"],
      "timeout_seconds": 30
    }
  ]
}
```
