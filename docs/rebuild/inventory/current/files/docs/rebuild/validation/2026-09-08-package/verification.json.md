# `docs/rebuild/validation/2026-09-08-package/verification.json`

- 형식: `100644`
- 바이트: 5129
- SHA-256: `b48678a7580cda960ec8dc1c2a9b3f4442851490027e4ed4075ab7d9257989ea`
- 인코딩: `utf-8`

```
{
  "command": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v",
  "exit_code": 0,
  "tests": 111,
  "elapsed_seconds": 28.27,
  "additional_model_prompts": 0,
  "log_sha256": "645c53b169d6cff7f261d93aa67acc515a103343fb4025f34e500a5fb76c65bb",
  "source_sha256": {
    "evals/README.md": "746a2b3f2d92e9fe9800b2a701a980e2bae8ea150e232768e2722ffcd75be9d5",
    "evals/__init__.py": "23e43df2038bd9d3adc1496512d11db1310d10498411f9dce957fe8f28e3e1d0",
    "evals/cases.json": "aac833c12183f12c23f4a58e088713130cfc9ce599be1902dfe05256e41a015d",
    "evals/fixtures/bounds/README.md": "c8d7a361ed4fa845f83b4f4293ab40e8950e57fba66cb22957212927a8167655",
    "evals/fixtures/bounds/mathlib.py": "3a2fe2662497265d0d17d57f08b5d298448f010215baab3f9a93ae442fee296c",
    "evals/fixtures/bounds/notes.txt": "e9551430733b70654a9b5109759f3b4f57840039267a634147426d2a1bd11053",
    "evals/fixtures/bounds/test_mathlib.py": "80ec21f265da49a2efbd25efea1ab54fad017d7ddd9856745101fcbb6e63f5c6",
    "evals/fixtures/merge-records/README.md": "eab6071254e4867ec4327540cfb1afd255c63d367ef44c37252d5655e811fed0",
    "evals/fixtures/merge-records/app.py": "b3cda19c426317b623565a34d3c52beb90778d9145f15b32caca7980118588ca",
    "evals/fixtures/merge-records/notes.txt": "f829a4827d6f66fbac0bc683c5d19f91c601337ff6404fb77ee119f1d57d8ec8",
    "evals/fixtures/merge-records/records.py": "4a81a71f72cc545f1d0e0408a3f144ffb6cb0629346388b6cb8cc22a83c14a9d",
    "evals/fixtures/merge-records/test_records.py": "74fbc53df867e6b252feba5d35de30663a622dd7d6ca5c42d5170d97e52aa27b",
    "evals/harness.py": "005dbcb68ea29282b1bfd95338ce5c768e39c76868dae8e74e8d9d58cd41a05f",
    "evals/probe.py": "0c124848ea6df51f4ac97ce7d545767ce338aa6b9f9e3c35d61141070396f71b",
    "gtg/__init__.py": "d33dad4c6806fb8fe0743f55e39ca607ac7df4c271d75a59a9d4e02f34f896bb",
    "gtg/__main__.py": "f875c8971392777e24616b876370971827f44cd5f8c3eb837e1de172f1bebefb",
    "gtg/checkpoints.py": "891a3ce8ee3674e82e3004aaba0c22a31440f6b7c918ab85dbf283bf3eff46a7",
    "gtg/hooks.py": "7239ad9294cc1edfbc8b60c17e85bf9aac94c61700911fb6374af6a4b60c8f83",
    "gtg/inspection.py": "bb9761e94a74fc67c473b79ee047d22ebf096adbe57b0397d3f8a2388a57fad3",
    "gtg/install.py": "b2d2609ada2584c016f8ee4a27a0834c216409ad3c2f6e7432d0114684b5d3d8",
    "gtg/install_journal.py": "1d0d0e12d548d9a9f125ae7a9d4b37e0db998d1c44d42a5e5d5232bc776b1bfb",
    "gtg/legacy.py": "ad6f1d8a48d9a7f55e82a9988bd1576a3d73b877fd66d9b7ba6bd033bc7951a3",
    "gtg/package.py": "ab59215b746bc8ab1cce994594deabfa91c4bcfbe5a43e0ab32b7c034dc382b7",
    "gtg/runner.py": "ce81a9d5c9813e240b25a8ca93d6b02f1efec4fc3e75552c78c6252939d24267",
    "gtg/sessions.py": "35006a1f18f848d797c83080719c4373ba555015f25c1b4eb9c791bd7dfb7662",
    "gtg/spec.py": "a31e4fb5edac39593958e87a8a86a4a3ae525e8c0caf813cf4b63ada0c0aaaf7",
    "gtg/store.py": "d820a97f760acd5b89f5fc84f1ac29a0738ab10592db8400c695f5e3ea8f233e",
    "profile/rules/gtg.md": "37d6987d0f4e6794de6211daaf59c56fe82c8010e4ba547b236a6e4691d21665",
    "profile/skills/gtg-build/SKILL.md": "43b09a1329064e61f75fb724a7779bbebad3ae17abacc580abb1cedd47a2d8c8",
    "profile/skills/gtg-build/references/code-intake.md": "8840325030a4fd4c0db0664a5457eeb168e1902a42bbe705e21ad71f98dd7478",
    "profile/skills/gtg-build/references/task-contract.md": "4bb1eb405fe8b6131486982aa19218110d96e4e84ab5f863101f605cbc1150e4",
    "profile/skills/gtg-interface/SKILL.md": "25e5280544be9d88925de469cc9590588122466f3ea7ded62cf0bb8e59f12102",
    "profile/skills/gtg-research/SKILL.md": "79cf34d6a09722eb1ffe4bb93d4aaf1aa381c5327c1c64ecbe797564af8b3fde",
    "tests/test_catalog.py": "f2bca8e8609ecab50e8447c516dd9a708df24ec585f1e1381ba5c9b25999ea65",
    "tests/test_checkpoints.py": "055218c2c6b3ddf7050309769e1ebc192f989cebfd31f9dee973522860a91fbb",
    "tests/test_evals.py": "eeb19ce1bd0af99e6424e4b799783f4c30d146211d0726570ba477938321fb51",
    "tests/test_hooks.py": "3c34150c2059ba06e244ad021b49265062ca767daa868803fb2a95d5d2cb7d73",
    "tests/test_inspection.py": "bb659339d2674ee607b9d0d713baecc1cad46a7b74f61f0d0db50b3cb45ab736",
    "tests/test_install.py": "934abb08137bc425c8f293df8b61676812009d76d48858b1714176d619bcc013",
    "tests/test_install_crash.py": "f5a9098a6357f52f344333b758c4cc01ce665d33a77460bf32621593f6a8aa14",
    "tests/test_long_scenario.py": "ad35a2d381b5749d19e6e40c640f7237cbaf0b1b86d35d64676ac0f2428900fc",
    "tests/test_multi_workspace.py": "01c24919407e6073b80061da4f575e11508e023ecfcceb0c2514e2373251ffde",
    "tests/test_package_hooks.py": "2de19bd5bcd8a4bae8ecd0744af54010bf2a29ffa0a0a62d2374eaf08166614c",
    "tests/test_package_sources.py": "bedde0a8aee65b80547a12deeb8baac79193f87496e955a5ecbd55fc15b20cd1",
    "tests/test_process_lifecycle.py": "ab7bbf23c25c50dea889f833245058ab188caaf098052d7989de96c5857e903d",
    "tests/test_runtime.py": "a3117658eb56419bcd2a546199ccb7c7f461ebce5dfdb8503f4d1de062e86a3a",
    "tests/test_scenario.py": "a7ebbc4cd9657114235d9e8d06db0232a4800f19cc46822327f747e08006c70d",
    "tests/test_session_start.py": "c069bd350e175bc396442eebe6810275ec36c60fb97c0669933fae779f4fbba2"
  }
}
```
