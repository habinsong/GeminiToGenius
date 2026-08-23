# GeminiToGenius

[![License: MIT](https://img.shields.io/github/license/habinsong/GeminiToGenius?style=flat-square)](LICENSE)
[![Latest release](https://img.shields.io/github/v/release/habinsong/GeminiToGenius?display_name=tag&sort=semver&style=flat-square)](https://github.com/habinsong/GeminiToGenius/releases)

> A harness to make Gemini less dumb.

[English](README.md) · [한국어](docs/README.ko.md) · [日本語](docs/README.ja.md) · [简体中文](docs/README.zh-CN.md)

Versioned global rules, hooks, and skills for Gemini 3.7 Flash (High) in Antigravity and Antigravity IDE.

## First install

macOS. Run one command:

```bash
git clone https://github.com/habinsong/GeminiToGenius.git && bash GeminiToGenius/scripts/install.sh
```

The script does this in order:

1. updates the clone with `git pull --ff-only`
2. moves the installed Gemini profile into a dated backup folder
3. installs the current profile (v2.12.0)
4. runs the profile and hook checks

It does not use `curl | sh`. The checkout is on disk before anything runs.

Requirements: macOS, `git`, `python3`, and `rsync`. `/GTG` UI checks also need Google Chrome or Chromium already installed.

After `Installed agy-focus v2.12.0` appears, restart Antigravity or Antigravity IDE.

## What gets installed

| Item | Current (v2.12.0) |
| --- | --- |
| Model target | Gemini 3.7 Flash (High) Hybrid Reasoning |
| Global Engineering Rules | 22 complete rules (GEMINI.md 100% mapped) |
| Architecture Guardrail | 500-Line Limit Rule (500 LOC max per file) |
| Debugging Pipeline | 7-step debugging & 4-field blocker reporting |
| UI/UX Design System | Windows 11 & WinUI 3 Fluent Design System 2.0 |
| Lifecycle hooks | 14 |
| Focused skills | 11 |
| Plugins | none |
| MCP | only for an explicit connection task |

Ordinary requests route automatically. Start strict repository or UI work with `/GTG`.

```text
/GTG Build a webpage explaining "habinsong/GeminiToGenius"
```

`/GTG` keeps the strict contract active for the whole request: prompt repeat-back, source before docs, complete file reads, 500-line architecture limits, surgical minimum changes, browser renders at 320 px, 768 px, and desktop width, and post-write verification.

## Why `GEMINI.md` stays global

- Antigravity loads `~/.gemini/GEMINI.md` as a [global rule](https://antigravity.google/docs/ide/rules).
- The v2.12.0 entrypoint establishes 22 comprehensive engineering standards: prompt repeat-back, single-responsibility boundaries, 500-line limits, 7-step debugging, and strict verification gates.
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
"skills": 11
hook runner tests passed
```

## Change versions

Use the installer for both current and historical profiles. It keeps the same update → backup → install → verify order.

```bash
bash scripts/install.sh --version v2.12.0
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

- **Zero AI Slop**: no vague AI marketing copy, wand icons, fake metrics, or decorative 3D art.
- **Windows 11 & WinUI 3 Fluent System**: authentic Mica/Acrylic surfaces, Settings Cards, ToggleSwitches, and Windows Terminal.
- **500-Line Limit Rule**: no single source file may exceed 500 lines without modular SRP decomposition.
- **Full View Reads**: complete 1-to-N file reads required; partial snippets and hallucination are strictly forbidden.
- **Chrome Visual Measurements**: bundled `verify_ui_render.py` validates 320px, 768px, and 1280px viewports with zero horizontal overflow.
- **5-Field Standard Reports**: final turn reports structured as Summary, Changed Files, Commands Executed, Verification Results, and Remaining Risks.

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
