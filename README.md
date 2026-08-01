# GeminiToGenius

[![License: MIT](https://img.shields.io/github/license/habinsong/GeminiToGenius?style=flat-square)](LICENSE)
[![Latest release](https://img.shields.io/github/v/release/habinsong/GeminiToGenius?display_name=tag&sort=semver&style=flat-square)](https://github.com/habinsong/GeminiToGenius/releases)

> A harness to make Gemini less dumb.

[English](README.md) · [한국어](docs/README.ko.md) · [日本語](docs/README.ja.md) · [简体中文](docs/README.zh-CN.md)

Versioned global rules, hooks, and skills for Gemini 3.6 Flash (High) in Antigravity and Antigravity IDE.

## First install

macOS. Run one command:

```bash
git clone https://github.com/habinsong/GeminiToGenius.git && bash GeminiToGenius/scripts/install.sh
```

The script does this in order:

1. updates the clone with `git pull --ff-only`
2. moves the installed Gemini profile into a dated backup folder
3. installs the current profile
4. runs the profile and hook checks

It does not use `curl | sh`. The checkout is on disk before anything runs.

Requirements: macOS, `git`, `python3`, and `rsync`. `/GTG` UI checks also need Google Chrome or Chromium already installed.

After `Installed agy-focus v...` appears, restart Antigravity or Antigravity IDE.

## What gets installed

| Item | Current |
| --- | --- |
| Model target | Gemini 3.6 Flash (High) |
| Always-on rules | 12 |
| Lifecycle hooks | 14 |
| Focused skills | 10 |
| Plugins | none |
| MCP | only for an explicit connection task |

Ordinary requests route automatically. Start strict repository or UI work with `/GTG`.

```text
/GTG "habinsong/GeminiToGenius" 를 설명하는 웹페이지 만들어줘
```

`/GTG` keeps the strict contract active for the whole request: source before docs, complete file reads, first-party repository evidence, pre-write UI gates, browser renders at 320 px and desktop width, and post-write verification.

## Why `GEMINI.md` stays global

- Antigravity loads `~/.gemini/GEMINI.md` as a [global rule](https://antigravity.google/docs/ide/rules).
- The v2.0.0 entrypoint is 4,127 characters: routing, safety, evidence, and completion gates only.
- Detailed code, architecture, UI, copy, and research procedures load as [focused skills](https://antigravity.google/docs/skills?app=antigravity-ide).
- [Hooks](https://antigravity.google/docs/hooks) enforce high-risk boundaries without adding the whole procedure to every prompt.
- Unrelated repository history and task-specific documents are not injected by default.

## Existing users

From an older clone, run the same script:

```bash
cd /path/to/GeminiToGenius
bash scripts/install.sh
```

It updates the checkout first, so an old installed profile moves to the current profile automatically. If the clone has tracked edits, the script stops before `git pull`; commit, stash, or discard those edits first.

Each run prints a restore point such as:

```text
/Users/you/.gemini-backup-YYYYMMDD-HHMMSS
```

## Verify an installation

```bash
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
python3 "$HOME/.gemini/config/agy-focus/current/scripts/test_hook_runner.py"
```

Expected markers:

```text
"ok": true
"rules": 12
"hooks": 14
hook runner tests passed
```

## Change versions

Use the installer for both current and historical profiles. It keeps the same update → backup → install → verify order.

```bash
bash scripts/install.sh --version v2.0.0
bash scripts/install.sh --help
```

Run `bash scripts/install.sh` to return to the latest profile.

## Remove

This removes the links and moves the profile into a dated folder. It does not delete the folder.

```bash
REMOVED_DIR="$HOME/.gemini-removed-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$REMOVED_DIR/config"

if [ -L "$HOME/.gemini/GEMINI.md" ]; then unlink "$HOME/.gemini/GEMINI.md"; fi
if [ -L "$HOME/.gemini/config/hooks.json" ]; then unlink "$HOME/.gemini/config/hooks.json"; fi
if [ -L "$HOME/.gemini/config/skills" ]; then unlink "$HOME/.gemini/config/skills"; fi
if [ -e "$HOME/.gemini/config/agy-focus" ] || [ -L "$HOME/.gemini/config/agy-focus" ]; then
  mv "$HOME/.gemini/config/agy-focus" "$REMOVED_DIR/config/agy-focus"
fi

printf '%s\n' "$REMOVED_DIR"
```

Delete that printed folder only after checking it:

```bash
rm -rf "$REMOVED_DIR"
```

## Restore a backup

Replace the placeholder with the path printed by the installer.

```bash
BACKUP_DIR="$HOME/.gemini-backup-YYYYMMDD-HHMMSS"
mv "$BACKUP_DIR/config/agy-focus" "$HOME/.gemini/config/agy-focus"
mv "$BACKUP_DIR/GEMINI.md" "$HOME/.gemini/GEMINI.md"
mv "$BACKUP_DIR/config/hooks.json" "$HOME/.gemini/config/hooks.json"
mv "$BACKUP_DIR/config/skills" "$HOME/.gemini/config/skills"
```

## UI and implementation rules

- no vague AI copy, empty future-talk, wand icons, fake metrics, fake dashboards, or decorative 3D art
- no purple-blue default gradients, glass glow, nested round-card grids, identical spacing/radii, or animation without a job
- use the real product, user task, data, states, hierarchy, existing design system, and accessibility as evidence
- start mobile-first, preserve 320 CSS px reflow, visible focus, reduced motion, and measured performance claims
- run the bundled `verify_ui_render.py`; it uses installed Chrome to fail on 320px horizontal clipping and writes mobile and desktop screenshots without installing Playwright
- map the repository, then read the affected source, call path, state/data path, and tests in full; README and search snippets are not implementation evidence
- when describing another GitHub repository, read its README/overview and a separate install script, manifest, or source file directly; search summaries do not count
- keep UI state, domain decisions, I/O, persistence, and external processes out of one God Object

## Layout

- `agy-focus/versions/` — versioned profiles
- `agy-focus/current` — current profile link
- `scripts/install.sh` — update, backup, install, verify
- `installed/` — checked copy of the current installed surfaces

## Help and contribution

- [Support](SUPPORT.md)
- [Security](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

MIT. See [LICENSE](LICENSE).
