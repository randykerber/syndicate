# PRD: ETF Pro Plus & Portfolio Solutions Email Parsing

**Date:** 2025-11-07
**Status:** Draft v0.1
**Author:** Claude Code

---

## Executive Summary

Extend the Hedgeye email parsing pipeline to extract and process two additional Hedgeye report types:

1. **ETF Pro Plus** - Long/short portfolio positions with trend ranges
2. **Portfolio Solutions** - Daily/weekly ETF rankings with **Keith McCullough's actual trades**

Similar to the existing Risk Range pipeline, these parsers will extract essential data from .eml files, produce structured CSV and Markdown outputs, enrich with current prices, and enable time-series analysis.

---

## Background

### Current State
- Successfully parsing Risk Range™ Signals emails
- Pipeline: `.eml` → extract data → CSV + Markdown → combine → enrich with prices → plots
- 2,897 records across 51 symbols processed
- Idempotent, timestamp-based processing
- **Risk Ranges cover:** Indexes + ETFs + Individual stocks (mixed)

### New Requirements
- Two new email types appearing in `/Users/rk/d/downloads/hedgeye/raw/eml/`:
  - **ETF Pro Plus** reports (weekly + updates) - also called "ETF Pro" or "etf-pro" (all synonyms)
  - **Portfolio Solutions** re-ranks (daily + weekly)
- Need to extract, structure, and track over time

### Key Distinctions
| Product | Position Sizing | Instrument Types |
|---------|----------------|------------------|
| **Risk Range™** | N/A (just ranges) | Indexes + ETFs + Stocks |
| **ETF Pro** | Binary (in/out only) | ETFs only (purchasable) |
| **Portfolio Solutions** | Specific (100bps, 50bps, "all") | ETFs only (purchasable) |

**Important:** ETF Pro changes are additions/removals ONLY - no position sizing information included.

---

## Goals

### Primary Goals
1. Extract actionable portfolio data from ETF Pro and Portfolio Solutions emails
2. Track Keith McCullough's actual trades over time (Portfolio Solutions)
3. Monitor ETF Pro portfolio composition and changes
4. Enable time-series analysis of portfolio evolution
5. Integrate with existing Obsidian workflow

### Secondary Goals
- Correlate with Risk Range data where applicable
- Identify patterns in portfolio adjustments
- Support eventual syndicate agent integration

---

## Data Sources

### 1. ETF Pro Plus Emails

#### Weekly Report
**Subject:** `ETF Pro Plus - New Weekly Report`
**Frequency:** Weekly (typically weekends)
**Content:**

**BULLISH Section (Long Positions):**
```
TICKER | DESCRIPTION | DATE ADDED | RECENT PRICE | TREND RANGE | ASSET CLASS
QQQ    | Nasdaq 100  | 5/23/2025  | $629.07      | $610.00-$644.00 | Domestic Equities
AAAU   | Physical Gold| 2/28/2025  | $39.48       | $38.18-$42.16   | Foreign Currency
```

**BEARISH Section (Short Positions):**
```
TICKER | DESCRIPTION | DATE ADDED | RECENT PRICE | TREND RANGE | ASSET CLASS
CANE   | Sugar       | 7/14/2025  | $9.30        | $8.91-$9.82  | Commodities
FXY    | Japanese Yen| 9/30/2025  | $59.66       | $59.08-$60.71 | Foreign Currencies
```

#### Update Emails
**Subject:** `UPDATE: N New ETF Pro Change(s)`
**Frequency:** As needed (intraday)
**Content:**

**Four possible change types:**
```
We are ADDING Long:
Robotics Automation (ROBO)

We are ADDING Short:
US Market Neutral (BTAL)

We are REMOVING Long:
Uranium (URA)

We are REMOVING Short:
Euro (FXE)
```

**Example:** November 5, 2025 update shows 3 of 4 types (missing "REMOVING Short")

**Note:** ETF Pro updates are **binary** - positions are either in or out. No position sizing information (unlike Portfolio Solutions which specifies "100bps", "50bps", "all").

### 2. Portfolio Solutions Emails

#### Daily Re-Rank
**Subject:** `Portfolio Solutions: Daily ETF Re-Rank (MM/DD/YYYY) | Top Movers: ...`
**Frequency:** Daily (market days)
**Content:**

**Ranked ETF List:**
```
Macro ETFs by Rank: FDRXX, CLOX, BUXX, CLOZ, QQQ, UUP, YCS, BBN, TLT, LQD, ...
```

**Top/Bottom Movers:**
```
1-WEEK RE-RANK HISTORY & CALLOUTS
Top Movers: YCS (+10), UUP (+9), QQQ (+7), QTUM (+7), BBN (+5)
Bottom Movers: IWM (-13), XLV (-9), AQWA (-8), TLT (-4), LQD (-4)
```

**Keith's Commentary (MOST IMPORTANT):**
```
Keith's Commentary: "In the PA today, I sold all URA. I sold 100bps LQD.
Sold 50bps BBN, TLT, PINK, PALL, CPER. Bought 100bps UUP. Bought 50bps MAGS, QQQ, YCS."
```

#### Weekly Re-Rank
**Subject:** `PORTFOLIO SOLUTIONS: Weekly ETF Re-Rank (MM/DD/YYYY) | Top Movers: ...`
**Frequency:** Weekly
**Content:** Similar to daily, with weekly perspective

---

## Data Extraction Requirements

### ETF Pro Plus - Weekly Report

**Extract:**
1. Report date (from email date or subject)
2. For each BULLISH position:
   - Ticker symbol
   - Description
   - Date added
   - Recent price
   - Trend range (low, high)
   - Asset class
3. For each BEARISH position:
   - Same fields as BULLISH

**Output Schema (CSV):**
```csv
report_date,position_type,ticker,description,date_added,price,range_low,range_high,asset_class
2025-11-02,LONG,QQQ,Nasdaq 100,2025-05-23,629.07,610.00,644.00,Domestic Equities
2025-11-02,SHORT,CANE,Sugar,2025-07-14,9.30,8.91,9.82,Commodities
```

### ETF Pro Plus - Update Emails

**Extract:**
1. Update date/time
2. For each change (4 possible types):
   - **ADDING Long** - New long position added
   - **ADDING Short** - New short position added
   - **REMOVING Long** - Long position removed
   - **REMOVING Short** - Short position removed
3. For each change:
   - Action: ADDING or REMOVING
   - Side: Long or Short
   - Ticker symbol
   - Description (if provided)

**Output Schema (CSV):**
```csv
update_datetime,action,side,ticker,description
2025-11-05 10:54:00,ADDING,LONG,ROBO,Robotics Automation
2025-11-05 10:54:00,ADDING,SHORT,BTAL,US Market Neutral
2025-11-05 10:54:00,ADDING,SHORT,IAK,US Insurance
2025-11-07 14:43:02,REMOVING,LONG,URA,Uranium
```

**Note:** No position sizing - changes are binary (in/out only).

### Portfolio Solutions - Daily Re-Rank

**Extract:**
1. Report date
2. Ranked ETF list (ordered)
3. Top movers (1-week) with rank changes
4. Bottom movers (1-week) with rank changes
5. Top movers (1-month) with rank changes
6. Bottom movers (1-month) with rank changes
7. **Keith's Commentary - Trades** (PRIORITY #1):
   - Parse each trade action
   - Action: bought/sold
   - Size: "all", "100bps", "50bps", etc.
   - Ticker(s)

**Output Schema - Rankings (CSV):**
```csv
report_date,rank,ticker
2025-11-07,1,FDRXX
2025-11-07,2,CLOX
2025-11-07,3,BUXX
```

**Output Schema - Rank Changes (CSV):**
```csv
report_date,period,ticker,rank_change
2025-11-07,1week,YCS,+10
2025-11-07,1week,UUP,+9
2025-11-07,1month,IWM,-10
```

**Output Schema - Keith's Trades (CSV) - MOST IMPORTANT:**
```csv
report_date,action,size,ticker
2025-11-07,SOLD,all,URA
2025-11-07,SOLD,100bps,LQD
2025-11-07,SOLD,50bps,BBN
2025-11-07,SOLD,50bps,TLT
2025-11-07,SOLD,50bps,PINK
2025-11-07,SOLD,50bps,PALL
2025-11-07,SOLD,50bps,CPER
2025-11-07,BOUGHT,100bps,UUP
2025-11-07,BOUGHT,50bps,MAGS
2025-11-07,BOUGHT,50bps,QQQ
2025-11-07,BOUGHT,50bps,YCS
```

### Portfolio Solutions - Weekly Re-Rank

**Extract:** Same as daily, but weekly frequency and perspective

---

## Processing Pipeline

### Phase 1: Email Parsing
Similar to existing Risk Range parser:

```
Input:  /Users/rk/d/downloads/hedgeye/raw/eml/*.eml
↓
Parse HTML email body
↓
Extract structured data based on email type
↓
Output:
  - /Users/rk/d/downloads/hedgeye/prod/etf_pro/csv/[date].csv
  - /Users/rk/d/downloads/hedgeye/prod/portfolio_solutions/csv/[date].csv
```

### Phase 2: Data Combination
Combine individual daily/weekly files into master datasets:

```
Input:  Daily CSV files
↓
Combine and deduplicate
↓
Output: Combined time-series CSV files
  - etf_pro_positions_all.csv
  - etf_pro_updates_all.csv
  - portfolio_solutions_rankings_all.csv
  - portfolio_solutions_trades_all.csv (KEITH'S TRADES)
```

### Phase 3: Enrichment
Add current market prices (similar to Risk Range enhancement):

```
Input:  Combined CSV files
↓
Fetch latest prices from FMP/Yahoo
↓
Calculate metrics:
  - Current position vs trend range
  - Rank change momentum
  - Trade execution analysis
↓
Output: Enriched CSV files
```

### Phase 4: Visualization
Generate plots and summaries:

1. **ETF Pro Portfolio Evolution**
   - Position sizes over time
   - Long/short ratio
   - Asset class allocation

2. **Portfolio Solutions Tracking**
   - Rank changes heatmap
   - Keith's trade activity over time
   - Top movers frequency

3. **Cross-reference with Risk Range**
   - ETF Pro trend ranges vs Risk Ranges
   - Correlation analysis

### Phase 5: Obsidian Integration

**Markdown Output Locations:**
- `/Users/rk/d/downloads/hedgeye/prod/etf_pro/md/`
- `/Users/rk/d/downloads/hedgeye/prod/portfolio_solutions/md/`

**Markdown Format (ETF Pro - Weekly Snapshot):**
```markdown
# ETF Pro Plus Portfolio - 2025-11-02

## Long Positions (23)
| Ticker | Description | Price | Trend Range | Asset Class |
|--------|-------------|-------|-------------|-------------|
| QQQ | Nasdaq 100 | $629.07 | $610.00-$644.00 | Domestic Equities |
| AAAU | Physical Gold | $39.48 | $38.18-$42.16 | Foreign Currency |

## Short Positions (11)
| Ticker | Description | Price | Trend Range | Asset Class |
|--------|-------------|-------|-------------|-------------|
| CANE | Sugar | $9.30 | $8.91-$9.82 | Commodities |
```

**Markdown Format (Portfolio Solutions - Daily Trades):**
```markdown
# Portfolio Solutions - 2025-11-07

## Keith's Trades
**Sold:**
- URA (all)
- LQD (100bps)
- BBN, TLT, PINK, PALL, CPER (50bps each)

**Bought:**
- UUP (100bps)
- MAGS, QQQ, YCS (50bps each)

## Rankings
1. FDRXX
2. CLOX
3. BUXX
...

## Top Movers (1-week)
- YCS: +10
- UUP: +9
- QQQ: +7
```

---

## Technical Considerations

### Parser Architecture

**Option 1: Extend Existing Parser**
- Add new email type detection to `parse_eml.py`
- Pros: Reuse existing infrastructure
- Cons: More complex, mixed concerns

**Option 2: Separate Parsers**
- Create `parse_etf_pro.py` and `parse_portfolio_solutions.py`
- Pros: Clean separation, easier to maintain
- Cons: Some code duplication

**Recommendation:** Option 2 (separate parsers) following similar patterns to existing Risk Range parser

### Data Storage

**Directory Structure:**
```
/Users/rk/d/downloads/hedgeye/
├── raw/eml/                          # Input emails
├── prod/
│   ├── daily/                         # Existing Risk Range
│   │   ├── csv/
│   │   └── md/
│   ├── etf_pro/                       # NEW
│   │   ├── weekly/csv/
│   │   ├── weekly/md/
│   │   ├── updates/csv/
│   │   ├── updates/md/
│   │   └── combined/csv/
│   ├── portfolio_solutions/           # NEW
│   │   ├── daily/csv/
│   │   ├── daily/md/
│   │   ├── weekly/csv/
│   │   ├── weekly/md/
│   │   └── combined/csv/
│   └── all/
│       ├── csv/                       # Combined datasets
│       └── plots/                     # Visualizations
```

### Configuration

Add to `conf/config.yaml`:
```yaml
paths:
  # Existing paths...
  etf_pro_weekly_csv: /Users/rk/d/downloads/hedgeye/prod/etf_pro/weekly/csv
  etf_pro_weekly_md: /Users/rk/d/downloads/hedgeye/prod/etf_pro/weekly/md
  etf_pro_updates_csv: /Users/rk/d/downloads/hedgeye/prod/etf_pro/updates/csv
  etf_pro_updates_md: /Users/rk/d/downloads/hedgeye/prod/etf_pro/updates/md
  portfolio_solutions_daily_csv: /Users/rk/d/downloads/hedgeye/prod/portfolio_solutions/daily/csv
  portfolio_solutions_daily_md: /Users/rk/d/downloads/hedgeye/prod/portfolio_solutions/daily/md
  portfolio_solutions_weekly_csv: /Users/rk/d/downloads/hedgeye/prod/portfolio_solutions/weekly/csv
  portfolio_solutions_weekly_md: /Users/rk/d/downloads/hedgeye/prod/portfolio_solutions/weekly/md

parsing:
  # Existing settings...
  etf_pro_subject_patterns:
    - "ETF Pro Plus - New Weekly Report"
    - "UPDATE:.*ETF Pro Change"
  portfolio_solutions_subject_patterns:
    - "Portfolio Solutions: Daily ETF Re-Rank"
    - "PORTFOLIO SOLUTIONS: Weekly ETF Re-Rank"
```

### Symbol Canonicalization

Reuse existing `symbol_canonicalization.py`:
- ETF symbols should be more standardized than Risk Range symbols
- May need minimal additions for FX pairs or commodities

### Price Enrichment

Leverage existing FMP/Yahoo integration:
- Most ETF Pro tickers are standard ETFs (easy to price)
- Some may be commodities or FX (already handled)

---

## Integration with Existing Systems

### Risk Range Correlation

**Question:** How do ETF Pro "Trend Ranges" relate to Risk Range™ Signals?

**Analysis:**
- **ETF Pro trend ranges:** Price ranges for ETF positions (ETFs only, purchasable)
- **Risk Range signals:** Price ranges for securities/indices (mixed: indexes + ETFs + stocks)
- **Likely overlap:** Some ETF Pro positions (QQQ, GDX, etc.) appear in Risk Range reports
- **Opportunity:** Cross-reference to validate consistency

**Example:**
```
Risk Range: QQQ $610.00-$644.00 (covers the ETF)
ETF Pro:    QQQ $610.00-$644.00 (LONG position)
→ CONSISTENT: Long position aligns with Risk Range
```

**Key Differences:**
| Aspect | ETF Pro | Risk Range |
|--------|---------|------------|
| Coverage | ETFs only | Indexes + ETFs + Stocks |
| Purpose | Portfolio positions (binary in/out) | Price ranges for analysis |
| Sizing | No sizing info | N/A (just ranges) |

### Syndicate Integration

When integrated with Syndicate agents:

**Use Cases:**
1. **Portfolio Tracking Agent**
   - Monitor Keith's actual trades
   - Alert on significant position changes
   - Track performance over time

2. **ETF Pro Analysis Agent**
   - Compare portfolio composition to market conditions
   - Identify sector/asset class tilts
   - Correlate with Risk Range signals

3. **Trading Ideas Agent**
   - Extract actionable trades from Keith's commentary
   - Compare to personal portfolio
   - Generate trade notifications

---

## Success Criteria

### Phase 1: Basic Parsing
- [ ] Successfully parse all ETF Pro weekly reports
- [ ] Successfully parse all ETF Pro update emails
- [ ] Successfully parse all Portfolio Solutions daily re-ranks
- [ ] Successfully parse all Portfolio Solutions weekly re-ranks
- [ ] Extract Keith's trades with 100% accuracy

### Phase 2: Data Quality
- [ ] No duplicate records in combined datasets
- [ ] All dates in ISO 8601 format
- [ ] Symbol canonicalization applied correctly
- [ ] Price enrichment working for 95%+ of tickers

### Phase 3: Integration
- [ ] Markdown files readable in Obsidian
- [ ] CSV files queryable with existing tools
- [ ] Plots generated successfully
- [ ] Pipeline runs idempotently

### Phase 4: Insights
- [ ] Can track portfolio evolution over time
- [ ] Can identify Keith's most frequent trades
- [ ] Can correlate with Risk Range data
- [ ] Can generate actionable summaries

---

## Open Questions

### 1. Implementation Location
**Question:** Build parsers in `hedgeye-kb` (this project) or `syndicate`?

**Considerations:**
- **hedgeye-kb pros:**
  - Existing infrastructure for email parsing
  - Similar data flow and patterns
  - Already has FMP/Yahoo integration
- **hedgeye-kb cons:**
  - Scheduled for migration to syndicate
  - May need to move code later

- **syndicate pros:**
  - Final destination for code
  - Agent integration built-in
- **syndicate cons:**
  - Need to set up parsing infrastructure
  - Duplicate effort if code structure differs

**Recommendation:** TBD - needs discussion

### 2. Parser Granularity
**Question:** Single parser for all types, or separate parsers per email type?

**Options:**
- A) One parser with type detection: `parse_hedgeye_emails.py`
- B) Separate parsers: `parse_etf_pro.py`, `parse_portfolio_solutions.py`
- C) Separate parsers per frequency: `parse_etf_pro_weekly.py`, `parse_etf_pro_updates.py`, etc.

**Recommendation:** Option B (separate by product) - clean separation, easier to maintain

### 3. Keith's Trade Parsing Strategy
**Question:** How to reliably parse Keith's commentary text?

**Challenges:**
- Free-form text: "I sold all URA. I sold 100bps LQD. Sold 50bps BBN, TLT, PINK..."
- Multiple tickers in one sentence: "Sold 50bps BBN, TLT, PINK, PALL, CPER"
- Size variations: "all", "100bps", "50bps"
- Implicit subjects: "Sold..." (subject "I" implied)

**Proposed Approach:**
1. Regex patterns for action phrases: `(sold|bought|selling|buying)`
2. Extract size: `(all|\d+bps)`
3. Extract tickers: Comma-separated list or individual mentions
4. Handle both formats:
   - "I sold 100bps LQD" → one trade
   - "Sold 50bps BBN, TLT, PINK" → three trades at same size

**Validation:** Cross-reference with portfolio changes in weekly reports

### 4. Historical Data
**Question:** Should we backfill historical data or start from now?

**Options:**
- A) Parse only new emails going forward
- B) Parse all available historical emails in `/raw/eml/`

**Recommendation:** Option B - parse all available to build historical dataset

### 5. Data Retention
**Question:** Keep all raw parsed data or only combined/enriched?

**Recommendation:** Keep both:
- Daily/weekly CSV files for audit trail
- Combined files for analysis
- Similar to existing Risk Range approach

---

## Next Steps

### Immediate (PRD Phase)
1. Review and refine this PRD
2. Decide: hedgeye-kb vs syndicate implementation
3. Validate data extraction schemas with sample emails
4. Confirm output format requirements

### Development (Implementation Phase)
1. Create directory structure
2. Implement ETF Pro parser (weekly reports first)
3. Implement ETF Pro parser (updates)
4. Implement Portfolio Solutions parser (daily)
5. Implement Portfolio Solutions parser (weekly)
6. Implement data combination logic
7. Implement price enrichment
8. Implement Markdown generation
9. Test end-to-end pipeline
10. Add to full pipeline script

### Future Enhancements
- Visualization dashboards
- Trade performance tracking
- Portfolio rebalancing alerts
- Risk Range correlation analysis
- Syndicate agent integration

---

## Appendix A: Sample Email Patterns

### ETF Pro Weekly Report Text Pattern
```
BULLISHTICKERDATE ADDEDRECENT PRICE*TREND RANGESASSET CLASS
Income Short MaturityBUXX10/25/2023$20.27$20.22$20.31Domestic Fixed Income
Physical GoldAAAU2/28/2025$39.48$38.18$42.16Foreign Currency
```

### ETF Pro Update Text Pattern (Nov 5, 2025 - 3 of 4 types)
```
Dear ETF Pro Plus Subscriber,

Below is a Real-Time Update to ETF Pro Plus:

We are ADDING Long:

Robotics Automation (ROBO)

We are ADDING Short:

US Market Neutral (BTAL)

US Insurance (IAK)
```

**Note:** This example shows 3 of 4 possible change types. Missing: "We are REMOVING Short:"
Example of 4th type: "We are REMOVING Short: Euro (FXE)"

### Portfolio Solutions Daily Text Pattern
```
Macro ETFs by Rank: FDRXX, CLOX, BUXX, CLOZ, QQQ, UUP, YCS, BBN, TLT, LQD, ...

Keith's Commentary: "In the PA today, I sold all URA. I sold 100bps LQD.
Sold 50bps BBN, TLT, PINK, PALL, CPER. Bought 100bps UUP. Bought 50bps MAGS, QQQ, YCS."
```

---

## Appendix B: Data Schema Summary

### ETF Pro - Weekly Positions
```python
{
    'report_date': str,      # ISO 8601
    'position_type': str,    # 'LONG' or 'SHORT'
    'ticker': str,
    'description': str,
    'date_added': str,       # ISO 8601
    'price': float,
    'range_low': float,
    'range_high': float,
    'asset_class': str
}
```

### ETF Pro - Updates (Binary: In/Out Only)
```python
{
    'update_datetime': str,  # ISO 8601 with time
    'action': str,           # 'ADDING' or 'REMOVING'
    'side': str,             # 'LONG' or 'SHORT'
    'ticker': str,
    'description': str       # Optional
}
```

**Note:** ETF Pro changes are binary (position in or out). No position sizing information, unlike Portfolio Solutions which includes "100bps", "50bps", "all".

### Portfolio Solutions - Rankings
```python
{
    'report_date': str,      # ISO 8601
    'rank': int,
    'ticker': str
}
```

### Portfolio Solutions - Rank Changes
```python
{
    'report_date': str,      # ISO 8601
    'period': str,           # '1week' or '1month'
    'ticker': str,
    'rank_change': int       # Can be negative
}
```

### Portfolio Solutions - Keith's Trades (PRIORITY)
```python
{
    'report_date': str,      # ISO 8601
    'action': str,           # 'BOUGHT' or 'SOLD'
    'size': str,             # 'all', '100bps', '50bps', etc.
    'ticker': str
}
```

---

**Document Status:** Draft v0.1 - Ready for review and refinement