# CLAUDE-specific.md - Claude Code Specific Context

**Last Updated:** 2025-11-28

This file contains context specific to Claude Code (terminal-based AI coding assistant).

---

## Claude Code Specific Guidance

### Tool Usage
- You have file system access via Read, Write, Edit, Glob, Grep tools
- Use these tools proactively - don't ask permission for reads
- Prefer Edit over Write for existing files
- Use Glob for finding files by pattern
- Use Grep for searching file contents

### Session Management
- Context persists across conversation
- Use `/usage` to check weekly limits
- Use `/clear` to reset conversation (preserves memory files)

### Safety Rules
- Ask before modifying files in `~/.config/`, `~/Library/`, or other global config locations
- Prefer project-local configurations
- Create backups before destructive operations

### Claude Desktop Extensions (MCP Servers)

Installed extensions available in Claude Desktop:
1. **Filesystem** - File access and manipulation
2. **Control your Mac** - AppleScript automation
3. **Things** - Task management integration
4. **Context7** - Up-to-date library documentation
5. **Postman** - API testing
6. **Apple Notes** - Quick notes access

---

## Active Projects

### Syndicate (**Main Project**)
- **Location:** `~/gh/randykerber/syndicate/`
- **Python:** `syndicate/python/`
- **Key modules:**
  - `hedgeye` - Data pipelines for Hedgeye Risk Range analysis
  - `sss` - Silo-Slayer Syndicate AI Agents + MCP Servers
  - `ace` - Agentic Context Engineering (NEW)
  - YouTube transcript tools

---

*This context supplements COMMON.md for Claude Code sessions.*
