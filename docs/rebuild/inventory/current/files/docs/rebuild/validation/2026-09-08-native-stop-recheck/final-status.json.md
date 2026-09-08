# `docs/rebuild/validation/2026-09-08-native-stop-recheck/final-status.json`

- 형식: `100644`
- 바이트: 438
- SHA-256: `5a698f97c12335600bc87c33e972bb679b291c9f27b0e506d79556e28f72ad0b`
- 인코딩: `utf-8`

```
{
  "task_id": "08b8259e31984f08b56710bdda9b0f8f",
  "goal": "현재 호스트의 종료 훅 재개를 받은 뒤 등록된 레코드 회귀 검사를 실행합니다.",
  "verified": true,
  "checks": [
    {
      "id": "records-regression",
      "criterion": "필드 병합·순서·입력 보존·ID 0·누락 ID를 포함한 기존 회귀 검사 6개가 통과합니다.",
      "status": "passed"
    }
  ],
  "checkpoint": null
}
```
