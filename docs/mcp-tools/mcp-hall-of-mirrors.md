# MCP Hall of Mirrors
*"Transparent but impenetrable walls" - A survival guide to MCP's parallel universes*

## The Problem

MCP (Model Context Protocol) promised **"one protocol to rule them all"** for AI tool integration. Instead, it created **multiple overlapping configuration systems** that don't talk to each other, with no clear documentation of how they interact.

## The MCP Multiverse

### Universe 1: Claude Desktop MCP
**Location**: `~/.config/claude/claude_desktop_config.json` (varies by OS)
**Purpose**: Built-in MCP integration for Claude Desktop app
**Format**: JSON configuration file
**Scope**: Claude Desktop only

### Universe 2: Claude Code CLI MCP
**Commands**: `claude mcp add/list/get/remove`
**Location**: `~/.claude.json` (local/user scope) or `.mcp.json` (project scope)
**Purpose**: Command-line MCP server management
**Scopes**: 
- `local` - Private to current project
- `user` - Available globally for user
- `project` - Shared via `.mcp.json` in repository

### Universe 3: Claude Code Slash Commands
**Interface**: `/mcp` interactive command in Claude Code sessions
**Purpose**: Runtime MCP server management and authentication
**Limitation**: May not show all configured servers, unclear relationship to CLI config

### Universe 4: Shared Config Files
**Example**: `./config/mcp-config.json`
**Purpose**: Language-agnostic MCP configurations for Python/JavaScript tools
**Usage**: Custom implementations read these files directly

### Universe 5: Direct MCP API Calls
**Method**: Direct HTTP/stdio communication with MCP servers
**Purpose**: Bypass all configuration systems
**Example**: Our Context7 integration via bash commands

## Real-World Symptoms

### The Configuration Contradiction
- `claude mcp get context7` reports: ✅ **Connected**
- `/mcp` slash command shows: **Only JetBrains server visible**
- Direct API calls to Context7: ✅ **Work perfectly**

### The Documentation Gap
**No single source explains:**
- How these systems interact (or don't)
- Which takes precedence when conflicts occur
- Why some servers appear in some interfaces but not others
- How to troubleshoot cross-system issues

## What Actually Works (August 2025)

### ✅ Context7 Integration
**Method**: Direct API calls via bash commands
**Pattern**: 2-step process (resolve-library-id → get-library-docs)
**Status**: Reliable, bypasses all configuration complexity

**Working Commands**:
```bash
# Step 1: Resolve library ID
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "resolve-library-id", "arguments": {"libraryName": "library-name"}}}' | npx -y @upstash/context7-mcp --api-key $CONTEXT7_API_KEY

# Step 2: Get documentation
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "get-library-docs", "arguments": {"context7CompatibleLibraryID": "/resolved/library/id", "topic": "specific topic", "tokens": 8000}}}' | npx -y @upstash/context7-mcp --api-key $CONTEXT7_API_KEY
```

### ✅ Shared Configuration Pattern
**File**: `./config/mcp-config.json`
**Usage**: Both Python and JavaScript read same config
**Benefit**: Single source of truth, language-agnostic

## Survival Strategies

### 1. Embrace the Chaos
**Accept**: No one has the complete picture of MCP interactions
**Reality**: Even Anthropic docs are fragmented across products
**Approach**: Document what works, ignore what doesn't

### 2. Multi-Path Redundancy
**Don't rely on single configuration method**
- CLI configuration for management
- Direct API calls for reliability
- Shared configs for multi-language projects

### 3. Working > Perfect
**Context7 example**: Direct API calls work reliably, so we use them
**Philosophy**: Functional trumps architectural purity

### 4. Document Your Own Map
**Keep local documentation** of what actually works in your environment
**Don't trust universal documentation** - MCP implementations vary widely

## The Meta-Problem

### Enterprise Software Syndrome
**Symptom**: Overcomplicated solutions to simple problems
**Cause**: Multiple teams building overlapping solutions without coordination
**Effect**: No single person understands the complete system

### The Fragmentation Trap
**Original Promise**: "One protocol for all AI tools"
**Current Reality**: "Five ways to configure the same thing, none compatible"
**User Experience**: Transparent but impenetrable walls everywhere

## Recommendations

### For This Project
1. **Use what works**: Context7 via direct API calls
2. **Maintain shared configs**: `mcp-config.json` for multi-language consistency
3. **Ignore broken interfaces**: Skip `/mcp` slash command confusion
4. **Document working patterns**: This file and project CLAUDE.md

### For Future Projects
1. **Start simple**: Direct API calls over complex configurations
2. **Single source of truth**: One config system per project
3. **Test early**: MCP integration issues appear late in development
4. **Plan for fragmentation**: Multiple approaches may be needed

## Tools for Sanity

### Diagnostic Commands
```bash
# Check CLI configuration
claude mcp list
claude mcp get <server-name>

# Test direct server communication
npx -y @upstash/context7-mcp --api-key $CONTEXT7_API_KEY

# Check slash command interface
/mcp
```

### Working Integrations
- **Context7**: Live documentation via direct API ✅
- **Shared configs**: Multi-language configuration ✅
- **JetBrains**: IDE integration via MCP ✅

## The Bottom Line

**MCP is powerful but poorly integrated.** Each universe works in isolation, documentation is fragmented, and no single authority has the complete picture.

**Survival approach**: Use what works, document what doesn't, and build redundancy across multiple MCP universes.

*The maze has many paths to the same destination - choose the ones that don't have invisible walls.*

---

**Last Updated**: August 2025  
**Status**: Context7 working via direct API calls  
**Next**: Consider consolidating to fewer MCP universes as ecosystem matures