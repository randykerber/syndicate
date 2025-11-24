# Python Project Structure Reference

**Purpose**: Clarify Python terminology and how it maps to this project's structure.

## Python Terminology

### Core Concepts

- **Module**: A single `.py` file containing Python code
  - Example: `price_cache.py` is a module
  - Can be imported: `import price_cache`

- **Package**: A directory containing modules and/or subpackages, marked by `__init__.py`
  - Example: `syndicate/` is a package
  - Example: `syndicate/data_sources/hedgeye/` is a subpackage
  - Can be imported: `import syndicate` or `from syndicate.data_sources import hedgeye`

- **Library**: A collection of packages/modules (informal term)
  - Example: "the syndicate library" = all code in `src/syndicate/`

- **Class**: A blueprint for creating objects (defined with `class` keyword)
  - Example: `class SyndicateAgent:` in `agents.py`

- **Script**: A `.py` file meant to be run directly (has `if __name__ == "__main__":`)
  - Example: `run_full_rr_pipeline.py` in `scripts/`

- **Root** (context-dependent):
  - **Project Root**: `/Users/rk/gh/randykerber/syndicate/python/` (where `pyproject.toml` is)
  - **Package Root**: `src/syndicate/` (the installable package)
  - **Workspace Root**: `/Users/rk/gh/randykerber/syndicate/` (the Git repo root)

## Project Structure

```
python/                          ← PROJECT ROOT (where pyproject.toml lives)
├── src/                         ← Source code directory
│   └── syndicate/               ← PACKAGE ROOT (the installable package)
│       ├── __init__.py          ← Makes it a package
│       ├── agents.py            ← Module
│       ├── data_sources/        ← Subpackage
│       │   └── hedgeye/         ← Subpackage
│       │       ├── __init__.py  ← Makes it a package
│       │       ├── price_cache.py  ← Module
│       │       └── fmp/         ← Subpackage
│       │           └── price_fetcher.py  ← Module
│       └── ...
├── scripts/                     ← Standalone scripts (NOT part of package)
│   └── hedgeye/
│       └── run_full_rr_pipeline.py  ← Script
├── tests/                       ← Test files
├── servers/                     ← Server scripts (NOT part of package)
├── demos/                       ← Demo scripts (NOT part of package)
├── config/                      ← Configuration files
└── pyproject.toml              ← Project definition

```

## Import Rules

### What Can Be Imported?

**From `src/syndicate/` (the package):**
- ✅ `from hedgeye import price_cache`
- ✅ `from syndicate.agents import SyndicateAgent`
- ✅ `import syndicate`

**From `scripts/`, `servers/`, `demos/` (NOT in package):**
- ❌ Cannot be imported by package code
- ✅ Can import from package: `from hedgeye import ...`
- ✅ Can be run directly: `python scripts/hedgeye/run_full_rr_pipeline.py`

### Import Paths

**Package imports** (from anywhere):

```python
# Absolute imports (preferred)
from hedgeye.ds.prices import price_cache
from hedgeye.price_cache import get_daily_prices

# Relative imports (within package only)
from .price_cache import get_daily_prices  # Same package
from ..config_loader import load_config  # Parent package
```

**Script imports** (from scripts/):

```python
# Scripts import from package
from hedgeye.ds.rr.rr_pipeline import run_full_rr_pipeline
```

## Visibility Rules

### Files in `src/syndicate/`:
- ✅ **Visible** to other package code via imports
- ✅ **Visible** to scripts via `from syndicate...`
- ✅ **Installed** when package is installed (`uv sync`)

### Files in `scripts/`, `servers/`, `demos/`:
- ❌ **NOT visible** to package code (can't be imported)
- ✅ **Runnable** directly: `python scripts/hedgeye/run_full_rr_pipeline.py`
- ✅ **Can import** from package: `from syndicate...`

### Files at project root (`python/duh.py`):
- ❌ **NOT importable** by package code
- ✅ **Runnable** directly: `python duh.py`
- ⚠️ **Can import** from package IF run from project root: `from syndicate...`
- ⚠️ **Path issues** if run from elsewhere

## Running Code

### Running Scripts:
```bash
# From project root
cd /Users/rk/gh/randykerber/syndicate/python
uv run python scripts/hedgeye/run_full_rr_pipeline.py

# Or as module (if script is in package)
uv run python -m hedgeye.process_etf_pro_weekly
```

### Running Package Code:
```bash
# As module (preferred)
uv run python -m hedgeye.cr_merge_ranges

# Direct import in Python
uv run python -c "from hedgeye import price_cache; ..."
```

## Key Points

1. **Package Root** = `src/syndicate/` (the installable package)
2. **Project Root** = `python/` (where `pyproject.toml` is)
3. **Package Name** = `syndicate` (from `pyproject.toml`)
4. **Import Path** = `from syndicate...` (matches package name, not folder name)
5. **Scripts** = standalone files in `scripts/`, `servers/`, `demos/` (not part of package)
6. **Package Code** = everything in `src/syndicate/` (importable, installable)

## Common Questions

**Q: Is `src` the root?**
A: No. `src/` is just a directory. The package root is `src/syndicate/`.

**Q: Is `syndicate` the root?**
A: Depends on context:
- Package root: `src/syndicate/`
- Package name: `syndicate`
- Import root: `syndicate` (what you import)

**Q: Can I put a file at `python/duh.py` and import it?**
A: Not easily. It's not part of the package. Better to:
- Put it in `src/syndicate/` if it's package code
- Put it in `scripts/` if it's a standalone script

**Q: Why `src/syndicate/` instead of just `syndicate/`?**
A: Common Python practice. Separates source code from other files (tests, scripts, config). Makes it clear what gets installed.

**Q: What's the difference between `scripts/` and package code?**
A: 
- `scripts/` = runnable utilities, not importable
- Package code = reusable modules, importable and installable

