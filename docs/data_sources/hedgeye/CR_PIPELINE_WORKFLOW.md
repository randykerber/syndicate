# CR (Combo Ranges) Pipeline Workflow & Data Artifacts

## Overview

The CR pipeline combines data from three sources to create enriched position ranges with trend ranges (from EP), trade ranges (from RR, translated), and current prices.

## Pipeline Steps

### 1. Parse EP (ETF Pro Plus) Weekly Emails
- **Input**: `/Users/rk/d/downloads/hedgeye/raw/eml/etf_pro_weekly/*.eml`
- **Script**: `process_etf_pro_weekly.py`
- **Output**: `/Users/rk/d/downloads/hedgeye/prod/etf_pro/csv/etf_pro_weekly_YYYY-MM-DD.csv`
- **Columns**: 
  - `report_date`: Date of weekly report
  - `position_type`: LONG or SHORT
  - `ticker`: Symbol (e.g., AAAU, BUXX)
  - `description`: Position description
  - `date_added`: When position was added to portfolio
  - `recent_price`: Current price of ticker (in ticker's coordinate system)
  - `trend_low`: Lower bound of trend range
  - `trend_high`: Upper bound of trend range
  - `asset_class`: Asset classification

**Note**: EP data is weekly snapshots. Each file contains the full portfolio state at that date.

### 2. Parse PS (Portfolio Solutions) Daily Emails
- **Input**: `/Users/rk/d/downloads/hedgeye/raw/eml/portfolio_solutions/*.eml`
- **Script**: `process_portfolio_solutions.py`
- **Output**: `/Users/rk/d/downloads/hedgeye/prod/ps/csv/ps_daily_YYYY-MM-DD.csv`
- **Columns**:
  - `report_date`: Date of daily report
  - `rank`: Portfolio rank (1 = highest)
  - `ticker`: Symbol
  - `name`: ETF name

**Note**: PS data is daily. Each file contains the ranking for that day.

### 3. Parse RR (Risk Range) Emails
- **Input**: `/Users/rk/d/downloads/hedgeye/raw/eml/risk_range/*.eml`
- **Script**: `run_rr_parser.py` → `parse_rr_emails.py`
- **Output**: 
  - Individual: `/Users/rk/d/downloads/hedgeye/prod/daily/csv/risk_range_YYYY-MM-DD.csv`
  - Combined: `/Users/rk/d/downloads/hedgeye/prod/all/csv/combined_risk_range.csv`
- **Columns**:
  - `date`: Date of risk range
  - `index`: Reference symbol (e.g., GOLD, SPX, DXY)
  - `trend`: BULLISH or BEARISH
  - `buy_trade`: Lower trade range bound
  - `sell_trade`: Upper trade range bound
  - `prev_close`: Previous close price (in reference symbol's coordinate system)
  - `bucket`: IN, OUT, or NEUTRAL

**Note**: RR data is daily. Reference symbols may differ from tradable tickers (e.g., GOLD vs AAAU).

### 4. Merge All Sources (`cr_merge_ranges.py`)
- **Inputs**:
  - Latest EP weekly CSV (current portfolio state)
  - Latest PS daily CSV (current rankings)
  - Combined RR CSV (all historical RR data)
  - Mapping table: `/Users/rk/d/downloads/hedgeye/prod/ranges/p-to-r-mapping.csv`
- **Output**: `/Users/rk/d/downloads/hedgeye/prod/ranges/base/position_ranges_base.csv`
- **Purpose**: Creates a snapshot of current portfolio state with all available data sources merged

**Key Logic**:
- Uses **latest** EP and PS files only (current state snapshot)
- Historical EP/PS data is preserved in individual CSV files
- Maps p_sym (tradable) → r_sym (RR reference) using mapping table
- Example: AAAU (p_sym) → GOLD (r_sym)

**Output Columns**:
- Base: `p_sym`, `description`, `position_type`, `date_added`, `asset_class`, `rank`
- EP: `trend_low`, `trend_high`, `report_date_epp`
- PS: `report_date_ps`
- RR: `r_sym`, `proxy_type`, `trade_low`, `trade_high`, `rr_prev_close`, `rr_trend`, `rr_date`
- Mapping: `r_sym`, `proxy_type`

### 5. Enrich with Prices (`cr_enrich_ranges.py`)
- **Input**: `position_ranges_base.csv`
- **Output**: `/Users/rk/d/downloads/hedgeye/prod/ranges/enriched/position_ranges_enriched.csv`
- **Purpose**: 
  1. Fetches current prices for p_sym and r_sym
  2. Calculates proxy-translated trade ranges (p_trade_low, p_trade_high)
  3. Adds interpretability fields (% distances, etc.)

**Translation Formula**:
- For positions with r_sym (proxy):
  - `m = trade_low / r_current`
  - `n = trade_high / r_current`
  - `p_trade_low = p_current * m`
  - `p_trade_high = p_current * n`

**Output Columns** (additional):
- Prices: `p_current`, `r_current`
- Translated ranges: `p_trade_low`, `p_trade_high`
- Percentages: `trend_pct_from_low`, `trend_pct_from_high`, `trade_pct_from_low`, `trade_pct_from_high`, `p_trade_pct_from_low`, `p_trade_pct_from_high`

## Key Data Files

### Mapping Table
- **Path**: `/Users/rk/d/downloads/hedgeye/prod/ranges/p-to-r-mapping.csv`
- **Purpose**: Maps tradable symbols (p_sym) to RR reference symbols (r_sym)
- **Columns**: `p_sym`, `r_sym`, `mapping_type`, `confidence`, `notes`, `proxy_type`
- **Example**: AAAU → GOLD (tight proxy)

### Base Merge
- **Path**: `/Users/rk/d/downloads/hedgeye/prod/ranges/base/position_ranges_base.csv`
- **Purpose**: Snapshot of current portfolio state with all raw data merged
- **Note**: This is a **snapshot**, not historical time series

### Enriched Data
- **Path**: `/Users/rk/d/downloads/hedgeye/prod/ranges/enriched/position_ranges_enriched.csv`
- **Purpose**: Final enriched data with prices and translated ranges
- **Note**: Also a **snapshot** (current state only)

## Time-Series Plotting

The `cr_time_series_plotting.py` module creates historical time series by:

1. **Loading EP time series**: 
   - Loads all EP weekly CSVs
   - Forward-fills weekly values to daily (each weekly value applies until next update)
   - Uses `recent_price` as p_current (price in p_sym coordinates)

2. **Loading RR time series**:
   - Loads all RR daily CSVs for r_sym (e.g., GOLD for AAAU)
   - Translates trade ranges to p_sym coordinates using:
     - `p_current` from EP data (e.g., AAAU price ~$40)
     - Translation factors from RR data (e.g., GOLD trade ranges)

3. **Merging and plotting**:
   - Merges EP and RR data by date
   - Plots trend ranges (blue), trade ranges (green), and price (black)
   - **All values in p_sym coordinate system** (e.g., AAAU ~$40, not GOLD ~$4000)

**Important**: The price series uses EP `recent_price` only - it does NOT fall back to RR `prev_close` because that would be in r_sym coordinates (wrong scale).

## Coordinate Systems

- **p_sym coordinates**: Tradable ticker's native price scale
  - Example: AAAU ~$40 per share
- **r_sym coordinates**: RR reference symbol's price scale
  - Example: GOLD ~$4000 per ounce

Translation is necessary because RR data is in r_sym coordinates but we want to plot in p_sym coordinates for the tradable ticker.

## Running the Pipeline

**Quick Reference**: See `PIPELINE_QUICK_REFERENCE.md` for a concise command cheat sheet.

```bash
# All commands run from python/ directory

# 1. Process RR (Risk Range) emails
uv run python scripts/hedgeye/run_full_rr_pipeline.py

# 2. Process EP (ETF Pro Plus) weekly emails
uv run python -m syndicate.data_sources.hedgeye.process_etf_pro_weekly

# 3. Process PS (Portfolio Solutions) daily emails
uv run python -m syndicate.data_sources.hedgeye.process_portfolio_solutions

# 4. Merge all sources (uses latest EP/PS files)
uv run python -m syndicate.data_sources.hedgeye.cr_merge_ranges

# 5. Enrich with prices
uv run python -m syndicate.data_sources.hedgeye.cr_enrich_ranges

# 6. Generate time-series plots
uv run python scripts/hedgeye/generate_cr_time_series_plots.py
```

## Data Artifacts Summary

| File | Type | Purpose | Historical? |
|------|------|---------|-------------|
| `etf_pro_weekly_*.csv` | EP | Weekly portfolio snapshots | Yes (one per week) |
| `ps_daily_*.csv` | PS | Daily rankings | Yes (one per day) |
| `risk_range_*.csv` | RR | Daily risk ranges | Yes (one per day) |
| `combined_risk_range.csv` | RR | All RR data combined | Yes (all dates) |
| `position_ranges_base.csv` | CR | Merged snapshot | No (latest only) |
| `position_ranges_enriched.csv` | CR | Enriched snapshot | No (latest only) |

**Note**: The base and enriched CSVs are snapshots. For historical time series, use the plotting functions which load all individual EP/PS/RR files.

