# Syndicate Python

Python agent intelligence for the SiloSlayer Syndicate system.

## Features

- Session-persistent agents with conversation memory
- Async human-AI communication system  
- Agent orchestration and complex workflows
- "English as programming language" coordination

## Quick Start

```bash
uv sync
python -m pytest tests/
```

## Core Components

- **SyndicateAgent**: Base class for session-persistent agents
- **WeatherAgent**: Weather information with human disambiguation
- **ContentRouter**: Intelligent content routing agent
- **HumanQueue**: Async communication with push notifications
- **SessionManager**: SQLite session persistence

## Usage

```python
from sss import SyndicateAgent

agent = SyndicateAgent(
    name="ContentRouter",
    instructions="Route content to appropriate silos...",
    session_id="user_123"
)

response = await agent.chat("Where should I save this note?")
```