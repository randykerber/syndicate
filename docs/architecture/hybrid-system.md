# Hybrid Python+JavaScript Architecture

## Overview

The Syndicate system uses a hybrid architecture where Python handles AI agent intelligence and JavaScript provides native tool integrations, unified through the MCP (Model Context Protocol).

## Design Principles

### Language Separation by Strengths
- **Python**: Agent orchestration, AI workflows, session persistence, complex logic
- **JavaScript**: Native app integrations, UI components, platform-specific automations

### MCP as Integration Layer
- **Protocol-based communication** enables language-agnostic tool sharing
- **Loose coupling** between Python agents and JavaScript tools
- **Independent deployment** of each language component

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Syndicate System                        │
├─────────────────────────────────────────────────────────────┤
│  Python Side (Agent Intelligence)                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ SyndicateAgent  │  │ WeatherAgent    │  │ ContentRouter│ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│           │                    │                    │       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           Session Persistence (SQLite)               │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                   MCP Protocol Layer                        │
├─────────────────────────────────────────────────────────────┤
│  JavaScript Side (Tool Integration)                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Raycast         │  │ Drafts          │  │ Obsidian    │ │
│  │ Extensions      │  │ Actions         │  │ Plugins     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Communication Patterns

### Python → JavaScript
- Python agents call MCP tools provided by JavaScript servers
- Agents request tool execution via MCP protocol
- JavaScript executes native tool operations and returns results

### JavaScript → Python  
- JavaScript tools can trigger Python agent workflows
- Push notifications alert agents to new content
- Human responses flow back to waiting agent processes

## Benefits

1. **Best of Both Worlds**: Leverage each language's ecosystem strengths
2. **Independent Evolution**: Each side can evolve without breaking the other
3. **Flexible Deployment**: Deploy to different environments as needed
4. **Developer Experience**: Use preferred tools and IDEs for each language