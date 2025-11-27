# CSV Files Used for CR Time-Series Plotting

## Summary

The `cr_time_series_plotting.py` module reads **3 types of CSV files** directly (no intermediate merged files):

1. **EP Weekly CSVs** - All files matching pattern
2. **RR Daily CSVs** - All files matching pattern (via `load_all_risk_range_data()`)
3. **Mapping CSV** - Single file

## Input CSV Files (Read Only)

### 1. EP Weekly CSVs (Trend Ranges)
- **Location**: `/Users/rk/d/downloads/hedgeye/prod/etf_pro/csv/`
- **Pattern**: `etf_pro_weekly_YYYY-MM-DD.csv`
- **Read by**: `load_ep_time_series()` - reads ALL matching files
- **Columns used**:
  - `report_date` - Date of weekly report
  - `ticker` - Symbol (e.g., "AAAU")
  - `trend_low` - Lower trend range bound
  - `trend_high` - Upper trend range bound
  - `recent_price` - Price at report date
- **Usage**: 
  - Loads all weekly files for the ticker
  - Forward-fills weekly values to daily time series
  - Provides trend ranges over time

### 2. RR Daily CSVs (Trade Ranges)
- **Location**: `/Users/rk/d/downloads/hedgeye/prod/daily/csv/`
- **Pattern**: `risk_range_*.csv` (all files matching this pattern)
- **Read by**: `load_all_risk_range_data()` → `load_rr_time_series_with_translation()`
- **Columns used**:
  - `date` - Date of risk range
  - `index` - Reference symbol (e.g., "GOLD" for AAAU)
  - `buy_trade` - Lower trade range bound (in r_sym coordinates)
  - `sell_trade` - Upper trade range bound (in r_sym coordinates)
  - `prev_close` - Previous close price (in r_sym coordinates)
- **Usage**:
  - Loads all daily RR files
  - Filters for r_sym (from mapping)
  - Translates trade ranges from r_sym to p_sym coordinates using daily prices

### 3. Mapping CSV (Symbol Translation)
- **Location**: `/Users/rk/d/downloads/hedgeye/prod/ranges/`
- **File**: `p-to-r-mapping.csv`
- **Read by**: `plot_cr_time_series()`
- **Columns used**:
  - `p_sym` - Portfolio symbol (tradable, e.g., "AAAU")
  - `r_sym` - Risk Range reference symbol (e.g., "GOLD")
  - `proxy_type` - Type of proxy relationship
- **Usage**: Maps p_sym → r_sym to find which RR data to load

## External Data Sources (Not CSV)

### 4. Daily Prices (yfinance API)
- **Source**: Yahoo Finance via `yfinance` library
- **Fetched by**: `fetch_historical_daily_prices()`
- **Usage**: 
  - Fetches daily closing prices for p_sym (e.g., AAAU)
  - Used for plotting price history
  - Used for translating RR trade ranges from r_sym to p_sym coordinates
- **No caching** (fetched fresh each time for debugging)

## Output Files (Created, Not Read)

### 5. Plot PNG
- **Location**: `/Users/rk/d/downloads/hedgeye/prod/ranges/plots/cr_timeseries_test/`
- **Pattern**: `cr_timeseries_*.png`
- **Created by**: `plot_cr_time_series()`
- **Overwrites**: Yes (freely overwrites existing plots)

## Files NOT Used by Time-Series Plotting

These files are used by other CR pipeline scripts but **NOT** by time-series plotting:

- **PS Daily CSVs**: Used by `cr_merge_ranges.py` for snapshot merge, but not needed for time-series
- **Base Merge CSV** (`position_ranges_base.csv`): Used by `cr_enrich_ranges.py`, but time-series plotting reads source files directly
- **Enriched CSV** (`position_ranges_enriched.csv`): Used by `cr_plotting.py` for snapshot plots, but time-series plotting builds its own time series

## Data Flow

```
EP Weekly CSVs (all files)
    ↓
load_ep_time_series()
    ↓
Daily trend ranges (forward-filled)

RR Daily CSVs (all files)
    ↓
load_all_risk_range_data()
    ↓
Filter by r_sym (from mapping)
    ↓
load_rr_time_series_with_translation()
    ↓
Translate using daily prices
    ↓
Daily trade ranges (in p_sym coordinates)

Daily Prices (yfinance)
    ↓
fetch_historical_daily_prices()
    ↓
Daily closing prices (p_sym)

Merge all by date → Plot
```

## Key Points

1. **Time-series plotting reads source files directly** - doesn't use intermediate merged CSVs
2. **All EP weekly files** are loaded (not just latest) - builds historical time series
3. **All RR daily files** are loaded (not just latest) - builds historical time series
4. **Translation happens on-the-fly** - RR ranges translated from r_sym to p_sym coordinates using daily prices
5. **No caching** - prices fetched fresh each time (for debugging simplicity)

