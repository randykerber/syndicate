---
name: hedgeye-pipelines
description: Hedgeye financial data pipeline conventions — file locations, naming, CSV processing, price fetching, key files. Load when working on Hedgeye code in the Syndicate project.
user-invocable: false
---

# Hedgeye Pipeline Conventions

## Data Location (External to Project)

Hedgeye data lives **outside the repo** — always use absolute paths, never relative.

```
/Users/rk/d/downloads/hedgeye/
├── raw/eml/              # Input emails (*.eml)
├── prod/
│   ├── ranges/           # Position range CSVs (*_YYYY-MM-DD.csv)
│   │   └── enriched/     # Enriched with live prices
│   └── cache/            # Daily price cache (JSON)
└── archive/
```

## File Naming
- All output filenames include date: `*_YYYY-MM-DD.csv`
- Snake case for all column names
- Always include `report_date` column in outputs

## CSV Processing
- Read with `dtype=str` first, then convert types explicitly — prevents ticker symbols from being misread as numbers
- Standard columns: `ticker`, `price`, `rr_upper`, `rr_lower`, `report_date`

## Price Fetching — Three-Tier Fallback
1. FMP mapping via `he_to_fmp.csv` — special symbols (commodities, forex, indexes)
2. FMP direct lookup
3. yfinance fallback
- When live price unavailable: fall back to `rr_prev_close` from Risk Range report
- Cache daily prices as JSON to avoid repeated API calls

## Key Files
- `merge_position_ranges.py` — combines ETF Pro + Portfolio Solutions + Risk Range data
- `enrich_position_ranges.py` — fetches prices, calculates proxy ranges
- `fetch_prices.py` — multi-source price fetching with fallbacks
- `he_to_fmp.csv` — symbol mapping for special asset types

## Cross-reference
Cursor rules (code-example level detail): `syndicate/.cursor/rules/hedgeye.mdc`
