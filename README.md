# GeminiToGenius

[![License: MIT](https://img.shields.io/github/license/habinsong/GeminiToGenius?style=flat-square)](LICENSE)
[![Latest release](https://img.shields.io/github/v/release/habinsong/GeminiToGenius?display_name=tag&sort=semver&style=flat-square)](https://github.com/habinsong/GeminiToGenius/releases)

> Gemini kept getting dumber in real work. This puts it on rails.

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

Requirements: macOS, `git`, `python3`, and `rsync`.

After `Installed agy-focus v...` appears, restart Antigravity or Antigravity IDE.

## What gets installed

| Item | Current |
| --- | --- |
| Model target | Gemini 3.6 Flash (High) |
| Always-on rules | 12 |
| Lifecycle hooks | 13 |
| Automatic skills | 8 |
| Plugins | none |
| MCP | only for an explicit connection task |

The profile routes ordinary language. No slash command or @mention is required.

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
"hooks": 13
hook runner tests passed
```

## Change versions

The installer always returns to the current profile. Switch only when you need to reproduce an older behavior.

```bash
find "$HOME/.gemini/config/agy-focus/versions" \
  -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort -V

ln -sfn versions/v1.12.0 "$HOME/.gemini/config/agy-focus/current"
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
```

Run `bash scripts/install.sh` later to return to the latest profile.

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

## UI rules

- no vague AI copy, empty future-talk, wand icons, fake metrics, or decorative 3D art
- no purple-blue default gradients, repeated round-card grids, or animation without a job
- build from the real task, existing system, hierarchy, and accessibility
- read safe workspace text files before changing code; a search result or a few lines is not a full read

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
