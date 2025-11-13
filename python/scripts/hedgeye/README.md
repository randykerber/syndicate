# Scripts

Top-level commands for the Hedgeye Risk Range pipeline.

## Commands

### `run_full_pipeline.py`
Complete end-to-end pipeline: parse emails → combine data → generate plots

### `parse_emails.py`
Parse .eml files into CSV/Markdown outputs
- `python scripts/parse_emails.py` - Process all unprocessed files  
- `python scripts/parse_emails.py path/to/file.eml` - Process single file

### `combine_data.py`
Merge individual CSV files into master dataset

### `generate_plots.py`
Create time series plots for all symbols

### `create_conf.py`
Create configuration template (legacy - config should exist)

Purpose

  - scripts/run_full_pipeline.py - Complete pipeline
  - scripts/parse_emails.py - Email parsing only (supports single file or batch)
  - scripts/combine_data.py - Data combination only
  - scripts/generate_plots.py - Plot generation only
    
  Usage:
  python scripts/run_full_pipeline.py              # Everything
  python scripts/parse_emails.py                   # Parse all emails  
  python scripts/parse_emails.py path/to/file.eml  # Parse single file
  python scripts/combine_data.py                   # Combine CSVs
  python scripts/generate_plots.py                 # Generate plots

