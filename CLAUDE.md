# CLAUDE.md - Silo-Slayer Syndicate Project

This file provides project-specific guidance to Claude Code when working with the Syndicate codebase.

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

**Environment Setup**:
```bash
cd python/
uv sync  # Install dependencies
```

**Running Agents**:
```bash
# Test individual MCP servers
uv run human_input_server.py
uv run push_server.py
uv run drafts_server.py

# Run agents with session persistence
python -c "from src.syndicate.agents import WeatherAgent; import asyncio; asyncio.run(WeatherAgent().chat('Paris'))"
```

**JavaScript Commands**:
```bash
cd js/
npm run build      # Build TypeScript
npm run tools      # Tool inventory report
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

**Context7 Usage**: Available via MCP for live API documentation. Use when discussing:
- OpenAI SDK changes and updates
- MCP protocol specifications  
- Library API references
- Tool configuration guides
- Framework documentation

Trigger phrases: "latest docs", "current API", "recent changes", or any technical question about external tools.

The goal is creating AI agents that actually work with real tools through intelligent human collaboration, not just impressive demos.

## Current Status: Architecture Complete, Development-Ready

### ✅ Recently Completed (August 2025)

**Project Structure Cleanup:**
- JavaScript project reorganized: proper test structure (`./js/tests/` not `./js/src/__tests__/`)
- Shared configuration implemented: single `./config/mcp-config.json` used by both Python and JavaScript
- Python config files moved from `./config/` to proper location in `./python/src/syndicate/`
- Context engineering system established in `./context/` folder

**Tool Ecosystem Validated:**
- **37 tools total**: 4 custom + 30 MCP + 3 OpenAI built-ins
- All tools discoverable through JavaScript ToolRegistry
- Shared MCP config working across languages
- Python utility (`shared_config.py`) for accessing shared configs

### 🎯 Core Architecture Status

**Two-Component Architecture Operational:**

1. **Tool Ecosystem**: 
   - MCP tools: filesystem, obsidian (2 vaults), sequential-thinking, tavily
   - Python MCP servers: human_input, push, drafts, accounts, market
   - JavaScript tools: file ops, system commands, reminders

2. **Human-AI Disambiguation System**:
   - `HumanQueue`: File-based async request/response ✅
   - `ask_human_choice()` and `ask_human_text()` functions ✅
   - Push notifications via Pushover ✅
   - Session-persistent agents with SQLite ✅

**Configuration Management:**
- Shared configs: `./config/mcp-config.json` (language-agnostic)
- Python-specific: `./python/src/syndicate/mcp_agent_configs.py`, `weather_config.py`
- JavaScript reads shared config via `../config/mcp-config.json`
- Environment variable substitution working in both languages

### 🚀 Next Implementation Priorities

1. **End-to-end demo** - Complete parameter extraction → human disambiguation → tool execution
2. **Production workflows** - Connect to real Drafts processing, note routing
3. **Context engineering** - Finalize tiered context strategy (Obsidian → tools)
4. **Agent templates** - Expand instruction templates for different use cases
5. **OpenAI Agents SDK session refactoring** - Explore replacing custom SQLite session persistence with new automatic conversation history feature (March 2025 release)

### 🔧 Technical Status

**Development Environment:**
- IntelliJ configured for JavaScript/TypeScript with proper test structure
- Python package structure following modern standards
- Build processes working: `npm run build` (JS), `uv sync` (Python)

**Tool Integration:**
- JavaScript: 37 tools via ToolRegistry, MCP clients operational
- Python: Shared config utilities, agent framework ready
- Both languages can access same MCP servers and configuration

**Context System:**
- Global context: `~/.claude/CLAUDE.md` (user identity/preferences)
- Project context: `./CLAUDE.md` (working memory, updated freely)
- Documentation: `./docs/` (human-readable explanations)
- Context source: `./context/` (canonical Obsidian-managed files)

**Context7 Integration:**
- Installed local MCP server: `npm i -g @upstash/context7-mcp`
- Configured as stdio server (better than remote HTTP)
- Available globally via user-scoped MCP configuration
- **Usage pattern**: 2-step process (resolve-library-id → get-library-docs) - documented in global ~/.claude/CLAUDE.md
- **Status**: ✅ Working - successfully retrieved current Claude Code and OpenAI Agents SDK documentation

**Ready for focused development on core agent patterns and real-world tool integration.**