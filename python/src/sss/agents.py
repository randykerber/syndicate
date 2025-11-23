"""
Syndicate Agents - Session-persistent AI agents with conversation memory

Core agent patterns for the SiloSlayer Syndicate system.
"""

import asyncio
import os
from datetime import datetime
from typing import Optional
from agents import Agent, Runner, SQLiteSession


class   SyndicateAgent:
    """Base class for session-persistent Syndicate agents."""

    def __init__(self,
                 name: str,
                 instructions: str,
                 session_id: Optional[str] = None,
                 model: str = "gpt-4o-mini"):
        """
        Initialize a Syndicate agent with session persistence.

        Args:
            name: Agent name
            instructions: System instructions for the agent
            session_id: Unique session identifier (auto-generated if None)
            model: OpenAI model to use
        """
        self.name = name
        self.instructions = instructions
        self.model = model
        self.session_id = session_id or f"{name.lower()}_{int(datetime.now().timestamp())}"
        self.session = None
        self.agent = None

    def create_session(self, sessions_dir: str = "./syndicate_sessions") -> SQLiteSession:
        """Create persistent SQLite session for conversation memory."""
        os.makedirs(sessions_dir, exist_ok=True)
        db_path = os.path.join(sessions_dir, f"{self.session_id}.db")
        self.session = SQLiteSession(self.session_id, db_path=db_path)
        print(f"🗄️  Session created: {self.session_id}")
        return self.session

    def create_agent(self) -> Agent:
        """Create OpenAI Agent SDK agent."""
        self.agent = Agent(
            name=self.name,
            instructions=self.instructions,
            model=self.model
        )
        return self.agent

    async def chat(self, message: str, max_turns: int = 5) -> str:
        """
        Send message to agent with session persistence.

        Args:
            message: User message
            max_turns: Maximum conversation turns

        Returns:
            Agent response string
        """
        if not self.session:
            self.create_session()

        if not self.agent:
            self.create_agent()

        result = await Runner.run(
            self.agent,
            message,
            session=self.session,
            max_turns=max_turns
        )

        # Extract clean response
        if hasattr(result, 'final_output'):
            return str(result.final_output)
        return str(result)

    def clear_session(self):
        """Clear conversation history."""
        if self.session:
            self.session.clear_session()
            print(f"🗑️  Session cleared: {self.session_id}")


class WeatherAgent(SyndicateAgent):
    """Weather assistant with location disambiguation capabilities."""

    def __init__(self, session_id: Optional[str] = None):
        instructions = f"""
You are a friendly and helpful weather assistant. Your role is to provide weather forecasts for locations chosen by humans.

CORE BEHAVIOR:
- You are conversational and helpful
- You help humans specify exact locations when queries are ambiguous
- You can engage in natural dialogue to resolve uncertainty
- You provide weather forecasts once locations are clarified

PARAMETER EXTRACTION AND DISAMBIGUATION:
1. If a location is clearly unambiguous (like "Denver, Colorado"), proceed directly
2. If a location might be ambiguous (like "Springfield"), offer numbered options for clarification
3. If you receive a misspelled location, correct it and show the proper spelling (e.g., "Coloraddo Springs" → "Colorado Springs, Colorado, USA")
4. Always include full location details in responses (e.g., "Guadalajara" → "Guadalajara, Jalisco, Mexico")
5. For common locations, expand to full names (e.g., "Denver" → "Denver, Colorado, USA")

CONVERSATION FLOW:
- Greet users warmly when they first interact
- Ask clarifying questions when needed
- Provide numbered options for ambiguous inputs
- Accept both numbered responses and text responses
- Use tools to accomplish tasks once parameters are clarified
- Offer to help with additional requests after each completion

TERMINATION:
- Users can say "exit", "goodbye", "quit", or similar to end the session
- Always acknowledge termination gracefully

TOOL INTEGRATION:
- Use available tools to accomplish tasks once parameters are resolved
- If tool calls fail due to ambiguous parameters, engage human for clarification
- Always confirm successful tool execution with clear feedback

Current date and time: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
"""

        super().__init__(
            name="WeatherAgent",
            instructions=instructions,
            session_id=session_id
        )


class ContentRouter(SyndicateAgent):
    """Content routing agent for SiloSlayer operations."""

    def __init__(self, session_id: Optional[str] = None):
        instructions = """
You are a content routing specialist for the SiloSlayer Syndicate.

Your job is to help humans decide where to store different types of content:

ROUTING OPTIONS:
1. Obsidian Main vault - Financial analysis, investing, market research
2. Obsidian Tech vault - Development, AI tools, technical documentation  
3. Bear notes - Personal reference, mobile-accessible content
4. Digital junk drawer - Quick reference, temporary items
5. 1Password - Credentials, codes, ephemeral reference data

When given content, analyze it and suggest the best destination with reasoning.
If unclear, offer numbered options and ask for clarification.

Remember our conversation and learn the human's preferences over time.
"""

        super().__init__(
            name="ContentRouter",
            instructions=instructions,
            session_id=session_id
        )


# Utility functions for common agent patterns
async def create_weather_agent(session_id: Optional[str] = None) -> WeatherAgent:
    """Create a weather agent with session persistence."""
    return WeatherAgent(session_id=session_id)


async def create_content_router(session_id: Optional[str] = None) -> ContentRouter:
    """Create a content routing agent with session persistence."""
    return ContentRouter(session_id=session_id)


# Demo functions for testing
async def demo_weather_disambiguation():
    """Demo weather location disambiguation with session persistence."""
    print("🌤️ SyndicateAgent Weather Demo")
    print("=" * 40)

    agent = WeatherAgent("weather_demo")

    # Test the Paris disambiguation sequence
    messages = [
        "Paris",  # Should trigger disambiguation
        "1"       # Should remember and choose France
    ]

    for i, message in enumerate(messages, 1):
        print(f"\n💬 Turn {i}: {message}")
        response = await agent.chat(message)
        print(f"🌤️ WeatherAgent: {response}")
        print("-" * 30)

    print("\n✅ Demo completed!")


if __name__ == "__main__":
    asyncio.run(demo_weather_disambiguation())

