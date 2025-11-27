# Processing Logic Analysis: "Already Processed" Checks

**Purpose**: Document how the pipeline determines if an email needs processing, especially when the `prod` directory is renamed/recreated.

## Overview

All three email processing scripts check if an email has already been processed by verifying if the corresponding output CSV file exists in the configured output directory.

## Processing Logic Locations

### 1. EP (ETF Pro Weekly) Processing

**File**: `python/src/syndicate/data_sources/hedgeye/process_etf_pro_weekly.py`

**Logic**:
- Line 111-113: Loads `csv_dir` from config: `Path(config["paths"]["etf_pro_csv_dir"])`
- Line 24-43: `is_already_processed()` function:
  ```python
  def is_already_processed(eml_filename: str, csv_dir: Path) -> bool:
      # Extract date from filename
      match = re.match(r'etf_pro_weekly_(\d{4}-\d{2}-\d{2})\.eml', eml_filename)
      if match:
          date = match.group(1)
          csv_path = csv_dir / f"etf_pro_weekly_{date}.csv"
          return csv_path.exists()  # ← Checks if file exists in csv_dir
      return False
  ```
- Line 129: Used in filter: `if not is_already_processed(eml.name, csv_dir)`

**Key Point**: Checks if CSV exists in `config["paths"]["etf_pro_csv_dir"]` which resolves to `${prod_root}/etf_pro/csv`

### 2. PS (Portfolio Solutions) Processing

**File**: `python/src/syndicate/data_sources/hedgeye/process_portfolio_solutions.py`

**Logic**:
- Line 317-319: Loads `csv_dir` from config: `Path(config["paths"]["portfolio_solutions_csv_dir"])`
- Line 122-149: `is_already_processed()` function:
  ```python
  def is_already_processed(eml_filename: str, csv_dir: Path) -> bool:
      # Extract date from filename (handles multiple formats)
      match = re.match(r'ps_daily_(\d{4}-\d{2}-\d{2})\.eml', eml_filename)
      if match:
          date = match.group(1)
          csv_path = csv_dir / f"ps_daily_{date}.csv"
          return csv_path.exists()  # ← Checks if file exists in csv_dir
      # Also handles original filename format
      # ...
  ```
- Line 335: Used in filter: `if not is_already_processed(eml.name, csv_dir)`

**Key Point**: Checks if CSV exists in `config["paths"]["portfolio_solutions_csv_dir"]` which resolves to `${prod_root}/ps/csv`

### 3. RR (Risk Range) Processing

**File**: `python/src/syndicate/data_sources/hedgeye/run_rr_parser.py`

**Logic**:
- Line 8-10: Loads `CSV_OUTPUT_DIR` from config at module level: `config["paths"]["csv_output_dir"]`
- Line 37-51: `process_all_unprocessed()` function:
  ```python
  def process_all_unprocessed():
      raw_dir = Path(RAW_EML_DIR)
      for eml_file in raw_dir.glob("risk_range_*.eml"):
          report_date, _, _ = parse_eml(str(eml_file))
          out_csv = Path(CSV_OUTPUT_DIR) / f"risk_range_{report_date}.csv"
          if not out_csv.exists():  # ← Checks if file exists
              # Process email
          else:
              print(f"⏭️ Skipped (already exists): {eml_file.name}")
  ```

**Key Point**: Checks if CSV exists in `config["paths"]["csv_output_dir"]` which resolves to `${prod_root}/daily/csv`

## Behavior with Renamed Prod Directory

### Scenario: Rename old `prod`, create new empty `prod`

**If config is NOT updated** (still points to old renamed directory):
- ❌ **Problem**: Scripts will check old directory, find CSVs, skip all emails
- ❌ **Result**: No processing happens even though new `prod` directory is empty

**If config IS updated** (points to new empty `prod` directory):
- ✅ **Correct**: Scripts will check new directory, don't find CSVs, process all emails
- ✅ **Result**: All emails get re-processed into the new directory

### Correct Workflow

1. **Rename old prod directory**:
   ```bash
   mv /Users/rk/d/downloads/hedgeye/prod /Users/rk/d/downloads/hedgeye/prod_backup_YYYYMMDD
   ```

2. **Update config** (`python/config/hedgeye.yaml`):
   ```yaml
   base_paths:
     prod_root: /Users/rk/d/downloads/hedgeye/prod  # Points to new (empty) directory
   ```

3. **Create new empty prod directory structure** (scripts will create subdirectories automatically)

4. **Run pipeline**: All emails will be re-processed because CSVs don't exist in new directory

## Summary

**All three processing scripts**:
- ✅ Load output directory paths from config (`hedgeye.yaml`)
- ✅ Check if output CSV files exist using `Path.exists()`
- ✅ Will correctly re-process emails if config points to new empty directory
- ❌ Will incorrectly skip emails if config still points to old renamed directory

**Conclusion**: The logic will work correctly **IF** you update `prod_root` in `hedgeye.yaml` to point to the new directory after renaming the old one.

