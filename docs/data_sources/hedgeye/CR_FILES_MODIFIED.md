# CR Pipeline - Files Modified in ~/d/downloads

## Summary

**The time-series plotting code (`cr_time_series_plotting.py`) is READ-ONLY** - it only reads existing files and creates new PNG plot files. It does NOT modify any existing CSV files.

However, **other CR pipeline scripts DO overwrite existing files**. See details below.

## Time-Series Plotting (`cr_time_series_plotting.py`)

### Files READ (no modifications):
- `/Users/rk/d/downloads/hedgeye/prod/etf_pro/csv/etf_pro_weekly_*.csv` - EP weekly data
- `/Users/rk/d/downloads/hedgeye/prod/all/csv/combined_risk_range.csv` - RR combined data
- `/Users/rk/d/downloads/hedgeye/prod/ranges/p-to-r-mapping.csv` - Symbol mappings

### Files WRITTEN (new files only):
- `/Users/rk/d/downloads/hedgeye/prod/ranges/plots/cr_timeseries_test/*.png` - Plot images (new files, never overwrites)

**✅ Safe to run** - No existing files are modified.

## Other CR Pipeline Scripts

### `cr_merge_ranges.py`
**WRITES (OVERWRITES if exists):**
- `/Users/rk/d/downloads/hedgeye/prod/ranges/base/position_ranges_base.csv`

**⚠️ This file gets overwritten each time you run the merge script.**

### `cr_enrich_ranges.py`
**WRITES (OVERWRITES if exists):**
- `/Users/rk/d/downloads/hedgeye/prod/ranges/enriched/position_ranges_enriched.csv`
- `/Users/rk/d/downloads/hedgeye/prod/ranges/enriched/position_ranges_enriched.txt`

**⚠️ These files get overwritten each time you run the enrich script.**

## Recommendation

If you want to preserve the current state of the base and enriched CSVs before running merge/enrich scripts:

```bash
# Backup before running merge/enrich
cd /Users/rk/d/downloads/hedgeye/prod/ranges

# Backup base merge
if [ -f base/position_ranges_base.csv ]; then
    cp base/position_ranges_base.csv base/position_ranges_base.csv.backup.$(date +%Y%m%d-%H%M%S)
fi

# Backup enriched data
if [ -f enriched/position_ranges_enriched.csv ]; then
    cp enriched/position_ranges_enriched.csv enriched/position_ranges_enriched.csv.backup.$(date +%Y%m%d-%H%M%S)
    cp enriched/position_ranges_enriched.txt enriched/position_ranges_enriched.txt.backup.$(date +%Y%m%d-%H%M%S)
fi
```

## Next Steps for Time-Series Plotting

The plotting code needs these improvements:

1. **Fetch daily AAAU prices** for all dates in the plot range (currently only uses weekly EP prices)
2. **Add RR trade ranges** (daily) - already loading but need to ensure translation is correct
3. **Merge EP + RR data** to determine date range, then fetch prices for all those dates

These improvements will only create new files (plots) or potentially cache daily prices in a new file - they won't modify existing CSVs.

