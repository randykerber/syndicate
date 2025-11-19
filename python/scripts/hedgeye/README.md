# Scripts

Top-level commands for the Hedgeye Risk Range pipeline.

## Commands

### `run_full_rr_pipeline.py`
Complete end-to-end Risk Range pipeline: parse emails → combine data → generate plots

### `parse_rr_emails.py`
Parse Risk Range .eml files into CSV/Markdown outputs
- `python scripts/parse_rr_emails.py` - Process all unprocessed files  
- `python scripts/parse_rr_emails.py path/to/file.eml` - Process single file

### `combine_rr_data.py`
Merge individual Risk Range CSV files into master dataset

### `generate_rr_plots.py`
Create time series plots for all Risk Range symbols

### `create_conf.py`
Create configuration template (legacy - config should exist)

Purpose

  - scripts/run_full_rr_pipeline.py - Complete Risk Range pipeline
  - scripts/parse_rr_emails.py - Risk Range email parsing only (supports single file or batch)
  - scripts/combine_rr_data.py - Risk Range data combination only
  - scripts/generate_rr_plots.py - Risk Range plot generation only
    
  Usage:
  python scripts/run_full_rr_pipeline.py              # Everything
  python scripts/parse_rr_emails.py                   # Parse all Risk Range emails  
  python scripts/parse_rr_emails.py path/to/file.eml  # Parse single file
  python scripts/combine_rr_data.py                   # Combine Risk Range CSVs
  python scripts/generate_rr_plots.py                 # Generate Risk Range plots

