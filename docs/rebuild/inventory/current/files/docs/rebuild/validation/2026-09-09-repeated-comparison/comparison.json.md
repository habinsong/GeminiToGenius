# `docs/rebuild/validation/2026-09-09-repeated-comparison/comparison.json`

- 형식: `100644`
- 바이트: 59998
- SHA-256: `8b0bff10bf3e196c111cd73f6c2a14b72a6eb667692ec1eb7de90ca3833d7b1d`
- 인코딩: `utf-8`

```
{
  "kind": "harness_comparison",
  "schema_version": 1,
  "comparable": true,
  "blocking_reasons": [],
  "arms": [
    {
      "arm": "agy-gtg",
      "model": "gemini-3.8-flash-high",
      "trials": 16,
      "passed": 14,
      "ungraded": 0,
      "unstable": 0,
      "human_review": 2,
      "scope_violation_trials": 0,
      "cases": [
        "bounds",
        "bounds",
        "dead-code",
        "dead-code",
        "inspect-only",
        "inspect-only",
        "merge-records",
        "merge-records",
        "refactor-pricing",
        "refactor-pricing",
        "report-export",
        "report-export",
        "resume-export",
        "resume-export",
        "run-tests-only",
        "run-tests-only"
      ],
      "profiles": [
        "gtg"
      ],
      "total_duration_seconds": 1038.798,
      "unobserved_runs": 0,
      "runs_that_executed_code": 16,
      "case_results": {
        "bounds": {
          "attempts": 2,
          "passed": 2
        },
        "dead-code": {
          "attempts": 2,
          "passed": 2
        },
        "inspect-only": {
          "attempts": 2,
          "passed": 0
        },
        "merge-records": {
          "attempts": 2,
          "passed": 2
        },
        "refactor-pricing": {
          "attempts": 2,
          "passed": 2
        },
        "report-export": {
          "attempts": 2,
          "passed": 2
        },
        "resume-export": {
          "attempts": 2,
          "passed": 2
        },
        "run-tests-only": {
          "attempts": 2,
          "passed": 2
        }
      },
      "cases_always_passed": 7
    },
    {
      "arm": "agy-plain",
      "model": "gemini-3.8-flash-high",
      "trials": 16,
      "passed": 14,
      "ungraded": 0,
      "unstable": 0,
      "human_review": 2,
      "scope_violation_trials": 0,
      "cases": [
        "bounds",
        "bounds",
        "dead-code",
        "dead-code",
        "inspect-only",
        "inspect-only",
        "merge-records",
        "merge-records",
        "refactor-pricing",
        "refactor-pricing",
        "report-export",
        "report-export",
        "resume-export",
        "resume-export",
        "run-tests-only",
        "run-tests-only"
      ],
      "profiles": [
        "baseline"
      ],
      "total_duration_seconds": 934.404,
      "unobserved_runs": 0,
      "runs_that_executed_code": 14,
      "case_results": {
        "bounds": {
          "attempts": 2,
          "passed": 2
        },
        "dead-code": {
          "attempts": 2,
          "passed": 2
        },
        "inspect-only": {
          "attempts": 2,
          "passed": 0
        },
        "merge-records": {
          "attempts": 2,
          "passed": 2
        },
        "refactor-pricing": {
          "attempts": 2,
          "passed": 2
        },
        "report-export": {
          "attempts": 2,
          "passed": 2
        },
        "resume-export": {
          "attempts": 2,
          "passed": 2
        },
        "run-tests-only": {
          "attempts": 2,
          "passed": 2
        }
      },
      "cases_always_passed": 7
    },
    {
      "arm": "claude-code",
      "model": "claude-sonnet-5",
      "trials": 16,
      "passed": 12,
      "ungraded": 0,
      "unstable": 0,
      "human_review": 2,
      "scope_violation_trials": 2,
      "cases": [
        "bounds",
        "bounds",
        "dead-code",
        "dead-code",
        "inspect-only",
        "inspect-only",
        "merge-records",
        "merge-records",
        "refactor-pricing",
        "refactor-pricing",
        "report-export",
        "report-export",
        "resume-export",
        "resume-export",
        "run-tests-only",
        "run-tests-only"
      ],
      "profiles": [
        "baseline"
      ],
      "total_duration_seconds": 831.149,
      "unobserved_runs": 0,
      "runs_that_executed_code": 14,
      "case_results": {
        "bounds": {
          "attempts": 2,
          "passed": 2
        },
        "dead-code": {
          "attempts": 2,
          "passed": 2
        },
        "inspect-only": {
          "attempts": 2,
          "passed": 0
        },
        "merge-records": {
          "attempts": 2,
          "passed": 2
        },
        "refactor-pricing": {
          "attempts": 2,
          "passed": 2
        },
        "report-export": {
          "attempts": 2,
          "passed": 2
        },
        "resume-export": {
          "attempts": 2,
          "passed": 0
        },
        "run-tests-only": {
          "attempts": 2,
          "passed": 2
        }
      },
      "cases_always_passed": 6
    },
    {
      "arm": "codex-cli",
      "model": "gpt-5.6-terra",
      "trials": 16,
      "passed": 13,
      "ungraded": 0,
      "unstable": 0,
      "human_review": 2,
      "scope_violation_trials": 1,
      "cases": [
        "bounds",
        "bounds",
        "dead-code",
        "dead-code",
        "inspect-only",
        "inspect-only",
        "merge-records",
        "merge-records",
        "refactor-pricing",
        "refactor-pricing",
        "report-export",
        "report-export",
        "resume-export",
        "resume-export",
        "run-tests-only",
        "run-tests-only"
      ],
      "profiles": [
        "baseline"
      ],
      "total_duration_seconds": 1461.911,
      "unobserved_runs": 0,
      "runs_that_executed_code": 16,
      "case_results": {
        "bounds": {
          "attempts": 2,
          "passed": 2
        },
        "dead-code": {
          "attempts": 2,
          "passed": 2
        },
        "inspect-only": {
          "attempts": 2,
          "passed": 0
        },
        "merge-records": {
          "attempts": 2,
          "passed": 2
        },
        "refactor-pricing": {
          "attempts": 2,
          "passed": 2
        },
        "report-export": {
          "attempts": 2,
          "passed": 2
        },
        "resume-export": {
          "attempts": 2,
          "passed": 1
        },
        "run-tests-only": {
          "attempts": 2,
          "passed": 2
        }
      },
      "cases_always_passed": 6
    }
  ],
  "trials": [
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-gtg-bounds-1",
      "trial_id": "53af2515c78a456d8f2e451285745341",
      "arm": "agy-gtg",
      "model": "gemini-3.8-flash-high",
      "profile": "gtg",
      "case_id": "bounds",
      "prompt_sha256": "efd7ae2a272dd72a43d7d0bfbbe48bb6d69d380263bf774ad58bd47acaa1a3ca",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 37.11,
        "executed_workspace_file_count": 14
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-gtg-bounds-2",
      "trial_id": "86ccd55b803c40a7b7a5a97692ce0491",
      "arm": "agy-gtg",
      "model": "gemini-3.8-flash-high",
      "profile": "gtg",
      "case_id": "bounds",
      "prompt_sha256": "efd7ae2a272dd72a43d7d0bfbbe48bb6d69d380263bf774ad58bd47acaa1a3ca",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 59.188,
        "executed_workspace_file_count": 17
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-gtg-dead-code-1",
      "trial_id": "1c8fe3c1564a45af9eb1101e199a5b92",
      "arm": "agy-gtg",
      "model": "gemini-3.8-flash-high",
      "profile": "gtg",
      "case_id": "dead-code",
      "prompt_sha256": "1460a5165c5f30597db203fc7fd90e62c5cd8af2189795aeb510364506fe9428",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 52.13,
        "executed_workspace_file_count": 15
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-gtg-dead-code-2",
      "trial_id": "fae4006ff22e4d1e83dc6863591cff9a",
      "arm": "agy-gtg",
      "model": "gemini-3.8-flash-high",
      "profile": "gtg",
      "case_id": "dead-code",
      "prompt_sha256": "1460a5165c5f30597db203fc7fd90e62c5cd8af2189795aeb510364506fe9428",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 71.949,
        "executed_workspace_file_count": 18
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-gtg-inspect-only-1",
      "trial_id": "013bf002d9a949a881bf411769820285",
      "arm": "agy-gtg",
      "model": "gemini-3.8-flash-high",
      "profile": "gtg",
      "case_id": "inspect-only",
      "prompt_sha256": "61ae284a0ed9d5f5d0baa2090d8e1ddc2d57aa9c26e9466a8d341cd83addf368",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": false,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 31.539,
        "executed_workspace_file_count": 14
      },
      "grades": 1,
      "requires_human_review": true
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-gtg-inspect-only-2",
      "trial_id": "ba2965e73fe74dcd8032dc3f8f07e952",
      "arm": "agy-gtg",
      "model": "gemini-3.8-flash-high",
      "profile": "gtg",
      "case_id": "inspect-only",
      "prompt_sha256": "61ae284a0ed9d5f5d0baa2090d8e1ddc2d57aa9c26e9466a8d341cd83addf368",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": false,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 27.939,
        "executed_workspace_file_count": 14
      },
      "grades": 1,
      "requires_human_review": true
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-gtg-merge-records-1",
      "trial_id": "206364a52e4649d5bc76eec2a59ff3d3",
      "arm": "agy-gtg",
      "model": "gemini-3.8-flash-high",
      "profile": "gtg",
      "case_id": "merge-records",
      "prompt_sha256": "e6fa0f8453486c3e2d163a7267bfe8205af11fa4eba216b01cea3175891c0406",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 56.448,
        "executed_workspace_file_count": 15
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-gtg-merge-records-2",
      "trial_id": "e4f2a2089ad744cf9e2b8f11825e81a5",
      "arm": "agy-gtg",
      "model": "gemini-3.8-flash-high",
      "profile": "gtg",
      "case_id": "merge-records",
      "prompt_sha256": "e6fa0f8453486c3e2d163a7267bfe8205af11fa4eba216b01cea3175891c0406",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 83.106,
        "executed_workspace_file_count": 18
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-gtg-refactor-pricing-1",
      "trial_id": "ed35a7fc526e41d585ad428562d626ab",
      "arm": "agy-gtg",
      "model": "gemini-3.8-flash-high",
      "profile": "gtg",
      "case_id": "refactor-pricing",
      "prompt_sha256": "7f0a477991878d39a8682d84dad72fedd91672f587d771dbe16656844fc4deab",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 109.149,
        "executed_workspace_file_count": 18
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-gtg-refactor-pricing-2",
      "trial_id": "773d4a98dd184ccf937e1033854a5a67",
      "arm": "agy-gtg",
      "model": "gemini-3.8-flash-high",
      "profile": "gtg",
      "case_id": "refactor-pricing",
      "prompt_sha256": "7f0a477991878d39a8682d84dad72fedd91672f587d771dbe16656844fc4deab",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 61.778,
        "executed_workspace_file_count": 15
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-gtg-report-export-1",
      "trial_id": "94bcdd33c23e48fe88db77637be05873",
      "arm": "agy-gtg",
      "model": "gemini-3.8-flash-high",
      "profile": "gtg",
      "case_id": "report-export",
      "prompt_sha256": "136061947d1b1a4d05c15de411b05e62d32dabd2296c2fced2048892ea976856",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 85.261,
        "executed_workspace_file_count": 19
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-gtg-report-export-2",
      "trial_id": "af4fec0abd1140eeb7ae837daacd56cc",
      "arm": "agy-gtg",
      "model": "gemini-3.8-flash-high",
      "profile": "gtg",
      "case_id": "report-export",
      "prompt_sha256": "136061947d1b1a4d05c15de411b05e62d32dabd2296c2fced2048892ea976856",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 116.199,
        "executed_workspace_file_count": 19
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-gtg-resume-export-1",
      "trial_id": "f4cfdd3e53e74c9f88b8c0d3735d5afb",
      "arm": "agy-gtg",
      "model": "gemini-3.8-flash-high",
      "profile": "gtg",
      "case_id": "resume-export",
      "prompt_sha256": "cc2ec967a8409cec3e105f597deec7cf5946702bd934b368e811523121d8c9dd",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 69.685,
        "executed_workspace_file_count": 19
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-gtg-resume-export-2",
      "trial_id": "feaef650820f41bfae1a6830f4196399",
      "arm": "agy-gtg",
      "model": "gemini-3.8-flash-high",
      "profile": "gtg",
      "case_id": "resume-export",
      "prompt_sha256": "cc2ec967a8409cec3e105f597deec7cf5946702bd934b368e811523121d8c9dd",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 124.203,
        "executed_workspace_file_count": 19
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-gtg-run-tests-only-1",
      "trial_id": "d17c12440a554024b916c70d9a6a7355",
      "arm": "agy-gtg",
      "model": "gemini-3.8-flash-high",
      "profile": "gtg",
      "case_id": "run-tests-only",
      "prompt_sha256": "a11ddb20a0e34ecfd24ac3a2b6cb78109208647a56803735298ae851a2f31669",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 25.069,
        "executed_workspace_file_count": 14
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-gtg-run-tests-only-2",
      "trial_id": "89a84a698c914c088cff22cd4ebd5a80",
      "arm": "agy-gtg",
      "model": "gemini-3.8-flash-high",
      "profile": "gtg",
      "case_id": "run-tests-only",
      "prompt_sha256": "a11ddb20a0e34ecfd24ac3a2b6cb78109208647a56803735298ae851a2f31669",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 28.045,
        "executed_workspace_file_count": 14
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-plain-bounds-1",
      "trial_id": "7e43e0d173974b568c9b2aa894ee970c",
      "arm": "agy-plain",
      "model": "gemini-3.8-flash-high",
      "profile": "baseline",
      "case_id": "bounds",
      "prompt_sha256": "efd7ae2a272dd72a43d7d0bfbbe48bb6d69d380263bf774ad58bd47acaa1a3ca",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 36.51,
        "executed_workspace_file_count": 2
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-plain-bounds-2",
      "trial_id": "2992ab2b33514f76be69042154b0e713",
      "arm": "agy-plain",
      "model": "gemini-3.8-flash-high",
      "profile": "baseline",
      "case_id": "bounds",
      "prompt_sha256": "efd7ae2a272dd72a43d7d0bfbbe48bb6d69d380263bf774ad58bd47acaa1a3ca",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 45.028,
        "executed_workspace_file_count": 2
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-plain-dead-code-1",
      "trial_id": "9eedc3dd3fdd4959b8f131098b74675f",
      "arm": "agy-plain",
      "model": "gemini-3.8-flash-high",
      "profile": "baseline",
      "case_id": "dead-code",
      "prompt_sha256": "1460a5165c5f30597db203fc7fd90e62c5cd8af2189795aeb510364506fe9428",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 66.859,
        "executed_workspace_file_count": 3
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-plain-dead-code-2",
      "trial_id": "3788725341ea4e9b95fade200a2c023c",
      "arm": "agy-plain",
      "model": "gemini-3.8-flash-high",
      "profile": "baseline",
      "case_id": "dead-code",
      "prompt_sha256": "1460a5165c5f30597db203fc7fd90e62c5cd8af2189795aeb510364506fe9428",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 75.505,
        "executed_workspace_file_count": 3
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-plain-inspect-only-1",
      "trial_id": "1936e2414c4145dd8457e0258946f648",
      "arm": "agy-plain",
      "model": "gemini-3.8-flash-high",
      "profile": "baseline",
      "case_id": "inspect-only",
      "prompt_sha256": "61ae284a0ed9d5f5d0baa2090d8e1ddc2d57aa9c26e9466a8d341cd83addf368",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": false,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 19.837,
        "executed_workspace_file_count": 0
      },
      "grades": 1,
      "requires_human_review": true
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-plain-inspect-only-2",
      "trial_id": "b7dc9228d8aa481c90583f6b8cf2ddd4",
      "arm": "agy-plain",
      "model": "gemini-3.8-flash-high",
      "profile": "baseline",
      "case_id": "inspect-only",
      "prompt_sha256": "61ae284a0ed9d5f5d0baa2090d8e1ddc2d57aa9c26e9466a8d341cd83addf368",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": false,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 18.209,
        "executed_workspace_file_count": 0
      },
      "grades": 1,
      "requires_human_review": true
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-plain-merge-records-1",
      "trial_id": "32de1df3be1d479c9c9dac6d7bbf098d",
      "arm": "agy-plain",
      "model": "gemini-3.8-flash-high",
      "profile": "baseline",
      "case_id": "merge-records",
      "prompt_sha256": "e6fa0f8453486c3e2d163a7267bfe8205af11fa4eba216b01cea3175891c0406",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 140.534,
        "executed_workspace_file_count": 3
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-plain-merge-records-2",
      "trial_id": "1c1b9624415e40c897f8cb66abfc5af9",
      "arm": "agy-plain",
      "model": "gemini-3.8-flash-high",
      "profile": "baseline",
      "case_id": "merge-records",
      "prompt_sha256": "e6fa0f8453486c3e2d163a7267bfe8205af11fa4eba216b01cea3175891c0406",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 40.765,
        "executed_workspace_file_count": 3
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-plain-refactor-pricing-1",
      "trial_id": "88ca08f727844f37932f62b80c99163e",
      "arm": "agy-plain",
      "model": "gemini-3.8-flash-high",
      "profile": "baseline",
      "case_id": "refactor-pricing",
      "prompt_sha256": "7f0a477991878d39a8682d84dad72fedd91672f587d771dbe16656844fc4deab",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 42.472,
        "executed_workspace_file_count": 3
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-plain-refactor-pricing-2",
      "trial_id": "c9e425fd627d4fd898c1904ad808031c",
      "arm": "agy-plain",
      "model": "gemini-3.8-flash-high",
      "profile": "baseline",
      "case_id": "refactor-pricing",
      "prompt_sha256": "7f0a477991878d39a8682d84dad72fedd91672f587d771dbe16656844fc4deab",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 46.678,
        "executed_workspace_file_count": 3
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-plain-report-export-1",
      "trial_id": "8f928510a9d64735ad8232a0bb8658d6",
      "arm": "agy-plain",
      "model": "gemini-3.8-flash-high",
      "profile": "baseline",
      "case_id": "report-export",
      "prompt_sha256": "136061947d1b1a4d05c15de411b05e62d32dabd2296c2fced2048892ea976856",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 75.882,
        "executed_workspace_file_count": 4
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-plain-report-export-2",
      "trial_id": "8004707a6ab14564b5e257d39df545de",
      "arm": "agy-plain",
      "model": "gemini-3.8-flash-high",
      "profile": "baseline",
      "case_id": "report-export",
      "prompt_sha256": "136061947d1b1a4d05c15de411b05e62d32dabd2296c2fced2048892ea976856",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 101.37,
        "executed_workspace_file_count": 4
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-plain-resume-export-1",
      "trial_id": "07065e3a15e74d878932bb5d156e87dc",
      "arm": "agy-plain",
      "model": "gemini-3.8-flash-high",
      "profile": "baseline",
      "case_id": "resume-export",
      "prompt_sha256": "cc2ec967a8409cec3e105f597deec7cf5946702bd934b368e811523121d8c9dd",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 117.645,
        "executed_workspace_file_count": 4
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-plain-resume-export-2",
      "trial_id": "a7b3d96983744e1da296ea2bfa2789d8",
      "arm": "agy-plain",
      "model": "gemini-3.8-flash-high",
      "profile": "baseline",
      "case_id": "resume-export",
      "prompt_sha256": "cc2ec967a8409cec3e105f597deec7cf5946702bd934b368e811523121d8c9dd",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 60.132,
        "executed_workspace_file_count": 4
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-plain-run-tests-only-1",
      "trial_id": "01f988ca238044b593c8d9e288ccd6e5",
      "arm": "agy-plain",
      "model": "gemini-3.8-flash-high",
      "profile": "baseline",
      "case_id": "run-tests-only",
      "prompt_sha256": "a11ddb20a0e34ecfd24ac3a2b6cb78109208647a56803735298ae851a2f31669",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 28.69,
        "executed_workspace_file_count": 2
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/agy-plain-run-tests-only-2",
      "trial_id": "bbf4263fcef34639a55e47bb53c2bf1e",
      "arm": "agy-plain",
      "model": "gemini-3.8-flash-high",
      "profile": "baseline",
      "case_id": "run-tests-only",
      "prompt_sha256": "a11ddb20a0e34ecfd24ac3a2b6cb78109208647a56803735298ae851a2f31669",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 18.288,
        "executed_workspace_file_count": 2
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/claude-code-bounds-1",
      "trial_id": "48106a6ff82640b8a26a53e72b561b6d",
      "arm": "claude-code",
      "model": "claude-sonnet-5",
      "profile": "baseline",
      "case_id": "bounds",
      "prompt_sha256": "efd7ae2a272dd72a43d7d0bfbbe48bb6d69d380263bf774ad58bd47acaa1a3ca",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 31.906,
        "executed_workspace_file_count": 2
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/claude-code-bounds-2",
      "trial_id": "fd5b005d2b814eb3bcc57f2cccba49a7",
      "arm": "claude-code",
      "model": "claude-sonnet-5",
      "profile": "baseline",
      "case_id": "bounds",
      "prompt_sha256": "efd7ae2a272dd72a43d7d0bfbbe48bb6d69d380263bf774ad58bd47acaa1a3ca",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 43.413,
        "executed_workspace_file_count": 2
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/claude-code-dead-code-1",
      "trial_id": "5c7e570a8a884cfab35ff85d7dfccb3b",
      "arm": "claude-code",
      "model": "claude-sonnet-5",
      "profile": "baseline",
      "case_id": "dead-code",
      "prompt_sha256": "1460a5165c5f30597db203fc7fd90e62c5cd8af2189795aeb510364506fe9428",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 41.002,
        "executed_workspace_file_count": 3
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/claude-code-dead-code-2",
      "trial_id": "201e04ef12b74a9b95a4fde9fd154d33",
      "arm": "claude-code",
      "model": "claude-sonnet-5",
      "profile": "baseline",
      "case_id": "dead-code",
      "prompt_sha256": "1460a5165c5f30597db203fc7fd90e62c5cd8af2189795aeb510364506fe9428",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 38.993,
        "executed_workspace_file_count": 3
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/claude-code-inspect-only-1",
      "trial_id": "79a2ad0de0f24c04b0a495604b8a842a",
      "arm": "claude-code",
      "model": "claude-sonnet-5",
      "profile": "baseline",
      "case_id": "inspect-only",
      "prompt_sha256": "61ae284a0ed9d5f5d0baa2090d8e1ddc2d57aa9c26e9466a8d341cd83addf368",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": false,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 25.029,
        "executed_workspace_file_count": 0
      },
      "grades": 1,
      "requires_human_review": true
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/claude-code-inspect-only-2",
      "trial_id": "cbd5df8d79e548d4862f945e410ad065",
      "arm": "claude-code",
      "model": "claude-sonnet-5",
      "profile": "baseline",
      "case_id": "inspect-only",
      "prompt_sha256": "61ae284a0ed9d5f5d0baa2090d8e1ddc2d57aa9c26e9466a8d341cd83addf368",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": false,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 23.19,
        "executed_workspace_file_count": 0
      },
      "grades": 1,
      "requires_human_review": true
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/claude-code-merge-records-1",
      "trial_id": "d8caf1d0cc3741e3846de15d88ecf1f8",
      "arm": "claude-code",
      "model": "claude-sonnet-5",
      "profile": "baseline",
      "case_id": "merge-records",
      "prompt_sha256": "e6fa0f8453486c3e2d163a7267bfe8205af11fa4eba216b01cea3175891c0406",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 48.991,
        "executed_workspace_file_count": 3
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/claude-code-merge-records-2",
      "trial_id": "2466767b0fff4680bc060a244d6e88fe",
      "arm": "claude-code",
      "model": "claude-sonnet-5",
      "profile": "baseline",
      "case_id": "merge-records",
      "prompt_sha256": "e6fa0f8453486c3e2d163a7267bfe8205af11fa4eba216b01cea3175891c0406",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 71.769,
        "executed_workspace_file_count": 3
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/claude-code-refactor-pricing-1",
      "trial_id": "f3c909f493654b91ad6c3d0bb5c65765",
      "arm": "claude-code",
      "model": "claude-sonnet-5",
      "profile": "baseline",
      "case_id": "refactor-pricing",
      "prompt_sha256": "7f0a477991878d39a8682d84dad72fedd91672f587d771dbe16656844fc4deab",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 66.679,
        "executed_workspace_file_count": 3
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/claude-code-refactor-pricing-2",
      "trial_id": "289e90f88df24a8a94de2892c8c056e6",
      "arm": "claude-code",
      "model": "claude-sonnet-5",
      "profile": "baseline",
      "case_id": "refactor-pricing",
      "prompt_sha256": "7f0a477991878d39a8682d84dad72fedd91672f587d771dbe16656844fc4deab",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 59.668,
        "executed_workspace_file_count": 3
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/claude-code-report-export-1",
      "trial_id": "d5c5a874f58b4640a3761cdf4679a23c",
      "arm": "claude-code",
      "model": "claude-sonnet-5",
      "profile": "baseline",
      "case_id": "report-export",
      "prompt_sha256": "136061947d1b1a4d05c15de411b05e62d32dabd2296c2fced2048892ea976856",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 110.241,
        "executed_workspace_file_count": 4
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/claude-code-report-export-2",
      "trial_id": "3b1fb735c1e14512938166cde6c5f628",
      "arm": "claude-code",
      "model": "claude-sonnet-5",
      "profile": "baseline",
      "case_id": "report-export",
      "prompt_sha256": "136061947d1b1a4d05c15de411b05e62d32dabd2296c2fced2048892ea976856",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 100.205,
        "executed_workspace_file_count": 4
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/claude-code-resume-export-1",
      "trial_id": "ab7b174c17aa4ceaa74ffb124f7bd5ba",
      "arm": "claude-code",
      "model": "claude-sonnet-5",
      "profile": "baseline",
      "case_id": "resume-export",
      "prompt_sha256": "cc2ec967a8409cec3e105f597deec7cf5946702bd934b368e811523121d8c9dd",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": false,
      "scope_violations": [
        "progress.json"
      ],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 74.102,
        "executed_workspace_file_count": 4
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/claude-code-resume-export-2",
      "trial_id": "bb1a93761ca34f1a8d187f875edf45ed",
      "arm": "claude-code",
      "model": "claude-sonnet-5",
      "profile": "baseline",
      "case_id": "resume-export",
      "prompt_sha256": "cc2ec967a8409cec3e105f597deec7cf5946702bd934b368e811523121d8c9dd",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": false,
      "scope_violations": [
        "progress.json"
      ],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 59.27,
        "executed_workspace_file_count": 4
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/claude-code-run-tests-only-1",
      "trial_id": "11baf63a18744e08bece86515292d0fa",
      "arm": "claude-code",
      "model": "claude-sonnet-5",
      "profile": "baseline",
      "case_id": "run-tests-only",
      "prompt_sha256": "a11ddb20a0e34ecfd24ac3a2b6cb78109208647a56803735298ae851a2f31669",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 18.59,
        "executed_workspace_file_count": 2
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/claude-code-run-tests-only-2",
      "trial_id": "208f36c2bf6147048de8cd8dc87bb9c7",
      "arm": "claude-code",
      "model": "claude-sonnet-5",
      "profile": "baseline",
      "case_id": "run-tests-only",
      "prompt_sha256": "a11ddb20a0e34ecfd24ac3a2b6cb78109208647a56803735298ae851a2f31669",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 18.101,
        "executed_workspace_file_count": 2
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/codex-cli-bounds-1",
      "trial_id": "c05608a69c624b2ab172a7b4affa8c9d",
      "arm": "codex-cli",
      "model": "gpt-5.6-terra",
      "profile": "baseline",
      "case_id": "bounds",
      "prompt_sha256": "efd7ae2a272dd72a43d7d0bfbbe48bb6d69d380263bf774ad58bd47acaa1a3ca",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 88.011,
        "executed_workspace_file_count": 2
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/codex-cli-bounds-2",
      "trial_id": "a1d5094f42294745b48381f177e5db92",
      "arm": "codex-cli",
      "model": "gpt-5.6-terra",
      "profile": "baseline",
      "case_id": "bounds",
      "prompt_sha256": "efd7ae2a272dd72a43d7d0bfbbe48bb6d69d380263bf774ad58bd47acaa1a3ca",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 78.609,
        "executed_workspace_file_count": 2
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/codex-cli-dead-code-1",
      "trial_id": "cf58eeba8f20421a8e8231325be28f16",
      "arm": "codex-cli",
      "model": "gpt-5.6-terra",
      "profile": "baseline",
      "case_id": "dead-code",
      "prompt_sha256": "1460a5165c5f30597db203fc7fd90e62c5cd8af2189795aeb510364506fe9428",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 122.129,
        "executed_workspace_file_count": 3
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/codex-cli-dead-code-2",
      "trial_id": "057e71acf3914bdab7eadca4db1cd973",
      "arm": "codex-cli",
      "model": "gpt-5.6-terra",
      "profile": "baseline",
      "case_id": "dead-code",
      "prompt_sha256": "1460a5165c5f30597db203fc7fd90e62c5cd8af2189795aeb510364506fe9428",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 122.687,
        "executed_workspace_file_count": 3
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/codex-cli-inspect-only-1",
      "trial_id": "557af482f5a0431aaa0268e1e72a6ba9",
      "arm": "codex-cli",
      "model": "gpt-5.6-terra",
      "profile": "baseline",
      "case_id": "inspect-only",
      "prompt_sha256": "61ae284a0ed9d5f5d0baa2090d8e1ddc2d57aa9c26e9466a8d341cd83addf368",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": false,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 83.537,
        "executed_workspace_file_count": 2
      },
      "grades": 1,
      "requires_human_review": true
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/codex-cli-inspect-only-2",
      "trial_id": "57ceb65faa6948b9b370ea3b2f9b8773",
      "arm": "codex-cli",
      "model": "gpt-5.6-terra",
      "profile": "baseline",
      "case_id": "inspect-only",
      "prompt_sha256": "61ae284a0ed9d5f5d0baa2090d8e1ddc2d57aa9c26e9466a8d341cd83addf368",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": false,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 81.637,
        "executed_workspace_file_count": 2
      },
      "grades": 1,
      "requires_human_review": true
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/codex-cli-merge-records-1",
      "trial_id": "5332f3e475a342e5a5f4b3d2e78deec1",
      "arm": "codex-cli",
      "model": "gpt-5.6-terra",
      "profile": "baseline",
      "case_id": "merge-records",
      "prompt_sha256": "e6fa0f8453486c3e2d163a7267bfe8205af11fa4eba216b01cea3175891c0406",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 116.295,
        "executed_workspace_file_count": 3
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/codex-cli-merge-records-2",
      "trial_id": "387d06235e6a472bbdc9c05de1ef0008",
      "arm": "codex-cli",
      "model": "gpt-5.6-terra",
      "profile": "baseline",
      "case_id": "merge-records",
      "prompt_sha256": "e6fa0f8453486c3e2d163a7267bfe8205af11fa4eba216b01cea3175891c0406",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 122.803,
        "executed_workspace_file_count": 3
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/codex-cli-refactor-pricing-1",
      "trial_id": "24722743b59d47958dde8582ae654455",
      "arm": "codex-cli",
      "model": "gpt-5.6-terra",
      "profile": "baseline",
      "case_id": "refactor-pricing",
      "prompt_sha256": "7f0a477991878d39a8682d84dad72fedd91672f587d771dbe16656844fc4deab",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 79.248,
        "executed_workspace_file_count": 3
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/codex-cli-refactor-pricing-2",
      "trial_id": "be87be2d47e3423291dfb0c66dc166d4",
      "arm": "codex-cli",
      "model": "gpt-5.6-terra",
      "profile": "baseline",
      "case_id": "refactor-pricing",
      "prompt_sha256": "7f0a477991878d39a8682d84dad72fedd91672f587d771dbe16656844fc4deab",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 95.359,
        "executed_workspace_file_count": 3
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/codex-cli-report-export-1",
      "trial_id": "2ae1f842f2814490b024d793f06ead51",
      "arm": "codex-cli",
      "model": "gpt-5.6-terra",
      "profile": "baseline",
      "case_id": "report-export",
      "prompt_sha256": "136061947d1b1a4d05c15de411b05e62d32dabd2296c2fced2048892ea976856",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 96.166,
        "executed_workspace_file_count": 4
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/codex-cli-report-export-2",
      "trial_id": "e3de28a0f07c4466a8adcaa6c691d4e4",
      "arm": "codex-cli",
      "model": "gpt-5.6-terra",
      "profile": "baseline",
      "case_id": "report-export",
      "prompt_sha256": "136061947d1b1a4d05c15de411b05e62d32dabd2296c2fced2048892ea976856",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 100.598,
        "executed_workspace_file_count": 4
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/codex-cli-resume-export-1",
      "trial_id": "85466598ccde4e0fa03d0953fc6106c1",
      "arm": "codex-cli",
      "model": "gpt-5.6-terra",
      "profile": "baseline",
      "case_id": "resume-export",
      "prompt_sha256": "cc2ec967a8409cec3e105f597deec7cf5946702bd934b368e811523121d8c9dd",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 100.158,
        "executed_workspace_file_count": 4
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/codex-cli-resume-export-2",
      "trial_id": "20e06d8d02b24f2f8b501d6997163307",
      "arm": "codex-cli",
      "model": "gpt-5.6-terra",
      "profile": "baseline",
      "case_id": "resume-export",
      "prompt_sha256": "cc2ec967a8409cec3e105f597deec7cf5946702bd934b368e811523121d8c9dd",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": false,
      "scope_violations": [
        "progress.json"
      ],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 105.608,
        "executed_workspace_file_count": 4
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/codex-cli-run-tests-only-1",
      "trial_id": "2db876bb966c4b19a28bd74642908986",
      "arm": "codex-cli",
      "model": "gpt-5.6-terra",
      "profile": "baseline",
      "case_id": "run-tests-only",
      "prompt_sha256": "a11ddb20a0e34ecfd24ac3a2b6cb78109208647a56803735298ae851a2f31669",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 36.474,
        "executed_workspace_file_count": 2
      },
      "grades": 1,
      "requires_human_review": false
    },
    {
      "trial": "/private/tmp/claude-501/-Users-songhabin-GeminiToGenius/2494908b-f2b3-4f21-ba8e-894560a67d26/scratchpad/comparison/codex-cli-run-tests-only-2",
      "trial_id": "b6081760074b4afab0c3edc9e0dc835e",
      "arm": "codex-cli",
      "model": "gpt-5.6-terra",
      "profile": "baseline",
      "case_id": "run-tests-only",
      "prompt_sha256": "a11ddb20a0e34ecfd24ac3a2b6cb78109208647a56803735298ae851a2f31669",
      "definition_digest": "40c00aba8ec6df0c82ed3bc3c2d16bc1143b5b83e26ddf441a8e1f31ac32cc69",
      "state": "graded",
      "passed": true,
      "scope_violations": [],
      "observation": {
        "status": "completed",
        "returncode": 0,
        "duration_seconds": 32.592,
        "executed_workspace_file_count": 2
      },
      "grades": 1,
      "requires_human_review": false
    }
  ],
  "labels_are_self_declared": true,
  "model_performance_claim": false,
  "note": "같은 사례·요청·채점 기준을 공유할 때만 comparable이 참입니다. 실행 하네스·모델·사용량은 사용자가 선언한 라벨이며 이 보고서가 확인하지 않습니다."
}
```
