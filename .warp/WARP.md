---
id: syndicate.warp.project
owner: Randy Kerber  
updated: 2025-09-07
scope: project
extends: ~/.warp/WARP.md
---

# Warp AI — Silo-Slayer Syndicate System (SSS)

This project-specific context extends your global WARP.md with SSS-specific patterns and workflows.

## Project Mission
**Information Liberation** through AI agents that break users out of "app silos" using natural language → parameter extraction → tool execution workflows.

## Architecture Overview

### Hybrid Multi-Language System
```
syndicate/
├── python/        # Agent orchestration, MCP servers, AI workflows  
├── js/            # Native integrations, rich UI, tool registry
├── config/        # Shared configuration (mcp-config.json)
└── .warp/         # Warp-specific project context (this file)
```

**Why Hybrid**: Python for AI/ML ecosystem + JavaScript for native tool integrations, unified by MCP Protocol.

## Core Development Patterns

### 1. Session-Persistent Agents
All agents inherit conversation memory via SQLiteSession:
```python
from syndicate import SyndicateAgent

agent = SyndicateAgent(
    name="ContentRouter", 
    instructions="Route content to appropriate silos...",
    session_id="user_123"
)
```

### 2. Human-in-the-Loop Disambiguation  
**Essential Pattern**: AI + Human parameter resolution through conversation
- File-based async queue system (`HumanQueue`)
- Multi-turn workflows: "Paris" → "Which Paris?" → "1" → "Paris, France"
- Push notifications for mobile interaction

### 3. English as Programming Language
**Core Concept**: Natural language input → AI parameter extraction → Tool API calls
- No rigid forms or UIs - conversation resolves ambiguity
- Multi-turn dialogue for missing/ambiguous parameters

## Key File Locations

### Python Package (`python/`)
**Essential Core**:
- `src/syndicate/agents.py` - Base SyndicateAgent framework
- `src/syndicate/human_interface.py` - Async human-AI communication (**CRITICAL**)  
- `servers/human_input_server.py` - MCP server for disambiguation (**CRITICAL**)

**MCP Servers**: `human_input`, `push`, `drafts`, `accounts`, `market`

### JavaScript Package (`js/`)
**Core Components**:
- `src/tools/tool-registry.ts` - Central tool discovery (37 tools total)
- `src/agents/reminder-agent.ts` - Working OpenAI Agent SDK example
- `src/mcp/mcp-client-proper.ts` - MCP server communication

## Development Commands

### Python (UV Only - Modern Interface)
```bash
cd python/
uv sync                           # Install dependencies
uv add package-name              # Add dependency
uv run servers/human_input_server.py  # Run MCP server
uv run demos/wendy_weather.py    # Run agent demo
uv run pytest                    # Run tests
```

### JavaScript  
```bash
cd js/
npm install                      # Install dependencies  
npm run build                    # Build TypeScript
npm run tools                    # Tool inventory report
npm test                        # Run tests
```

### Shared Configuration
- **Single source**: `config/mcp-config.json` used by both languages
- **Python access**: via `shared_config.py` utility
- **Environment vars**: Substitution working in both languages

## Mission-Specific Context

### SiloSlayer Target
**Problem**: 1219+ unprocessed Drafts notes + daily information overflow
**Strategy**: AI-assisted triage to reduce growth from 50+/month to 5-10/month
**Tools**: Drafts server, content categorization, Obsidian/Bear routing

### Tool Ecosystem (37 Total)
- **Custom Tools (4)**: File ops, system commands, reminders  
- **MCP Tools (31)**: Filesystem, Obsidian (2 vaults), sequential-thinking, Tavily, Context7
- **OpenAI Built-ins (3)**: web_search, code_interpreter, file_search

## Testing Philosophy
Focus on core patterns:
- ✅ Can agents extract parameters from ambiguous input?
- ✅ Does human disambiguation work through conversation?
- ✅ Are tool calls executed correctly with resolved parameters?

## Current Status: Architecture Complete, Development-Ready

### ✅ Foundation Complete
- Session persistence with SQLiteSession
- Human-in-the-loop communication patterns  
- Conversational disambiguation flows
- Push notification integration
- Hybrid Python+JavaScript architecture
- Clean project structure with shared configuration

### 🎯 Next Implementation Priorities  
1. End-to-end parameter extraction → disambiguation → tool execution demos
2. Production Drafts processing workflows
3. Agent instruction template expansion
4. OpenAI Agents SDK session refactoring evaluation

## Warp-Specific Notes

**Context Strategy**:
- This file: Project-specific SSS patterns
- `~/.warp/WARP.md`: Global Randy Kerber context (user-level)
- `CLAUDE.md`: Detailed technical context (comprehensive reference)

**Key Differences from Claude Code**:
- Focus on **plan-then-execute** workflows vs. immediate coding
- Emphasize **tool composition** and **agent orchestration**  
- Prioritize **human-AI collaboration patterns** over pure automation

Success means: AI agents that work with real tools through intelligent human collaboration, not just demos.
