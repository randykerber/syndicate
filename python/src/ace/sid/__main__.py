"""
CLI entry point for SID - System Instruction Deployer.

Usage:
    uv run python -m ace.sid deploy claude
    uv run python -m ace.sid deploy gemini
    uv run python -m ace.sid deploy all
"""

import sys
from pathlib import Path

from ace.sid.claude_builder import build_claude_context


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 3:
        print("Usage: python -m ace.sid deploy <agent>")
        print("\nAgents:")
        print("  claude  - Build and deploy CLAUDE.md")
        print("  gemini  - Build and deploy GEMINI.md (coming soon)")
        print("  warp    - Build and deploy WARP.md (coming soon)")
        print("  all     - Build and deploy all agents (coming soon)")
        sys.exit(1)

    command = sys.argv[1]
    agent = sys.argv[2]

    if command != "deploy":
        print(f"Unknown command: {command}")
        print("Available commands: deploy")
        sys.exit(1)

    # Dispatch to appropriate builder
    if agent == "claude":
        deployed = build_claude_context()
        print(f"\n✅ Claude context deployed to: {deployed}")

    elif agent in ["gemini", "warp", "cursor", "chatgpt"]:
        print(f"❌ Builder for {agent} not yet implemented")
        sys.exit(1)

    elif agent == "all":
        print("❌ 'all' command not yet implemented")
        sys.exit(1)

    else:
        print(f"Unknown agent: {agent}")
        print("Available agents: claude, gemini, warp, cursor, chatgpt, all")
        sys.exit(1)


if __name__ == "__main__":
    main()
