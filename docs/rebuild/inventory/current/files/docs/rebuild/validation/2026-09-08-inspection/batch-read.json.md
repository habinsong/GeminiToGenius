# `docs/rebuild/validation/2026-09-08-inspection/batch-read.json`

- 형식: `100644`
- 바이트: 1270
- SHA-256: `66214c3fc06677d73e9a0c68e3270b9b3d5b6d3bc10a4e9a07583667c7b55321`
- 인코딩: `utf-8`

```
{
  "kind": "offline_batch_read_check",
  "fixture": "evals/fixtures/merge-records",
  "initial_native_file_reads": 5,
  "batch_cli_invocations": 1,
  "files": [
    {
      "path": "records.py",
      "complete": true,
      "range_complete": true,
      "file_sha256": "4a81a71f72cc545f1d0e0408a3f144ffb6cb0629346388b6cb8cc22a83c14a9d"
    },
    {
      "path": "test_records.py",
      "complete": true,
      "range_complete": true,
      "file_sha256": "74fbc53df867e6b252feba5d35de30663a622dd7d6ca5c42d5170d97e52aa27b"
    },
    {
      "path": "app.py",
      "complete": true,
      "range_complete": true,
      "file_sha256": "b3cda19c426317b623565a34d3c52beb90778d9145f15b32caca7980118588ca"
    },
    {
      "path": "notes.txt",
      "complete": true,
      "range_complete": true,
      "file_sha256": "f829a4827d6f66fbac0bc683c5d19f91c601337ff6404fb77ee119f1d57d8ec8"
    },
    {
      "path": "README.md",
      "complete": true,
      "range_complete": true,
      "file_sha256": "eab6071254e4867ec4327540cfb1afd255c63d367ef44c37252d5655e811fed0"
    }
  ],
  "content_bytes": 1125,
  "serialized_bytes": 3460,
  "identical_to_source_bytes": true,
  "cli_elapsed_seconds": 0.175887,
  "model_called": false,
  "actual_model_call_reduction": null
}
```
