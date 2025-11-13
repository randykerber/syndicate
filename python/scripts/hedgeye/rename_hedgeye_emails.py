#!/usr/bin/env python3
"""
Rename Hedgeye email files to include dates for easy identification.

Renames files to format: {type}_{date}.eml
- etf_pro_weekly_2025-11-02.eml
- etf_pro_update_2025-11-05.eml
- ps_daily_2025-11-07.eml
- ps_weekly_2025-10-31.eml

Usage:
    python scripts/rename_hedgeye_emails.py /path/to/folder/
    python scripts/rename_hedgeye_emails.py /path/to/folder/ --dry-run
"""

import argparse
import sys
from pathlib import Path
from email import policy
from email.parser import BytesParser
from datetime import datetime
import re


def parse_eml_date(eml_path):
    """Extract date from email headers or subject."""
    try:
        with open(eml_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)

        subject = msg.get('subject', '')
        date_header = msg.get('date', '')

        # Try to extract date from subject first (more reliable for Hedgeye emails)
        # Portfolio Solutions: "Daily ETF Re-Rank (11/7/2025)" or "(11_7_2025)"
        match = re.search(r'\((\d{1,2})[/_](\d{1,2})[/_](\d{4})\)', subject)
        if match:
            month, day, year = match.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        # Risk Range: "RISK RANGE™ SIGNALS_ April 10, 2025"
        match = re.search(r'([A-Z][a-z]+)\s+(\d{1,2}),?\s+(\d{4})', subject)
        if match:
            month_name, day, year = match.groups()
            try:
                month_num = datetime.strptime(month_name, '%B').month
                return f"{year}-{str(month_num).zfill(2)}-{day.zfill(2)}"
            except:
                pass

        # Fallback: Parse Date header
        if date_header:
            try:
                date_obj = datetime.strptime(date_header, '%a, %d %b %Y %H:%M:%S %z')
                return date_obj.strftime('%Y-%m-%d')
            except:
                # Try other common formats
                for fmt in ['%d %b %Y %H:%M:%S %z', '%a, %d %b %Y %H:%M:%S %Z']:
                    try:
                        date_obj = datetime.strptime(date_header, fmt)
                        return date_obj.strftime('%Y-%m-%d')
                    except:
                        continue

        return None
    except Exception as e:
        print(f"Error parsing {eml_path.name}: {e}", file=sys.stderr)
        return None


def detect_email_type(eml_path):
    """Detect email type from filename and subject."""
    try:
        with open(eml_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)

        subject = msg.get('subject', '')
        filename = eml_path.name.lower()

        # ETF Pro
        if 'etf pro' in filename or 'etf pro' in subject.lower():
            if 'update' in filename or 'update' in subject.lower() or 'change' in subject.lower():
                return 'etf_pro_update'
            else:
                return 'etf_pro_weekly'

        # Portfolio Solutions
        if 'portfolio solutions' in subject.lower() or 'portfolio solutions' in filename:
            if 'daily' in subject.lower():
                return 'ps_daily'
            elif 'weekly' in subject.lower():
                return 'ps_weekly'
            else:
                return 'ps'  # Unknown PS type

        # Risk Range
        if 'risk range' in subject.lower() or 'risk range' in filename:
            return 'risk_range'

        return 'unknown'
    except Exception as e:
        print(f"Error detecting type for {eml_path.name}: {e}", file=sys.stderr)
        return 'unknown'


def generate_new_name(eml_path):
    """Generate new filename: {type}_{date}.eml"""
    email_type = detect_email_type(eml_path)
    date_str = parse_eml_date(eml_path)

    if not date_str:
        return None, f"Could not extract date"

    if email_type == 'unknown':
        return None, f"Could not detect email type"

    # Generate new name
    new_name = f"{email_type}_{date_str}.eml"
    return new_name, None


def rename_emails(folder_path, dry_run=False):
    """Rename all .eml files in folder."""
    folder = Path(folder_path)

    if not folder.is_dir():
        print(f"Error: {folder_path} is not a directory", file=sys.stderr)
        return

    eml_files = list(folder.glob('*.eml'))

    if not eml_files:
        print(f"No .eml files found in {folder_path}")
        return

    print(f"Found {len(eml_files)} .eml files in {folder_path}")
    print()

    renamed_count = 0
    skipped_count = 0
    error_count = 0

    for eml_file in sorted(eml_files):
        new_name, error = generate_new_name(eml_file)

        if error:
            print(f"⚠️  SKIP: {eml_file.name}")
            print(f"   Reason: {error}")
            skipped_count += 1
            continue

        new_path = eml_file.parent / new_name

        # Check if target already exists
        if new_path.exists() and new_path != eml_file:
            print(f"⚠️  SKIP: {eml_file.name}")
            print(f"   Target already exists: {new_name}")
            skipped_count += 1
            continue

        # Check if already correctly named
        if eml_file.name == new_name:
            print(f"✓  OK: {eml_file.name} (already correct)")
            skipped_count += 1
            continue

        # Perform rename
        if dry_run:
            print(f"🔍 DRY-RUN: {eml_file.name}")
            print(f"   Would rename to: {new_name}")
        else:
            try:
                eml_file.rename(new_path)
                print(f"✅ RENAMED: {eml_file.name}")
                print(f"   New name: {new_name}")
                renamed_count += 1
            except Exception as e:
                print(f"❌ ERROR: {eml_file.name}")
                print(f"   Failed to rename: {e}")
                error_count += 1

        print()

    # Summary
    print("=" * 60)
    if dry_run:
        print("DRY-RUN SUMMARY:")
        print(f"  Would rename: {renamed_count}")
    else:
        print("SUMMARY:")
        print(f"  ✅ Renamed: {renamed_count}")
    print(f"  ⚠️  Skipped: {skipped_count}")
    if error_count > 0:
        print(f"  ❌ Errors: {error_count}")


def main():
    parser = argparse.ArgumentParser(
        description='Rename Hedgeye emails to include dates'
    )
    parser.add_argument('folder', help='Folder containing .eml files')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be renamed without actually renaming')

    args = parser.parse_args()

    rename_emails(args.folder, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
