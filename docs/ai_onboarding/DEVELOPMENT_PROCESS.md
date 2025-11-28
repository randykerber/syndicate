# Development Process: Live Documentation

This document explains our current workflow for exploring requirements and designing agent behavior.

## The Goal: Explore Before Building

The primary goal right now is **requirements exploration**, not production implementation. We need to understand what a "good" agent interaction looks like before we can automate it.

The core of this process is a collaborative, interactive chat between the user and an AI assistant.

## The "Live Documentation" Method

Our method is to treat the conversational exploration itself as a form of documentation.

1.  **Create a Case File**: For each new task or example (e.g., a new YouTube video to analyze), we create a dedicated Markdown file in `@docs/use_cases/`.

2.  **Simulate the Interaction**: The AI assistant acts as the agent, and the user provides feedback. This multi-turn conversation is captured in the case file.
    -   The AI provides a response.
    -   The user critiques it, asks follow-up questions, and refines the goal.
    -   This loop continues until a successful outcome is reached for that case.

3.  **The Output is a "Golden Record"**: The resulting Markdown file becomes a "golden record" of a successful interaction. It contains the user's goal, the agent's responses, the user's feedback, and the final, successful result.

This process ensures we have a deep understanding of the user's needs and a set of concrete examples to guide future implementation and testing.

## Canonical Example

The first successful run-through of this process is documented at:

`@docs/use_cases/youtube_triage/case_01_the_everything_bubble.md`

Please review this file to see a real example of the "Live Documentation" method in action. It demonstrates how we moved from an initial request to a final, successful triage decision.
