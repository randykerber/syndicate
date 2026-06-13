# CLAUDE.md - Silo-Slayer Syndicate Project

This file provides project-specific guidance to Claude Code when working with the Syndicate codebase.

---

## 🗺️ Context Map

**⚠️ FIRST**: Read `data/ace/CONTEXT_MAP.md` — master index of available context sources and loading instructions.

---

## Current Projects

- Hedgeye pipeline automation (subproject: `python/hedgeye/` within this repo)
- Context Engineering + MCP (Model Context Protocol) for AI Agent tools
- Silo-Slayer Syndicate System (SSS) — agent network to break app/data silos

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
- `push_server.py` - Mobile push notifications via Pushover (subscription lapsed; account exists, reactivate if needed)
- `drafts_server.py` - Drafts processing for SiloSlayer mission
- `accounts_server.py` - Investment/trading account management
- `market_server.py` - Stock price simulation

### JavaScript Package (`js/`)

**Core Components** (`src/`):
- `agents/reminder-agent.ts` - Working OpenAI Agent SDK example
- `tools/tool-registry.ts` - Central tool discovery (37 tools)
- `tools/simple-tools.ts` - File, system operations
- `mcp/mcp-client-proper.ts` - MCP server communication

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
- `human_input_server.py` - Human disambiguation
- `push_server.py` - Mobile notifications (Pushover subscription lapsed; reactivate if needed)

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

### Running Syndicate Code

**MCP Servers**:
```bash
cd python/
uv run servers/human_input_server.py
uv run servers/push_server.py
uv run servers/drafts_server.py
```

**Agents**:
```bash
uv run demos/wendy_weather.py
uv run python -c "from src.syndicate.agents import WeatherAgent; import asyncio; asyncio.run(WeatherAgent().chat('Paris'))"
```

**Tests & tools**:
```bash
uv run pytest
uv run black .
uv run ruff check
```

**JavaScript**:
```bash
cd js/
npm run build        # Build TypeScript
npm run tools        # Tool inventory report
```

## Design Philosophy

**Not Another Chatbot**: Agents execute real tool calls with extracted parameters
**Not Rule-Based Automation**: AI handles ambiguity and edge cases through conversation
**Not Rigid APIs**: Natural language instructions converted to precise tool execution
**Not Single-Language**: Hybrid architecture leverages each language's strengths

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

## Available CC Skills (Syndicate-specific)

- `/hedgeye-pipelines` — Hedgeye pipeline conventions: data paths, file naming, CSV processing, three-tier price fallback, key files. Load when working on Hedgeye code.

## Current Status

Architecture is in place. Current focus is Hedgeye pipeline automation.

**What's Working:**
- Hybrid Python/JS architecture with shared MCP config
- Human-in-the-loop disambiguation system
- Session-persistent agents with SQLite

**Context System:**
- Global: `~/.claude/CLAUDE.md` (user identity/preferences)
- Project CC: `./CLAUDE.md` (this file) + `.claude/skills/` (hedgeye-pipelines)
- Cross-tool: `./AGENTS.md` (shared with Cursor, Gemini, etc.)
- Cursor-specific: `./.cursor/rules/`

## Knowledge base (Clob)

Obsidian project hub: `_Claude/ClobProjects/syndicate/SS Syndicate.md`
Claude entry point: `_Claude/ClobProjects/syndicate/index.md`
Read index.md at session start for project state and session list.

## Compaction instructions

When compacting, preserve:
- Current task and immediate next steps
- Decisions made and their rationale
- File paths created or modified
- Open questions not yet resolved
- Pointer to Obsidian session summary
