"""
Claude Context Builder - Builds CLAUDE.md from parts.

Version 0.1: Simple concatenation of COMMON.md + CLAUDE-specific.md
"""

from pathlib import Path
from typing import List

from ace.sid.builder import ContextBuilder


class ClaudeBuilder(ContextBuilder):
    """
    Build and deploy CLAUDE.md for Claude Code.

    Input parts (v0.1):
    - data/ace/agent/common/COMMON.md
    - data/ace/agent/claude/CLAUDE-specific.md

    Output:
    - ~/gh/randykerber/env/dot/config/claude/CLAUDE.md
    """

    def __init__(self):
        super().__init__()
        self.agent_name = "claude"
        self.output_filename = "CLAUDE.md"

    def gather_inputs(self) -> List[Path]:
        """
        Collect parts needed for Claude context.

        Version 0.1: COMMON.md + CLAUDE-specific.md
        """
        inputs = []

        # Part 1: Common context (shared across all agents)
        common_path = self.data_dir / "agent" / "common" / "COMMON.md"
        if common_path.exists():
            inputs.append(common_path)
            print(f"   ✓ Found: {common_path.name}")
        else:
            print(f"   ⚠️  Missing: {common_path}")

        # Part 2: Claude-specific context
        claude_specific = self.data_dir / "agent" / "claude" / "CLAUDE-specific.md"
        if claude_specific.exists():
            inputs.append(claude_specific)
            print(f"   ✓ Found: {claude_specific.name}")
        else:
            print(f"   ⚠️  Missing: {claude_specific}")

        if not inputs:
            raise FileNotFoundError("No input parts found for Claude context build")

        return inputs


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
