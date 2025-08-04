# Essential Agentic System Architecture

## Minimal Agentic System (4 Essential Elements)

### 1. Agent (LLM)
- **Role**: Decision maker that can reason about what to do next
- **Critical capability**: Function calling / tool use
- **Remove this**: No intelligence, just a script

### 2. Tool(s)
- **Role**: Actions the agent can perform in the world
- **Critical capability**: Do something beyond generating text
- **Remove this**: Agent can only talk, not act (just a chatbot)

### 3. Tool Interface Protocol
- **Role**: Standardized way for agent to discover and call tools
- **Critical capability**: Dynamic tool discovery + execution
- **Remove this**: Agent can't know what tools exist or how to use them

### 4. Execution Loop
- **Role**: Orchestrates agent → tool selection → tool execution → agent response
- **Critical capability**: Multi-turn reasoning with tool results
- **Remove this**: Single-shot only, no iterative problem solving

## MCP Architecture

```
Agent (OpenAI/Claude) ← MCP Client ← MCP Server → Tools
     ↑                    ↑            ↑         ↑
  Reasoning           Protocol    Discovery   Actions
```

**MCP's role**: It IS the "Tool Interface Protocol" - the standardized communication layer that lets any agent discover and use any tool without custom integration.

**The magic**: Agent asks "what tools are available?", MCP server responds with tool schemas, agent decides which to use, calls it, gets results, continues reasoning.

**Without MCP**: You'd need custom integration code for every agent ↔ tool combination. With MCP: Universal plug-and-play.

## Minimal Working Example

1. Agent: "I need to read a file"
2. MCP Client: "What tools are available?" 
3. MCP Server: "I have read_file(path)"
4. Agent: "Call read_file('/path/to/file')"
5. Tool executes, returns content
6. Agent: "Based on the file content, I should..."

## Key Insight

Remove any of these 4 elements and it's no longer agentic - just automation or chat.

## Agent vs Actor Terminology

### Autonomous Actors (Traditional ABM)
- **World Agents**: Other apps (Drafts, Obsidian, Apple Reminders) acting autonomously
- **System Agents**: Schedulers, monitors, file watchers, notification systems
- **Rule Agents**: Simple logic-based actors ("if X then Y")
- **Human Agents**: You, other users making decisions in the system
- **Environmental Agents**: External systems, APIs, data sources

### LLM Assistants (OpenAI/Anthropic style)
- **Chat Assistants**: LLM + tool-calling wrapper (OpenAI Agent SDK)
- **Reasoning Engines**: The LLM component that does the thinking
- **Tool Orchestrators**: The wrapper that manages tool execution

## Multi-Actor Architecture Insight

**Current limitation**: Everything non-LLM gets flattened into "tools"

**Better model**: Network of autonomous actors (including human) with communication protocols

**MCP as Universal Actor Interface**: Every actor (human, AI, app) can be exposed as an MCP tool with text input/output, creating a uniform communication protocol across all system participants.

## Agent Escape Hatch Pattern

**Standard MCP Server** provides structured tools for common operations:
- `create_draft()`, `search_drafts()`, `get_draft()`

**Plus Agent Tool** for complex/ambiguous requests:
- `drafts_agent("Find that draft about the project we discussed last week with budget concerns")`

**Like customer service**: Press 1-9 for common tasks, Press 0 for human agent when you need flexible intelligence.

## Specialist Agent Model

Instead of one generic AI trying to know everything, create specialized agents:

- **`drafts_agent`**: Expert in Drafts docs, APIs, scripting, workflows
- **`obsidian_agent`**: PKM specialist understanding graph relationships, plugins
- **`reminders_agent`**: Task management expert knowing GTD, scheduling systems

Each becomes a domain expert, bilingual translator, and workflow consultant for their specific system.