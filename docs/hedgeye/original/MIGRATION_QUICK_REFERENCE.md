# Quick Reference: Transferring Cursor Configuration to rstudio

## Summary: What to Transfer

### ✅ Via Git (Already in Repo or Ready to Commit)
- `AGENTS.md` - Cursor project instructions
- `.cursorignore` - Files to exclude from context  
- `docs/CURSOR_CONFIG.md` - Documentation
- `docs/MIGRATE_TO_RSTUDIO.md` - Full migration guide

**Action:** Commit and push these files, then pull on rstudio

### 📦 Manual Copy (Not in Git)
- `.env` - Environment variables
- `.envrc` - direnv configuration
- `.python-version` - Python version (3.13)

**Action:** Use backup script or manually copy

### ⚙️ Cursor Global Settings
- `~/Library/Application Support/Cursor/User/settings.json` - User preferences
- `~/.cursor/mcp.json` - MCP server configuration

**Action:** Use backup script or manually copy

## Quick Start

### On idlewood (Source):

```bash
# 1. Commit new Cursor config files
cd ~/gh/randykerber/hedgeye-kb
git add AGENTS.md .cursorignore docs/CURSOR_CONFIG.md docs/MIGRATE_TO_RSTUDIO.md
git commit -m "Add Cursor 2.0 configuration and migration docs"
git push

# 2. Create backup bundle
./scripts/migration/backup_for_rstudio.sh
# This creates: ~/Desktop/hedgeye-kb-migration-YYYYMMDD-HHMMSS/
```

### On rstudio (Destination):

```bash
# 1. Pull the repo (gets Cursor config files)
cd ~/gh/randykerber/hedgeye-kb
git pull

# 2. Restore backup (after transferring backup directory)
./scripts/migration/restore_on_rstudio.sh ~/path/to/backup-directory

# 3. Verify
# - Open project in Cursor
# - Check that AGENTS.md is recognized
# - Test: python scripts/run_full_pipeline.py
```

## File Locations Reference

| File | idlewood Location | rstudio Location |
|------|------------------|------------------|
| **Project Files** |
| `AGENTS.md` | `~/gh/.../hedgeye-kb/AGENTS.md` | Same (via git) |
| `.cursorignore` | `~/gh/.../hedgeye-kb/.cursorignore` | Same (via git) |
| `.env` | `~/gh/.../hedgeye-kb/.env` | Same (manual copy) |
| `.envrc` | `~/gh/.../hedgeye-kb/.envrc` | Same (manual copy) |
| **Cursor Settings** |
| User Settings | `~/Library/Application Support/Cursor/User/settings.json` | Same |
| MCP Config | `~/.cursor/mcp.json` | Same |

## Important Considerations

### Platform Differences
- **idlewood:** Intel chip
- **rstudio:** Apple Silicon M4 Max
- **Impact:** Python/uv may need Apple Silicon versions

### Data Files
- Location: `$HOME/d/downloads/hedgeye/`
- **Status:** ✅ Already copied to rstudio (no action needed)

### MCP Server
- **Location:** `~/.cursor/mcp.json`
- **Action:** Review and update MCP server configuration if needed (especially localhost URLs)

## Troubleshooting

**Cursor not recognizing AGENTS.md?**
- Verify file is in project root
- Restart Cursor
- Check Cursor version (2.0+)

**Settings not applied?**
- Ensure Cursor is closed when copying settings files
- Restart Cursor after restoration

**MCP server errors?**
- Update `mcp.json` with correct hostname if server moved
- Verify server is running on rstudio

## See Also

- Full guide: `docs/MIGRATE_TO_RSTUDIO.md`
- Cursor config: `docs/CURSOR_CONFIG.md`
- Project context: `AGENTS.md`

