"""
Cursor Context Builder - Builds CURSORRULES.md from parts.

Uses warehouse as source of truth.
"""

from pathlib import Path

from ace.sid.builder import ContextBuilder


class CursorBuilder(ContextBuilder):
    """
    Build and deploy CURSORRULES.md for Cursor AI.

    Input parts:
    - warehouse/common/COMMON.md
    - warehouse/agents/cursor/CURSOR-specific.md

    Output:
    - ~/gh/randykerber/env/dot/config/cursor/CURSORRULES.md
    """

    def __init__(self):
        super().__init__()
        self.agent_name = "cursor"
        self.output_filename = "CURSORRULES.md"


def build_cursor_context() -> Path:
    """
    Convenience function to build Cursor context.

    Returns:
        Path to deployed CURSORRULES.md
    """
    builder = CursorBuilder()
    return builder.run()


if __name__ == "__main__":
    # Allow running directly for testing
    build_cursor_context()
