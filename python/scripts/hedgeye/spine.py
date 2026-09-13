#!/usr/bin/env python3
"""Hand-run entry point for the Hedgeye event spine.

uv run python scripts/hedgeye/spine.py status
uv run python scripts/hedgeye/spine.py extract ss
uv run python scripts/hedgeye/spine.py read-rosters --latest 3
uv run python scripts/hedgeye/spine.py check && ... load && ... render
"""

from hedgeye.spine.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
