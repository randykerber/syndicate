# Hedgeye Pipeline Scripts

**Simple, consistent commands to run Hedgeye data pipelines.**

All commands assume you're in the `python/` directory:
```bash
cd ~/gh/randykerber/syndicate/python
```

---

## Quick Reference

### Run Everything
```bash
uv run python scripts/hedgeye/run_both_pipelines.py
```
Runs RR pipeline → CR pipeline in sequence. **This is what you want most of the time.**

### Run Individual Pipelines

**Risk Range (RR) only:**
```bash
uv run python scripts/hedgeye/run_rr_pipeline.py
```

**Current Range (CR) only:**
```bash
uv run python scripts/hedgeye/run_cr_pipeline.py
```

### Utilities

**Clear today's price cache** (force fresh price fetches):
```bash
uv run python scripts/hedgeye/clear_today_price_cache.py
```

---

## What Each Pipeline Does

### Risk Range (RR) Pipeline
1. Parse Risk Range .eml files
2. Rename files to standard format: `risk_range_YYYY-MM-DD.eml`
3. Combine all historical RR data with symbol canonicalization
4. Generate enhanced plots with current FMP prices (with Yahoo fallback)

**Outputs:**
- Data: `~/d/prod/hedgeye/rr/all/csv/combined_risk_range.csv`
- Plots: `~/d/view/hedgeye/plots/plots_with_fmp_YYYYMMDD/*.png`

### Current Range (CR) Pipeline
1. Parse ETF Pro Plus weekly emails
2. Parse Portfolio Solutions daily emails
3. Merge position ranges from EP, PS, and RR
4. Enrich with current prices and proxy calculations
5. Generate CR time-series plots

**Outputs:**
- Data: `~/d/view/hedgeye/data/cr/position_ranges_enriched.csv`
- Plots: `~/d/view/hedgeye/plots/cr_time_series/*.png`

### Combined Pipeline
Runs both in sequence (RR first, then CR, since CR depends on RR data).

---

## What These Scripts Are

**Thin wrappers** that import and call functions from `src/hedgeye/ds/`.

**Why?** So you can also import and call these functions from your own Python code:

```python
from hedgeye.ds.rr.rr_pipeline import run_full_rr_pipeline
from hedgeye.ds.cr.cr_merge_ranges import main as merge_cr

# Use in your own code
run_full_rr_pipeline(generate_enhanced_plots=False)
merge_cr()
```

---

## Design Philosophy

**ONE clear way to do each task:**
- Want to run RR? → `run_rr_pipeline.py`
- Want to run CR? → `run_cr_pipeline.py`
- Want to run both? → `run_both_pipelines.py`

No ambiguity, no decisions, no confusion.

---

## Legacy Note

The following standalone scripts have been **removed** (replaced by modules):
- ❌ `parse_etf_pro.py` → Use `uv run python -m hedgeye.ds.ep.process_etf_pro_weekly`
- ❌ `parse_portfolio_solutions.py` → Use `uv run python -m hedgeye.ds.ps.process_portfolio_solutions`
- ❌ `combine_rr_data.py` → Part of `run_rr_pipeline.py`
- ❌ `generate_rr_plots.py` → Part of `run_rr_pipeline.py`
- ❌ `generate_enhanced_rr_plots.py` → Part of `run_rr_pipeline.py`

If you need to run individual steps, use the module commands or import the functions directly.
