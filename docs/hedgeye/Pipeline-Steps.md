# Current Range (CR) Full Pipeline - Working Commands

**Last Updated:** 2025-11-28

This document contains the current working commands for the full CR pipeline, from RR email processing through final CR plots.

## Prerequisites

All commands assume you're in the `python/` directory:
```bash
cd /Users/rk/gh/randykerber/syndicate/python
```

## Full Pipeline Steps (1-6)

### Step 1: Process Risk Range Email

**Command:**
```bash
uv run python scripts/hedgeye/run_rr_pipeline.py
```

**What it does:**
- Parses all new .eml files from the Risk Range email folder
- Renames files to standard format: `risk_range_YYYY-MM-DD.eml`
- Extracts trade ranges (buy/sell) for each symbol
- Combines all historical RR data with symbol canonicalization
- Generates enhanced plots with current FMP prices (with Yahoo fallback)
- Outputs:
  - `/Users/rk/d//prod/hedgeye/rr/all/csv/combined_risk_range.csv`
  - `/Users/rk/d/view/hedgeye/plots/plots_with_fmp_YYYYMMDD/*.png`

**Expected output:**
```
=== Starting Full Pipeline ===
=== Step: Parsing emails ===
📝 Renamed: RISK RANGE™ SIGNALS_ NOVEMBER 28, 2025.eml → risk_range_2025-11-28.eml
✅ Email parsing completed
=== Step: Loading and combining data ===
✅ Combined 3393 records from 51 symbols
=== Generating Enhanced Risk Range Plots ===
Successfully fetched 61 latest prices
✅ Saved: .../AAPL.png (x35)
✅ Full pipeline completed
```

---

### Step 2: Parse ETF Pro (EP) Email

**Command:**
```bash
uv run python -m hedgeye.ds.ep.process_etf_pro_weekly
```

**What it does:**
- Auto-detects all ETF Pro Plus weekly emails in configured directory
- Renames files to standard format: `etf_pro_weekly_YYYY-MM-DD.eml`
- Extracts LONG and SHORT portfolio positions
- Parses: ticker, name, position type, date added, recent price, trend range, asset class
- Skips already-processed emails (checks if CSV exists)
- Output: `etf_pro_weekly_YYYY-MM-DD.csv` in configured CSV directory

**Expected output:**
```
Processing ETF Pro Plus weekly emails...
📝 Renamed: ETF PRO PLUS - New Weekly Report.eml → etf_pro_weekly_2025-11-27.eml
✅ Processed: etf_pro_weekly_2025-11-27.eml
  Found XX long, XX short positions
  💾 Saved: etf_pro_weekly_2025-11-27.csv
⏭️ Skipped (already exists): etf_pro_weekly_2025-11-20.eml
```

---

### Step 3: Parse Portfolio Solutions (PS) Email

**Command:**
```bash
uv run python -m hedgeye.ds.ps.process_portfolio_solutions
```

**What it does:**
- Auto-detects all Portfolio Solutions emails in configured directory
- Renames files to standard format: `portfolio_solutions_YYYY-MM-DD.eml`
- Extracts portfolio rankings (ETFs by Rank)
- Parses: rank, ticker, name
- Skips already-processed emails (checks if CSV exists)
- Output: `portfolio_solutions_YYYY-MM-DD.csv` in configured CSV directory

**Expected output:**
```
Processing Portfolio Solutions emails...
📝 Renamed: Portfolio Solutions Daily Re-Rank (11/27/2025).eml → portfolio_solutions_2025-11-27.eml
✅ Processed: portfolio_solutions_2025-11-27.eml
  Found XX ranked positions
  💾 Saved: portfolio_solutions_2025-11-27.csv
⏭️ Skipped (already exists): portfolio_solutions_2025-11-26.eml
```

---

### Step 4: CR Merge

**Command:**
```bash
uv run python -m hedgeye.ds.cr.cr_merge_ranges
```

**What it does:**
- Combines data from:
  1. ETF Pro Plus (EPP) weekly portfolio - trend ranges, LONG/SHORT positions
  2. Portfolio Solutions (PS) daily - portfolio ranks
  3. Risk Range (RR) combined - trade ranges for reference symbols
  4. Symbol mapping table - p_sym to r_sym mappings
  5. Live prices - current prices for both p_sym and r_sym
- Creates merged CSV with all raw data
- Output: `/Users/rk/d/view/hedgeye/data/cr/cr_merged_YYYY-MM-DD.csv`

**Expected output:**
```
=== CR Merge - Combining Position Ranges ===
Loading source data...
  ✓ Loaded XX EPP positions from etf_pro_plus_YYYY-MM-DD.csv
  ✓ Loaded XX PS positions from portfolio_solutions_YYYY-MM-DD.csv
  ✓ Loaded XXXX RR records
  ✓ Loaded mapping table

✅ Merge Complete!
Summary:
  Total positions: XX
  With trend ranges: XX
  With trade ranges: XX
  LONG positions: XX
  SHORT positions: XX
```

**Note:** Order doesn't matter between Steps 2 and 3, but both must complete before Step 4.

---

### Step 5: CR Enrich

**Command:**
```bash
uv run python -m hedgeye.ds.cr.cr_enrich_ranges
```

**What it does:**
- Loads merged CR data from Step 4
- Fetches current prices for all portfolio symbols (p_sym) and reference symbols (r_sym)
- Calculates proxy trade ranges (p_trade_low/high) by applying RR signal to current price
- Adds enrichment columns: p_current, r_current, p_trade_low, p_trade_high
- Output: `/Users/rk/d/view/hedgeye/data/cr/cr_enriched_YYYY-MM-DD.csv`

**Expected output:**
```
=== CR Enrich - Adding Current Prices ===
Loading merged data...
Fetching current prices...
  Fetching prices for XX portfolio symbols...
  Fetching prices for XX reference symbols...
✅ Enrichment Complete!
Summary:
  Total positions: XX
  With p_current: XX
  With r_current: XX
  With proxy trade ranges: XX
```

---

### Step 6: CR Plotting

**Command:**
```bash
uv run python scripts/hedgeye/generate_cr_time_series_plots.py
```

**What it does:**
- Loads enriched CR data from Step 5
- Generates time-series plots for all tickers showing:
  - Historical trend ranges (from EP)
  - Historical trade ranges (from RR or proxy)
  - Current price with latest position
  - 30-day lookback window (configurable)
- Output: `/Users/rk/d/view/hedgeye/plots/cr_time_series_YYYYMMDD/*.png`

**Expected output:**
```
=== Generating CR Time-Series Plots ===
Loaded XX enriched positions
Generating plots for XX tickers...
✅ Saved: .../AAPL.png
✅ Saved: .../SPY.png
...
Plot generation complete:
  ✅ Successful: XX
  ❌ Failed: 0
```

---

## Quick Reference: Full Pipeline

```bash
# From project root
cd /Users/rk/gh/randykerber/syndicate/python

# Step 1: Process RR email
uv run python scripts/hedgeye/run_full_rr_pipeline.py

# Step 2: Parse EP email (auto-processes all new emails)
uv run python -m hedgeye.ds.ep.process_etf_pro_weekly

# Step 3: Parse PS email (auto-processes all new emails)
uv run python -m hedgeye.ds.ps.process_portfolio_solutions

# Step 4: Merge CR data
uv run python -m hedgeye.ds.cr.cr_merge_ranges

# Step 5: Enrich with current prices
uv run python -m hedgeye.ds.cr.cr_enrich_ranges

# Step 6: Generate CR plots
uv run python scripts/hedgeye/generate_cr_time_series_plots.py
```

---

## TODO: Create Full CR Pipeline Script

Create `scripts/hedgeye/run_full_cr_pipeline.py` similar to `run_full_rr_pipeline.py`:
- Auto-detect latest EP and PS emails
- Run all 6 steps in sequence
- Error handling and status reporting
- Optional step skipping (like RR pipeline)

---

## Notes

- Steps 2 and 3 can run in any order, both needed before Step 4
- Steps 4, 5, 6 must run in sequence
- All scripts use config from `hedgeye.config_loader`
- Font warnings about emoji glyphs are cosmetic, plots work fine
- Yahoo Finance fallback works automatically for commodities when FMP free tier doesn't cover them