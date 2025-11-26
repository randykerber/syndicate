#!/usr/bin/env python3
"""
Interactive chat with Wendy the Weather Agent

Demonstrates Human-Agent Interaction (HAI) pattern with disambiguation.
Type your messages to chat with Wendy. Type 'quit' to exit.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sss.agents import WeatherAgent


async def chat_with_wendy():
    """Interactive REPL for chatting with Wendy weather agent."""
    print("=" * 60)
    print("🌤️  Chat with Wendy - Weather Agent Demo")
    print("=" * 60)
    print("Wendy can help with weather queries and demonstrates the")
    print("Human-Agent Interaction (HAI) pattern with disambiguation.")
    print()
    print("Try: 'Paris', 'Springfield', 'Denver', 'coloraddo springs'")
    print("Type 'quit' to exit")
    print("=" * 60)
    print()

    # Create agent with session persistence
    agent = WeatherAgent("wendy_interactive")

    print("Wendy: Hello! I'm Wendy, your weather assistant. What location would you like to know about?")
    print()

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            # Check for exit
            if user_input.lower() in ["quit", "exit", "goodbye", "bye"]:
                print()
                print("Wendy: Goodbye! Have a great day! 👋")
                print()
                break

            # Skip empty input
            if not user_input:
                continue

            # Send to agent and get response
            response = await agent.chat(user_input)

            # Display response
            print()
            print(f"Wendy: {response}")
            print()

        except KeyboardInterrupt:
            print()
            print()
            print("Wendy: Interrupted. Goodbye! 👋")
            print()
            break
        except Exception as e:
            print()
            print(f"❌ Error: {e}")
            print()
            break


if __name__ == "__main__":
    asyncio.run(chat_with_wendy())
