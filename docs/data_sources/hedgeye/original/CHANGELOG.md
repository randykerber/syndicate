# Changelog

## [0.2.0] – 2025-06-15

### Added
- Risk Range `.eml` email parser:
  - Extracts structured data (trend, buy/sell levels, close prices, trend/bucket status)
  - Handles batch parsing from a raw `.eml` directory
- CSV output generation per report day
- Config system:
  - Centralized in `conf/config.yaml`
  - Supports input/output directory paths
- DataFrame construction:
  - Appends all daily CSVs into one combined DataFrame
  - Output to `combined_risk_range.csv`
- Plotting:
  - Generates time-series plots per ticker (`prev_close`, `buy_trade`, `sell_trade`)
  - All plots saved to configurable directory, sanitized for safe filenames
- Script orchestration:
  - `scripts/generate_all_plots.py` for bulk plot creation
- Python environment setup:
  - Uses `uv` with `pyproject.toml`
  - Optional `.envrc` support via `direnv` and bash integration

### Changed
- Project version bumped from `0.1.0` → `0.2.0`

### Removed
- Dropped unused and third-party dependencies (e.g. `mem0ai`, `posthog`, `matplotlib extras`)
- Removed `main.py` placeholder and deprecated modules

---

This changelog marks the transition from early prototype to working MVP.
