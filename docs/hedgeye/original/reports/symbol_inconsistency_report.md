# Symbol Case and Naming Inconsistencies Report

**Analysis Date:** June 22, 2025  
**Data Source:** `/Users/rk/d/downloads/hedgeye/prod/all/csv/combined_risk_range.csv`  
**Data Range:** April 3, 2025 to June 20, 2025  
**Total Records:** 2,110  
**Unique Symbols:** 50  

## Executive Summary

The analysis has identified **3 major case inconsistencies** affecting **6 symbols** that are likely causing empty plots. These inconsistencies split data that should be combined, resulting in incomplete datasets for visualization.

## Critical Case Inconsistencies Found

### 1. COPPER vs Copper
- **COPPER**: 58 data points (major variant)
- **Copper**: 9 data points (minor variant)
- **Total Combined**: 67 data points
- **Impact**: Data is split across two symbols, likely causing incomplete plots

### 2. SILVER vs Silver  
- **SILVER**: 56 data points (major variant)
- **Silver**: 4 data points (minor variant)
- **Total Combined**: 60 data points
- **Impact**: Data is split across two symbols, likely causing incomplete plots

### 3. BITCOIN vs Bitcoin
- **BITCOIN**: 54 data points (major variant)
- **Bitcoin**: 1 data point (minor variant)
- **Total Combined**: 55 data points
- **Impact**: Data is split across two symbols, likely causing incomplete plots

## Symbol Data Distribution

### High-Volume Symbols (>50 data points)
These symbols have substantial data and should plot successfully:
- LQD: 66 points
- UST10Y: 65 points
- NATGAS: 64 points
- UST30Y: 62 points
- TSLA: 61 points
- UST2Y: 60 points
- BRENT: 58 points
- COPPER: 58 points (but missing 9 more from "Copper")
- RUT: 58 points
- AMZN: 58 points
- GOOGL: 58 points

### Low-Volume Symbols (<10 data points)
These symbols may produce empty or sparse plots:
- XLRE: 9 points
- Copper: 9 points (should be combined with COPPER)
- AMLP: 5 points
- Silver: 4 points (should be combined with SILVER)
- XLE: 3 points
- ITA: 3 points
- XLI: 2 points
- SPMO: 2 points
- REITS: 1 point
- Bitcoin: 1 point (should be combined with BITCOIN)
- XLY: 1 point

## Recommendations

### Immediate Actions Required

1. **Data Standardization**: Implement a symbol normalization process that converts all symbols to uppercase before storage or processing.

2. **Data Consolidation**: Merge the case-variant data:
   - Combine "Copper" (9) + "COPPER" (58) = 67 total points
   - Combine "Silver" (4) + "SILVER" (56) = 60 total points  
   - Combine "Bitcoin" (1) + "BITCOIN" (54) = 55 total points

3. **Parser Updates**: Modify the email parsing logic to normalize symbol names during extraction.

4. **Plotting Logic**: Update the plotting code to handle case-insensitive symbol matching.

### Data Quality Issues

The analysis also reveals symbols with very few data points that may not be suitable for meaningful time series visualization:
- 11 symbols have fewer than 10 data points
- 5 symbols have 5 or fewer data points
- 3 symbols have only 1-2 data points

## Root Cause Analysis

The case inconsistencies suggest that the email parsing process is extracting symbols exactly as they appear in the source emails, without standardization. This could be due to:

1. Inconsistent formatting in Hedgeye email reports
2. Lack of symbol normalization in the parsing pipeline
3. Different email templates or formats over time

## Next Steps

1. **Fix Data Pipeline**: Implement symbol normalization in `/Users/rk/gh/randykerber/syndicate/python/src/hedgeye/ds/rr/parse_eml.py`
2. **Reprocess Data**: Re-run the parsing pipeline with normalized symbols
3. **Update Plotting Code**: Ensure plotting logic handles symbol lookups case-insensitively
4. **Data Validation**: Add validation to detect and flag potential duplicate symbols during processing