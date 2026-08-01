# Contributing

Thanks for taking the project seriously.

## Before opening an issue

- Read the relevant section of the README.
- Include the profile version, model target, app name, and exact reproduction steps.
- Remove tokens, private paths, private prompts, and screenshots with personal data.
- Use Discussions for ideas and usage questions.

## Before opening a pull request

- Keep the change inside the requested scope.
- Preserve the versioned profile structure.
- Regenerate `GEMINI.md` when rule files change.
- Run `python3 agy-focus/versions/v1.14.1/scripts/verify_profile.py` with the profile linked under `~/.gemini`.
- Keep README translations in sync when user-facing behavior changes.

## Pull request checklist

- [ ] The change is explained in the PR body.
- [ ] No secrets or private local paths are included.
- [ ] The relevant profile verification passed.
- [ ] Documentation matches the installed behavior.
