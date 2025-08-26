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

**Tool Inventory (37 Total)**:
- **Custom Tools (4)**: File ops, system commands, reminders
- **MCP Tools (30)**: Filesystem, Obsidian, sequential-thinking, Tavily
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

The goal is creating AI agents that actually work with real tools through intelligent human collaboration, not just impressive demos.

## Current Status: Ready for Implementation

### ✅ Confirmed Working Components

**Two-Component Architecture Validated:**

1. **Tool Ecosystem**: 
   - 30 MCP tools (filesystem, obsidian, sequential-thinking, tavily)
   - 5 Python MCP servers (human_input, push, drafts, accounts, market)
   - 4 JavaScript custom tools (file ops, system commands)

2. **Human-AI Disambiguation System**:
   - `HumanQueue`: File-based async request/response ✅
   - `ask_human_choice()`: Present options for disambiguation ✅
   - `ask_human_text()`: Custom text input ✅
   - Push notifications via Pushover ✅
   - Session-persistent agents with SQLite ✅

### 🎯 Core Pattern Proof-of-Concept

**The Test Case Pattern**:
- AI agent receives ambiguous request (e.g., "Save this Luke Gromen note")
- AI identifies fillable vs ambiguous parameters
- AI initiates conversation with human ("Which vault? What filename?")
- Human provides disambiguation via file-based queue
- AI executes tool with resolved parameters

### 🚀 Next Session Priorities

1. **Create working end-to-end demo** - Complete the pattern with simulated responses
2. **Connect to real MCP tools** - Make actual tool calls after disambiguation  
3. **Test push notification flow** - Verify mobile alerts work
4. **Build production workflow** - File processing, note routing, etc.

### 🔧 Technical Status

**Python**: `from agents import Agent, Runner, SQLiteSession` ✅ Working
**JavaScript**: `const { Agent, run } = require('@openai/agents')` ✅ Working  
**SyndicateAgent**: Session persistence functional ✅
**Human Interface**: All functions operational, queue system ready ✅

**Foundation is solid and ready for implementation.**