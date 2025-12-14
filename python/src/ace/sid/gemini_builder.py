"""
Gemini Context Builder - Builds GEMINI.md from parts.

Uses warehouse as source of truth.
"""

from pathlib import Path

from ace.sid.builder import ContextBuilder


class GeminiBuilder(ContextBuilder):
    """
    Build and deploy GEMINI.md for Gemini AI.

    Input parts:
    - warehouse/common/COMMON.md
    - warehouse/agents/gemini/GEMINI-specific.md
    - warehouse/common/PERSONAL.md (personal context)

    Output:
    - ~/gh/randykerber/env/dot/config/gemini/GEMINI.md
    """

    def __init__(self):
        super().__init__()
        self.agent_name = "gemini"
        self.output_filename = "GEMINI.md"

    @property
    def include_personal(self) -> bool:
        return True  # Gemini handles both coding and personal topics


def build_gemini_context() -> Path:
    """
    Convenience function to build Gemini context.

    Returns:
        Path to deployed GEMINI.md
    """
    builder = GeminiBuilder()
    return builder.run()


if __name__ == "__main__":
    # Allow running directly for testing
    build_gemini_context()
