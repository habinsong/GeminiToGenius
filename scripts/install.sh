#!/usr/bin/env bash
# Update this checkout, back up the installed profile, install the current profile, then verify it.

set -euo pipefail

fail() {
  printf 'install failed: %s\n' "$*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "missing command: $1"
}

backup_item() {
  local source_path="$1"
  local backup_path="$2"
  if [ -e "$source_path" ] || [ -L "$source_path" ]; then
    mv "$source_path" "$backup_path"
  fi
}

require_command git
require_command python3
require_command rsync

skip_update=false
case "${1:-}" in
  "") ;;
  --skip-update) skip_update=true ;;
  *) fail "usage: bash scripts/install.sh [--skip-update]" ;;
esac

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
repo_root="$(CDPATH= cd -- "$script_dir/.." && pwd -P)"
user_home="${HOME:?HOME is required}"
gemini_home="$user_home/.gemini"
config_root="$gemini_home/config"
profile_root="$config_root/agy-focus"

git -C "$repo_root" rev-parse --is-inside-work-tree >/dev/null 2>&1 || fail "run this from a Git checkout"
if [ "$skip_update" = false ]; then
  if [ -n "$(git -C "$repo_root" status --porcelain --untracked-files=no)" ]; then
    fail "checkout has tracked changes; commit, stash, or discard them before updating"
  fi
  printf '%s\n' 'Updating checkout...'
  git -C "$repo_root" pull --ff-only
else
  printf '%s\n' 'Skipping checkout update...'
fi

current_link="$(readlink "$repo_root/agy-focus/current")" || fail "cannot read agy-focus/current"
case "$current_link" in
  versions/*) ;;
  *) fail "agy-focus/current must point inside versions/" ;;
esac
profile_version="$(tr -d '\n' < "$repo_root/agy-focus/$current_link/VERSION")"
[ -n "$profile_version" ] || fail "current profile version is empty"

backup_dir="$user_home/.gemini-backup-$(date +%Y%m%d-%H%M%S)"
if [ -e "$backup_dir" ]; then
  backup_dir="${backup_dir}-1"
fi

printf '%s\n' 'Backing up installed Gemini profile...'
mkdir -p "$backup_dir/config" "$config_root"
backup_item "$gemini_home/GEMINI.md" "$backup_dir/GEMINI.md"
backup_item "$profile_root" "$backup_dir/config/agy-focus"
backup_item "$config_root/hooks.json" "$backup_dir/config/hooks.json"
backup_item "$config_root/skills" "$backup_dir/config/skills"

printf 'Installing agy-focus v%s...\n' "$profile_version"
mkdir -p "$profile_root"
rsync -a --exclude '__pycache__/' --exclude '*.pyc' "$repo_root/agy-focus/" "$profile_root/"
ln -sfn "$current_link" "$profile_root/current"
ln -sfn config/agy-focus/current/GEMINI.md "$gemini_home/GEMINI.md"
ln -sfn agy-focus/current/hooks/hooks.json "$config_root/hooks.json"
ln -sfn agy-focus/current/skills "$config_root/skills"

printf '%s\n' 'Verifying installation...'
PYTHONDONTWRITEBYTECODE=1 python3 "$profile_root/current/scripts/verify_profile.py"
PYTHONDONTWRITEBYTECODE=1 python3 "$profile_root/current/scripts/test_hook_runner.py"

printf '\nInstalled agy-focus v%s\nBackup: %s\nRestart Antigravity or Antigravity IDE.\n' "$profile_version" "$backup_dir"
