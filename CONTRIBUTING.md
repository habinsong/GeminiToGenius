# Contributing

Keep changes small and keep the install path honest.

## Before opening an issue

- Run `bash scripts/install.sh` in a clean checkout, or include why that was not possible.
- Include the profile version, model, app, command output, and shortest reproduction.
- Remove tokens, private prompts, private paths, and screenshots with personal data.

## Before opening a pull request

- Preserve old profiles. Add a version only when profile behavior changes.
- Regenerate `GEMINI.md` when current rule files change.
- Keep the first-install command, installer behavior, backup paths, and translations in sync.
- Run these checks:

```bash
bash -n scripts/install.sh
python3 agy-focus/current/scripts/test_hook_runner.py
AGY_INSTALL_HOME="$(mktemp -d)" bash scripts/install.sh --skip-update
```

Use `AGY_INSTALL_HOME`, not `HOME`, when testing the installer without changing your real Gemini profile.

## Pull request checklist

- [ ] The change has a concrete user-facing reason.
- [ ] No secrets, private paths, or private prompts are included.
- [ ] Profile and hook checks passed.
- [ ] Installation and restore instructions match the script.
