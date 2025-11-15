#!/usr/bin/env python3
"""
Process Portfolio Solutions daily emails.

This script:
1. Finds all .eml files in the raw directory
2. Checks which have already been processed (based on output CSV existence)
3. For each unprocessed email:
   - Renames it to standard format (ps_daily_YYYY-MM-DD.eml)
   - Extracts ranked portfolio positions → CSV
   - Extracts Keith's commentary → markdown file
4. Saves outputs to prod directory

Usage:
    uv run python -m syndicate.data_sources.hedgeye.process_portfolio_solutions
"""

import re
from pathlib import Path
from datetime import datetime
from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup
import pandas as pd

from syndicate.data_sources.hedgeye.config_loader import load_config


def parse_eml_file(eml_path: Path) -> tuple[str, str, str]:
    """
    Extract HTML content from .eml file.

    Returns:
        Tuple of (html_content, subject, date_str)
    """
    with open(eml_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    subject = msg.get('subject', 'Unknown')
    date_str = msg.get('date', '')

    # Get HTML content
    html_content = None
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                html_content = part.get_content()
                break
    else:
        if msg.get_content_type() == 'text/html':
            html_content = msg.get_content()

    return html_content, subject, date_str


def extract_date_from_subject(subject: str) -> str:
    """
    Extract date from email subject like 'Portfolio Solutions: Daily ETF Re-Rank (11/14/2025)'.

    Returns:
        Date string in YYYY-MM-DD format
    """
    # Try to find date pattern like (11/14/2025) or (11_14_2025)
    match = re.search(r'\((\d{1,2})[/_](\d{1,2})[/_](\d{4})\)', subject)
    if match:
        month, day, year = match.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    # Fallback to today
    return datetime.now().strftime('%Y-%m-%d')


def parse_portfolio_rankings_table(soup: BeautifulSoup) -> list[dict]:
    """
    Parse Portfolio Solutions rankings from comma-separated list with <abbr> tags.

    Returns:
        List of dicts with ranking data: [{'rank': 1, 'ticker': 'FDRXX', 'name': '...'}, ...]
    """
    rankings = []

    # Find the paragraph with "Macro ETFs by Rank:" or "ETFs by Rank:"
    paragraphs = soup.find_all('p')

    for p in paragraphs:
        text = p.get_text()
        if 'Macro ETFs by Rank:' in text or 'ETFs by Rank:' in text:
            # Found the rankings paragraph
            abbrs = p.find_all('abbr')

            # First ticker might not have abbr tag (like FDRXX)
            strong = p.find('strong')
            if strong:
                strong_text = strong.get_text()
                if ':' in strong_text:
                    after_colon = strong_text.split(':', 1)[1].strip()
                    first_item = after_colon.split(',')[0].strip()
                    # Check if it's a ticker (all caps, 2-5 letters)
                    if re.match(r'^[A-Z]{2,5}$', first_item):
                        rankings.append({
                            'rank': 1,
                            'ticker': first_item,
                            'name': ''
                        })

            # Process all <abbr> tags
            for abbr in abbrs:
                ticker = abbr.get_text(strip=True)
                name = abbr.get('name', '')

                rankings.append({
                    'rank': len(rankings) + 1,
                    'ticker': ticker,
                    'name': name
                })

            break  # Found rankings, stop searching

    return rankings


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
    # Matches: ps_daily_2025-11-14.eml or Portfolio Solutions... (11_14_2025).eml

    # Try standard format first: ps_daily_YYYY-MM-DD.eml
    match = re.match(r'ps_daily_(\d{4}-\d{2}-\d{2})\.eml', eml_filename)
    if match:
        date = match.group(1)
        csv_path = csv_dir / f"ps_daily_{date}.csv"
        return csv_path.exists()

    # Try original format: (MM_DD_YYYY) or (MM/DD/YYYY)
    match = re.search(r'\((\d{1,2})[/_](\d{1,2})[/_](\d{4})\)', eml_filename)
    if match:
        month, day, year = match.groups()
        date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        csv_path = csv_dir / f"ps_daily_{date}.csv"
        return csv_path.exists()

    # Can't determine date from filename
    return False


def extract_keiths_commentary(soup: BeautifulSoup) -> str:
    """
    Extract Keith's daily commentary/moves from the email.

    Returns:
        Text of Keith's commentary, formatted with line breaks
    """
    paragraphs = soup.find_all('p')

    for p in paragraphs:
        text = p.get_text(strip=True)

        # Look for Keith's Commentary specifically
        if "Keith's Commentary:" in text or 'Keith\'s Commentary:' in text:
            # Extract the commentary portion
            # Pattern: Keith's Commentary:"In the PA today, I sold..."

            # Find the quoted section
            if '"' in text:
                # Extract between quotes
                start = text.index('"')
                end = text.rindex('"')
                commentary = text[start+1:end]

                # Strip boilerplate "In the PA today, I "
                if commentary.startswith("In the PA today, I "):
                    commentary = commentary[len("In the PA today, I "):]

                # Add newlines before " Bought" and " Sold"
                commentary = commentary.replace(" Bought", "\nBought")
                commentary = commentary.replace(" Sold", "\nSold")

                return commentary.strip()

    # No commentary found
    return ""


def save_commentary(commentary: str, report_date: str, csv_dir: Path) -> Path:
    """
    Save Keith's commentary to markdown file.

    Returns:
        Path to saved markdown file
    """
    md_path = csv_dir.parent / 'commentary' / f"ps_commentary_{report_date}.md"
    md_path.parent.mkdir(parents=True, exist_ok=True)

    # Create markdown with frontmatter
    md_content = f"""---
date: {report_date}
source: Portfolio Solutions Daily
type: keiths-commentary
---

# Keith's Commentary - {report_date}

{commentary}
"""

    md_path.write_text(md_content)
    return md_path


def rename_if_needed(eml_path: Path, report_date: str) -> Path:
    """
    Rename file to standard format if needed.

    Args:
        eml_path: Current path to .eml file
        report_date: Report date in YYYY-MM-DD format

    Returns:
        Path to file (renamed or original)
    """
    standard_name = f"ps_daily_{report_date}.eml"

    # Already in standard format?
    if eml_path.name == standard_name:
        print(f"✓ Filename already standard: {eml_path.name}")
        return eml_path

    # Rename to standard format
    new_path = eml_path.parent / standard_name
    eml_path.rename(new_path)
    print(f"📝 Renamed: {eml_path.name} → {standard_name}")

    return new_path


def save_to_csv(rankings: list[dict], report_date: str, csv_dir: Path) -> Path:
    """
    Save rankings to CSV file.

    Returns:
        Path to saved CSV file
    """
    # Create DataFrame
    df = pd.DataFrame(rankings)

    # Add report_date column
    df['report_date'] = report_date

    # Reorder columns: report_date, rank, ticker, name
    df = df[['report_date', 'rank', 'ticker', 'name']]

    # Save to CSV
    csv_path = csv_dir / f"ps_daily_{report_date}.csv"
    df.to_csv(csv_path, index=False)

    return csv_path


def process_single_email(eml_path: Path, csv_dir: Path) -> bool:
    """
    Process a single Portfolio Solutions email.

    Returns:
        True if processing succeeded, False otherwise
    """
    print(f"\n📧 Processing: {eml_path.name}")

    # Parse email
    html_content, subject, date_str = parse_eml_file(eml_path)
    if not html_content:
        print("  ❌ Could not extract HTML content")
        return False

    # Extract report date from subject
    report_date = extract_date_from_subject(subject)
    print(f"  📅 Report date: {report_date}")

    # Rename file if needed
    eml_path = rename_if_needed(eml_path, report_date)

    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract rankings table
    rankings = parse_portfolio_rankings_table(soup)
    if not rankings:
        print("  ⚠️  No rankings found - format change?")
        return False

    print(f"  ✓ Found {len(rankings)} ranked positions")

    # Extract Keith's commentary
    commentary = extract_keiths_commentary(soup)
    print(f"  ✓ Extracted commentary ({len(commentary)} chars)")

    # Save outputs
    csv_path = save_to_csv(rankings, report_date, csv_dir)
    print(f"  💾 Saved CSV: {csv_path.name}")

    md_path = save_commentary(commentary, report_date, csv_dir)
    print(f"  💾 Saved commentary: {md_path.name}")

    return True


def main():
    """Process all unprocessed Portfolio Solutions emails"""
    config = load_config()
    raw_dir = Path(config["paths"]["portfolio_solutions_raw_eml_dir"])
    csv_dir = Path(config["paths"]["portfolio_solutions_csv_dir"])

    # Ensure output directories exist
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
        try:
            if process_single_email(eml_path, csv_dir):
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")
            fail_count += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"✅ Successfully processed: {success_count}")
    if fail_count > 0:
        print(f"❌ Failed: {fail_count}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()