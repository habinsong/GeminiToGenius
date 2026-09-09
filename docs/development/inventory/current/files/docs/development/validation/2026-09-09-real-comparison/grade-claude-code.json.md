# `docs/development/validation/2026-09-09-real-comparison/grade-claude-code.json`

- 형식: `100644`
- 바이트: 2097
- SHA-256: `61e52a9ec827d3be0cd36091e086dd3c2a36ddba3d9924e3bbf74d5ce7fd3d1f`
- 인코딩: `utf-8`

```
{
  "kind": "artifact_grade",
  "trial_id": "664f948f6b8f41dd80c24d98cb14ff71",
  "case_id": "bounds",
  "definition_digest": "1c38d3f94ebe436166b465fc7ca323428c0b1fe5a7fdb64f5e50987edfc94717",
  "candidate_files": {
    "notes.txt": "e9551430733b70654a9b5109759f3b4f57840039267a634147426d2a1bd11053",
    "mathlib.py": "2ed45c162e80ffa23c5c359aef6e9a83fda522c9ae6b02ae326e7614c21d789a",
    "test_mathlib.py": "ae41c1165f77d10d6042d5e464c7a6621ad6a2bad4cb593dde8e613ace7fa235",
    "README.md": "c8d7a361ed4fa845f83b4f4293ab40e8950e57fba66cb22957212927a8167655"
  },
  "prompt_sha256": "efd7ae2a272dd72a43d7d0bfbbe48bb6d69d380263bf774ad58bd47acaa1a3ca",
  "profile": "baseline",
  "checked_at": "2026-09-08T15:52:34.150751+00:00",
  "artifact_passed": true,
  "scope_passed": true,
  "functional_passed": true,
  "requires_human_review": false,
  "changed_paths": [
    "mathlib.py",
    "test_mathlib.py"
  ],
  "scope_violations": [],
  "grading_changed_paths": [],
  "git_state_unchanged": null,
  "observed_git_state": null,
  "grading_environment": {
    "python_version": "3.14.6",
    "system": "Darwin",
    "machine": "arm64",
    "host_logical_cpus": 8,
    "per_group_timeout_seconds": 5,
    "stdout_read_limit_bytes": 131072,
    "candidate_bytecode_cache": "fresh_per_group",
    "bytecode_writes": false,
    "cpu_limit_enforced": false,
    "memory_limit_enforced": false,
    "os_sandbox": false
  },
  "oracle_unchanged": true,
  "checks": [
    {
      "index": 0,
      "passed": true,
      "group": 0
    },
    {
      "index": 1,
      "passed": true,
      "group": 0
    },
    {
      "index": 2,
      "passed": true,
      "group": 0
    },
    {
      "index": 3,
      "passed": true,
      "group": 0
    },
    {
      "index": 4,
      "passed": true,
      "group": 0
    },
    {
      "index": 5,
      "passed": true,
      "group": 0
    }
  ],
  "execution": {
    "groups": [
      {
        "module": "mathlib.py",
        "function": "clamp",
        "returncode": 0
      }
    ]
  },
  "model_performance_claim": false,
  "runtime_observation": null
}
```
