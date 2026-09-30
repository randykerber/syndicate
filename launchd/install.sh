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
  # the plists name rstudio's uv (/opt/homebrew/bin); substitute this machine's
  UV="$(command -v uv)"
  sed "s#/opt/homebrew/bin/uv#$UV#" "$plist" > "$AGENTS/$label.plist"
  launchctl bootstrap "gui/$UID_" "$AGENTS/$label.plist"
  echo "installed $label"
done
