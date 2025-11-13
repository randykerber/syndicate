#!/usr/bin/env python3
"""
Parse ETF Pro Plus weekly emails and extract portfolio data.

Usage:
    python scripts/parse_etf_pro.py /path/to/email.eml
    python scripts/parse_etf_pro.py /path/to/email.eml --format markdown
    python scripts/parse_etf_pro.py /path/to/email.eml --output my_portfolio.csv
"""

import argparse
import sys
from pathlib import Path
from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup
import re
from datetime import datetime


def parse_eml_file(eml_path):
    """Extract HTML content from .eml file."""
    with open(eml_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    # Extract subject and date
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


def extract_date_from_subject(subject):
    """Extract date from email subject or return today."""
    # Try to find date in subject like "ETF Pro Plus - New Weekly Report"
    # The date is usually in the email body/timestamp
    return datetime.now().strftime('%Y-%m-%d')


def parse_etf_pro_table(soup, position_type='BULLISH'):
    """
    Parse ETF Pro portfolio table for either BULLISH (long) or BEARISH (short).

    Returns list of dicts with portfolio data.
    """
    positions = []

    # Find the table with the specified header
    thead = soup.find('thead', class_=position_type.lower())
    if not thead:
        return positions

    # Get the parent table and find tbody
    table = thead.find_parent('table')
    if not table:
        return positions

    tbody = thead.find_next_sibling('tbody')
    if not tbody:
        return positions

    # Parse each row
    for tr in tbody.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) < 7:
            continue

        # Extract text from each cell
        name = tds[0].get_text(strip=True)
        ticker = tds[1].get_text(strip=True)
        date_added = tds[2].get_text(strip=True)
        recent_price = tds[3].get_text(strip=True)
        trend_low = tds[4].get_text(strip=True)
        trend_high = tds[5].get_text(strip=True)
        asset_class = tds[6].get_text(strip=True)

        positions.append({
            'ticker': ticker,
            'name': name,
            'position': 'LONG' if position_type == 'BULLISH' else 'SHORT',
            'date_added': date_added,
            'recent_price': recent_price,
            'trend_low': trend_low,
            'trend_high': trend_high,
            'asset_class': asset_class
        })

    return positions


def format_as_csv(positions):
    """Format positions as CSV string."""
    if not positions:
        return ""

    # Header
    csv_lines = ['ticker,name,position,date_added,recent_price,trend_low,trend_high,asset_class']

    # Data rows
    for pos in positions:
        csv_lines.append(
            f"{pos['ticker']},{pos['name']},{pos['position']},"
            f"{pos['date_added']},{pos['recent_price']},"
            f"{pos['trend_low']},{pos['trend_high']},{pos['asset_class']}"
        )

    return '\n'.join(csv_lines)


def format_as_markdown(long_positions, short_positions, report_date):
    """Format positions as Obsidian-style markdown."""
    md = f"""---
date: {report_date} Wanting to get a command mode working.
type: etf-pro-portfolio
source: Hedgeye ETF Pro Plus
---

# ETF Pro Plus Portfolio - {report_date}

## Long Positions ({len(long_positions)})

| Ticker | Name | Date Added | Price | Trend Range | Asset Class |
|--------|------|------------|-------|-------------|-------------|
"""

    for pos in long_positions:
        md += f"| **{pos['ticker']}** | {pos['name']} | {pos['date_added']} | "
        md += f"{pos['recent_price']} | {pos['trend_low']} - {pos['trend_high']} | "
        md += f"{pos['asset_class']} |\n"

    md += f"""
## Short Positions ({len(short_positions)})

| Ticker | Name | Date Added | Price | Trend Range | Asset Class |
|--------|------|------------|-------|-------------|-------------|
"""

    for pos in short_positions:
        md += f"| **{pos['ticker']}** | {pos['name']} | {pos['date_added']} | "
        md += f"{pos['recent_price']} | {pos['trend_low']} - {pos['trend_high']} | "
        md += f"{pos['asset_class']} |\n"

    md += f"""
## Summary

- **Total Long Positions:** {len(long_positions)}
- **Total Short Positions:** {len(short_positions)}
- **Total Positions:** {len(long_positions) + len(short_positions)}

---
*Generated from ETF Pro Plus weekly report*
"""

    return md


def main():
    parser = argparse.ArgumentParser(description='Parse ETF Pro Plus weekly emails')
    parser.add_argument('eml_file', help='Path to .eml file')
    parser.add_argument('--format', choices=['csv', 'markdown'], default='csv',
                       help='Output format (default: csv)')
    parser.add_argument('--output', help='Output file path (default: stdout)')
    parser.add_argument('--separate', action='store_true',
                       help='Create separate files for long/short (CSV only)')

    args = parser.parse_args()

    # Parse email
    html_content, subject, date_str = parse_eml_file(args.eml_file)
    if not html_content:
        print("Error: Could not extract HTML content from email", file=sys.stderr)
        sys.exit(1)

    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract portfolios
    long_positions = parse_etf_pro_table(soup, 'BULLISH')
    short_positions = parse_etf_pro_table(soup, 'BEARISH')

    if not long_positions and not short_positions:
        print("Warning: No positions found in email", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(long_positions)} long positions, {len(short_positions)} short positions")

    # Extract date from filename or use today
    eml_path = Path(args.eml_file)
    report_date = extract_date_from_subject(subject)

    # Generate output
    if args.format == 'markdown':
        output = format_as_markdown(long_positions, short_positions, report_date)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Saved markdown to {args.output}")
        else:
            print(output)

    else:  # CSV
        if args.separate:
            # Save separate files
            base_name = args.output if args.output else f"etf_pro_{report_date}"
            if base_name.endswith('.csv'):
                base_name = base_name[:-4]

            long_file = f"{base_name}_long.csv"
            short_file = f"{base_name}_short.csv"

            with open(long_file, 'w') as f:
                f.write(format_as_csv(long_positions))
            print(f"Saved long positions to {long_file}")

            with open(short_file, 'w') as f:
                f.write(format_as_csv(short_positions))
            print(f"Saved short positions to {short_file}")

        else:
            # Combined CSV
            all_positions = long_positions + short_positions
            output = format_as_csv(all_positions)

            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Saved CSV to {args.output}")
            else:
                print(output)


if __name__ == '__main__':
    main()
