#!/usr/bin/env python3
"""
Parse Portfolio Solutions emails and extract portfolio rankings table.

NOTE: This script extracts ONLY the portfolio rankings table.
Keith's Commentary trades are skipped (too variable for simple parsing).

Usage:
    python scripts/parse_portfolio_solutions.py /path/to/email.eml
    python scripts/parse_portfolio_solutions.py /path/to/email.eml --format markdown
    python scripts/parse_portfolio_solutions.py /path/to/email.eml --output rankings.csv
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
    """Extract date from email subject like 'Portfolio Solutions: Daily ETF Re-Rank (11/7/2025)'."""
    # Try to find date pattern like (11/7/2025) or (11_7_2025)
    match = re.search(r'\((\d{1,2})[/_](\d{1,2})[/_](\d{4})\)', subject)
    if match:
        month, day, year = match.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    # Fallback to today
    return datetime.now().strftime('%Y-%m-%d')


def parse_portfolio_rankings_table(soup):
    """
    Parse Portfolio Solutions rankings from comma-separated list with <abbr> tags.

    Returns list of dicts with ranking data.
    Structure: [{'rank': 1, 'ticker': 'FDRXX', 'name': 'Fidelity Govt MM'}, ...]
    """
    rankings = []

    # Find the paragraph with "Macro ETFs by Rank:"
    # The rankings are in <abbr> tags within a <strong> tag
    paragraphs = soup.find_all('p')

    for p in paragraphs:
        text = p.get_text()
        if 'Macro ETFs by Rank:' in text or 'ETFs by Rank:' in text:
            # Found the rankings paragraph
            # Extract all <abbr> tags (each contains a ticker and name)
            abbrs = p.find_all('abbr')

            # First ticker might not have abbr tag (like FDRXX)
            # Get the text and split by comma to find it
            strong = p.find('strong')
            if strong:
                strong_text = strong.get_text()
                # Extract first ticker before first comma
                if ':' in strong_text:
                    after_colon = strong_text.split(':', 1)[1].strip()
                    first_item = after_colon.split(',')[0].strip()
                    # Check if it's a ticker (all caps, 2-5 letters)
                    if re.match(r'^[A-Z]{2,5}$', first_item):
                        rankings.append({
                            'rank': 1,
                            'ticker': first_item,
                            'name': ''  # No name for first ticker
                        })

            # Now process all <abbr> tags
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


def format_as_csv(rankings):
    """Format rankings as CSV string."""
    if not rankings:
        return ""

    # Header
    csv_lines = ['rank,ticker,name']

    # Data rows
    for r in rankings:
        # Escape commas in name field
        name = r['name'].replace(',', ';')
        csv_lines.append(f"{r['rank']},{r['ticker']},{name}")

    return '\n'.join(csv_lines)


def format_as_markdown(rankings, report_date, email_type='daily'):
    """Format rankings as Obsidian-style markdown."""
    md = f"""---
date: {report_date}
type: portfolio-solutions-{email_type}
source: Hedgeye Portfolio Solutions
---

# Portfolio Solutions - {report_date}

## ETF Rankings ({len(rankings)} positions)

| Rank | Ticker | Name |
|------|--------|------|
"""

    for r in rankings:
        md += f"| {r['rank']} | **{r['ticker']}** | {r['name']} |\n"

    md += f"""
## Notes

- **Type:** {'Daily' if email_type == 'daily' else 'Weekly'} Re-Rank
- **Total Positions:** {len(rankings)}
- **Date:** {report_date}

---
*Generated from Portfolio Solutions email*
*Note: Keith's Commentary trades not extracted (manual review required)*
"""

    return md


def main():
    parser = argparse.ArgumentParser(description='Parse Portfolio Solutions emails')
    parser.add_argument('eml_file', help='Path to .eml file')
    parser.add_argument('--format', choices=['csv', 'markdown'], default='csv',
                       help='Output format (default: csv)')
    parser.add_argument('--output', help='Output file path (default: stdout)')
    parser.add_argument('--type', choices=['daily', 'weekly'], default='daily',
                       help='Email type (default: daily)')

    args = parser.parse_args()

    # Parse email
    html_content, subject, date_str = parse_eml_file(args.eml_file)
    if not html_content:
        print("Error: Could not extract HTML content from email", file=sys.stderr)
        sys.exit(1)

    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract rankings
    rankings = parse_portfolio_rankings_table(soup)

    if not rankings:
        print("Warning: No rankings found in email", file=sys.stderr)
        print("This might be a format change - manual review needed", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(rankings)} ranked positions")

    # Extract date
    report_date = extract_date_from_subject(subject)

    # Generate output
    if args.format == 'markdown':
        output = format_as_markdown(rankings, report_date, args.type)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Saved markdown to {args.output}")
        else:
            print(output)

    else:  # CSV
        output = format_as_csv(rankings)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Saved CSV to {args.output}")
        else:
            print(output)


if __name__ == '__main__':
    main()
