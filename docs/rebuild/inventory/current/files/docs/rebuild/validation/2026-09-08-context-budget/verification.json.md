# `docs/rebuild/validation/2026-09-08-context-budget/verification.json`

- 형식: `100644`
- 바이트: 4262
- SHA-256: `ff146f235c30a3da4eee75669d6d7ecbb108dfcc4b12127244b3ae23ea674f23`
- 인코딩: `utf-8`

```
{
  "command": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v",
  "exit_code": 0,
  "tests": 151,
  "elapsed_seconds": 84.095,
  "source_sha256": {
    "gtg/package.py": "ab59215b746bc8ab1cce994594deabfa91c4bcfbe5a43e0ab32b7c034dc382b7",
    "gtg/store.py": "111ec87f64fd48216d2cb1086e6b8c2bccb89732b20e4081e4c88f988e35e95b",
    "gtg/sessions.py": "4e7c18e51787e21643cda76b757cb128ba5bcab658c9ac140f0f103947eee30d",
    "gtg/runner.py": "b5e95be8c5c4f6517f99727308b5309a3dae2040c1a498fab39adac7b7535731",
    "gtg/hooks.py": "fc7485a5a20d4892b21bfc0fef50cd6c64c1e976671329d73e3cb9ce6b2381b4",
    "gtg/legacy.py": "ad6f1d8a48d9a7f55e82a9988bd1576a3d73b877fd66d9b7ba6bd033bc7951a3",
    "gtg/discovery.py": "21cb02fb912c49d0fbf7fad9a331a84dcb4f3d7bc34bbfd7d6914dfb5cc14b64",
    "gtg/__init__.py": "d33dad4c6806fb8fe0743f55e39ca607ac7df4c271d75a59a9d4e02f34f896bb",
    "gtg/spec.py": "a31e4fb5edac39593958e87a8a86a4a3ae525e8c0caf813cf4b63ada0c0aaaf7",
    "gtg/checkpoints.py": "891a3ce8ee3674e82e3004aaba0c22a31440f6b7c918ab85dbf283bf3eff46a7",
    "gtg/inspection.py": "bb9761e94a74fc67c473b79ee047d22ebf096adbe57b0397d3f8a2388a57fad3",
    "gtg/context_message.py": "9a1bff312712c0de177c69490c8f927d5c35b502be5f0f090d86ad450ce8199c",
    "gtg/install.py": "b2d2609ada2584c016f8ee4a27a0834c216409ad3c2f6e7432d0114684b5d3d8",
    "gtg/install_journal.py": "1d0d0e12d548d9a9f125ae7a9d4b37e0db998d1c44d42a5e5d5232bc776b1bfb",
    "gtg/__main__.py": "6fb286f6b27db4e3f42f5662d12378c5fba219dd4ae55243b89361c91b4064d2",
    "tests/test_package_hooks.py": "2de19bd5bcd8a4bae8ecd0744af54010bf2a29ffa0a0a62d2374eaf08166614c",
    "tests/test_context_message.py": "ce4e8a342adefa5dfc519b56f5af7b7cd7811633a3445afa9103c68dfa7e08ce",
    "tests/test_multi_workspace.py": "01c24919407e6073b80061da4f575e11508e023ecfcceb0c2514e2373251ffde",
    "tests/test_catalog.py": "f2bca8e8609ecab50e8447c516dd9a708df24ec585f1e1381ba5c9b25999ea65",
    "tests/test_install_crash.py": "f5a9098a6357f52f344333b758c4cc01ce665d33a77460bf32621593f6a8aa14",
    "tests/test_checkpoints.py": "055218c2c6b3ddf7050309769e1ebc192f989cebfd31f9dee973522860a91fbb",
    "tests/test_inspection.py": "bb659339d2674ee607b9d0d713baecc1cad46a7b74f61f0d0db50b3cb45ab736",
    "tests/test_runtime.py": "a3117658eb56419bcd2a546199ccb7c7f461ebce5dfdb8503f4d1de062e86a3a",
    "tests/test_hooks.py": "ab26c62e90dd994520d041a3d0776572a4d88b0bbb78d6a5d1b8f0a41f705da3",
    "tests/test_session_start.py": "c069bd350e175bc396442eebe6810275ec36c60fb97c0669933fae779f4fbba2",
    "tests/test_eval_export.py": "304d75ff5487d3d67d57a98f17ee4986801673d49e9b74938304bebe911da760",
    "tests/test_process_lifecycle.py": "ab7bbf23c25c50dea889f833245058ab188caaf098052d7989de96c5857e903d",
    "tests/test_eval_resume.py": "4d1dd3d2b933890886c1aa7d7af4136b98e79a8b6af6c50c368f61b297213928",
    "tests/test_long_scenario.py": "ad35a2d381b5749d19e6e40c640f7237cbaf0b1b86d35d64676ac0f2428900fc",
    "tests/test_task_handoff.py": "c02bc092e9be30433aba54d06a413be6a7215a20e3b86b55a2838cf7f3deaa19",
    "tests/test_evals.py": "36e87fc8b481ee588a360a4b152ee893ee5173ccd05fc72d1cfddd046911c913",
    "tests/test_install.py": "934abb08137bc425c8f293df8b61676812009d76d48858b1714176d619bcc013",
    "tests/test_scenario.py": "a7ebbc4cd9657114235d9e8d06db0232a4800f19cc46822327f747e08006c70d",
    "tests/test_package_sources.py": "bedde0a8aee65b80547a12deeb8baac79193f87496e955a5ecbd55fc15b20cd1",
    "profile/rules/gtg.md": "37d6987d0f4e6794de6211daaf59c56fe82c8010e4ba547b236a6e4691d21665",
    "profile/skills/gtg-research/SKILL.md": "79cf34d6a09722eb1ffe4bb93d4aaf1aa381c5327c1c64ecbe797564af8b3fde",
    "profile/skills/gtg-build/SKILL.md": "9f945c242a1b533d083486f95f1add26d5e13b5c88dd27d2cd038c05b1843d9c",
    "profile/skills/gtg-interface/SKILL.md": "25e5280544be9d88925de469cc9590588122466f3ea7ded62cf0bb8e59f12102",
    "profile/skills/gtg-build/references/code-intake.md": "8840325030a4fd4c0db0664a5457eeb168e1902a42bbe705e21ad71f98dd7478",
    "profile/skills/gtg-build/references/task-contract.md": "5564393c336d809431b32bc1a4414b79fcf1ab7a400c391c6cda6688b21862d0"
  },
  "log_sha256": "1da481407c92c0708a3369fa867aabd43249515b51de4e22c2f7b34504bf71cb",
  "additional_model_prompts": 0
}
```
