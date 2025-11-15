#!/usr/bin/env python3
"""
Process ETF Pro Plus weekly emails.

This script:
1. Finds all .eml files in the raw directory
2. Checks which have already been processed (based on output CSV existence)
3. For each unprocessed email:
   - Renames it to standard format (etf_pro_weekly_YYYY-MM-DD.eml)
   - Parses it to extract positions and trend ranges
   - Saves the result to CSV in the prod directory

Usage:
    uv run python -m syndicate.data_sources.hedgeye.process_etf_pro_weekly
"""

import re
from pathlib import Path
from typing import List
from syndicate.data_sources.hedgeye.config_loader import load_config
from syndicate.data_sources.hedgeye.parse_etf_pro_weekly import parse_eml, save_outputs, EtfProPosition


def is_already_processed(eml_filename: str, csv_dir: Path) -> bool:
    """
    Check if an email has already been processed.

    Args:
        eml_filename: Name of the .eml file
        csv_dir: Directory containing processed CSV files

    Returns:
        True if a matching CSV output exists
    """
    # Extract date from filename using regex
    # Matches: etf_pro_weekly_2025-11-09.eml

    # Standard format: etf_pro_weekly_YYYY-MM-DD.eml
    match = re.match(r'etf_pro_weekly_(\d{4}-\d{2}-\d{2})\.eml', eml_filename)
    if match:
        date = match.group(1)
        csv_path = csv_dir / f"etf_pro_weekly_{date}.csv"
        return csv_path.exists()

    # If filename doesn't match standard format, need to parse to check
    # For now, assume not processed
    return False


def rename_if_needed(eml_path: Path, report_date: str) -> Path:
    """
    Rename file to standard format if needed.

    Args:
        eml_path: Current path to .eml file
        report_date: Report date in YYYY-MM-DD format

    Returns:
        Path to file (renamed or original)
    """
    standard_name = f"etf_pro_weekly_{report_date}.eml"

    # Already in standard format?
    if eml_path.name == standard_name:
        print(f"  ✓ Filename already standard: {eml_path.name}")
        return eml_path

    # Rename to standard format
    new_path = eml_path.parent / standard_name
    eml_path.rename(new_path)
    print(f"  📝 Renamed: {eml_path.name} → {standard_name}")

    return new_path


def process_single_email(eml_path: Path, csv_dir: Path) -> bool:
    """
    Process a single ETF Pro Plus weekly email.

    Returns:
        True if processing succeeded, False otherwise
    """
    print(f"\n📧 Processing: {eml_path.name}")

    try:
        # Parse the email to get report date and positions
        report_date, positions = parse_eml(str(eml_path))
        print(f"  📅 Report date: {report_date}")

        # Rename file if needed
        eml_path = rename_if_needed(eml_path, report_date)

        # Report what we found
        print(f"  ✓ Found {len(positions)} positions")
        print(f"    LONG: {sum(1 for p in positions if p.position_type == 'LONG')}")
        print(f"    SHORT: {sum(1 for p in positions if p.position_type == 'SHORT')}")

        # Save to CSV
        save_outputs(report_date, positions, str(csv_dir))
        print(f"  💾 Saved: etf_pro_weekly_{report_date}.csv")

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    """Process all unprocessed ETF Pro Plus weekly emails"""
    config = load_config()
    raw_dir = Path(config["paths"]["etf_pro_raw_eml_dir"])
    csv_dir = Path(config["paths"]["etf_pro_csv_dir"])

    # Ensure output directory exists
    csv_dir.mkdir(parents=True, exist_ok=True)

    # Find all .eml files
    eml_files = list(raw_dir.glob("*.eml"))
    if not eml_files:
        print(f"❌ No .eml files found in {raw_dir}")
        return

    print(f"📂 Found {len(eml_files)} email files")

    # Filter to unprocessed emails only
    unprocessed = [
        eml for eml in eml_files
        if not is_already_processed(eml.name, csv_dir)
    ]

    if not unprocessed:
        print("✅ All emails already processed")
        return

    print(f"🆕 {len(unprocessed)} unprocessed emails to handle")

    # Process each unprocessed email
    success_count = 0
    fail_count = 0

    for eml_path in sorted(unprocessed, key=lambda p: p.stat().st_mtime):
        if process_single_email(eml_path, csv_dir):
            success_count += 1
        else:
            fail_count += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"✅ Successfully processed: {success_count}")
    if fail_count > 0:
        print(f"❌ Failed: {fail_count}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()