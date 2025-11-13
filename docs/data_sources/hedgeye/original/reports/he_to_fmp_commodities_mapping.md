# Hedgeye to FMP Commodities Mapping

## Overview

This document outlines the mapping of Hedgeye commodity symbols to FMP entity symbols, with important caveats about futures vs spot pricing.

## Commodities Mappings

The following Hedgeye commodity symbols are mapped to FMP futures contracts:

| Hedgeye Symbol | FMP Symbol | FMP Name | Entity Type | Notes |
|----------------|------------|----------|-------------|-------|
| BRENT | BZUSD | Brent Crude Oil | commodities | Brent Crude Oil futures |
| COPPER | HGUSD | Copper | commodities | Copper futures |
| Copper | HGUSD | Copper | commodities | Same as COPPER - different capitalization |
| GOLD | GCUSD | Gold Futures | commodities | Gold commodity futures |
| OIL | CLUSD | Crude Oil | commodities | WTI Crude Oil commodity |
| SILVER | SIUSD | Silver Futures | commodities | Silver commodity futures |
| ZN | ZNUSD | 10-Year T-Note Futures | commodities | 10-Year Treasury Note futures |
| ZB | ZBUSD | 30 Year U.S. Treasury Bond Futures | commodities | 30-Year Treasury Bond futures |

## Critical Caveat: Futures vs Spot Pricing

**IMPORTANT**: All commodity mappings currently use FMP futures contracts, not spot prices. This may not correspond to Hedgeye's price specifications.

### Potential Issues

1. **Price Discrepancies**: Futures prices may differ systematically from spot prices
2. **Contract Expiration**: Futures have expiration dates and roll-over effects
3. **Basis Risk**: The difference between futures and spot prices can vary over time
4. **Hedgeye Specification**: Need to verify if Hedgeye uses spot or futures prices

### Investigation Required

When comparing FMP prices with Hedgeye close prices, monitor for:

- Systematic price differences
- Patterns that suggest futures vs spot mismatch
- Whether Hedgeye documentation specifies spot or futures pricing

### Possible Solutions

If futures vs spot mismatch is confirmed:

1. **Find FMP spot price endpoints** (if available)
2. **Use different FMP symbols** for spot pricing
3. **Apply basis adjustments** if needed
4. **Document the relationship** between futures and spot for each commodity

## Next Steps

1. Use current mappings for initial data pipeline development
2. Compare Hedgeye vs FMP prices to identify discrepancies
3. Investigate FMP spot price availability if needed
4. Update mappings based on empirical findings
5. Document final resolution in this file

## Related Files

- `/Users/rk/d/downloads/fmp/he_to_fmp.csv` - Complete mapping table
- `src/hedgeye_kb/create_mapping_table.py` - Script to regenerate mappings 