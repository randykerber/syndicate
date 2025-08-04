# Syndicate

**Mission:** SiloSlayer Syndicate - AI agents for information liberation

Taming the "life-sucking beast" of information silos through coordinated AI agents executing intelligent content routing and human-AI collaboration.

## Architecture

### Hybrid Python + JavaScript System
- **`python/`** - Session-persistent agents and human-AI communication
- **`js/`** - Native tool integrations (Raycast, Drafts, Obsidian)  
- **`config/`** - Shared configuration and environment settings
- **`docs/`** - Unified documentation

### Core Components

#### Python Side (Agent Intelligence)
- **Session-persistent agents** with conversation memory (SQLiteSession)
- **Async human-AI communication** system with push notifications
- **Agent orchestration** and complex workflows
- **"English as programming language"** agent coordination

#### JavaScript Side (Tool Integration)  
- **Native app integrations** (Raycast extensions, Drafts actions)
- **MCP servers** for tool access and data exchange
- **Rich UI components** and automations
- **Apple Shortcuts** and iOS/macOS integration

## Quick Start

### Python Development
```bash
cd python
uv sync
python -m pytest tests/
```

### JavaScript Development  
```bash
cd js
npm install
npm test
```

### Configuration
Environment variables and shared settings are in `config/shared/`

## Development Environment

- **Single IntelliJ IDEA Ultimate project** for both languages
- **Claude Code integration** for AI-assisted development
- **Unified git repository** with atomic cross-language commits

## Core Patterns

### Session-Persistent Agents
```python
from syndicate import SyndicateAgent

agent = SyndicateAgent(
    name="ContentRouter",
    instructions="Route content to appropriate silos...",
    session_id="user_123"
)

response = await agent.chat("Where should I save this Luke Gromen podcast note?")
```

### Human-in-the-Loop Communication
```python
from syndicate import ask_human_choice

response = await ask_human_choice(
    agent_name="ContentRouter",
    question="Which vault for this financial content?", 
    options=["Obsidian Main", "Obsidian Tech", "Bear Notes"]
)
```

### Cross-Language Integration
```typescript
// JavaScript MCP server provides tools
// Python agents consume via MCP protocol
// Unified workflows across both languages
```

## Mission Components

### Universal Router
AI-powered content triage and routing system that breaks information out of app silos.

### Context Liberation  
Breaking information out of individual app silos into unified, searchable, AI-accessible formats.

### Human-AI Collaboration
Intelligent assistance that enhances human capability without replacement - agents ask for disambiguation, approval, and guidance.

### English as Programming Language
Natural language instructions drive agent behavior and coordination rather than rigid code structures.

## Project Status

**Foundation Phase Complete:**
- ✅ Session persistence with SQLiteSession
- ✅ Human-in-the-loop communication patterns
- ✅ Conversational disambiguation (Paris → choice → Paris, France)
- ✅ Push notification integration
- ✅ Hybrid Python+JavaScript architecture
- ✅ Clean project structure with organized configuration

**Next Phase:**
- SiloSlayer agent deployment
- Production mobile workflows
- Advanced cross-language integration