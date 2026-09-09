# `docs/development/validation/2026-09-09-native-certificate/replay-clean.json`

- 형식: `100644`
- 바이트: 1051
- SHA-256: `f56e4dfd0f8680ec8d0f25e6a568e232a170a386376134ccd5db60820e56c1ad`
- 인코딩: `utf-8`

```
{
  "task_id": "2d749f95adc14a51a2ae63e4ec3fb4d8",
  "goal": "README에 적어둔 재고 보고서 기능(low_stock, to_csv, report) 구현 및 기존 기능(restock) 유지",
  "workspace": "/private/var/folders/wt/88c641tj50z4rzrm6pfdld6c0000gn/T/gtg-native-resume-eyttktas/trial/workspace",
  "workspace_matches": true,
  "claimed_verified": true,
  "reconstructed": true,
  "checks": [
    {
      "id": "regression",
      "criterion": "기존 재고 관리(restock) 기능이 정상 동작하고 입력을 변경하지 않습니다.",
      "reconstructed": true,
      "reason": null,
      "returncode": 0,
      "fingerprint": "55ba1d1389e88ca97adab84559a14a950b5aa67125c2a9d322d179993ce78e41"
    },
    {
      "id": "report",
      "criterion": "재고 보고서 기능(low_stock, to_csv, report)이 명세대로 동작하고 입력을 변경하지 않습니다.",
      "reconstructed": true,
      "reason": null,
      "returncode": 0,
      "fingerprint": "b27e8256a7a1b8246087eacddd4f2952ec366102f997eac6beb3d3ef71ccd17c"
    }
  ]
}
```
