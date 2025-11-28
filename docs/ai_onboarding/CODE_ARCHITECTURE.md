# Code Architecture: SSSAgent and Project Structure

This document outlines the standards for writing and organizing Python code in this project.

## The `SSSAgent` Base Class

The `SyndicateAgent` class is **DEPRECATED**. All new agents **must** inherit from `SSSAgent`, which is defined in:

`@python/src/sss/agents/base.py`

This base class provides the core functionality for session management (memory) and tool execution using the `openai-agents` SDK.

## Separation of Concerns

The Python source code in `@python/src/` is organized by function:

-   **`sss/agents/`**: This is where the "brains" of the operation live. Each agent class should be a subclass of `SSSAgent` and contain the specific instructions and tools for its purpose.
    -   *Example*: `YouTubeTriageAgent` in `youtube.py`.

-   **`sss/tools/`**: This package contains the "hands" of the agents. These are the functions that interact with the outside world (e.g., fetching a transcript, reading a file). They should be plain Python functions that can be decorated for agent use.
    -   *Example*: `fetch_youtube_transcript()` in `youtube_tools.py`.

-   **`shared/`**: This is for utilities that are used across different packages, like `sss` and `hedgeye`.
    -   *Example*: The `load_config` function in `shared/config.py`.

-   **`scripts/`**: This directory, located at `@python/scripts/`, contains the entry points for running pipelines or performing operations. These scripts orchestrate the agents and tools to accomplish a task. They are not part of the importable `sss` library.
    -   *Example*: `run_youtube_triage.py`.

## Running Scripts

The established best practice for running scripts is to use the `uv run python ...` command from the `@python/` directory. This ensures the correct virtual environment and Python interpreter are used.

**Example:**
```sh
# From the ./python/ directory
uv run python scripts/run_youtube_triage.py <video_id>
```
