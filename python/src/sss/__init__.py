"""
SiloSlayer Syndicate - AI agents for information liberation

Core Components:
- agents: Session-persistent AI agents with conversation memory
- human_interface: Async human-AI communication system  
- sessions: SQLiteSession management and conversation persistence
- tools: Core SSS tools and utilities
"""

__version__ = "0.1.0"

from .agents import (
    SSSAgent,
    PersonalProductivityAgent,
    ContentRouterAgent,
)

# Legacy imports (may be deprecated)
# from .human_interface import HumanQueue, ask_human_choice, ask_human_approval, ask_human_text
# from .sessions import create_session, SessionManager

__all__ = [
    "SSSAgent",
    "PersonalProductivityAgent",
    "ContentRouterAgent",
]

