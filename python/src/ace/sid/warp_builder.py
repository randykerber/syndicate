"""
Warp Context Builder - Builds WARP.md from parts.

Uses warehouse as source of truth.
"""

from pathlib import Path

from ace.sid.builder import ContextBuilder


class WarpBuilder(ContextBuilder):
    """
    Build and deploy WARP.md for Warp AI.

    Input parts:
    - warehouse/common/COMMON.md
    - warehouse/agents/warp/WARP-specific.md

    Output:
    - ~/gh/randykerber/env/dot/config/warp/WARP.md
    """

    def __init__(self):
        super().__init__()
        self.agent_name = "warp"
        self.output_filename = "WARP.md"


def build_warp_context() -> Path:
    """
    Convenience function to build Warp context.

    Returns:
        Path to deployed WARP.md
    """
    builder = WarpBuilder()
    return builder.run()


if __name__ == "__main__":
    # Allow running directly for testing
    build_warp_context()