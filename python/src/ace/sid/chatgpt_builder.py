"""
ChatGPT Context Builder - Builds CHATGPT.md from parts.

Uses warehouse as source of truth.
"""

from pathlib import Path

from ace.sid.builder import ContextBuilder


class ChatGPTBuilder(ContextBuilder):
    """
    Build and deploy CHATGPT.md for ChatGPT.

    Input parts:
    - warehouse/common/COMMON.md
    - warehouse/agents/chatgpt/CHATGPT-specific.md
    - warehouse/common/PERSONAL.md (personal context)

    Output:
    - ~/gh/randykerber/env/dot/config/chatgpt/CHATGPT.md
    """

    def __init__(self):
        super().__init__()
        self.agent_name = "chatgpt"
        self.output_filename = "CHATGPT.md"

    @property
    def include_personal(self) -> bool:
        return True  # ChatGPT handles both coding and personal topics


def build_chatgpt_context() -> Path:
    """
    Convenience function to build ChatGPT context.

    Returns:
        Path to deployed CHATGPT.md
    """
    builder = ChatGPTBuilder()
    return builder.run()


if __name__ == "__main__":
    # Allow running directly for testing
    build_chatgpt_context()
