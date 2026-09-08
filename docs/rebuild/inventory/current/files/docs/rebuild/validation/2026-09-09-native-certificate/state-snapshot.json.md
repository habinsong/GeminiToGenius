# `docs/rebuild/validation/2026-09-09-native-certificate/state-snapshot.json`

- 형식: `100644`
- 바이트: 2284
- SHA-256: `4e82de82e248c9156a1dacaa19c3373614514e3079ff0e68f64540b63505edb9`
- 인코딩: `utf-8`

```
{
  "tasks": [
    {
      "id": "2d749f95adc14a51a2ae63e4ec3fb4d8",
      "workspace": "/private/var/folders/wt/88c641tj50z4rzrm6pfdld6c0000gn/T/gtg-native-resume-eyttktas/trial/workspace",
      "spec": {
        "schema_version": 1,
        "goal": "README에 적어둔 재고 보고서 기능(low_stock, to_csv, report) 구현 및 기존 기능(restock) 유지",
        "checks": [
          {
            "id": "regression",
            "criterion": "기존 재고 관리(restock) 기능이 정상 동작하고 입력을 변경하지 않습니다.",
            "argv": [
              "python3",
              "check_inventory.py"
            ],
            "watch": [
              "inventory.py",
              "check_inventory.py"
            ],
            "timeout_seconds": 30
          },
          {
            "id": "report",
            "criterion": "재고 보고서 기능(low_stock, to_csv, report)이 명세대로 동작하고 입력을 변경하지 않습니다.",
            "argv": [
              "python3",
              "check_report.py"
            ],
            "watch": [
              "report.py",
              "inventory.py",
              "check_report.py"
            ],
            "timeout_seconds": 30
          }
        ],
        "max_resumes": 2
      }
    }
  ],
  "runs": [
    {
      "check_id": "regression",
      "result": {
        "status": "passed",
        "returncode": 0,
        "before": "55ba1d1389e88ca97adab84559a14a950b5aa67125c2a9d322d179993ce78e41",
        "after": "55ba1d1389e88ca97adab84559a14a950b5aa67125c2a9d322d179993ce78e41",
        "duration_seconds": 0.039932
      }
    },
    {
      "check_id": "report",
      "result": {
        "status": "passed",
        "returncode": 0,
        "before": "b27e8256a7a1b8246087eacddd4f2952ec366102f997eac6beb3d3ef71ccd17c",
        "after": "b27e8256a7a1b8246087eacddd4f2952ec366102f997eac6beb3d3ef71ccd17c",
        "duration_seconds": 0.041921
      }
    }
  ],
  "sessions": [
    {
      "key": "8bcf05b1e001...",
      "paused": 0,
      "retries": 0,
      "reason": "",
      "last_stop": "{\"event\": \"Stop\", \"execution_num\": 0, \"termination_reason\": \"NO_TOOL_CALL\", \"fully_idle\": true, \"has_error\": false}",
      "turn_open": 0
    }
  ]
}
```
