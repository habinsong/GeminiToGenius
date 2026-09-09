# `docs/development/validation/2026-09-08-native-stop/trace-summary.json`

- 형식: `100644`
- 바이트: 1358
- SHA-256: `13f650560780932c9836a9ddaa68dcd625084682b2eae38f5781cb4f2de96875`
- 인코딩: `utf-8`

```
{
  "kind": "native_stop_trial",
  "host": "Antigravity",
  "host_version": "2.12.2",
  "selected_model_label": "Gemini 3.8 Flash High",
  "native_project_id": "203ebab1-6617-4748-892f-767073cd2526",
  "native_conversation_id": "b6f8b9a1-ea2b-422f-8c10-4422e2581385",
  "conversation_title": "종료 훅 연결 시험",
  "user_prompt_count": 1,
  "model_response_steps": 21,
  "inference_request_count": null,
  "tool_counts": {
    "view_file": 10,
    "list_dir": 4,
    "run_command": 5,
    "find_by_name": 1
  },
  "started_at": "2026-09-08T05:44:37Z",
  "last_response_at": "2026-09-08T05:45:39Z",
  "elapsed_seconds": 62.0,
  "final_response": "작업을 등록했습니다. 종료 훅의 재개를 기다립니다.",
  "host_turn_finished": true,
  "native_retry_verified": false,
  "registered_check_executed": false,
  "fixture_unchanged": true,
  "sessions": [
    {
      "task_id": "4fe8353aef3f4e4495b423010c7b829f",
      "paused": 1,
      "retries": 0,
      "last_event": null,
      "reason": "호스트 중단 또는 오류"
    }
  ],
  "runs": [],
  "raw_stop_input_captured": false,
  "termination_reason_received": null,
  "evidence_limit": "원문 Stop 입력은 보존되지 않았습니다. 자연 종료 뒤 중단·오류 분기로 저장된 결과를 확인했으나 원인 문자열은 아직 확인하지 못했습니다."
}
```
