# Cursor Configuration Summary

**Last Updated:** November 2025  
**Cursor Version:** 2.0

## Current State

### Cursor-Specific Files
**Status:** None currently exist in this project

The project does not have any Cursor-specific configuration files yet. The `.gitignore` file includes entries for Cursor files (`.cursor/`, `.cursor-settings.json`), but these directories/files don't exist yet.

### Other Tool Configuration Files

#### Claude Code (claude.ai/code)
- **Directory:** `.claude/`
- **Files:**
  - `CONTEXT.md` - Current development state and next priorities
  - `DECISIONS.md` - Architecture decisions and rationale
  - `BELIEFS.md` - Project-specific knowledge and assumptions
  - `MIGRATION_PLAN.md` - Migration planning documents
  - `SYNDICATE_VISION.md` - Vision documents
  - `settings.local.json` - Local settings
- **Purpose:** Provides context to Claude Code AI assistant
- **Status:** Active and maintained (last updated Oct 18, 2025)

#### JetBrains PyCharm/IntelliJ IDEA
- **Directory:** `.idea/`
- **Purpose:** IDE-specific settings, run configurations, code style
- **Status:** Present (last modified Nov 2, 2024)

#### Warp Terminal
- **File:** `WARP.md` (appears to be a duplicate of `CLAUDE.md`)
- **Status:** Present but may be outdated

## Cursor Version 2 Configuration Options

Cursor 2.0 supports multiple ways to configure AI behavior and project context:

### Option 1: `.cursor/rules/` Directory (Recommended for Complex Projects)

**Structure:**
```
.cursor/
  rules/
    project-overview.mdc
    coding-standards.mdc
    architecture.mdc
```

**File Format:** MDC (Markdown with metadata)
- Supports metadata (description, globs, alwaysApply)
- Can be categorized as: Always, Auto Attached, Agent Requested, or Manual
- More flexible and powerful than simple markdown

**Example `.cursor/rules/project-overview.mdc`:**
```mdc
---
description: Hedgeye KB project overview and context
alwaysApply: true
---

# Hedgeye Knowledge Base Project

This project parses Hedgeye email reports and converts them into structured data.

## Key Context
- Data files are in `$HOME/d/downloads/hedgeye`, not in the repo
- Pipeline is idempotent - safe to re-run
- Uses Python 3.13+ with `uv` package manager
```

### Option 2: `AGENTS.md` File (Simpler Alternative)

**Location:** Root of project (`/Users/rk/gh/randykerber/hedgeye-kb/AGENTS.md`)

**Format:** Simple Markdown file with project instructions

**Advantages:**
- Simpler than MDC files
- Easy to read and maintain
- Good for straightforward project guidelines

### Option 3: `.cursorrules` (Deprecated)

**Status:** Deprecated in Cursor 2.0  
**Recommendation:** Do not use. Migrate to `.cursor/rules/` if you have existing `.cursorrules` files.

### Additional Cursor Files

#### `.cursorignore`
- **Purpose:** Similar to `.gitignore`, tells Cursor which files to exclude from context
- **Status:** Not present, but could be useful for large data directories
- **Recommendation:** Consider creating if you want to exclude specific files from AI context

#### `.cursor/cli.json` (if using Cursor CLI)
- **Purpose:** CLI-specific configuration
- **Location:** Project-level or global (`~/.cursor/cli-config.json`)
- **Status:** Not needed unless using Cursor CLI

## Recommendations for This Project

### Immediate Actions

1. **Create `AGENTS.md`** (Simplest approach)
   - Migrate key information from `.claude/BELIEFS.md` and `CLAUDE.md`
   - Include project overview, common commands, and development preferences
   - This provides Cursor with essential context without complex setup

2. **Consider creating `.cursorignore`**
   - Exclude large data directories: `data/`, `example_output/`
   - Exclude cache: `__pycache__/`, `.cache/`, `_cache/`
   - Exclude virtual environments: `.venv/`, `venv/`, `env/`

### Optional Enhancements

3. **Create `.cursor/rules/` directory** (If you want more sophisticated rules)
   - Migrate from `.claude/` files to structured rules
   - Create separate rules for different aspects (architecture, coding standards, domain knowledge)
   - Use `alwaysApply: true` for critical context

4. **Update `.gitignore`**
   - Already includes `.cursor/` and `.cursor-settings.json` ✓
   - Consider adding `AGENTS.md` if you want it tracked (or keep it untracked for personal use)

## Migration Strategy

### From Claude Code to Cursor

The `.claude/` directory contains valuable context that should be preserved:

1. **Keep `.claude/` directory** - It's still useful if you use Claude Code
2. **Create `AGENTS.md`** - Extract key information for Cursor
3. **Consider syncing** - Keep both in sync if you use both tools

### Key Information to Include in Cursor Config

From `.claude/BELIEFS.md`:
- Domain knowledge about Hedgeye Risk Range™
- Data locations (`$HOME/d/downloads/hedgeye`)
- Development philosophy (immutability, idempotency)
- Technology choices (Python 3.13+, `uv` package manager)

From `CLAUDE.md`:
- Common commands (pipeline execution, dependency management)
- Architecture overview
- Directory structure

From `.claude/CONTEXT.md`:
- Current development status
- Next priorities (MCP server development)
- Known issues

## Files Managed by Cursor (When Created)

Once you create Cursor configuration files, these will be managed by Cursor:

- `.cursor/rules/*.mdc` - Project rules (if using rules directory)
- `AGENTS.md` - Project instructions (if using simple approach)
- `.cursorignore` - Files to exclude from context
- `.cursor/cli.json` - CLI configuration (if using CLI)

**Note:** All of these are already in `.gitignore`, so they won't be committed unless you explicitly want to share them.

## Comparison: Cursor vs Other Tools

| Tool | Config Location | Format | Status |
|------|----------------|--------|--------|
| **Cursor 2.0** | `.cursor/rules/` or `AGENTS.md` | MDC or Markdown | Not yet configured |
| **Claude Code** | `.claude/` | Markdown | Active |
| **PyCharm** | `.idea/` | XML/JSON | Active |
| **Warp** | `WARP.md` | Markdown | Present (may be outdated) |

## Next Steps

1. ✅ Review this document
2. ⬜ Create `AGENTS.md` with essential project context
3. ⬜ (Optional) Create `.cursorignore` to exclude large directories
4. ⬜ (Optional) Create `.cursor/rules/` for more sophisticated configuration
5. ⬜ Test Cursor 2.0 with the new configuration

