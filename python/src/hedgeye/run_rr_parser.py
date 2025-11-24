import re
import sys
from pathlib import Path
from hedgeye.parse_rr_eml import parse_eml, save_outputs
from hedgeye.config_loader import load_config

# Load config
config = load_config()
RAW_EML_DIR = config["paths"]["raw_eml_dir"]
CSV_OUTPUT_DIR = config["paths"]["csv_output_dir"]

def rename_non_standard_files():
    """Rename files that don't match risk_range_YYYY-MM-DD.eml pattern"""
    raw_dir = Path(RAW_EML_DIR)
    for eml_file in raw_dir.glob("*.eml"):
        # Skip if already in correct format
        if re.match(r"risk_range_\d{4}-\d{2}-\d{2}\.eml", eml_file.name):
            continue

        try:
            # Parse to get date
            report_date, _, _ = parse_eml(str(eml_file))
            new_name = f"risk_range_{report_date}.eml"
            new_path = raw_dir / new_name

            # Rename
            eml_file.rename(new_path)
            print(f"📝 Renamed: {eml_file.name} → {new_name}")
        except Exception as e:
            print(f"⚠️ Could not rename {eml_file.name}: {e}")

def process_single_file(file_path: str):
    report_date, entries, changes = parse_eml(file_path)
    save_outputs(report_date, entries, changes)
    print(f"✅ Processed single file: {Path(file_path).name}")

def process_all_unprocessed():
    # First, rename any files that don't match the standard format
    rename_non_standard_files()

    raw_dir = Path(RAW_EML_DIR)
    for eml_file in raw_dir.glob("risk_range_*.eml"):
        try:
            report_date, _, _ = parse_eml(str(eml_file))
            out_csv = Path(CSV_OUTPUT_DIR) / f"risk_range_{report_date}.csv"
            if not out_csv.exists():
                report_date, entries, changes = parse_eml(str(eml_file))
                save_outputs(report_date, entries, changes)
                print(f"✅ Processed: {eml_file.name}")
            else:
                print(f"⏭️ Skipped (already exists): {eml_file.name}")
        except Exception as e:
            print(f"❌ Error processing {eml_file.name}: {e}")

def main():
    if len(sys.argv) > 1:
        process_single_file(sys.argv[1])
    else:
        process_all_unprocessed()

if __name__ == "__main__":
    main()
