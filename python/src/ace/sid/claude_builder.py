"""
Claude Context Builder - Builds CLAUDE.md from parts.

Version 0.2: Uses warehouse as source of truth.
"""

from pathlib import Path

from ace.sid.builder import ContextBuilder


class ClaudeBuilder(ContextBuilder):
    """
    Build and deploy CLAUDE.md for Claude Code.

    Input parts:
    - warehouse/common/COMMON.md
    - warehouse/agents/claude/CLAUDE-specific.md

    Output:
    - ~/gh/randykerber/env/dot/config/claude/CLAUDE.md
    """

    def __init__(self):
        super().__init__()
        self.agent_name = "claude"
        self.output_filename = "CLAUDE.md"


def build_claude_context() -> Path:
    """
    Convenience function to build Claude context.

    Returns:
        Path to deployed CLAUDE.md
    """
    builder = ClaudeBuilder()
    return builder.run()


if __name__ == "__main__":
    # Allow running directly for testing
    build_claude_context()
