# Hedgeye Pipeline Quick Reference

**Purpose**: Quick command reference to regenerate all plots and data from scratch.

**When to use**: After receiving new emails, or when refreshing all outputs.

## Complete Pipeline Sequence

All commands should be run from `/Users/rk/gh/randykerber/syndicate/python`:

### Step 1: Run RR (Risk Range) Pipeline
Processes Risk Range emails and generates combined RR data.
```bash
uv run python scripts/hedgeye/run_full_rr_pipeline.py
```
**Output**: `prod/all/csv/combined_risk_range.csv`

### Step 2: Process EP (ETF Pro) Weekly Emails
Processes weekly ETF Pro Plus portfolio snapshots.
```bash
uv run python -m syndicate.data_sources.hedgeye.process_etf_pro_weekly
```
**Output**: `prod/etf_pro/csv/etf_pro_weekly_YYYY-MM-DD.csv`

### Step 3: Process PS (Portfolio Solutions) Daily Emails
Processes daily Portfolio Solutions rankings.
```bash
uv run python -m syndicate.data_sources.hedgeye.process_portfolio_solutions
```
**Output**: `prod/ps/csv/ps_daily_YYYY-MM-DD.csv`

### Step 4: Run CR Merge
Merges EP, PS, and RR data into base snapshot.
```bash
uv run python -m syndicate.data_sources.hedgeye.cr_merge_ranges
```
**Output**: `prod/ranges/base/position_ranges_base.csv`

### Step 5: Run CR Enrich
Adds current prices and calculates proxy-translated trade ranges.
```bash
uv run python -m syndicate.data_sources.hedgeye.cr_enrich_ranges
```
**Output**: `prod/ranges/enriched/position_ranges_enriched.csv`

### Step 6: Generate CR Time-Series Plots
Creates time-series plots with trend ranges, trade ranges, and price history.
```bash
uv run python scripts/hedgeye/generate_cr_time_series_plots.py
```
**Output**: `prod/ranges/plots/cr_timeseries/cr_timeseries_*.png`

## Notes

- **Idempotent**: Each step checks for already-processed files and skips them
- **Latest files**: CR merge uses the **latest** EP and PS files (snapshot, not historical)
- **Price cache**: Steps 5-6 use price cache to avoid redundant API calls
- **Market hours**: Price fetching respects market hours (doesn't cache today during trading hours)

## Common Scenarios

### After receiving new emails
Run steps 1-3 to process new emails, then steps 4-6 to regenerate outputs.

### To refresh prices only
Run step 5 (enrich) to fetch fresh prices, then step 6 to regenerate plots.

### Full refresh from scratch
Delete relevant output directories, then run all steps 1-6.

## Data Directory Structure

Paths defined in `python/config/hedgeye.yaml` (use `${prod_root}` and `${raw_root}` variables):

```
${raw_root}/eml/
  ├── risk_range/           # RR emails
  ├── etf_pro_weekly/       # EP weekly emails
  └── portfolio_solutions/  # PS daily emails

${prod_root}/
  ├── daily/csv/            # Individual RR CSVs
  ├── all/csv/              # Combined RR CSV
  ├── etf_pro/csv/          # EP weekly CSVs
  ├── ps/csv/               # PS daily CSVs
  └── ranges/
      ├── base/             # Merged snapshot
      ├── enriched/         # Enriched snapshot
      └── plots/            # Time-series plots
```

