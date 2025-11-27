"""
Base agent class for Silo-Slayer Syndicate.

This module provides the core abstraction layer for SSS agents,
designed to work with OpenAI Agents SDK with potential future
support for other providers (Anthropic, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Literal, Optional
from pathlib import Path

# OpenAI Agents SDK imports
from agents import Agent, Runner, SQLiteSession


class SSSAgent(ABC):
    """
    Base class for all SSS agents.

    Provides a unified interface for building conversational AI agents
    with persistent memory, tool use, and human-in-the-loop capabilities.

    Philosophy:
    - English as programming language
    - Multi-turn conversation with memory
    - Parameter extraction from natural language
    - Human disambiguation when needed
    - Tool execution with proper permissions
    """

    def __init__(
        self,
        name: str,
        instructions: str,
        tools: Optional[List[Callable]] = None,
        session_id: Optional[str] = None,
        session_db: str = "sss_sessions.db",
        model: str = "gpt-4o",
        provider: Literal["openai"] = "openai",
    ):
        """
        Initialize an SSS agent.

        Args:
            name: Agent name (used for identification)
            instructions: System instructions/prompt for the agent
            tools: List of tool functions the agent can use
            session_id: Session ID for conversation persistence (default: agent name)
            session_db: Path to SQLite database for session storage
            model: Model to use (e.g., "gpt-4o", "gpt-4o-mini")
            provider: Provider to use (currently only "openai" supported)
        """
        self.name = name
        self.instructions = instructions
        self.tools = tools or []
        self.model = model
        self.provider = provider

        # Session management - automatic conversation history
        self.session_id = session_id or f"{name.lower().replace(' ', '_')}_session"
        self.session = SQLiteSession(self.session_id, session_db)

        # Create the underlying agent
        self._agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the underlying OpenAI Agent."""
        if self.provider == "openai":
            return Agent(
                name=self.name,
                instructions=self.instructions,
                model=self.model,
                tools=self.tools,
            )
        else:
            raise NotImplementedError(f"Provider {self.provider} not yet supported")

    async def chat(self, message: str) -> str:
        """
        Send a message to the agent and get a response.

        Conversation history is automatically maintained via the session.

        Args:
            message: User message

        Returns:
            Agent's response text
        """
        result = await Runner.run(
            self._agent,
            message,
            session=self.session
        )
        return result.final_output

    def chat_sync(self, message: str) -> str:
        """
        Synchronous version of chat().

        Args:
            message: User message

        Returns:
            Agent's response text
        """
        result = Runner.run_sync(
            self._agent,
            message,
            session=self.session
        )
        return result.final_output

    async def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history from the session.

        Args:
            limit: Maximum number of messages to retrieve (None = all)

        Returns:
            List of conversation messages
        """
        return await self.session.get_items(limit=limit)

    async def clear_history(self):
        """Clear all conversation history for this session."""
        await self.session.clear_session()

    def add_tool(self, tool: Callable):
        """
        Add a new tool to the agent.

        Args:
            tool: Tool function (should be decorated with @tool if needed)
        """
        self.tools.append(tool)
        # Recreate agent with new tools
        self._agent = self._create_agent()


class PersonalProductivityAgent(SSSAgent):
    """
    Specialized agent for personal productivity and automation tasks.

    Designed for:
    - Processing notes and drafts
    - Routing information to proper destinations
    - Task management
    - Calendar and reminder assistance
    """

    def __init__(
        self,
        name: str = "ProductivityAssistant",
        session_id: Optional[str] = None,
        **kwargs
    ):
        instructions = """You are a personal productivity assistant.

Your role is to help the user:
- Process notes and drafts from various sources
- Route information to the appropriate destination (Obsidian, Bear, 1Password, etc.)
- Extract key information from natural language input
- Ask clarifying questions when needed
- Execute productivity-related tasks

When uncertain about:
- Which app/vault to use
- File naming conventions
- Categories or tags

Always ask the user for clarification rather than guessing.

Be concise but thorough. Focus on getting things done efficiently."""

        super().__init__(
            name=name,
            instructions=instructions,
            session_id=session_id,
            **kwargs
        )


class ContentRouterAgent(SSSAgent):
    """
    Specialized agent for routing content from input sources (Drafts, voice notes)
    to appropriate destinations (Obsidian vaults, Bear, etc.).

    Core capability: "English as programming language" for destination routing.
    """

    def __init__(
        self,
        name: str = "ContentRouter",
        session_id: Optional[str] = None,
        **kwargs
    ):
        instructions = """You are a content routing specialist.

Your job is to analyze incoming content and determine:
1. What type of content it is (note, task, reference, password, etc.)
2. Where it should be stored (which app, which vault, which folder)
3. What metadata to attach (tags, categories, dates)

When routing content, extract:
- Subject/title from the content
- Appropriate tags
- Target destination

Ask for clarification when:
- Multiple valid destinations exist
- The content type is ambiguous
- Additional metadata is needed

Be decisive but ask when truly uncertain."""

        super().__init__(
            name=name,
            instructions=instructions,
            session_id=session_id,
            **kwargs
        )
