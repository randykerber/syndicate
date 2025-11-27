# Plan: Generate CR Time-Series Plots for All Tickers

## Current State
- ✅ Working for 4 test tickers (AAAU, QQQ, TLT, UUP)
- ✅ Price cache system in place
- ✅ Inverted proxy logic implemented (TLT, BBN, BUXX, etc.)
- ✅ 30-day lookback window (debugging mode)

## Implementation Plan

### Phase 1: Batch Plotting Function

**Function**: `generate_all_cr_time_series_plots()`

**Steps**:
1. **Get all tickers** from EP weekly CSVs (source of truth for portfolio)
   - Load all EP weekly files
   - Extract unique tickers
   - Sort alphabetically

2. **Pre-fetch all prices** (batch operation, uses cache)
   - Determine date range (days_back from now)
   - Get unique list of all tickers
   - Batch fetch via `get_daily_prices()` (handles caching)
   - This ensures we have prices before plotting starts

3. **Load mapping table** once (for all tickers)

4. **Loop through tickers**:
   - Try to generate plot
   - Handle errors gracefully (continue on failure)
   - Track statistics:
     - Successful plots
     - Failed plots (with reasons)
     - EP-only plots (no RR data)
     - RR-only plots (no EP data)
     - Both EP+RR plots

5. **Output organization**:
   - Directory: `/Users/rk/d/downloads/hedgeye/prod/ranges/plots/cr_timeseries/`
   - Filename: `cr_timeseries_{ticker}.png`
   - Flat structure (no subdirectories)

6. **Summary report**:
   - Total tickers processed
   - Successful: X
   - Failed: Y (list reasons)
   - EP-only: Z tickers
   - RR-only: W tickers
   - Both: V tickers

### Phase 2: Error Handling Strategy

**Categories of tickers**:
1. **Full data** (EP + RR + prices) → Generate full plot with trend ranges + trade ranges
2. **EP-only** (no RR mapping) → Plot EP trend ranges + prices only (no trade ranges)
3. **RR-only** (no EP data) → Skip (not in portfolio)
4. **No prices** → Skip with warning
5. **Translation failure** → Skip with error message

**Note**: Most tickers in the portfolio have RR data via proxy mappings. Only a few tickers (like AQWA, BTAL, CANE) have no RR coverage.

**Error handling**:
- Individual ticker failures don't stop batch
- Log all failures with ticker name and reason
- Continue processing remaining tickers

### Phase 3: Configuration Options

**Parameters**:
- `days_back`: Default 100 (increase from 30 for production)
- `output_dir`: Configurable output directory
- `tickers_filter`: Optional list to filter specific tickers
- `require_rr_data`: Boolean - skip tickers without RR? (default: False)
- `require_ep_data`: Boolean - skip tickers without EP? (default: True)

### Phase 4: Performance Optimizations

1. **Price fetching**: Already optimized with cache
   - First run: Fetches all missing prices
   - Subsequent runs: Uses cache, only fetches new dates

2. **Batch operations**: 
   - Load mapping once
   - Load EP data once (all files)
   - Load RR data once (all files)
   - Pre-fetch all prices

3. **Memory**: Close plots after saving (already done with `plt.close()`)

### Phase 5: Output & Reporting

**Console output**:
- Progress indicator (X/Y tickers processed)
- Per-ticker status (✅ or ❌)
- Summary statistics at end

**Optional outputs**:
- Failed tickers CSV (ticker, reason, timestamp)
- Summary CSV (ticker, has_ep, has_rr, has_prices, status)

## Implementation Details

### Function Signature
```python
def generate_all_cr_time_series_plots(
    days_back: int = 100,
    output_dir: Optional[Path] = None,
    tickers_filter: Optional[List[str]] = None,
    require_rr_data: bool = False,
    require_ep_data: bool = True
) -> Dict[str, Any]:
    """
    Generate CR time-series plots for all tickers.
    
    Returns:
        Dictionary with statistics: {
            'total': int,
            'successful': int,
            'failed': int,
            'ep_only': int,
            'failed_list': List[Dict[str, str]]
        }
    """
```

### Ticker Discovery
- Load all EP weekly CSVs
- Extract unique tickers from `ticker` column
- Filter by `tickers_filter` if provided

### Pre-fetching Prices
- Get all unique tickers
- Determine date range: `now() - days_back` to `now()`
- Call `get_daily_prices(all_tickers, start_date, end_date)`
- This populates cache and ensures prices available

### Plot Generation Loop
```python
for ticker in tickers:
    try:
        # Check if has EP data
        # Check if has RR data (via mapping)
        # Generate plot
        # Save plot
        # Track success
    except Exception as e:
        # Log error
        # Track failure
        # Continue
```

## Questions to Decide

1. **days_back**: 
   - Keep at 30 for now? 
   - Or increase to 100 for production?
   - **Recommendation**: Make it a parameter, default 100

2. **Filtering**:
   - Only tickers with both EP+RR? 
   - Or include EP-only?
   - **Recommendation**: Include EP-only (show what we have)

3. **Output location**:
   - Same directory as test plots?
   - Or separate production directory?
   - **Recommendation**: Separate directory `cr_timeseries/` (not `cr_timeseries_test/`)

4. **Script location**:
   - Add to `cr_time_series_plotting.py`?
   - Or create separate script like `generate_cr_plots.py`?
   - **Recommendation**: Add to module, create script wrapper

## Next Steps

1. ✅ Review and approve plan
2. Implement `generate_all_cr_time_series_plots()` function
3. Create script wrapper: `scripts/hedgeye/generate_cr_time_series_plots.py`
4. Test with small subset (10 tickers)
5. Run full batch (all ~37 tickers)
6. Review results and iterate

