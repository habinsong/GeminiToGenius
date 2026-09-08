# `.github/PULL_REQUEST_TEMPLATE.md`

- 형식: `100644`
- 바이트: 603
- SHA-256: `1a72c7ccce36b13c87a358a3e2e9215ec4682ea709df3c3e291929994d1208e2`
- 인코딩: `utf-8`

```
## What changed

<!-- State the user-visible change in a few lines. -->

## Why

<!-- Link the issue or explain the problem. -->

## Verification

- [ ] `python3 agy-focus/current/scripts/verify_profile.py` passed
- [ ] `python3 agy-focus/current/scripts/test_hook_runner.py` passed
- [ ] `bash scripts/install.sh --skip-update` passed in a disposable `HOME` when the installer changed
- [ ] First-install and translated README files match the installer when installation changed
- [ ] No secrets, private paths, or private prompts included

## Notes

<!-- Include compatibility or migration notes. -->
```
