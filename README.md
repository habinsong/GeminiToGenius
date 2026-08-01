# GeminiToGenius

[![License: MIT](https://img.shields.io/github/license/habinsong/GeminiToGenius?style=flat-square)](LICENSE)
[![Latest release](https://img.shields.io/github/v/release/habinsong/GeminiToGenius?display_name=tag&sort=semver&style=flat-square)](https://github.com/habinsong/GeminiToGenius/releases)
[![GitHub stars](https://img.shields.io/github/stars/habinsong/GeminiToGenius?style=flat-square)](https://github.com/habinsong/GeminiToGenius/stargazers)

> A versioned focus harness for Gemini 3.6 Flash (High) in Antigravity and Antigravity IDE.

[English](README.md) · [한국어](docs/README.ko.md) · [日本語](docs/README.ja.md) · [简体中文](docs/README.zh-CN.md)

GeminiToGenius keeps the model on the current instruction, active window, relevant files, and verifiable result.

It is a prompt-first operating harness:

- 12 always-on instruction files
- 8 lifecycle hooks
- 4 focused skills
- versioned profiles from `v1.0.0` to `v1.13.0`
- no external plugins
- MCP only when the task requires an MCP connection

## Why this exists

Long always-on instructions get clipped or diluted. This project splits the rules into short files, generates one entrypoint, and keeps every change versioned.

The goal is simple: less drift, fewer side quests, and a smaller instruction surface for Gemini to follow.

## Compatibility

| Target | Supported profile |
| --- | --- |
| Antigravity | `2.4.x` |
| Antigravity IDE | `2.1.x` |
| Model target | `Gemini 3.6 Flash (High)` |

## Install

macOS instructions. The commands preserve the existing Gemini setup before replacing it.

### 1. Clone

```bash
git clone https://github.com/habinsong/GeminiToGenius.git
cd GeminiToGenius
```

### 2. Update the clone

After a fresh clone, the checkout is already current. Run this when reusing an existing clone.

```bash
cd GeminiToGenius
git pull --ff-only
```

### 3. Back up the current profile

Run this immediately before installing the profile.

```bash
BACKUP_DIR="$HOME/.gemini-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR" "$HOME/.gemini/config"

if [ -e "$HOME/.gemini/config/agy-focus" ] || [ -L "$HOME/.gemini/config/agy-focus" ]; then
  mv "$HOME/.gemini/config/agy-focus" "$BACKUP_DIR/agy-focus"
fi

if [ -e "$HOME/.gemini/GEMINI.md" ] || [ -L "$HOME/.gemini/GEMINI.md" ]; then
  mv "$HOME/.gemini/GEMINI.md" "$BACKUP_DIR/GEMINI.md"
fi

if [ -e "$HOME/.gemini/config/hooks.json" ] || [ -L "$HOME/.gemini/config/hooks.json" ]; then
  mv "$HOME/.gemini/config/hooks.json" "$BACKUP_DIR/hooks.json"
fi

if [ -e "$HOME/.gemini/config/skills" ] || [ -L "$HOME/.gemini/config/skills" ]; then
  mv "$HOME/.gemini/config/skills" "$BACKUP_DIR/skills"
fi

printf '%s\n' "$BACKUP_DIR"
```

Keep the printed path. It is the restore point.

### 4. Install the profile

```bash
cp -a agy-focus "$HOME/.gemini/config/agy-focus"

ln -sfn versions/v1.13.0 \
  "$HOME/.gemini/config/agy-focus/current"
ln -sfn config/agy-focus/current/GEMINI.md \
  "$HOME/.gemini/GEMINI.md"
ln -sfn agy-focus/current/hooks/hooks.json \
  "$HOME/.gemini/config/hooks.json"
ln -sfn agy-focus/current/skills \
  "$HOME/.gemini/config/skills"
```

### 5. Verify

```bash
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
```

Expected values:

```text
"ok": true
"rules": 12
"hooks": 8
"target": "Gemini 3.6 Flash (High)"
```

Restart Antigravity or Antigravity IDE after installation.

## Update

```bash
cd GeminiToGenius
git pull --ff-only
```

Then run steps 3–5 again. The backup must happen before the profile is replaced.

## Switch versions

List the versions installed by the profile:

```bash
find "$HOME/.gemini/config/agy-focus/versions" \
  -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort -V
```

Switch to a version, then verify it:

```bash
ln -sfn versions/v1.12.0 \
  "$HOME/.gemini/config/agy-focus/current"
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
```

## Remove and restore

The removal block moves the installed profile to a dated folder first.

```bash
REMOVED_DIR="$HOME/.gemini-removed-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$REMOVED_DIR"

if [ -L "$HOME/.gemini/GEMINI.md" ]; then
  unlink "$HOME/.gemini/GEMINI.md"
fi
if [ -L "$HOME/.gemini/config/hooks.json" ]; then
  unlink "$HOME/.gemini/config/hooks.json"
fi
if [ -L "$HOME/.gemini/config/skills" ]; then
  unlink "$HOME/.gemini/config/skills"
fi
if [ -d "$HOME/.gemini/config/agy-focus" ]; then
  mv "$HOME/.gemini/config/agy-focus" "$REMOVED_DIR/agy-focus"
fi

printf '%s\n' "$REMOVED_DIR"
```

Delete that dated folder only after checking the printed path:

```bash
rm -rf "$REMOVED_DIR"
```

To restore the pre-install setup:

```bash
BACKUP_DIR="$HOME/.gemini-backup-YYYYMMDD-HHMMSS"
mv "$BACKUP_DIR/agy-focus" "$HOME/.gemini/config/agy-focus"
mv "$BACKUP_DIR/GEMINI.md" "$HOME/.gemini/GEMINI.md"
mv "$BACKUP_DIR/hooks.json" "$HOME/.gemini/config/hooks.json"
mv "$BACKUP_DIR/skills" "$HOME/.gemini/config/skills"
```

## Repository layout

- `agy-focus/versions/` — versioned rules, hooks, skills, manifests, and changelogs
- `agy-focus/current` — symlink to the active profile version
- `agy-focus/state/` — public runtime snapshot with the local workspace path removed
- `installed/` — copy of the current global installation
- `legacy/` — preserved legacy entrypoint
- `.github/` — issue forms, pull request template, security, support, and CI files

Generated runtime files such as `__pycache__`, `*.pyc`, and `.DS_Store` are excluded.

## UI guardrails

The active profile also carries anti-slop rules for interface work:

- no vague AI copy, abstract wand icons, or decorative 3D art
- no purposeless hover effects or empty micro-interactions
- no repeated rounded-card grids or mechanical symmetry
- no default `Inter`/`Roboto` treatment by habit
- no purple-to-blue neon gradients as a default solution
- review intrinsic sizing, fluid type, asymmetric layout, and mobile-first behavior

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening an issue or pull request. Use Discussions for ideas and usage questions. Do not paste tokens, private paths, or private prompts into public issues.

## License

MIT. See [LICENSE](LICENSE).
