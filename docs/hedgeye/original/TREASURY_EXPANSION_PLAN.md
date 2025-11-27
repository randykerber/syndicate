# Treasury Expansion Plan

## Current Treasury Coverage (5 instruments)
```
US3M   -> indexes:^IRX     (Yahoo - Real-time)
UST2Y  -> treasury:year2   (FMP - Only 2Y source found)
UST5Y  -> indexes:^FVX     (Yahoo - Real-time)
UST10Y -> indexes:^TNX     (Yahoo - Real-time)
UST30Y -> indexes:^TYX     (Yahoo - Real-time)
```

## Future FRED Integration (Option A: Hybrid Strategy)

### Add Regular Treasury Gaps (6 instruments)
```
UST1M  -> fred:DGS1MO     (FRED - Daily)
UST6M  -> fred:DGS6MO     (FRED - Daily)
UST1Y  -> fred:DGS1       (FRED - Daily)
UST3Y  -> fred:DGS3       (FRED - Daily)
UST7Y  -> fred:DGS7       (FRED - Daily)
UST20Y -> fred:DGS20      (FRED - Daily)
```

### Add TIPS - Treasury Inflation-Protected Securities (4 instruments)
```
US5YT  -> fred:DFII5      (FRED - 5-Year TIPS)
US10YT -> fred:DFII10     (FRED - 10-Year TIPS)
US20YT -> fred:DFII20     (FRED - 20-Year TIPS)
US30YT -> fred:DFII30     (FRED - 30-Year TIPS)
```

## Complete Coverage Summary
- **Current**: 5 treasury instruments
- **After FRED**: 15 treasury instruments
- **Regular Curve**: 11 points (1M → 3M → 6M → 1Y → 2Y → 3Y → 5Y → 7Y → 10Y → 20Y → 30Y)
- **TIPS Curve**: 4 points (5Y → 10Y → 20Y → 30Y inflation-protected)

## Implementation Notes
- Keep real-time Yahoo/FMP for existing symbols
- Add FRED for gaps using existing API key
- Requires `fredapi` package: `uv add fredapi`
- FRED updates daily around 4:15 PM ET
- FRED provides official Federal Reserve data

## FRED API Integration
- Base URL: `https://api.stlouisfed.org/fred/series/observations`
- Series format: `DGS{duration}` for regular, `DFII{duration}` for TIPS
- Requires API key (already available)