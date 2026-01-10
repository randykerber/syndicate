# Warp Agent Context System

*Reference for understanding how Warp loads and uses context*  
*Last updated: 2026-01-02*

NOTE: This file also in Obsidian 'Tech' vault.

## Overview

Warp's agents use multiple context sources to inform responses. Context loading is **dynamic and hierarchical** - not everything is loaded permanently, but retrieved on-demand based on query and location.

## Context Types

### 1. Global Rules (Persistent, Cross-Project)
- **Location**: Stored in Warp's internal database (not files)
- **Access**: Warp Drive → Personal → Rules → Global, or `/add-rule` command
- **Scope**: Applies to ALL projects and directories
- **Best for**: 
  - OS/shell preferences (macOS, zsh)
  - Command safety verification policies
  - Universal coding standards
  - Personal preferences that never change

**Example use cases:**
- macOS-specific command syntax rules
- "Always verify destructive commands against man pages"
- Preferred error handling patterns

### 2. Project Rules (Context-Aware)
- **Location**: WARP.md files in Git repositories
- **Hierarchy**: 
  ```
  /repo/WARP.md              (repository root - broadest)
  /repo/subdir/WARP.md       (subdirectory - more specific)
  /repo/subdir/deep/WARP.md  (nested - most specific)
  ```
- **Precedence**: More specific (deeper) files take priority over parent files
- **Scope**: Only applies when working within that Git repository
- **Trigger**: Automatically loaded based on current working directory

**Supported filenames** (all treated as project rules):
- `WARP.md` (recommended)
- `CLAUDE.md`
- `AGENTS.md`
- `.cursorrules`
- `GEMINI.md`
- `.clinerules`
- `.windsurfrules`
- `.github/copilot-instructions.md`

**Best for:**
- Project architecture patterns
- Tech stack details (Python + uv, JavaScript + npm)
- Testing commands and workflows
- Deployment procedures
- MCP server configurations

### 3. Codebase Index (Semantic Search)
- **Location**: Git-tracked repositories
- **Management**: Settings → Code → Codebase Index
- **Privacy**: No code stored on Warp servers, indexed locally
- **Trigger**: Automatically indexed when entering new Git repos
- **Usage**: Agents search indexed code when query is code-related
- **Exclusions**: Use `.warpindexingignore` to exclude files

### 4. Warp Drive (Personal Knowledge Base)
- **Components**:
  - **Workflows** - Saved command sequences
  - **Notebooks** - Documentation and notes
  - **Prompts** - Reusable AI prompt templates
  - **Environment Variables** - Saved env vars
  - **Rules** - Global rules storage
- **Usage**: Agents automatically pull from Drive contents when relevant
- **Visibility**: Context appears under "References" or "Derived from" in conversations
- **Toggle**: Settings → AI → Knowledge → Warp Drive as Agent Mode Context (enabled by default)

### 5. MCP Servers (External Tools & Data)
- **Configuration**: MCP server definitions in Warp settings
- **Trigger**: Loaded dynamically when query matches MCP server capabilities
- **Examples**: GitHub, Linear, Figma, Slack, Sentry, custom servers
- **Permissions**: Controllable via Settings → AI → Agents → Permissions

### 6. Ad-hoc Context (Manual, Per-Query)
- **Blocks**: Terminal output attached via sparkle icon or CMD+UP
- **Files**: Referenced with `@filename` syntax
- **Images**: Attached screenshots/diagrams
- **URLs**: Public website content (scraped and sent to model)
- **Scope**: Only applies to current conversation

## Context Loading Strategy

### Dynamic Loading (On-Demand)
Warp does NOT load all context permanently. Instead:

1. **Location-based**: When you `cd` into a directory, relevant WARP.md files are loaded
2. **Query-based**: MCP servers matching the query intent are activated
3. **Code-based**: Semantic search of indexed codebases when code is mentioned
4. **Pattern-based**: Warp Drive Workflows/Prompts matching the query pattern

This is similar to Claude's deprecated "skills" concept - available but not always loaded.

### Hierarchical Precedence
When multiple context sources conflict:
1. **Most specific wins**: `/repo/python/WARP.md` > `/repo/WARP.md` > Global Rules
2. **Project over personal**: Project WARP.md > Global Rules (for project-specific overrides)
3. **Explicit over implicit**: Ad-hoc attached context > automatic context

## Context Window Considerations

### Known Limitations
- **Issue**: Rules may be dropped when context window is reached or after summarization ([GitHub #7199](https://github.com/warpdotdev/warp/issues/7199))
- **Mitigation**: Keep rules concise; prioritize critical information
- **Trade-off**: More comprehensive rules = better accuracy BUT higher token usage

### Best Practices
- **Global Rules**: Keep lean, focus on critical safety checks and OS facts
- **Project Rules**: Detailed but focused on project-specific patterns
- **Use hierarchy**: Common patterns in root WARP.md, specific details in subdirectory files
- **MCP for large context**: Offload large datasets to MCP servers rather than embedding in rules

## Practical Setup for Solo Developer

### Recommended Structure
```
Warp Database (via UI)
└── Global Rules
    ├── macOS Command Safety
    ├── Shell Preferences (zsh/bash)
    └── Universal Coding Standards

Git Repositories
├── /Users/rk/gh/randykerber/syndicate/
│   ├── .warp/WARP.md          # SSS architecture, MCP patterns
│   ├── python/
│   │   └── WARP.md            # Python/uv specific conventions
│   └── js/
│       └── WARP.md            # JavaScript/npm specific conventions
│
├── /Users/rk/gh/randykerber/other-project/
│   └── WARP.md                # Other project context
│
└── /path/to/another-repo/
    └── WARP.md

Warp Drive (Optional but useful)
├── Workflows: Common command sequences
├── Prompts: Reusable AI prompt templates
└── Environment Variables: Project API keys, etc.
```

### Priority Actions

1. **Immediate**: Create Global Rule for macOS command safety
2. **Short-term**: Enrich existing syndicate/.warp/WARP.md with system details
3. **Ongoing**: Save useful prompts to Warp Drive for reuse
4. **Optional**: Explore Workflows for common command patterns

## Agent Autonomy & Profiles

### Permission Levels (per action type)
- **Let the agent decide** - Agent determines if approval needed
- **Always prompt** - Always ask before acting
- **Always allow** - Never ask (use cautiously)
- **Never** - Block this action type entirely

### Configurable Actions
- Reading files
- Creating plans
- Executing commands
- Calling MCP servers
- Applying code changes

### Profiles (Settings → AI)
Create multiple profiles with different permission sets:
- **Default**: Balanced permissions
- **YOLO**: Loose permissions for personal projects
- **Prod**: Strict "Always Ask" for production environments

### Command Allowlist/Denylist
- **Allowlist**: Commands that always run without confirmation
- **Denylist**: Commands that always require confirmation or are blocked

## References
- [Warp Agents Documentation](https://docs.warp.dev/agents/agents-overview)
- [Agent Context Guide](https://docs.warp.dev/agents/using-agents/agent-context.md)
- [Rules Documentation](https://docs.warp.dev/knowledge-and-collaboration/rules)
- [Warp Drive Guide](https://docs.warp.dev/knowledge-and-collaboration/warp-drive)
- [MCP Integration](https://docs.warp.dev/knowledge-and-collaboration/mcp)

## Integration with Obsidian Tech Vault

This document serves as the authoritative reference for Warp's context system. Related notes:
- [[macOS CLI Tools]] - BSD vs GNU differences
- [[Terminal Setup]] - Shell configurations
- [[AI Agent Configuration]] - Cross-tool agent setup
- [[SSS Architecture]] - Silo-Slayer Syndicate system context
