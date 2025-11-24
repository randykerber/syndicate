# Hedgeye Migration - Claude Code Briefing

**Date**: 2025-11-12
**From**: Claude Code (hedgeye-kb project)
**To**: Claude Code (syndicate project)
**Status**: Ready to begin migration

---

## Executive Summary

We're migrating the **hedgeye-kb** project into **syndicate** as a data source. The hedgeye-kb project processes Hedgeye financial email reports (Risk Range, ETF Pro, Portfolio Solutions) into structured data, CSVs, and plots with real-time price overlays from FMP/Yahoo Finance APIs.

**Migration Approach**: Hybrid (copy all code, fix incrementally, test step-by-step)

**Key Success Metric**: Regenerate `~/d/downloads/hedgeye/prod/` and compare with backup

---

## What You're Receiving

### Source Project: hedgeye-kb
- **Location**: `~/gh/randykerber/hedgeye-kb/`
- **Status**: Git clean, final state, ready to copy
- **Language**: Python 3.13
- **Structure**: Standalone project with parsers, processors, pipelines

### What It Does
Processes Hedgeye email reports through a pipeline:
1. **Parse** `.eml` files (HTML emails) → Extract Risk Range data
2. **Save** to CSV and Markdown (daily files)
3. **Combine** all CSVs into master dataset
4. **Plot** time series with risk ranges + current price overlays
5. **Generate** dashboard showing status across all symbols

### Key Components
- **Parsers**: `parse_eml.py` (Risk Range), `parse_etf_pro.py`, `parse_portfolio_solutions.py`
- **Processors**: `use_rr.py` (data combining), `enhanced_plotting.py` (plotting)
- **Pipeline**: `run_full_pipeline.py` (orchestrates everything)
- **Config**: `config.yaml` (all paths and settings)
- **Utils**: `symbol_canonicalization.py`, FMP integration

### Data Sources
- **Input**: Email files at `~/d/downloads/hedgeye/raw/eml/`
- **Output**: Processed data at `~/d/downloads/hedgeye/prod/`
- **Dependencies**: FMP entity data at `~/d/downloads/fmp/`

---

## Current State

### Both Projects are Git Clean
✅ **hedgeye-kb**: Final state committed and pushed
✅ **syndicate**: Clean state, ready for migration

### Production Data Backup
✅ **Backed up**: `~/d/downloads/hedgeye/prod/` → `prod.backup.YYYYMMDD/`
⚠️ **Important**: Original prod/ moved away so nothing accidentally uses old location

### File Counts (for validation)
- **Email files**: 96 total
  - Risk Range: 78 files
  - ETF Pro weekly: 2 files
  - ETF Pro updates: 8 files
  - Portfolio Solutions: 8 files
- **Daily CSVs**: ~76 pairs (risk_range + change_events)
- **Plots**: 36 active symbols (7-day recency filter)

---

## Migration Plan

### Phase 1: Setup & Config (30-45 min)
**Goal**: Merge dependencies and create structure

**Tasks**:
1. Create directory structure:
   ```bash
   mkdir -p src/syndicate/data_sources/hedgeye
   mkdir -p scripts/hedgeye
   mkdir -p docs/data_sources/hedgeye
   ```

2. Merge `pyproject.toml`:
   ```toml
   dependencies = [
       # ... existing syndicate deps ...

       # Add from hedgeye-kb:
       "beautifulsoup4>=4.12.3",
       "pandas>=2.3.0",
       "duckdb>=1.3.0",
       "matplotlib>=3.10.3",
       "pyspark==3.5.3",
       "yfinance>=0.2.63",
   ]

   [project.optional-dependencies]
   dev = [
       # ... existing dev deps ...
       "pandas-stubs==2.3.2.250926",
   ]
   ```

3. Copy config:
   ```bash
   cp ~/gh/randykerber/hedgeye-kb/conf/config.yaml \
      python/config/hedgeye.yaml
   ```

4. Review and adjust config paths (external data paths stay unchanged)

5. Install dependencies:
   ```bash
   cd python
   uv pip install -e ".[dev]"
   ```

6. **Commit**:
   ```bash
   git add python/pyproject.toml python/config/hedgeye.yaml
   git commit -m "Setup: Add hedgeye structure and dependencies"
   ```

### Phase 2: Copy Code & Scripts (30 min)
**Goal**: Get all hedgeye code into syndicate

**Tasks**:
1. Copy source code:
   ```bash
   cp -r ~/gh/randykerber/hedgeye-kb/src/hedgeye_kb/* \
         python/src/syndicate/data_sources/hedgeye/
   ```

2. Copy scripts:
   ```bash
   cp -r ~/gh/randykerber/hedgeye-kb/scripts/* \
         python/scripts/hedgeye/
   ```

3. Copy docs (keep separate initially):
   ```bash
   mkdir -p docs/data_sources/hedgeye/original
   cp -r ~/gh/randykerber/hedgeye-kb/docs/* \
         docs/data_sources/hedgeye/original/
   ```

4. **Commit** (even though it's broken):
   ```bash
   git add python/src/syndicate/data_sources/hedgeye/
   git add python/scripts/hedgeye/
   git add docs/data_sources/hedgeye/
   git commit -m "Migration: Copy hedgeye code, scripts, and docs (pre-fix)"
   ```

### Phase 3: Fix Imports - Bottom Up (2-3 hours)
**Goal**: Fix imports module by module, starting with lowest dependencies

**Strategy**: Test each module independently before moving up dependency chain

**Modules in Dependency Order**:
1. `config_loader.py` - No dependencies (just loads YAML)
2. `symbol_canonicalization.py` - Only pandas
3. `parse_eml.py` - Depends on config_loader
4. `use_rr.py` - Depends on config_loader, symbol_canonicalization
5. `enhanced_plotting.py` - Depends on use_rr, config_loader
6. `pipeline.py` - Depends on all of the above
7. Scripts - Depend on all modules

**For Each Module**:

```python
# OLD imports:
from hedgeye_kb.config_loader import load_config
from hedgeye_kb.symbol_canonicalization import canonicalize_symbol

# NEW imports:
from hedgeye.config_loader import load_config
from hedgeye.ds.rr.symbol_canonicalization import canonicalize_symbol
```

**Test After Each Fix**:
```bash
# Example for config_loader
python -c "from hedgeye.config_loader import load_config; print(load_config())"
```

**Commit After Each Module**:
```bash
git add python/src/syndicate/data_sources/hedgeye/<module>.py
git commit -m "Fix: Update imports in <module>.py"
```

### Phase 4: Test Pipeline Step-by-Step (2-3 hours)
**Goal**: Validate each pipeline stage works before running full pipeline

**DON'T**: Try to run full pipeline first (creates mess)
**DO**: Test each step independently

#### Step 1: Parse Single Email
```bash
cat > python/test_step1_parse.py << 'EOF'
#!/usr/bin/env python3
"""Test: Parse a single Risk Range email"""
from hedgeye.parse_eml import parse_risk_range_email

email_path = "/Users/rk/d/downloads/hedgeye/raw/eml/risk_range/risk_range_2025-11-12.eml"
entries, changes = parse_risk_range_email(email_path)

print(f"✅ Parsed {len(entries)} risk range entries")
print(f"✅ Found {len(changes)} change events")
EOF

python python/test_step1_parse.py
```

#### Step 2: Save to CSV
```bash
cat > python/test_step2_save.py << 'EOF'
#!/usr/bin/env python3
"""Test: Save parsed data to CSV"""
from hedgeye.parse_eml import parse_risk_range_email
import pandas as pd
from pathlib import Path

email_path = "/Users/rk/d/downloads/hedgeye/raw/eml/risk_range/risk_range_2025-11-12.eml"
entries, changes = parse_risk_range_email(email_path)

# Save to test location
output_dir = Path("./test_output")
output_dir.mkdir(exist_ok=True)
df = pd.DataFrame(entries)
df.to_csv(output_dir / "test_risk_range.csv", index=False)

print(f"✅ Saved {len(df)} rows to test_output/test_risk_range.csv")
EOF

python python/test_step2_save.py
```

#### Step 3: Combine Data
```bash
cat > python/test_step3_combine.py << 'EOF'
#!/usr/bin/env python3
"""Test: Load and combine all CSV files"""
from hedgeye.use_rr import load_all_risk_range_data

df = load_all_risk_range_data()
print(f"✅ Loaded {len(df)} total records")
print(f"   Symbols: {df['index'].nunique()}")
print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
EOF

python python/test_step3_combine.py
```

#### Step 4: Generate Single Plot
```bash
cat > python/test_step4_plot.py << 'EOF'
#!/usr/bin/env python3
"""Test: Generate a single plot"""
from hedgeye.enhanced_plotting import display_rr_with_latest_price
from hedgeye.use_rr import load_all_risk_range_data
from pathlib import Path

df = load_all_risk_range_data()
fig = display_rr_with_latest_price(df, 'SPX')

output_dir = Path("./test_output")
output_dir.mkdir(exist_ok=True)
fig.savefig(output_dir / "test_SPX.png")
print("✅ Generated test plot: test_output/test_SPX.png")
EOF

python python/test_step4_plot.py
```

#### Step 5: Full Pipeline
```bash
# Only after all steps work!
cd python
python scripts/hedgeye/run_full_pipeline.py
```

### Phase 5: Validate Results (30 min)
**Goal**: Confirm migration success by comparing outputs

**Compare CSVs**:
```bash
# Daily CSVs
diff -r ~/d/downloads/hedgeye/prod.backup.*/daily/csv \
        ~/d/downloads/hedgeye/prod/daily/csv

# Combined CSV
diff ~/d/downloads/hedgeye/prod.backup.*/all/csv/combined_risk_range.csv \
     ~/d/downloads/hedgeye/prod/all/csv/combined_risk_range.csv
```

**Compare Plots**:
```bash
# Count plots
old_count=$(ls ~/d/downloads/hedgeye/prod.backup.*/all/plots_with_fmp_*/*.png 2>/dev/null | wc -l)
new_count=$(ls ~/d/downloads/hedgeye/prod/all/plots_with_fmp_*/*.png 2>/dev/null | wc -l)

echo "Old plots: $old_count"
echo "New plots: $new_count"

# Should both be 36 (after 7-day filtering)
```

**Success Criteria**:
- ✅ Same number of CSV files in daily/csv/
- ✅ Same total rows in combined CSV
- ✅ Same number of plots (36 active symbols)
- ✅ No import errors
- ✅ Pipeline completes successfully

---

## Important Paths & Files

### External Data (Don't Move These)
```
~/d/downloads/hedgeye/
├── raw/eml/                    # Email source files (96 files)
│   ├── risk_range/            # 78 files
│   ├── etf_pro_weekly/        # 2 files
│   ├── etf_pro_updates/       # 8 files
│   └── portfolio_solutions/   # 8 files
├── prod/                       # OUTPUT: Pipeline generates this
│   ├── daily/csv/             # risk_range_YYYY-MM-DD.csv
│   ├── all/csv/               # combined_risk_range.csv
│   ├── all/plots_with_fmp_*/  # 36 PNG files
│   ├── ps/                    # Portfolio Solutions output
│   ├── epp/                   # ETF Pro output
│   └── rta/                   # Real Time Alerts (future)
└── prod.backup.YYYYMMDD/      # Backup for comparison

~/d/downloads/fmp/
├── entities/                   # FMP entity data
└── he_to_fmp.csv              # ⚠️ CRITICAL: Symbol mapping file
```

### Config File Locations
```
# OLD (hedgeye-kb):
~/gh/randykerber/hedgeye-kb/conf/config.yaml

# NEW (syndicate):
~/gh/randykerber/syndicate/python/config/hedgeye.yaml
```

### Key Configuration Settings
```yaml
paths:
  raw_eml_dir: /Users/rk/d/downloads/hedgeye/raw/eml/risk_range
  csv_output_dir: /Users/rk/d/downloads/hedgeye/prod/daily/csv
  markdown_output_dir: /Users/rk/d/downloads/hedgeye/prod/daily/md
  combined_csv_output_dir: /Users/rk/d/downloads/hedgeye/prod/all/csv
  plots_output_dir: /Users/rk/d/downloads/hedgeye/prod/all/plots
  fmp_data_base_dir: /Users/rk/d/downloads/fmp/entities

plotting:
  max_days_since_update: 7  # Only plot symbols with recent data
```

---

## Key Technical Details

### Symbol Canonicalization
- Hedgeye uses various symbol formats: `SPX`, `S&P 500`, `USD/YEN`
- FMP API requires specific format: `^GSPC`, `USDJPY`
- Mapping file: `~/d/downloads/fmp/he_to_fmp.csv`
- Module: `symbol_canonicalization.py`

### Price Data Flow
1. **Primary**: FMP API (paid, usage limits)
   - Hits 402 Payment Required for commodities (HGUSD, NGUSD, CLUSD, ZBUSD, ZNUSD)
2. **Fallback**: Yahoo Finance (free, unlimited)
   - Automatic fallback on FMP failure
   - Not cached locally (on-demand only)

### Plotting Features
- Time series with risk range bands (buy/sell/support/resistance)
- Current price overlay (blue dot)
- Status indicators (IN RANGE, BUY RANGE, SELL RANGE)
- Filters stale symbols (no data in last 7 days)
- Cleans up old plots automatically
- Generates dashboard summary

### Email Types
1. **Risk Range** - Daily market signals (78 files)
2. **ETF Pro Weekly** - Full portfolio (2 files)
3. **ETF Pro Updates** - Daily changes (8 files)
4. **Portfolio Solutions** - ETF rankings (8 files)
5. **Real Time Alerts** - Intraday signals (future)

---

## Common Issues & Solutions

### Import Errors
**Problem**: `ModuleNotFoundError: No module named 'hedgeye_kb'`
**Solution**: Change all imports from `hedgeye_kb.*` to `hedgeye.*`

### Config Path Issues
**Problem**: `FileNotFoundError: config.yaml`
**Solution**: Update `config_loader.py` to look in `python/config/hedgeye.yaml`

### Missing Dependencies
**Problem**: `ModuleNotFoundError: No module named 'yfinance'`
**Solution**: Ensure `uv pip install -e ".[dev]"` was run after merging pyproject.toml

### FMP API Quota
**Problem**: 402 Payment Required errors
**Solution**: Normal behavior for commodities - Yahoo Finance fallback works automatically

### Stale Plots
**Problem**: Old plots from previous runs remain
**Solution**: Already fixed - plotting code now cleans up stale plots

---

## Testing Strategy

### Unit Tests (Quick validation)
```bash
# Test each module independently
python -c "from hedgeye.config_loader import load_config"
python -c "from hedgeye.parse_eml import parse_risk_range_email"
# etc.
```

### Integration Tests (Step-by-step)
```bash
# Use test scripts (created in Phase 4)
python python/test_step1_parse.py
python python/test_step2_save.py
python python/test_step3_combine.py
python python/test_step4_plot.py
```

### End-to-End Test (Full pipeline)
```bash
cd python
python scripts/hedgeye/run_full_pipeline.py
```

### Validation Test (Compare with backup)
```bash
diff -r ~/d/downloads/hedgeye/prod.backup.*/daily/csv \
        ~/d/downloads/hedgeye/prod/daily/csv
```

---

## Success Criteria

### Must Have
- ✅ All imports working
- ✅ Full pipeline runs without errors
- ✅ Generates daily CSVs (risk_range_*.csv, change_events_*.csv)
- ✅ Generates combined CSV (combined_risk_range.csv)
- ✅ Generates 36 plots (active symbols only)
- ✅ Generates dashboard (risk_range_dashboard_*.png)
- ✅ Output matches backup data

### Nice to Have
- Clean up redundant imports
- Add `__init__.py` files for proper packages
- Refactor for better syndicate integration
- Update docs to match syndicate style

---

## Timeline Estimate

- **Phase 1** (Setup): 30-45 min
- **Phase 2** (Copy): 30 min
- **Phase 3** (Fix imports): 2-3 hours
- **Phase 4** (Test pipeline): 2-3 hours
- **Phase 5** (Validate): 30 min

**Total**: 6-8 hours (can spread over 2 days)

---

## IDE Notes (IntelliJ IDEA)

### Python Setup
1. Ensure Python plugin installed
2. Configure Python 3.13 interpreter for `python/` module
3. Mark `python/src/` as Sources Root
4. Mark `python/tests/` as Test Sources Root

### Testing in IDEA
- Use Python Console for quick import tests
- Create Run Configurations for test scripts
- Use debugger to step through import issues
- Terminal for running full pipeline

---

## Reference Documents

**Detailed Migration Plan**:
- `~/gh/randykerber/hedgeye-kb/docs/MIGRATION_TO_SYNDICATE.md`

**Original Project Docs**:
- Will be at `docs/data_sources/hedgeye/original/` after Phase 2

**Hedgeye-kb README**:
- `~/gh/randykerber/hedgeye-kb/README.md`

---

## Important Reminders

1. **hedgeye-kb is read-only** - Don't modify, only reference
2. **Test step-by-step** - Don't run full pipeline until steps work
3. **Commit frequently** - After each working module
4. **External data unchanged** - All paths in ~/d/downloads/ stay same
5. **Backup exists** - prod.backup.* for comparison
6. **Symbol count matters** - Should see 36 plots (7-day filter)

---

## Ready to Begin?

**Checklist**:
- ✅ Both repos git clean
- ✅ Production data backed up
- ✅ IntelliJ IDEA open with syndicate project
- ✅ This briefing document read and understood

**Start with Phase 1**: Setup & Config (30-45 min)

Let's migrate hedgeye into syndicate! 🚀

---

**Questions or Issues?**
Reference this document and the detailed migration plan. Take it step-by-step, test frequently, commit often.

Good luck!
— Claude Code (hedgeye-kb)
