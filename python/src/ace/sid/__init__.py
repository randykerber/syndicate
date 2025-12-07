"""
SID - System Instruction Deployer

Manages and provides system instructions from context files (CLAUDE.md, WARP.md, GEMINI.md, etc.)
to various AI tools and agents.

Purpose:
    - Load system instruction files from configured locations
    - Parse and format instructions for different AI tools
    - Provide unified interface for accessing context across tools
    - Support both global (~/.claude/) and project-specific (./) instructions
"""

from ace.sid.builder import ContextBuilder
from ace.sid.claude_builder import ClaudeBuilder, build_claude_context

__version__ = "0.1.0"

__all__ = [
    "ContextBuilder",
    "ClaudeBuilder",
    "build_claude_context",
]
