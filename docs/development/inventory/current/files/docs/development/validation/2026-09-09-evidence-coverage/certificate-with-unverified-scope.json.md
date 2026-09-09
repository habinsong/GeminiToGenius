# `docs/development/validation/2026-09-09-evidence-coverage/certificate-with-unverified-scope.json`

- 형식: `100644`
- 바이트: 844
- SHA-256: `b841fe2798e19d2b3b5e003329800a44e77ea1027e025405a91a761a7251d704`
- 인코딩: `utf-8`

```
{
  "schema_version": 1,
  "task_id": "f55e6576ea8e48abaa495d186f3fc37c",
  "goal": "덧셈을 확인합니다.",
  "workspace": "/private/tmp/demo",
  "verified": true,
  "checks": [
    {
      "id": "unit",
      "criterion": "덧셈이 올바릅니다.",
      "argv": [
        "python3",
        "check.py"
      ],
      "watch": [
        "check.py",
        "core.py",
        "untested.py"
      ],
      "timeout_seconds": 120,
      "status": "passed",
      "returncode": 0,
      "evidence_fingerprint": "b8e352a4afa35f5f8f4a0d13a227b4075eb88012288fd02743cb689646046218",
      "coverage_observed": true,
      "unexecuted_watch": [
        "untested.py"
      ]
    }
  ],
  "unverified_scope": [
    "untested.py"
  ],
  "created": 1788885656.94,
  "digest": "0cff554cdbaca83143b6848cdc4f5228740b1a239cdc55a8199a6b0636a06492"
}
```
