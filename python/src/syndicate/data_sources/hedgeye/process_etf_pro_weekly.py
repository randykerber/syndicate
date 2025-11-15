#!/usr/bin/env python3
"""
Process new ETF Pro Plus weekly email.

This script:
1. Finds the latest .eml file in the raw directory
2. Renames it to standard format (etf_pro_weekly_YYYY-MM-DD.eml) if needed
3. Parses it to extract positions and trend ranges
4. Saves the result to CSV in the prod directory

Usage:
    uv run python -m syndicate.data_sources.hedgeye.process_etf_pro_weekly
"""

import re
from pathlib import Path
from syndicate.data_sources.hedgeye.config_loader import load_config
from syndicate.data_sources.hedgeye.parse_etf_pro_weekly import parse_eml, save_outputs


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
        print(f"✓ Filename already standard: {eml_path.name}")
        return eml_path

    # Rename to standard format
    new_path = eml_path.parent / standard_name
    eml_path.rename(new_path)
    print(f"📝 Renamed: {eml_path.name} → {standard_name}")

    return new_path


def main():
    """Process the latest ETF Pro Plus weekly email"""
    config = load_config()
    raw_dir = Path(config["paths"]["etf_pro_raw_eml_dir"])

    # Find all .eml files
    eml_files = list(raw_dir.glob("*.eml"))
    if not eml_files:
        print("❌ No .eml files found in", raw_dir)
        return

    # Get the newest file by modification time (most recently added)
    latest_file = max(eml_files, key=lambda f: f.stat().st_mtime)
    print(f"\n📂 Found latest file: {latest_file.name}")
    print(f"   Modified: {latest_file.stat().st_mtime}")

    # Parse the email to get report date
    print(f"\n📖 Parsing email...")
    report_date, positions = parse_eml(str(latest_file))

    # Rename if needed
    latest_file = rename_if_needed(latest_file, report_date)

    # Report what we found
    print(f"\n📊 Report Date: {report_date}")
    print(f"   Total Positions: {len(positions)}")
    print(f"   LONG: {sum(1 for p in positions if p.position_type == 'LONG')}")
    print(f"   SHORT: {sum(1 for p in positions if p.position_type == 'SHORT')}")

    # Save to CSV
    save_outputs(report_date, positions)
    print(f"\n✅ Processing complete!")


if __name__ == "__main__":
    main()