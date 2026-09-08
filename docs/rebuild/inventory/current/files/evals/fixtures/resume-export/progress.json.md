# `evals/fixtures/resume-export/progress.json`

- 형식: `100644`
- 바이트: 1118
- SHA-256: `1e3a74b32c2ce4f68fb927042d7b5593fb8bc96d75d92761e2bdca046b825b1e`
- 인코딩: `utf-8`

```
{
  "spec": {
    "schema_version": 1,
    "goal": "CSV 다운로드 연결을 마치고 기존 JSON 동작과 사용자 파일명을 유지합니다.",
    "checks": [
      {
        "id": "serializer",
        "criterion": "완료한 CSV 직렬화의 헤더·인용·입력 보존 검사가 통과합니다.",
        "argv": ["python3", "-B", "-m", "unittest", "test_exports", "-v"],
        "watch": ["exports.py", "test_exports.py"]
      },
      {
        "id": "download",
        "criterion": "CSV 공개 다운로드 연결과 기존 JSON 다운로드 검사가 통과합니다.",
        "argv": ["python3", "-B", "-m", "unittest", "test_app", "-v"],
        "watch": ["app.py", "exports.py", "test_app.py"]
      }
    ]
  },
  "completed_checks": ["serializer"],
  "checkpoint": {
    "summary": "CSV 직렬화 구현과 관련 검사 3개를 마쳤습니다. 공개 다운로드의 CSV 연결은 남았습니다.",
    "next_action": "app.download에 CSV 경로를 연결하고 기존 JSON 및 사용자 파일명을 유지한 채 검증합니다.",
    "files": ["exports.py", "test_exports.py"]
  }
}
```
