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
requested_version=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --skip-update)
      skip_update=true
      shift
      ;;
    --version)
      [ "$#" -ge 2 ] || fail "--version requires a value such as v2.0.0"
      requested_version="$2"
      shift 2
      ;;
    -h|--help)
      printf '%s\n' 'usage: bash scripts/install.sh [--skip-update] [--version vX.Y.Z]'
      exit 0
      ;;
    *)
      fail "usage: bash scripts/install.sh [--skip-update] [--version vX.Y.Z]"
      ;;
  esac
done

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
repo_root="$(CDPATH= cd -- "$script_dir/.." && pwd -P)"
user_home="${AGY_INSTALL_HOME:-${HOME:?HOME is required}}"
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

selected_link="$(readlink "$repo_root/agy-focus/current")" || fail "cannot read agy-focus/current"
case "$selected_link" in
  versions/*) ;;
  *) fail "agy-focus/current must point inside versions/" ;;
esac
if [ -n "$requested_version" ]; then
  [[ "$requested_version" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] || fail "version must look like v2.0.0"
  selected_link="versions/$requested_version"
  [ -d "$repo_root/agy-focus/$selected_link" ] || fail "profile version not found: $requested_version"
fi
profile_version="$(tr -d '\n' < "$repo_root/agy-focus/$selected_link/VERSION")"
[ -n "$profile_version" ] || fail "selected profile version is empty"
[ "v$profile_version" = "${selected_link#versions/}" ] || fail "selected profile VERSION does not match its directory"

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
if [ -d "$profile_root/versions" ]; then
  find "$profile_root/versions" -mindepth 1 -maxdepth 1 ! -name "v$profile_version" -exec rm -rf {} +
fi
ln -sfn "$selected_link" "$profile_root/current"
ln -sfn config/agy-focus/current/GEMINI.md "$gemini_home/GEMINI.md"
ln -sfn agy-focus/current/hooks/hooks.json "$config_root/hooks.json"
ln -sfn agy-focus/current/skills "$config_root/skills"

printf '%s\n' 'Verifying installation...'
AGY_INSTALL_HOME="$user_home" PYTHONDONTWRITEBYTECODE=1 python3 "$profile_root/current/scripts/verify_profile.py"

printf '\nInstalled agy-focus v%s\nBackup: %s\nRestart Antigravity or Antigravity IDE.\n' "$profile_version" "$backup_dir"
