# `docs/development/validation/2026-09-08-native-stop/contract-replay.json`

- 형식: `100644`
- 바이트: 897
- SHA-256: `e3b5eae400d3dfb3a0a357654663bc90346f005f52f6ffad9a410f3dc165ec33`
- 인코딩: `utf-8`

```
{
  "kind": "contract_replay",
  "input_source": "https://atamel.dev/posts/2026/07-16_where_agy_hooks/",
  "actual_model_called": false,
  "input_workspace_and_session_substituted": true,
  "termination_reason": "NO_TOOL_CALL",
  "first_decision": "continue",
  "first_state": [
    {
      "key": "df1ad59a2ff125f3fa241bd8f0797131a402418e307c30bf657777fbd1946ac2",
      "paused": 0,
      "retries": 1,
      "reason": "",
      "last_stop": {
        "event": "Stop",
        "execution_num": 0,
        "termination_reason": "NO_TOOL_CALL",
        "fully_idle": true,
        "has_error": false
      }
    }
  ],
  "check_status": "passed",
  "final_decision": "stop",
  "final_verified": true,
  "last_stop": {
    "event": "Stop",
    "execution_num": 1,
    "termination_reason": "NO_TOOL_CALL",
    "fully_idle": true,
    "has_error": false
  },
  "native_failure_fixed_claim": false
}
```
