#!/bin/zsh
# Install / reinstall the syndicate launchd jobs for this user. Hand-run.
#   ./install.sh            install all plists in this folder
#   ./install.sh --remove   unload and delete them
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
AGENTS="$HOME/Library/LaunchAgents"
UID_="$(id -u)"
for plist in "$DIR"/com.rk.*.plist; do
  label="$(basename "$plist" .plist)"
  launchctl bootout "gui/$UID_/$label" 2>/dev/null || true
  if [[ "$1" == "--remove" ]]; then
    rm -f "$AGENTS/$label.plist"; echo "removed $label"; continue
  fi
  cp "$plist" "$AGENTS/$label.plist"   # plists call the project venv python; no per-machine path
  launchctl bootstrap "gui/$UID_" "$AGENTS/$label.plist"
  echo "installed $label"
done
