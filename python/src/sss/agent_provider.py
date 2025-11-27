"""
Agent Provider Interface and Implementations

This module defines a provider pattern for abstracting the underlying AI agent SDK.
"""

import os
from typing import Optional, List, Callable, Protocol
from agents import Agent, Runner, SQLiteSession


class AgentProvider(Protocol):
    """
    Protocol for an underlying AI agent implementation.
    This allows swapping out the agent backend (e.g., OpenAI, Anthropic).
    """
    async def chat(self, message: str, max_turns: int = 5) -> str:
        ...

    def clear_session(self):
        ...


class OpenAIAgentProvider:
    """
    An agent provider that uses the openai-agents SDK.
    """
    def __init__(self,
                 name: str,
                 instructions: str,
                 session_id: str,
                 model: str,
                 tools: Optional[List[Callable]] = None,
                 sessions_dir: str = "./syndicate_sessions"):
        self.name = name
        self.instructions = instructions
        self.session_id = session_id
        self.model = model
        self.tools = tools or []
        self.sessions_dir = sessions_dir

        self._session = self._create_session()
        self._agent = self._create_agent()

    def _create_session(self) -> SQLiteSession:
        """Create persistent SQLite session for conversation memory."""
        os.makedirs(self.sessions_dir, exist_ok=True)
        db_path = os.path.join(self.sessions_dir, f"{self.session_id}.db")
        session = SQLiteSession(self.session_id, db_path=db_path)
        print(f"🗄️  Session created via OpenAI Provider: {self.session_id}")
        return session

    def _create_agent(self) -> Agent:
        """Create OpenAI Agent SDK agent."""
        return Agent(
            name=self.name,
            instructions=self.instructions,
            model=self.model,
            tools=self.tools if self.tools else None
        )

    async def chat(self, message: str, max_turns: int = 5) -> str:
        """
        Send message to agent with session persistence using openai-agents Runner.
        """
        result = await Runner.run(
            self._agent,
            message,
            session=self._session,
            max_turns=max_turns
        )

        # Extract clean response
        if hasattr(result, 'final_output'):
            return str(result.final_output)
        return str(result)

    def clear_session(self):
        """Clear conversation history."""
        if self._session:
            self._session.clear_session()
            print(f"🗑️  Session cleared via OpenAI Provider: {self.session_id}")
