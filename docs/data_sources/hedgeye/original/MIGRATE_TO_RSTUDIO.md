# Migration Guide: idlewood → rstudio (Mac Studio M4 Max)

**Date:** November 2025  
**Source:** idlewood (2019 MacBook Pro, Intel)  
**Destination:** rstudio (2025 Mac Studio M4 Max)  
**Project:** hedgeye-kb

## Overview

This guide outlines what files and settings need to be transferred from idlewood to rstudio to enable seamless development of the hedgeye-kb project in Cursor.

## Files to Transfer

### 1. Project Files (via Git) ✓

These files should be committed to git on idlewood and pulled on rstudio:

- **`AGENTS.md`** - Cursor project instructions (NEW, not yet committed)
- **`.cursorignore`** - Files to exclude from Cursor context (NEW, not yet committed)
- **`docs/CURSOR_CONFIG.md`** - Cursor configuration documentation (NEW, not yet committed)

**Action Required:**
```bash
# On idlewood:
cd /Users/rk/gh/randykerber/hedgeye-kb
git add AGENTS.md .cursorignore docs/CURSOR_CONFIG.md
git commit -m "Add Cursor 2.0 configuration files"
git push

# On rstudio:
cd /Users/rk/gh/randykerber/hedgeye-kb
git pull
```

### 2. Project Files (Manual Copy - Not in Git)

These files are excluded from git but needed for local development:

#### Environment Files
- **`.env`** - Environment variables (sensitive, excluded from git)
- **`.envrc`** - direnv configuration (excluded from git)
- **`.python-version`** - Python version specification (if exists)

**Action Required:**
```bash
# On idlewood - copy to a secure location (USB drive, password manager, etc.)
cp /Users/rk/gh/randykerber/hedgeye-kb/.env ~/Desktop/hedgeye-kb-env-backup
cp /Users/rk/gh/randykerber/hedgeye-kb/.envrc ~/Desktop/hedgeye-kb-envrc-backup
cp /Users/rk/gh/randykerber/hedgeye-kb/.python-version ~/Desktop/hedgeye-kb-python-version

# On rstudio - restore from backup location
cp ~/path/to/backup/hedgeye-kb-env-backup /Users/rk/gh/randykerber/hedgeye-kb/.env
cp ~/path/to/backup/hedgeye-kb-envrc-backup /Users/rk/gh/randykerber/hedgeye-kb/.envrc
cp ~/path/to/backup/hedgeye-kb-python-version /Users/rk/gh/randykerber/hedgeye-kb/.python-version
```

### 3. Cursor Global Settings

#### User Settings
- **Location:** `~/Library/Application Support/Cursor/User/settings.json`
- **Contains:** Editor preferences, terminal settings, GitHub Copilot settings

**Current settings on idlewood:**
- Terminal: Uses Warp.app
- GitHub Copilot: Disabled for most file types
- Git autofetch: Enabled
- Markdown preview breaks: Enabled

**Action Required:**
```bash
# On idlewood - export settings
cp ~/Library/Application\ Support/Cursor/User/settings.json ~/Desktop/cursor-settings-backup.json

# On rstudio - import settings (after Cursor is installed)
cp ~/Desktop/cursor-settings-backup.json ~/Library/Application\ Support/Cursor/User/settings.json
```

**Note:** You may want to review and update these settings, especially:
- Verify Warp.app path exists on rstudio
- Check if any paths are Intel-specific

#### MCP Configuration
- **Location:** `~/.cursor/mcp.json`
- **Contains:** MCP server configurations

**Action Required:**
```bash
# On idlewood - export MCP config (if it exists)
[ -f ~/.cursor/mcp.json ] && cp ~/.cursor/mcp.json ~/Desktop/cursor-mcp-backup.json

# On rstudio - import MCP config (if needed)
mkdir -p ~/.cursor
[ -f ~/Desktop/cursor-mcp-backup.json ] && cp ~/Desktop/cursor-mcp-backup.json ~/.cursor/mcp.json
```

**Important Considerations:**
- MCP servers might need to be reconfigured for the new machine
- Update any localhost URLs if MCP servers are running locally
- Verify all MCP server endpoints are accessible on rstudio

### 4. Project-Specific Cursor Settings (If Any)

Check if there are any workspace-specific settings:
- **Location:** `~/Library/Application Support/Cursor/User/workspaceStorage/`
- These are workspace-specific and usually auto-generated, but may contain useful preferences

**Action Required:**
- Generally not needed to transfer - Cursor will recreate these
- If you have specific workspace settings, note them down and recreate manually

### 5. Other Tool Configurations

#### Claude Code (if still using)
- **Directory:** `.claude/` (in project)
- **Status:** Already in git (if committed) or can be manually copied
- **Note:** These files are for Claude Code, not Cursor, but may be useful for reference

#### PyCharm/IntelliJ IDEA
- **Directory:** `.idea/` (in project)
- **Status:** Usually in `.gitignore`, but project structure may be needed
- **Action:** Not critical for Cursor, but can be copied if you use PyCharm on rstudio

## Platform-Specific Considerations

### Intel (idlewood) → Apple Silicon (rstudio)

1. **Python/uv Installation:**
   - Python 3.13+ is required
   - `uv` package manager will need to be installed on rstudio
   - Virtual environments may need to be recreated

2. **Terminal Configuration:**
   - If using Warp, ensure it's installed on rstudio
   - Shell configuration (`.zshrc`, etc.) should be transferred separately

3. **Data Files:**
   - ✅ Data files in `$HOME/d/downloads/hedgeye/` have already been copied to rstudio
   - No action needed for data file migration

## Step-by-Step Migration Checklist

### Pre-Migration (on idlewood)

- [ ] Commit and push new Cursor config files (`AGENTS.md`, `.cursorignore`)
- [ ] Backup `.env`, `.envrc`, `.python-version` to secure location
- [ ] Export Cursor settings: `settings.json` and `mcp.json`
- [ ] Document any custom Cursor extensions you use
- [ ] Note any local MCP servers that need setup on rstudio

### On rstudio

- [ ] Install Cursor (if not already installed)
- [ ] Clone/pull the hedgeye-kb repository
- [ ] Restore environment files (`.env`, `.envrc`, `.python-version`)
- [ ] Install Python 3.13+ (Apple Silicon version)
- [ ] Install `uv` package manager
- [ ] Restore Cursor settings (`settings.json`, `mcp.json`)
- [ ] Install required Cursor extensions (if any)
- [ ] Set up MCP servers (if using)
- [ ] Verify data directory access (`$HOME/d/downloads/hedgeye/` - should already be present)
- [ ] Test the pipeline: `python scripts/run_full_pipeline.py`

### Verification

- [ ] Open project in Cursor on rstudio
- [ ] Verify `AGENTS.md` is recognized (Cursor should show project context)
- [ ] Verify `.cursorignore` is working (large directories excluded)
- [ ] Test git operations
- [ ] Test running the pipeline
- [ ] Verify Python environment and dependencies

## Quick Transfer Script

Here's a simple script to bundle everything on idlewood:

```bash
#!/bin/bash
# Run on idlewood to create transfer bundle

BACKUP_DIR=~/Desktop/hedgeye-kb-migration-$(date +%Y%m%d)
mkdir -p "$BACKUP_DIR"

# Project files (not in git)
cp ~/gh/randykerber/hedgeye-kb/.env "$BACKUP_DIR/" 2>/dev/null
cp ~/gh/randykerber/hedgeye-kb/.envrc "$BACKUP_DIR/" 2>/dev/null
cp ~/gh/randykerber/hedgeye-kb/.python-version "$BACKUP_DIR/" 2>/dev/null

# Cursor settings
mkdir -p "$BACKUP_DIR/cursor"
cp ~/Library/Application\ Support/Cursor/User/settings.json "$BACKUP_DIR/cursor/" 2>/dev/null
cp ~/.cursor/mcp.json "$BACKUP_DIR/cursor/" 2>/dev/null

echo "Backup created in: $BACKUP_DIR"
echo "Files to transfer:"
ls -la "$BACKUP_DIR"
```

## Data Files Location

**Important:** The actual Hedgeye data files are located at:
- `$HOME/d/downloads/hedgeye/` - Raw emails and processed data
- `$HOME/d/downloads/fmp/` - FMP data

**Status:** ✅ The `~/d` directory has already been copied to rstudio. No migration needed for data files.

## Post-Migration Notes

After migration, you may want to:
1. Update this document with any issues encountered
2. Document any rstudio-specific configurations needed
3. Consider setting up automated backups for configuration files
4. Test all development workflows on rstudio

## Troubleshooting

### Cursor not recognizing AGENTS.md
- Verify file is in project root
- Restart Cursor
- Check Cursor version (should be 2.0+)

### MCP server connection issues
- Verify server is running on rstudio (if local)
- Update `mcp.json` with correct hostname/port
- Check firewall settings

### Python/uv issues
- Ensure Python 3.13+ is installed (Apple Silicon version)
- Reinstall `uv`: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Recreate virtual environment

## Additional Resources

- Cursor 2.0 Documentation: https://docs.cursor.com
- Project Cursor Config: See `docs/CURSOR_CONFIG.md`
- Project Overview: See `AGENTS.md`

