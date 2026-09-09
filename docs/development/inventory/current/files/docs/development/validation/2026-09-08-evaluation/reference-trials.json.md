# `docs/development/validation/2026-09-08-evaluation/reference-trials.json`

- 형식: `100644`
- 바이트: 25000
- SHA-256: `dec81a68fc15d60aa489f74fde37c8551cab3ef1e422ebbf8b217fb032879254`
- 인코딩: `utf-8`

```
{
  "kind": "reference_validation",
  "additional_model_prompts": 0,
  "trials": [
    {
      "profile": "baseline",
      "model_called": false,
      "initial_user_diff": "diff --git a/app.py b/app.py\nindex 89225b6..bb8f197 100644\n--- a/app.py\n+++ b/app.py\n@@ -1,7 +1,7 @@\n from exports import to_json\n \n \n-DOWNLOAD_STEM = \"records\"\n+DOWNLOAD_STEM = \"현장 기록\"\n \n \n def download(records, format=\"json\"):\n",
      "initial_git_state": {
        "index": "dd358a28340c0dad771bf8107eda150b4eeec85cd8954f5c191a96a550523d19",
        "head": null
      },
      "reference_changes": [
        "app.py",
        "exports.py"
      ],
      "before": {
        "artifact_passed": false,
        "functional_passed": false,
        "scope_passed": true,
        "git_state_unchanged": true,
        "checks": [
          {
            "index": 0,
            "passed": false,
            "group": 1
          },
          {
            "index": 1,
            "passed": false,
            "group": 1
          },
          {
            "index": 2,
            "passed": true,
            "group": 1
          },
          {
            "index": 3,
            "passed": true,
            "group": 1
          },
          {
            "index": 4,
            "passed": true,
            "group": 1
          }
        ],
        "execution": {
          "groups": [
            {
              "module": "exports.py",
              "function": "to_csv",
              "error": "candidate_process_failed",
              "returncode": 1
            },
            {
              "module": "app.py",
              "function": "download",
              "returncode": 0
            }
          ],
          "error": "candidate_process_failed"
        },
        "model_performance_claim": false,
        "prompt_sha256": "136061947d1b1a4d05c15de411b05e62d32dabd2296c2fced2048892ea976856",
        "definition_digest": "1248e4837893652c13fec2a4d13163a25973ce4071f9bd8947c2b79869f39620",
        "candidate_files": {
          "exports.py": "3bb0d265067a84d71eefe4328e0c4f61d00381c13362454ba4dd6942ab280e6d",
          "notes.txt": "ea68fead1ada7abdfb8c2993617c96e6cd889aed964043ad179de964ef0d6837",
          "README.md": "e1e674e74505814c9cdefb19557e0ecdcaff534c6be9f02c65f6d3f3b98e24bc",
          "app.py": "bae4db1bef12b45a2c5d3bf3da720c6614ee336941889f3132b2d58a587edad3",
          "test_app.py": "525cae662a4a5b5ce52c103e826dde4b0eb6f5808bf1afebea5a17a73eb832a5"
        },
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
        }
      },
      "helper_only": {
        "artifact_passed": false,
        "functional_passed": false,
        "scope_passed": true,
        "git_state_unchanged": true,
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
            "index": 0,
            "passed": false,
            "group": 1
          },
          {
            "index": 1,
            "passed": false,
            "group": 1
          },
          {
            "index": 2,
            "passed": true,
            "group": 1
          },
          {
            "index": 3,
            "passed": true,
            "group": 1
          },
          {
            "index": 4,
            "passed": true,
            "group": 1
          }
        ],
        "execution": {
          "groups": [
            {
              "module": "exports.py",
              "function": "to_csv",
              "returncode": 0
            },
            {
              "module": "app.py",
              "function": "download",
              "returncode": 0
            }
          ]
        },
        "model_performance_claim": false,
        "prompt_sha256": "136061947d1b1a4d05c15de411b05e62d32dabd2296c2fced2048892ea976856",
        "definition_digest": "1248e4837893652c13fec2a4d13163a25973ce4071f9bd8947c2b79869f39620",
        "candidate_files": {
          "exports.py": "4c57125d9eb672d2129ccc403245a128f42f32c74897d8ff89276b93e723d04f",
          "notes.txt": "ea68fead1ada7abdfb8c2993617c96e6cd889aed964043ad179de964ef0d6837",
          "README.md": "e1e674e74505814c9cdefb19557e0ecdcaff534c6be9f02c65f6d3f3b98e24bc",
          "app.py": "bae4db1bef12b45a2c5d3bf3da720c6614ee336941889f3132b2d58a587edad3",
          "test_app.py": "525cae662a4a5b5ce52c103e826dde4b0eb6f5808bf1afebea5a17a73eb832a5"
        },
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
        }
      },
      "after": {
        "artifact_passed": true,
        "functional_passed": true,
        "scope_passed": true,
        "git_state_unchanged": true,
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
            "index": 0,
            "passed": true,
            "group": 1
          },
          {
            "index": 1,
            "passed": true,
            "group": 1
          },
          {
            "index": 2,
            "passed": true,
            "group": 1
          },
          {
            "index": 3,
            "passed": true,
            "group": 1
          },
          {
            "index": 4,
            "passed": true,
            "group": 1
          }
        ],
        "execution": {
          "groups": [
            {
              "module": "exports.py",
              "function": "to_csv",
              "returncode": 0
            },
            {
              "module": "app.py",
              "function": "download",
              "returncode": 0
            }
          ]
        },
        "model_performance_claim": false,
        "prompt_sha256": "136061947d1b1a4d05c15de411b05e62d32dabd2296c2fced2048892ea976856",
        "definition_digest": "1248e4837893652c13fec2a4d13163a25973ce4071f9bd8947c2b79869f39620",
        "candidate_files": {
          "exports.py": "4c57125d9eb672d2129ccc403245a128f42f32c74897d8ff89276b93e723d04f",
          "notes.txt": "ea68fead1ada7abdfb8c2993617c96e6cd889aed964043ad179de964ef0d6837",
          "README.md": "e1e674e74505814c9cdefb19557e0ecdcaff534c6be9f02c65f6d3f3b98e24bc",
          "app.py": "ea16d3aea0716289ff938b4445aa9473d6b65ab229e8097d55713df7345609da",
          "test_app.py": "525cae662a4a5b5ce52c103e826dde4b0eb6f5808bf1afebea5a17a73eb832a5"
        },
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
        }
      }
    },
    {
      "profile": "gtg",
      "model_called": false,
      "initial_user_diff": "diff --git a/app.py b/app.py\nindex 89225b6..bb8f197 100644\n--- a/app.py\n+++ b/app.py\n@@ -1,7 +1,7 @@\n from exports import to_json\n \n \n-DOWNLOAD_STEM = \"records\"\n+DOWNLOAD_STEM = \"현장 기록\"\n \n \n def download(records, format=\"json\"):\n",
      "initial_git_state": {
        "index": "dd358a28340c0dad771bf8107eda150b4eeec85cd8954f5c191a96a550523d19",
        "head": null
      },
      "reference_changes": [
        "app.py",
        "exports.py"
      ],
      "before": {
        "artifact_passed": false,
        "functional_passed": false,
        "scope_passed": true,
        "git_state_unchanged": true,
        "checks": [
          {
            "index": 0,
            "passed": false,
            "group": 1
          },
          {
            "index": 1,
            "passed": false,
            "group": 1
          },
          {
            "index": 2,
            "passed": true,
            "group": 1
          },
          {
            "index": 3,
            "passed": true,
            "group": 1
          },
          {
            "index": 4,
            "passed": true,
            "group": 1
          }
        ],
        "execution": {
          "groups": [
            {
              "module": "exports.py",
              "function": "to_csv",
              "error": "candidate_process_failed",
              "returncode": 1
            },
            {
              "module": "app.py",
              "function": "download",
              "returncode": 0
            }
          ],
          "error": "candidate_process_failed"
        },
        "model_performance_claim": false,
        "prompt_sha256": "136061947d1b1a4d05c15de411b05e62d32dabd2296c2fced2048892ea976856",
        "definition_digest": "1248e4837893652c13fec2a4d13163a25973ce4071f9bd8947c2b79869f39620",
        "candidate_files": {
          "exports.py": "3bb0d265067a84d71eefe4328e0c4f61d00381c13362454ba4dd6942ab280e6d",
          "notes.txt": "ea68fead1ada7abdfb8c2993617c96e6cd889aed964043ad179de964ef0d6837",
          "README.md": "e1e674e74505814c9cdefb19557e0ecdcaff534c6be9f02c65f6d3f3b98e24bc",
          "app.py": "bae4db1bef12b45a2c5d3bf3da720c6614ee336941889f3132b2d58a587edad3",
          "test_app.py": "525cae662a4a5b5ce52c103e826dde4b0eb6f5808bf1afebea5a17a73eb832a5",
          ".agents/plugins/geminitogenius/run.py": "df6f8577c5c1d224cf6d20b21f301baeea5b508ad6c3f87385d41a0175cf9a83",
          ".agents/plugins/geminitogenius/plugin.json": "c68b170acdb7edf356e51cda5163c97f6183488cc766fe5fbdf586da732b066a",
          ".agents/plugins/geminitogenius/gtg-manifest.json": "c2de573880137c006aaa1a8d266907f5031c5a5c60a5adcf051741ed36f4d5fc",
          ".agents/plugins/geminitogenius/hooks.json": "a6cc564c96721322b770319635eee890bc9085bedc4a4c308e32aa01d96e3e61",
          ".agents/plugins/geminitogenius/gtg/package.py": "ab59215b746bc8ab1cce994594deabfa91c4bcfbe5a43e0ab32b7c034dc382b7",
          ".agents/plugins/geminitogenius/gtg/store.py": "d820a97f760acd5b89f5fc84f1ac29a0738ab10592db8400c695f5e3ea8f233e",
          ".agents/plugins/geminitogenius/gtg/sessions.py": "35006a1f18f848d797c83080719c4373ba555015f25c1b4eb9c791bd7dfb7662",
          ".agents/plugins/geminitogenius/gtg/runner.py": "ce81a9d5c9813e240b25a8ca93d6b02f1efec4fc3e75552c78c6252939d24267",
          ".agents/plugins/geminitogenius/gtg/hooks.py": "7239ad9294cc1edfbc8b60c17e85bf9aac94c61700911fb6374af6a4b60c8f83",
          ".agents/plugins/geminitogenius/gtg/legacy.py": "ad6f1d8a48d9a7f55e82a9988bd1576a3d73b877fd66d9b7ba6bd033bc7951a3",
          ".agents/plugins/geminitogenius/gtg/__init__.py": "d33dad4c6806fb8fe0743f55e39ca607ac7df4c271d75a59a9d4e02f34f896bb",
          ".agents/plugins/geminitogenius/gtg/spec.py": "a31e4fb5edac39593958e87a8a86a4a3ae525e8c0caf813cf4b63ada0c0aaaf7",
          ".agents/plugins/geminitogenius/gtg/checkpoints.py": "891a3ce8ee3674e82e3004aaba0c22a31440f6b7c918ab85dbf283bf3eff46a7",
          ".agents/plugins/geminitogenius/gtg/inspection.py": "bb9761e94a74fc67c473b79ee047d22ebf096adbe57b0397d3f8a2388a57fad3",
          ".agents/plugins/geminitogenius/gtg/install.py": "b2d2609ada2584c016f8ee4a27a0834c216409ad3c2f6e7432d0114684b5d3d8",
          ".agents/plugins/geminitogenius/gtg/install_journal.py": "1d0d0e12d548d9a9f125ae7a9d4b37e0db998d1c44d42a5e5d5232bc776b1bfb",
          ".agents/plugins/geminitogenius/gtg/__main__.py": "f875c8971392777e24616b876370971827f44cd5f8c3eb837e1de172f1bebefb",
          ".agents/plugins/geminitogenius/rules/AGENTS.md": "37d6987d0f4e6794de6211daaf59c56fe82c8010e4ba547b236a6e4691d21665",
          ".agents/plugins/geminitogenius/skills/gtg-research/SKILL.md": "79cf34d6a09722eb1ffe4bb93d4aaf1aa381c5327c1c64ecbe797564af8b3fde",
          ".agents/plugins/geminitogenius/skills/gtg-build/SKILL.md": "43b09a1329064e61f75fb724a7779bbebad3ae17abacc580abb1cedd47a2d8c8",
          ".agents/plugins/geminitogenius/skills/gtg-build/references/code-intake.md": "8840325030a4fd4c0db0664a5457eeb168e1902a42bbe705e21ad71f98dd7478",
          ".agents/plugins/geminitogenius/skills/gtg-build/references/task-contract.md": "4bb1eb405fe8b6131486982aa19218110d96e4e84ab5f863101f605cbc1150e4",
          ".agents/plugins/geminitogenius/skills/gtg-interface/SKILL.md": "25e5280544be9d88925de469cc9590588122466f3ea7ded62cf0bb8e59f12102"
        },
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
        }
      },
      "helper_only": {
        "artifact_passed": false,
        "functional_passed": false,
        "scope_passed": true,
        "git_state_unchanged": true,
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
            "index": 0,
            "passed": false,
            "group": 1
          },
          {
            "index": 1,
            "passed": false,
            "group": 1
          },
          {
            "index": 2,
            "passed": true,
            "group": 1
          },
          {
            "index": 3,
            "passed": true,
            "group": 1
          },
          {
            "index": 4,
            "passed": true,
            "group": 1
          }
        ],
        "execution": {
          "groups": [
            {
              "module": "exports.py",
              "function": "to_csv",
              "returncode": 0
            },
            {
              "module": "app.py",
              "function": "download",
              "returncode": 0
            }
          ]
        },
        "model_performance_claim": false,
        "prompt_sha256": "136061947d1b1a4d05c15de411b05e62d32dabd2296c2fced2048892ea976856",
        "definition_digest": "1248e4837893652c13fec2a4d13163a25973ce4071f9bd8947c2b79869f39620",
        "candidate_files": {
          "exports.py": "4c57125d9eb672d2129ccc403245a128f42f32c74897d8ff89276b93e723d04f",
          "notes.txt": "ea68fead1ada7abdfb8c2993617c96e6cd889aed964043ad179de964ef0d6837",
          "README.md": "e1e674e74505814c9cdefb19557e0ecdcaff534c6be9f02c65f6d3f3b98e24bc",
          "app.py": "bae4db1bef12b45a2c5d3bf3da720c6614ee336941889f3132b2d58a587edad3",
          "test_app.py": "525cae662a4a5b5ce52c103e826dde4b0eb6f5808bf1afebea5a17a73eb832a5",
          ".agents/plugins/geminitogenius/run.py": "df6f8577c5c1d224cf6d20b21f301baeea5b508ad6c3f87385d41a0175cf9a83",
          ".agents/plugins/geminitogenius/plugin.json": "c68b170acdb7edf356e51cda5163c97f6183488cc766fe5fbdf586da732b066a",
          ".agents/plugins/geminitogenius/gtg-manifest.json": "c2de573880137c006aaa1a8d266907f5031c5a5c60a5adcf051741ed36f4d5fc",
          ".agents/plugins/geminitogenius/hooks.json": "a6cc564c96721322b770319635eee890bc9085bedc4a4c308e32aa01d96e3e61",
          ".agents/plugins/geminitogenius/gtg/package.py": "ab59215b746bc8ab1cce994594deabfa91c4bcfbe5a43e0ab32b7c034dc382b7",
          ".agents/plugins/geminitogenius/gtg/store.py": "d820a97f760acd5b89f5fc84f1ac29a0738ab10592db8400c695f5e3ea8f233e",
          ".agents/plugins/geminitogenius/gtg/sessions.py": "35006a1f18f848d797c83080719c4373ba555015f25c1b4eb9c791bd7dfb7662",
          ".agents/plugins/geminitogenius/gtg/runner.py": "ce81a9d5c9813e240b25a8ca93d6b02f1efec4fc3e75552c78c6252939d24267",
          ".agents/plugins/geminitogenius/gtg/hooks.py": "7239ad9294cc1edfbc8b60c17e85bf9aac94c61700911fb6374af6a4b60c8f83",
          ".agents/plugins/geminitogenius/gtg/legacy.py": "ad6f1d8a48d9a7f55e82a9988bd1576a3d73b877fd66d9b7ba6bd033bc7951a3",
          ".agents/plugins/geminitogenius/gtg/__init__.py": "d33dad4c6806fb8fe0743f55e39ca607ac7df4c271d75a59a9d4e02f34f896bb",
          ".agents/plugins/geminitogenius/gtg/spec.py": "a31e4fb5edac39593958e87a8a86a4a3ae525e8c0caf813cf4b63ada0c0aaaf7",
          ".agents/plugins/geminitogenius/gtg/checkpoints.py": "891a3ce8ee3674e82e3004aaba0c22a31440f6b7c918ab85dbf283bf3eff46a7",
          ".agents/plugins/geminitogenius/gtg/inspection.py": "bb9761e94a74fc67c473b79ee047d22ebf096adbe57b0397d3f8a2388a57fad3",
          ".agents/plugins/geminitogenius/gtg/install.py": "b2d2609ada2584c016f8ee4a27a0834c216409ad3c2f6e7432d0114684b5d3d8",
          ".agents/plugins/geminitogenius/gtg/install_journal.py": "1d0d0e12d548d9a9f125ae7a9d4b37e0db998d1c44d42a5e5d5232bc776b1bfb",
          ".agents/plugins/geminitogenius/gtg/__main__.py": "f875c8971392777e24616b876370971827f44cd5f8c3eb837e1de172f1bebefb",
          ".agents/plugins/geminitogenius/rules/AGENTS.md": "37d6987d0f4e6794de6211daaf59c56fe82c8010e4ba547b236a6e4691d21665",
          ".agents/plugins/geminitogenius/skills/gtg-research/SKILL.md": "79cf34d6a09722eb1ffe4bb93d4aaf1aa381c5327c1c64ecbe797564af8b3fde",
          ".agents/plugins/geminitogenius/skills/gtg-build/SKILL.md": "43b09a1329064e61f75fb724a7779bbebad3ae17abacc580abb1cedd47a2d8c8",
          ".agents/plugins/geminitogenius/skills/gtg-build/references/code-intake.md": "8840325030a4fd4c0db0664a5457eeb168e1902a42bbe705e21ad71f98dd7478",
          ".agents/plugins/geminitogenius/skills/gtg-build/references/task-contract.md": "4bb1eb405fe8b6131486982aa19218110d96e4e84ab5f863101f605cbc1150e4",
          ".agents/plugins/geminitogenius/skills/gtg-interface/SKILL.md": "25e5280544be9d88925de469cc9590588122466f3ea7ded62cf0bb8e59f12102"
        },
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
        }
      },
      "after": {
        "artifact_passed": true,
        "functional_passed": true,
        "scope_passed": true,
        "git_state_unchanged": true,
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
            "index": 0,
            "passed": true,
            "group": 1
          },
          {
            "index": 1,
            "passed": true,
            "group": 1
          },
          {
            "index": 2,
            "passed": true,
            "group": 1
          },
          {
            "index": 3,
            "passed": true,
            "group": 1
          },
          {
            "index": 4,
            "passed": true,
            "group": 1
          }
        ],
        "execution": {
          "groups": [
            {
              "module": "exports.py",
              "function": "to_csv",
              "returncode": 0
            },
            {
              "module": "app.py",
              "function": "download",
              "returncode": 0
            }
          ]
        },
        "model_performance_claim": false,
        "prompt_sha256": "136061947d1b1a4d05c15de411b05e62d32dabd2296c2fced2048892ea976856",
        "definition_digest": "1248e4837893652c13fec2a4d13163a25973ce4071f9bd8947c2b79869f39620",
        "candidate_files": {
          "exports.py": "4c57125d9eb672d2129ccc403245a128f42f32c74897d8ff89276b93e723d04f",
          "notes.txt": "ea68fead1ada7abdfb8c2993617c96e6cd889aed964043ad179de964ef0d6837",
          "README.md": "e1e674e74505814c9cdefb19557e0ecdcaff534c6be9f02c65f6d3f3b98e24bc",
          "app.py": "ea16d3aea0716289ff938b4445aa9473d6b65ab229e8097d55713df7345609da",
          "test_app.py": "525cae662a4a5b5ce52c103e826dde4b0eb6f5808bf1afebea5a17a73eb832a5",
          ".agents/plugins/geminitogenius/run.py": "df6f8577c5c1d224cf6d20b21f301baeea5b508ad6c3f87385d41a0175cf9a83",
          ".agents/plugins/geminitogenius/plugin.json": "c68b170acdb7edf356e51cda5163c97f6183488cc766fe5fbdf586da732b066a",
          ".agents/plugins/geminitogenius/gtg-manifest.json": "c2de573880137c006aaa1a8d266907f5031c5a5c60a5adcf051741ed36f4d5fc",
          ".agents/plugins/geminitogenius/hooks.json": "a6cc564c96721322b770319635eee890bc9085bedc4a4c308e32aa01d96e3e61",
          ".agents/plugins/geminitogenius/gtg/package.py": "ab59215b746bc8ab1cce994594deabfa91c4bcfbe5a43e0ab32b7c034dc382b7",
          ".agents/plugins/geminitogenius/gtg/store.py": "d820a97f760acd5b89f5fc84f1ac29a0738ab10592db8400c695f5e3ea8f233e",
          ".agents/plugins/geminitogenius/gtg/sessions.py": "35006a1f18f848d797c83080719c4373ba555015f25c1b4eb9c791bd7dfb7662",
          ".agents/plugins/geminitogenius/gtg/runner.py": "ce81a9d5c9813e240b25a8ca93d6b02f1efec4fc3e75552c78c6252939d24267",
          ".agents/plugins/geminitogenius/gtg/hooks.py": "7239ad9294cc1edfbc8b60c17e85bf9aac94c61700911fb6374af6a4b60c8f83",
          ".agents/plugins/geminitogenius/gtg/legacy.py": "ad6f1d8a48d9a7f55e82a9988bd1576a3d73b877fd66d9b7ba6bd033bc7951a3",
          ".agents/plugins/geminitogenius/gtg/__init__.py": "d33dad4c6806fb8fe0743f55e39ca607ac7df4c271d75a59a9d4e02f34f896bb",
          ".agents/plugins/geminitogenius/gtg/spec.py": "a31e4fb5edac39593958e87a8a86a4a3ae525e8c0caf813cf4b63ada0c0aaaf7",
          ".agents/plugins/geminitogenius/gtg/checkpoints.py": "891a3ce8ee3674e82e3004aaba0c22a31440f6b7c918ab85dbf283bf3eff46a7",
          ".agents/plugins/geminitogenius/gtg/inspection.py": "bb9761e94a74fc67c473b79ee047d22ebf096adbe57b0397d3f8a2388a57fad3",
          ".agents/plugins/geminitogenius/gtg/install.py": "b2d2609ada2584c016f8ee4a27a0834c216409ad3c2f6e7432d0114684b5d3d8",
          ".agents/plugins/geminitogenius/gtg/install_journal.py": "1d0d0e12d548d9a9f125ae7a9d4b37e0db998d1c44d42a5e5d5232bc776b1bfb",
          ".agents/plugins/geminitogenius/gtg/__main__.py": "f875c8971392777e24616b876370971827f44cd5f8c3eb837e1de172f1bebefb",
          ".agents/plugins/geminitogenius/rules/AGENTS.md": "37d6987d0f4e6794de6211daaf59c56fe82c8010e4ba547b236a6e4691d21665",
          ".agents/plugins/geminitogenius/skills/gtg-research/SKILL.md": "79cf34d6a09722eb1ffe4bb93d4aaf1aa381c5327c1c64ecbe797564af8b3fde",
          ".agents/plugins/geminitogenius/skills/gtg-build/SKILL.md": "43b09a1329064e61f75fb724a7779bbebad3ae17abacc580abb1cedd47a2d8c8",
          ".agents/plugins/geminitogenius/skills/gtg-build/references/code-intake.md": "8840325030a4fd4c0db0664a5457eeb168e1902a42bbe705e21ad71f98dd7478",
          ".agents/plugins/geminitogenius/skills/gtg-build/references/task-contract.md": "4bb1eb405fe8b6131486982aa19218110d96e4e84ab5f863101f605cbc1150e4",
          ".agents/plugins/geminitogenius/skills/gtg-interface/SKILL.md": "25e5280544be9d88925de469cc9590588122466f3ea7ded62cf0bb8e59f12102"
        },
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
        }
      }
    }
  ]
}
```
