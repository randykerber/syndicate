#!/bin/bash
# Backup script for migrating hedgeye-kb from idlewood to rstudio
# Run this on idlewood to create a transfer bundle

set -e

PROJECT_DIR="$HOME/gh/randykerber/hedgeye-kb"
BACKUP_DIR="$HOME/Desktop/hedgeye-kb-migration-$(date +%Y%m%d-%H%M%S)"
CURSOR_USER_DIR="$HOME/Library/Application Support/Cursor/User"
CURSOR_HOME_DIR="$HOME/.cursor"

echo "Creating migration backup..."
mkdir -p "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR/cursor"
mkdir -p "$BACKUP_DIR/project"

# Project files (not in git)
echo "Backing up project files..."
[ -f "$PROJECT_DIR/.env" ] && cp "$PROJECT_DIR/.env" "$BACKUP_DIR/project/" && echo "  ✓ .env"
[ -f "$PROJECT_DIR/.envrc" ] && cp "$PROJECT_DIR/.envrc" "$BACKUP_DIR/project/" && echo "  ✓ .envrc"
[ -f "$PROJECT_DIR/.python-version" ] && cp "$PROJECT_DIR/.python-version" "$BACKUP_DIR/project/" && echo "  ✓ .python-version"

# Cursor settings
echo "Backing up Cursor settings..."
[ -f "$CURSOR_USER_DIR/settings.json" ] && cp "$CURSOR_USER_DIR/settings.json" "$BACKUP_DIR/cursor/settings.json" && echo "  ✓ settings.json"
[ -f "$CURSOR_HOME_DIR/mcp.json" ] && cp "$CURSOR_HOME_DIR/mcp.json" "$BACKUP_DIR/cursor/mcp.json" && echo "  ✓ mcp.json"

# Create a manifest
cat > "$BACKUP_DIR/MANIFEST.txt" << EOF
Hedgeye KB Migration Backup
Created: $(date)
Source: idlewood
Destination: rstudio

Files included:
$(ls -laR "$BACKUP_DIR" | grep -v "^$" | grep -v "^d")

Restoration instructions:
1. Copy project files from project/ to /Users/rk/gh/randykerber/hedgeye-kb/
2. Copy cursor settings to appropriate locations on rstudio
3. See docs/MIGRATE_TO_RSTUDIO.md for full instructions
EOF

echo ""
echo "✓ Backup created: $BACKUP_DIR"
echo ""
echo "Contents:"
ls -la "$BACKUP_DIR"
echo ""
echo "Next steps:"
echo "1. Review the files in $BACKUP_DIR"
echo "2. Transfer to rstudio (USB drive, cloud storage, etc.)"
echo "3. Follow restoration instructions in docs/MIGRATE_TO_RSTUDIO.md"


