# `docs/rebuild/validation/2026-09-08-package/shell-contract.json`

- 형식: `100644`
- 바이트: 746
- SHA-256: `9abd39db21b6681aeddaef08c5570726ffa99845c9f33d333d8a838f18abb5f0`
- 인코딩: `utf-8`

```
{
  "shell": "/bin/sh",
  "shell_metacharacters_in_path": true,
  "working_directory_is_outside_package": true,
  "injected_marker_files_created": false,
  "state_database_created": false,
  "additional_model_prompts": 0,
  "results": [
    {
      "platform": "antigravity",
      "event": "PreInvocation",
      "exit_code": 0,
      "expected_output": true
    },
    {
      "platform": "antigravity",
      "event": "Stop",
      "exit_code": 0,
      "expected_output": true
    },
    {
      "platform": "gemini-cli",
      "event": "BeforeAgent",
      "exit_code": 0,
      "expected_output": true
    },
    {
      "platform": "gemini-cli",
      "event": "AfterAgent",
      "exit_code": 0,
      "expected_output": true
    }
  ]
}
```
