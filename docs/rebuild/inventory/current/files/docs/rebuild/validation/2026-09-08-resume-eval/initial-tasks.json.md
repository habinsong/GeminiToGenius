# `docs/rebuild/validation/2026-09-08-resume-eval/initial-tasks.json`

- 형식: `100644`
- 바이트: 1863
- SHA-256: `c7d4f36ff20c6f574dc2413f9cee6fde352dcd2cc391d0b50ac564084ce74ef2`
- 인코딩: `utf-8`

```
{
  "workspace": "/private/var/folders/wt/88c641tj50z4rzrm6pfdld6c0000gn/T/gtg-native-resume-eyttktas/trial/workspace",
  "tasks": [
    {
      "task_id": "f64294a8600d439d884089bc32801ef7",
      "goal": "문서 원문 보존 확인",
      "goal_truncated": false,
      "created_at": 1788855989.4593558,
      "last_activity_at": 1788855989.587772,
      "checkpoint": null,
      "checkpoint_truncated": false,
      "connections": [],
      "connections_truncated": false,
      "recorded_check_counts": {
        "passed": 1
      }
    },
    {
      "task_id": "3c1764d16ffc4f8aa101e0df716cd620",
      "goal": "CSV 다운로드 연결을 마치고 기존 JSON 동작과 사용자 파일명을 유지합니다.",
      "goal_truncated": false,
      "created_at": 1788855989.314003,
      "last_activity_at": 1788855989.452461,
      "checkpoint": {
        "summary": "CSV 직렬화 구현과 관련 검사 3개를 마쳤습니다. 공개 다운로드의 CSV 연결은 남았습니다.",
        "next_action": "app.download에 CSV 경로를 연결하고 기존 JSON 및 사용자 파일명을 유지한 채 검증합니다."
      },
      "checkpoint_truncated": false,
      "connections": [
        {
          "key": "5e0720896e677e74dff22407cfcfd9ec951116a387e356331c06d9a287167049",
          "paused": 1,
          "retries": 0,
          "reason": "다음 세션에서 남은 작업을 이어갑니다.",
          "turn_open": 1
        }
      ],
      "connections_truncated": false,
      "recorded_check_counts": {
        "passed": 1,
        "pending": 1
      }
    }
  ],
  "total": 2,
  "offset": 0,
  "next_offset": null,
  "current_files_checked": false,
  "content_trust": "saved_task_data",
  "state_path": "/private/var/folders/wt/88c641tj50z4rzrm6pfdld6c0000gn/T/gtg-native-resume-eyttktas/trial/workspace/.gtg/state.sqlite3"
}
```
