#!/bin/bash
# Restoration script for hedgeye-kb on rstudio
# Run this on rstudio after transferring the backup

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup-directory>"
    echo "Example: $0 ~/Desktop/hedgeye-kb-migration-20250115-120000"
    exit 1
fi

BACKUP_DIR="$1"
PROJECT_DIR="$HOME/gh/randykerber/hedgeye-kb"
CURSOR_USER_DIR="$HOME/Library/Application Support/Cursor/User"
CURSOR_HOME_DIR="$HOME/.cursor"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "Error: Backup directory not found: $BACKUP_DIR"
    exit 1
fi

echo "Restoring hedgeye-kb configuration on rstudio..."
echo "Backup source: $BACKUP_DIR"
echo ""

# Restore project files
echo "Restoring project files..."
[ -f "$BACKUP_DIR/project/.env" ] && cp "$BACKUP_DIR/project/.env" "$PROJECT_DIR/.env" && echo "  ✓ .env"
[ -f "$BACKUP_DIR/project/.envrc" ] && cp "$BACKUP_DIR/project/.envrc" "$PROJECT_DIR/.envrc" && echo "  ✓ .envrc"
[ -f "$BACKUP_DIR/project/.python-version" ] && cp "$BACKUP_DIR/project/.python-version" "$PROJECT_DIR/.python-version" && echo "  ✓ .python-version"

# Restore Cursor settings
echo "Restoring Cursor settings..."
mkdir -p "$CURSOR_USER_DIR"
[ -f "$BACKUP_DIR/cursor/settings.json" ] && cp "$BACKUP_DIR/cursor/settings.json" "$CURSOR_USER_DIR/settings.json" && echo "  ✓ settings.json"

mkdir -p "$CURSOR_HOME_DIR"
[ -f "$BACKUP_DIR/cursor/mcp.json" ] && cp "$BACKUP_DIR/cursor/mcp.json" "$CURSOR_HOME_DIR/mcp.json" && echo "  ✓ mcp.json"

echo ""
echo "✓ Restoration complete!"
echo ""
echo "Next steps:"
echo "1. Verify Cursor settings are correct (especially Warp terminal path)"
echo "2. Update MCP server URLs if needed (in ~/.cursor/mcp.json)"
echo "3. Test the project: cd $PROJECT_DIR && python scripts/run_full_pipeline.py"
echo "4. Open project in Cursor and verify AGENTS.md is recognized"


