# FMP API Test Results

Summary of Financial Modeling Prep API endpoint testing results.

## Stocks

`/api/v3/stock/list` → `stock-list-v3.csv`
- 85,473 rows : symbol, name, price, exchange, exchangeShortName, type

`/stable/stock-list` → `stock-list-stable.csv`
- 35,953 rows : symbol, companyName

## ETFs

`/api/v3/etf/list` → `etf-list-v3.csv`
- 13,028 rows : symbol, name, price, exchange, exchangeShortName, type

`/stable/etf-list` → `etf-list-stable.csv`
- 5,360 rows : symbol, name

## Indexes

`/api/v3/index/list` → `index-list-v3.csv`
- 0 rows : (no data returned)

`/stable/index-list` → `index-list-stable.csv`
- 194 rows : symbol, name, exchange, currency

## Countries

`/stable/available-countries` → `countries.csv`
- 120 rows : country

## Additional Entities

`/stable/available-exchanges` → `exchanges.csv`
- 71 rows : exchange, name, countryName, countryCode, symbolSuffix, delay

`/stable/available-industries` → `industries.csv`
- 159 rows : industry

`/stable/available-sectors` → `sectors.csv`
- 11 rows : sector

`/stable/commodities-list` → `commodities.csv`
- 40 rows : symbol, name, exchange, tradeMonth, currency

`/stable/forex-list` → `forex.csv`
- 1,542 rows : symbol, fromCurrency, toCurrency, fromName, toName

## File Organization & Symbolic Links

For convenience, symbolic links point to the best available data:

- `stocks.csv` → `stock-list-v3.csv` (85,476 rows - most comprehensive)
- `etfs.csv` → `etf-list-v3.csv` (13,032 rows - most comprehensive)  
- `indexes.csv` → `index-list-stable.csv` (194 rows - only working version)
- `countries.csv` → `countries-stable.csv` (119 rows - only working version)

**Usage:** Code can reference simple names (`stocks.csv`, `etfs.csv`, etc.) and automatically get the best available data.

## Notes

- **v3 API**: More comprehensive data, includes international exchanges
- **Stable API**: Subset data, appears more US-focused
- **v4 API**: Tested but returned 0 records (may require higher subscription)
- All files saved to: `/Users/rk/d/downloads/fmp/entities/` 

## Results of testing `v4` URLs -- none succeed

/api/v4/stock-list
Status: 200 (success)
Records: 0 rows
Result: Empty response

/api/v4/stock/list
Status: 200 (success)
Records: 0 rows
Result: Empty response

Summary:
✅ v4 endpoints exist (return 200 status codes)
❌ v4 endpoints return 0 records with your current subscription
🔍 v4 may require:
Higher subscription tier
Different authentication method
Additional parameters
Different endpoint naming convention
Comparison with working endpoints:
v3: Works with comprehensive data (85K+ stocks, 13K+ ETFs)
Stable: Works with subset data (35K+ stocks, 5K+ ETFs, 194 indexes)
v4: Exists but returns empty (0 records)

