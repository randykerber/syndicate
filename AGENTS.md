# AGENTS.md - Silo-Slayer Syndicate Project

Cross-tool context for AI coding agents (Cursor, Claude Code, Gemini CLI, Codex, etc.)

---

## About the User

**Name**: Randy Kerber  
**Mac username**: rk  
**Location**: Cañon City, Colorado (America/Denver timezone)  
**Expertise**: Python, Scala, Apache Spark, TypeScript/JavaScript, Knowledge Graphs, Data Pipelines, Finance/Investing

### Dev Stack & Apps

**PKM**: Obsidian (Tech/Fin vaults), Bear (personal), Drafts (universal capture), Apple Notes  
**Productivity**: Raycast, Things, Apple Reminders (alerts only), 1Password  
**Dev Tools**: Warp (terminal), IntelliJ, Cursor, Emacs, Claude Code  
**Browsers**: Arc (default), Chrome, Safari

---

## Project Overview

The **Silo-Slayer Syndicate System (SSS)** is an agentic AI framework designed to break users out of "app silos" and create intelligent human-AI collaborative workflows.

**Core Mission**: Information Liberation through "English as Programming Language"
- Natural language input → AI parameter extraction → Tool API calls
- Multi-turn Human-AI dialogue to resolve ambiguity
- Hybrid Python/JavaScript architecture connected via MCP (Model Context Protocol)

**Current Focus**: Hedgeye financial data pipeline automation (email parsing → CSV → merge → enrichment)

### Why Hybrid Python/JavaScript

- **Python**: Superior AI/ML ecosystem, mature MCP servers, agent orchestration
- **JavaScript**: Native app integrations (Raycast, Drafts, Obsidian plugins), rich UI
- **MCP Protocol**: Language-agnostic bridge enabling tool reuse across both

---

## Project Structure

```
syndicate/
├── AGENTS.md             # Cross-tool context (this file)
├── CLAUDE.md             # Claude Code specific
├── .cursor/rules/        # Cursor-specific rules (*.mdc)
├── python/
│   ├── src/
│   │   ├── sss/          # Silo-Slayer Syndicate agent framework
│   │   ├── hedgeye/      # Hedgeye data pipeline package
│   │   ├── fin/          # Financial data utilities
│   │   ├── ace/          # ACE context builder tools
│   │   └── shared/       # Shared utilities
│   ├── scripts/          # Production scripts
│   └── servers/          # MCP servers
├── js/src/               # Native tool integrations
├── config/               # Shared MCP configuration
├── data/ace/             # ACE Context Factory
│   ├── warehouse/        # Source parts library
│   └── FACTORY-MODEL.md  # Two-stage assembly model
└── docs/                 # Documentation
```

**External Data**: `/Users/rk/d/downloads/hedgeye/` (NOT in project, use absolute paths)

---

## Development Environment

### Primary Machine
- **Mac Studio** (hostname: rstudio)
- Apple M4 Max, 64GB unified memory
- macOS 26 "Tahoe"

### Terminal & Shell
- **Terminal**: Warp (Pro)
- **Shell**: zsh (interactive), bash (scripts)
- **OS**: macOS = BSD userland, NOT GNU coreutils

### Package Management

**Python** - Use `uv` (MANDATORY):
```bash
uv sync                    # Install dependencies
uv add package-name        # Add new dependency
uv run python script.py    # Run with project venv
uv run pytest              # Run tests
```
**NEVER suggest**: `pip install`, `python -m venv`

**JavaScript** - Use `npm`:
```bash
npm install                # Install dependencies
npm run build              # Build TypeScript
npm test                   # Run tests
```

**Node Version**: Use `fnm` (mandatory)

### Code Formatting
- **Python**: Black (line length: 88), Ruff (linter), type hints required
- **TypeScript**: Prettier, strict mode, functional patterns preferred

---

## Code Style Summary

### Python
- Follow PEP 8, type hints for all function signatures
- Docstrings: Google or NumPy style
- Async: Use `async/await` for I/O, `asyncio.gather()` for parallel
- Error handling: Explicit exception types, no bare `except:`

### JavaScript/TypeScript
- TypeScript for type safety
- Prefer `const` over `let`, never `var`
- Functional patterns preferred over classes
- Async/await, not callbacks

---

## Key Patterns

### Core Pattern: Parameter Extraction + Disambiguation

```
Human: "Add this to my investment notes"
Agent: Analyzes content → Identifies "investment" → Routes to Obsidian Fin vault
Agent: Missing filename → "What should I call this note?"
Human: "Luke Gromen Fed analysis"
Agent: Creates note with extracted parameters
```

This is the fundamental pattern: natural language → parameter extraction → human disambiguation when needed → tool execution.

### Session Persistence
- Agents inherit from `SyndicateAgent` for SQLite session storage
- Conversation history preserved across turns

### Human-in-the-Loop
- `ask_human_choice()` and `ask_human_text()` from `human_interface.py`
- Push notifications via `push_server.py`
- File-based async queue for human responses

### MCP Configuration
- Global registry: `~/.config/mcp/servers/`
- Project config: `./config/mcp-config.json`
- Python servers: `./python/servers/`

---

## Key Files

### Syndicate Framework
- `python/src/syndicate/agents.py` - Base SyndicateAgent class
- `python/src/syndicate/human_interface.py` - Human-AI interaction
- `python/servers/human_input_server.py` - MCP disambiguation server

### Hedgeye Pipeline
- `python/scripts/hedgeye/` - Pipeline scripts
- `/Users/rk/d/downloads/hedgeye/` - External data (absolute paths!)

---

## Response Preferences

### Style
- **Concise and direct** - No unnecessary preambles
- **Structured** - Markdown headings, bullet points, tables
- **Plan-then-execute** - Show plan, then commands, then ask confirm for destructive ops

### Safety
- **Ask before**: Modifying global configs, destructive commands, files outside project
- **Prefer**: Project-local configs, reversible changes, dry-run first
- **Never**: Commit secrets, use `rm -rf` without confirmation

---

## Version Control

- **VCS**: Git
- **Host**: GitHub (username: randykerber)
- **Repo Root**: `~/gh/randykerber/`

---

## Context Files

- `AGENTS.md` (this file) - Cross-tool context
- `CLAUDE.md` - Claude Code specific (context map, skills)
- `.cursor/rules/` - Cursor-specific rules (modular)

---

**Remember**: This project is about empowering users through AI-assisted information liberation. Code should be clear, maintainable, and focused on solving real workflow problems.
