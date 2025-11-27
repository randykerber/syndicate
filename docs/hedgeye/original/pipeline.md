# Data Pipeline

## Step-by-Step

1. Parse `.eml` file to extract embedded HTML.
2. Extract date, tables, and change text.
3. Generate:
   - Markdown tables for Obsidian sync.
   - CSV files for time series analysis.
4. Store outputs under:
   - `prod/daily/md/` for Markdown
   - `prod/daily/csv/` for CSV
