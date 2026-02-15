# CLAUDE.md - Silo-Slayer Syndicate Project

This file provides project-specific guidance to Claude Code when working with the Syndicate codebase.

---

## 🗺️ Context Map

**⚠️ FIRST**: Read `data/ace/CONTEXT_MAP.md` — master index of available context sources and loading instructions.

---

## User Context

Randy Kerber — AI/Data Engineer & Software Developer (Python, TypeScript, Scala). Based in Cañon City, Colorado (America/Denver).

### Current Projects
- Hedgeye RR automation + knowledge base (Main repo: `~/gh/randykerber/hedgeye-kb/`)
- Investing data warehouse (ticker-level) -- Still planning
- Context Engineering + MCP (Model Context Protocol) for AI Agent tools
- Silo-Slayer Syndicate System (SSS) — agent network to break app/data silos

### Preferences & Rules
- Concise, Markdown-first; ask before non-read actions or installing tools
- If IDE/UI steps don't match, **stop and ask for a quick screen description**
- Assume latest tool versions unless I say otherwise

### Dev Stack & Apps
Obsidian (iCloud); Drafts; Bear; Apple Notes/Reminders/Calendar/Mail/Messages/Contacts; Raycast; Warp; Emacs; IntelliJ; Claude Code; 1Password; Arc/Chrome/Safari.

### Quick Outcomes
- Help extract parameters from natural input → exact tool calls
- Use human-in-the-loop when ambiguities remain (offer options)
- Keep a minimal checklist of what you changed or created

## Project Overview

The Silo-Slayer Syndicate System creates an agentic team of AI agents designed to break users out of "app silos" and create intelligent, human-AI collaborative workflows using MCP (Model Context Protocol) for tool access.

### Core Mission: Information Liberation

**Problem**: Information scattered across tools creates "app prisons" where users can't find or use their own information outside the specific app that holds it.

**Solution**: AI agents using "English as programming language" to extract parameters from human input, execute tool calls, and engage humans through multi-turn conversation when disambiguation is needed.

## Architecture Principles

### 1. English as Programming Language

**Core Concept**: Natural language input → AI parameter extraction → Tool API calls
- AI handles ambiguity through conversation rather than rigid forms
- Multi-turn dialogue between Human and AI Agents resolve missing/ambiguous parameters
- Human-AI collaboration when AI can't determine correct values
- Graceful failure with persistent task queues

### 2. Hybrid Multi-Language Architecture

```
Syndicate System:
├── python/ - Agent orchestration, AI workflows, MCP servers
├── js/ - Native tool integrations, rich UI components  
└── MCP Protocol - Language-agnostic communication bridge
```

**Why Hybrid**:
- **Python**: Superior AI/ML ecosystem, mature MCP servers, agent orchestration
- **JavaScript**: Native tool integrations (Raycast, Drafts, Obsidian), rich UI capabilities
- **MCP Protocol**: Clean separation, tool reusability across languages

### 3. Session-Persistent Agent Framework

All agents inherit conversation memory across turns:
- **SQLiteSession**: Persistent conversation history across turns
- **Context Retention**: "Paris" → "Which Paris?" → "1" → "Paris, France" (remembered)
- **Multi-turn Workflows**: Complex tasks resolved through conversation
- **Human-in-the-loop**: File-based async queue system for human input

## Project Structure

### Python Package (`python/`)

**Core Framework** (`src/syndicate/`):
- `agents.py` - Base SyndicateAgent class with session persistence
- `human_interface.py` - Async human-AI communication system (**ESSENTIAL**)
- `instruction_templates.py` - Reusable agent instruction patterns
- `sessions.py` - Session management utilities

**MCP Servers** (Local Tools):
- `human_input_server.py` - Human-in-the-loop disambiguation (**ESSENTIAL**)
- `push_server.py` - Mobile push notifications via Pushover
- `drafts_server.py` - Drafts processing for SiloSlayer mission
- `accounts_server.py` - Investment/trading account management
- `market_server.py` - Stock price simulation

### JavaScript Package (`js/`)

**Core Components** (`src/`):
- `agents/reminder-agent.ts` - Working OpenAI Agent SDK example
- `tools/tool-registry.ts` - Central tool discovery (37 tools)
- `tools/simple-tools.ts` - File, system operations
- `mcp/mcp-client-proper.ts` - MCP server communication

**Tool Inventory (38 Total)**:
- **Custom Tools (4)**: File ops, system commands, reminders
- **MCP Tools (31)**: Filesystem, Obsidian, sequential-thinking, Tavily, Context7
- **OpenAI Built-ins (3)**: web_search, code_interpreter, file_search

**Native Integrations** (Superior API access):
- Raycast extensions for universal launcher integration
- Drafts actions for note processing (JavaScript runtime)
- Obsidian plugins for vault manipulation (full API)
- Apple Shortcuts for cross-device workflows

## Key Patterns and Workflows

### 1. Parameter Extraction Pattern

```
Human: "Add this to my investment notes"
Agent: Analyzes content → Identifies "investment" → Routes to Obsidian Main vault
Agent: Missing filename → "What should I call this note?"
Human: "Luke Gromen Fed analysis"  
Agent: Creates note with extracted parameters
```

### 2. Human-in-the-Loop Disambiguation

**File-based Async System**:
- Agent creates request file with numbered options
- Push notification alerts user on mobile
- Human responds via file/CLI/mobile
- Agent continues with resolved parameters

### 3. Tool Composition by Agent Type

**Base Tools** (All Agents):
- `push_server.py` - Mobile notifications
- `human_input_server.py` - Human disambiguation

**Specialized Combinations**:
- **Weather Agent**: Base + weather API + location disambiguation
- **Content Router**: Base + Drafts processing + web search
- **Trading Agent**: Base + accounts + market data
- **Research Agent**: Base + web fetch + memory storage

## Mission-Specific Applications

### SiloSlayer Syndicate

**Target**: 1219+ unprocessed Drafts notes + daily information overflow

**Strategy**: 
- AI-assisted triage for recent items (reduce growth rate from 50+/month to 5-10/month)
- Smart routing: Voice/text input → AI categorization → Proper destination
- "National debt" approach: Prevent growth rather than solve entire backlog

**Tools**: Drafts server, content categorization, destination routing (Obsidian, Bear, 1Password)

## Usage Patterns

### Creating New Agents

1. **Use instruction templates** from `instruction_templates.py`
2. **Select appropriate tool combination** from `mcp_params.py`
3. **Inherit from SyndicateAgent** for automatic session persistence
4. **Test with human disambiguation** scenarios

### Common Commands

**Python Environment Management (UV - Modern Interface Only)**:
```bash
cd python/
uv sync                    # Install all dependencies from pyproject.toml
uv add package-name        # Add new dependency  
uv remove package-name     # Remove dependency
uv lock --upgrade && uv sync  # Update packages to latest compatible versions
uv tree                    # Show dependency tree
```

**Running Python Code**:
```bash
# Run MCP servers
uv run servers/human_input_server.py
uv run servers/push_server.py  
uv run servers/drafts_server.py

# Run agents
uv run demos/wendy_weather.py
uv run python -c "from src.syndicate.agents import WeatherAgent; import asyncio; asyncio.run(WeatherAgent().chat('Paris'))"

# Run development tools
uv run pytest              # Run tests
uv run black .             # Format code
uv run ruff check          # Lint code
```

**JavaScript Commands**:
```bash
cd js/
npm run build              # Build TypeScript
npm run tools              # Tool inventory report
npm update                 # Update packages
```

## Design Philosophy

### What Makes This Different

**Not Another Chatbot**: Agents execute real tool calls with extracted parameters
**Not Rule-Based Automation**: AI handles ambiguity and edge cases through conversation  
**Not Rigid APIs**: Natural language instructions converted to precise tool execution
**Not Single-Language**: Hybrid architecture leverages each language's strengths

### Success Metrics

1. **Parameter Extraction Success**: Can AI correctly extract tool parameters from natural input?
2. **Human Collaboration**: Does multi-turn conversation resolve ambiguity effectively?
3. **Tool Integration**: Do agents successfully execute real tool calls?
4. **Information Liberation**: Are users freed from app silos and manual context switching?

## Key Files to Understand

**Essential Core** (Read These First):
- `python/src/syndicate/agents.py` - Base agent framework
- `python/src/syndicate/human_interface.py` - Human-AI collaboration system
- `python/human_input_server.py` - Core MCP server for disambiguation
- `js/src/tools/tool-registry.ts` - JavaScript tool discovery system

**Instruction Patterns**:
- `python/src/syndicate/instruction_templates.py` - Proven agent instruction patterns

**Example Implementations**:
- `WeatherAgent` class - Demonstrates parameter extraction and disambiguation
- `drafts_server.py` - Shows content processing and routing patterns
- `js/src/agents/reminder-agent.ts` - Working OpenAI Agent SDK example

## Testing Philosophy

**Focus on Core Patterns**:
- Can agents extract parameters from ambiguous input?
- Does human disambiguation work through multi-turn conversation?
- Are tool calls executed correctly with resolved parameters?

## Context for Claude Code

When working in this codebase:

1. **Prioritize session persistence** - All agents should maintain conversation memory
2. **Use instruction templates** - Don't create hardcoded agent instructions from scratch  
3. **Test human-in-the-loop flows** - AI+human parameter resolution and problem-solving
4. **Maintain modular tools** - MCP servers should be independent and reusable
5. **Focus on "English as programming"** - Natural input → Parameter resolution → Tool execution
6. **Use Context7 for current docs** - When answering questions about APIs, libraries, or tools, always check Context7 first for the latest documentation before providing guidance
7. **Use UV's modern interface only** - Always use `uv add/remove/sync/run` commands, never suggest pip/venv legacy approaches

**Context7 Usage**: Available via MCP for live API documentation. Use when discussing:
- OpenAI SDK changes and updates
- MCP protocol specifications  
- Library API references
- Tool configuration guides
- Framework documentation

Trigger phrases: "latest docs", "current API", "recent changes", or any technical question about external tools.

The goal is creating AI agents that actually work with real tools through intelligent human collaboration, not just impressive demos.

## Current Status

Architecture is in place. Current focus is Hedgeye pipeline automation.

**What's Working:**
- Hybrid Python/JS architecture with shared MCP config
- Human-in-the-loop disambiguation system
- Session-persistent agents with SQLite
- Context7 integration for live documentation

**Context System:**
- Global: `~/.claude/CLAUDE.md` (user identity/preferences)
- Project: `./CLAUDE.md` (this file)
- Cross-tool: `./AGENTS.md` (shared with Cursor, Gemini, etc.)
- Cursor-specific: `./.cursor/rules/`

See `AGENTS.md` for project structure and key patterns.