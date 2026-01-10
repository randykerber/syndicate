# Context in Cursor

How Cursor loads and uses context files to understand your project.

**Last Updated**: 2026-01-10  
**Confidence Level**: Mix of verified behavior and web research (uncertainties marked with ⚠️)

---

## TL;DR - What Cursor Actually Loads

| Source | Loaded? | When | Notes |
|--------|---------|------|-------|
| `.cursor/rules/*.mdc` | ✅ Yes | Based on globs/alwaysApply | **Recommended approach** |
| `AGENTS.md` | ✅ Yes | Always (if present) | Cross-tool standard |
| User Rules (Settings UI) | ✅ Yes | Always | Global, all projects |
| `.cursorrules` | ⚠️ Deprecated | Always (if present) | Legacy, still works |
| `CLAUDE.md` | ❌ No | — | Claude Code only |
| `GEMINI.md` | ❌ No | — | Gemini CLI only |
| `~/.cursor/` files | ❌ No rules | — | App state, not context |

**Key insight**: Cursor does NOT read `CLAUDE.md` or `GEMINI.md`. Those files are for their respective tools only.

---

## Context Sources in Detail

### 1. `.cursor/rules/` Directory (Recommended)

**Location**: `<project>/.cursor/rules/`  
**Format**: `.mdc` files (Markdown with YAML frontmatter)  
**Status**: ✅ Current recommended approach

Each `.mdc` file can specify:
- **`description`**: Semantic hint for when to apply (AI reads this)
- **`globs`**: File patterns that trigger auto-inclusion
- **`alwaysApply`**: If `true`, always included regardless of context

**Example** (`.cursor/rules/python.mdc`):
```markdown
---
description: Python code style and uv package management
globs: ["**/*.py", "python/**"]
alwaysApply: false
---

# Python Rules
- Use `uv`, never pip
- Type hints required
```

**Behavior**:
- `alwaysApply: true` → Loaded in every conversation
- `alwaysApply: false` + globs → Loaded when matching files are in context
- Multiple `.mdc` files can be active simultaneously

---

### 2. `AGENTS.md` (Cross-Tool Standard)

**Location**: `<project>/AGENTS.md` (or nested in subdirectories)  
**Format**: Standard Markdown  
**Status**: ✅ Supported, cross-tool compatible

`AGENTS.md` is the [AAIF/Linux Foundation standard](https://agents.md/) for providing context to AI coding agents. Works with:
- Cursor ✅
- Claude Code ✅
- Gemini CLI ✅
- OpenAI Codex ✅
- And many others

**Behavior**:
- Always loaded when present at project root
- Nested `AGENTS.md` files can override for subdirectories
- Simpler than `.cursor/rules/` but less granular

---

### 3. User Rules (Global Settings)

**Location**: Cursor Settings → General → Rules for AI  
**Format**: Plain text  
**Status**: ✅ Active

These rules apply to ALL projects, ALL conversations. Good for:
- Personal preferences (response style, formatting)
- Universal safety rules
- Environment info (OS, shell)

**⚠️ Important**: There is NO global file like `~/.cursor/rules/`. Global rules are **only** in the Settings UI.

---

### 4. `.cursorrules` (Deprecated)

**Location**: `<project>/.cursorrules`  
**Format**: Plain text / Markdown  
**Status**: ⚠️ Deprecated but still functional

This was the original Cursor-specific format. Still works, but:
- Cannot use globs or conditional loading
- Single monolithic file
- Cursor recommends migrating to `.cursor/rules/`

**Migration path**: 
```bash
# Archive old file
mv .cursorrules .cursorrules.deprecated.YYYY-MM-DD

# Create new modular rules
mkdir -p .cursor/rules
# Create .mdc files as needed
```

---

### 5. Files Cursor Does NOT Read

| File | Who Reads It | Cursor Behavior |
|------|--------------|-----------------|
| `CLAUDE.md` | Claude Code | ❌ Ignored by Cursor |
| `GEMINI.md` | Gemini CLI | ❌ Ignored by Cursor |
| `WARP.md` | Warp terminal | ❌ Ignored by Cursor |
| `~/.cursor/*.json` | Cursor app | Internal state, not context |

**⚠️ Common misconception**: Cursor does NOT automatically read `CLAUDE.md`. If you want both tools to share context, put it in `AGENTS.md`.

---

## Global vs Project Scope

### Global (All Projects)

| What | Where | Format |
|------|-------|--------|
| User Rules | Settings → General → Rules for AI | Plain text |
| Global MCP Servers | `~/.cursor/mcp.json` | JSON config |

**Note**: `~/.cursor/` directory contains app state (extensions, IDE state, MCP config) but NO rules files.

### Project/Workspace Scope

| What | Where | Format |
|------|-------|--------|
| Project Rules | `.cursor/rules/*.mdc` | YAML frontmatter + Markdown |
| Agent Instructions | `AGENTS.md` | Markdown |
| Legacy Rules | `.cursorrules` | Plain text (deprecated) |
| Project MCP | `config/mcp-config.json` | JSON config |

---

## Loading Priority & Behavior

When Cursor starts a conversation, it loads context in this order:

1. **User Rules** (global, from Settings)
2. **Project Rules** from `.cursor/rules/` where `alwaysApply: true`
3. **`AGENTS.md`** (if present)
4. **`.cursorrules`** (if present, legacy)
5. **Conditional Rules** from `.cursor/rules/` based on:
   - Files currently open/referenced
   - Glob pattern matches

**⚠️ Uncertainty**: The exact priority when rules conflict is not clearly documented. Empirically, more specific rules (glob-matched) seem to take precedence over general ones.

---

## What `~/.cursor/` Actually Contains

Based on inspection of `/Users/rk/.cursor/`:

```
~/.cursor/
├── ai-tracking/          # Usage tracking database
├── argv.json             # Launch arguments
├── extensions/           # VS Code extensions
├── ide_state.json        # Recently viewed files
├── mcp.json              # ✅ Global MCP server config
├── plans/                # Cursor's planning artifacts
└── projects/
    └── <project-hash>/
        ├── mcp-cache.json  # Cached MCP state
        ├── mcps/           # Project MCP data
        └── rules/          # ⚠️ Empty (mirrored from project?)
```

**Key finding**: `~/.cursor/mcp.json` is the global MCP config. But there's no global rules file here - rules are only in the Settings UI or per-project.

---

## This Project's Current Setup

### What Cursor Loads for `syndicate/`

| Source | File | Status |
|--------|------|--------|
| `.cursor/rules/always.mdc` | Safety, secrets, BSD commands | ✅ Always loaded |
| `.cursor/rules/python.mdc` | Python conventions, uv | ✅ When `**/*.py` in context |
| `.cursor/rules/hedgeye.mdc` | Pipeline paths, CSV rules | ✅ When `**/hedgeye/**` in context |
| `AGENTS.md` | Project overview, user context | ✅ Always loaded |
| `CLAUDE.md` | Claude Code context map | ❌ NOT loaded by Cursor |
| `.cursorrules.deprecated.*` | Old rules (archived) | ❌ Not loaded (renamed) |

### Files Cursor Will NOT Use

- `CLAUDE.md` - Only Claude Code reads this
- `data/ace/**` - ACE warehouse files (not auto-loaded)
- `context/**` - Manual context files (not auto-loaded)

---

## Verifying What's Loaded

To confirm Cursor has loaded your context:

1. **Ask directly**: "What context files did you load for this project?"
2. **Test with canary**: Add a unique phrase like `CANARY: pineapple-42` to a rule, then ask "What's the canary?"
3. **Check rule behavior**: If a glob-scoped rule should apply, test if the AI follows it

---

## Recommendations

### For Cross-Tool Compatibility

Put shared context in `AGENTS.md`:
- Project overview
- Code style basics
- Key patterns
- Safety rules

### For Cursor-Specific Features

Use `.cursor/rules/*.mdc` for:
- Conditional loading (globs)
- Detailed conventions per file type
- Rules that don't apply to other tools

### Avoid Duplication

| Context Type | Put In |
|--------------|--------|
| Shared across tools | `AGENTS.md` |
| Cursor-specific | `.cursor/rules/` |
| Claude Code specific | `CLAUDE.md` |
| Sensitive/detailed | `.cursor/rules/` with globs |

---

## Open Questions / Uncertainties

⚠️ **Not fully verified**:

1. **Conflict resolution**: When `.cursor/rules/` and `AGENTS.md` have conflicting instructions, which wins?

2. **Nested AGENTS.md**: Does Cursor support nested `AGENTS.md` files for monorepo subdirectories? (Documented as yes, not tested)

3. **Rule inheritance**: Do glob-scoped rules accumulate or replace each other?

4. **Settings sync**: Are User Rules synced via Cursor account, or machine-local only?

---

## Changelog

- **2026-01-10**: Initial version based on web research and local inspection
