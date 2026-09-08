# `docs/rebuild/validation/2026-09-08-harness-comparison/comparison-clean.json`

- 형식: `100644`
- 바이트: 2119
- SHA-256: `f06a634203fa58b3f0865b53051aab6e76557f4094d26083dc9ddc4b4ebd1577`
- 인코딩: `utf-8`

```
{
  "kind": "harness_comparison",
  "schema_version": 1,
  "comparable": true,
  "blocking_reasons": [],
  "arms": [
    {
      "arm": "demo-fixed",
      "model": "reference",
      "trials": 1,
      "passed": 1,
      "ungraded": 0,
      "unstable": 0,
      "human_review": 0,
      "scope_violation_trials": 0,
      "cases": [
        "bounds"
      ],
      "profiles": [
        "gtg"
      ]
    },
    {
      "arm": "demo-nofix",
      "model": "reference",
      "trials": 1,
      "passed": 0,
      "ungraded": 0,
      "unstable": 0,
      "human_review": 0,
      "scope_violation_trials": 0,
      "cases": [
        "bounds"
      ],
      "profiles": [
        "baseline"
      ]
    }
  ],
  "trials": [
    {
      "trial": "/private/tmp/gtg-compare-clean/arm-a",
      "trial_id": "57ae6c7a81614573998a084a541e71c5",
      "arm": "demo-nofix",
      "model": "reference",
      "profile": "baseline",
      "case_id": "bounds",
      "prompt_sha256": "efd7ae2a272dd72a43d7d0bfbbe48bb6d69d380263bf774ad58bd47acaa1a3ca",
      "definition_digest": "1c38d3f94ebe436166b465fc7ca323428c0b1fe5a7fdb64f5e50987edfc94717",
      "state": "graded",
      "passed": false,
      "scope_violations": [],
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/gtg-compare-clean/arm-b",
      "trial_id": "7d3404c831d946d9821582445a6aa3cf",
      "arm": "demo-fixed",
      "model": "reference",
      "profile": "gtg",
      "case_id": "bounds",
      "prompt_sha256": "efd7ae2a272dd72a43d7d0bfbbe48bb6d69d380263bf774ad58bd47acaa1a3ca",
      "definition_digest": "1c38d3f94ebe436166b465fc7ca323428c0b1fe5a7fdb64f5e50987edfc94717",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "grades": 1,
      "requires_human_review": false
    }
  ],
  "labels_are_self_declared": true,
  "model_performance_claim": false,
  "note": "같은 사례·요청·채점 기준을 공유할 때만 comparable이 참입니다. 실행 하네스·모델·사용량은 사용자가 선언한 라벨이며 이 보고서가 확인하지 않습니다."
}
```
