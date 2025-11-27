#!/usr/bin/env python3
"""
Simple demo of the new SSS Agent architecture using OpenAI Agents SDK.

Demonstrates:
- Creating a personal productivity agent
- Multi-turn conversation with automatic history
- Session persistence
"""

import asyncio
from sss.agents import PersonalProductivityAgent


async def main():
    print("=" * 60)
    print("SSS Agent Demo - Personal Productivity Assistant")
    print("=" * 60)
    print()

    # Create agent with persistent session
    agent = PersonalProductivityAgent(
        session_id="demo_session",
        model="gpt-4o-mini"  # Use mini for cost efficiency in demo
    )

    print(f"Agent: {agent.name}")
    print(f"Session: {agent.session_id}")
    print(f"Model: {agent.model}")
    print()

    # First turn - agent introduces itself
    print("=" * 60)
    print("Turn 1: Introduction")
    print("=" * 60)
    user_msg = "Hello! I need help organizing my notes."
    print(f"User: {user_msg}")

    response = await agent.chat(user_msg)
    print(f"\nAgent: {response}")
    print()

    # Second turn - agent remembers context
    print("=" * 60)
    print("Turn 2: Follow-up (tests memory)")
    print("=" * 60)
    user_msg = "I have about 50 unprocessed voice notes. What's the best way to tackle this?"
    print(f"User: {user_msg}")

    response = await agent.chat(user_msg)
    print(f"\nAgent: {response}")
    print()

    # Third turn - more specific request
    print("=" * 60)
    print("Turn 3: Specific task")
    print("=" * 60)
    user_msg = "I want to start with the most recent 5 notes. Can you help me process those?"
    print(f"User: {user_msg}")

    response = await agent.chat(user_msg)
    print(f"\nAgent: {response}")
    print()

    # Show conversation history
    print("=" * 60)
    print("Conversation History (stored in SQLite)")
    print("=" * 60)
    history = await agent.get_history()
    print(f"Total messages in session: {len(history)}")
    print()

    # Show last 4 messages (2 turns)
    print("Last 4 messages:")
    for msg in history[-4:]:
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        # Truncate long messages for display
        if isinstance(content, str):
            content_preview = content[:100] + "..." if len(content) > 100 else content
        else:
            content_preview = str(content)[:100] + "..."
        print(f"  {role}: {content_preview}")
    print()

    print("=" * 60)
    print("Demo complete!")
    print("=" * 60)
    print()
    print("Key features demonstrated:")
    print("  ✅ Automatic conversation history (SQLiteSession)")
    print("  ✅ Multi-turn context retention")
    print("  ✅ No manual history management required")
    print("  ✅ Clean, simple API")
    print()
    print(f"Session data saved in: sss_sessions.db")
    print(f"Session ID: {agent.session_id}")


if __name__ == "__main__":
    asyncio.run(main())
