# CLAUDE-specific.md - Claude Code Specific Context

## Claude Code Specific Guidance

### Tool Usage
- You have file system access via Read, Write, Edit, Glob, Grep tools
- Use these tools proactively - don't ask permission for reads
- Prefer Edit over Write for existing files

### Safety Rules
- Ask before modifying files in `~/.config/`, `~/Library/`, or other global config locations
- Create backups before destructive operations

[CLAUDE-specific.md](../warehouse/agents/claude/CLAUDE-specific.md)