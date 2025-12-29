#!/usr/bin/env python3
"""
Parser for Hedgeye ETF Pro Plus weekly emails.

Extracts trend ranges and position information from weekly portfolio snapshots.
Uses HTML table parsing for reliable column extraction.
"""

import quopri
import re
from datetime import datetime
from email import message_from_file
from pathlib import Path
from typing import List, NamedTuple, Tuple

from bs4 import BeautifulSoup


class EtfProPosition(NamedTuple):
    """ETF Pro Plus position with trend range"""
    ticker: str
    description: str
    position_type: str  # LONG or SHORT
    date_added: str  # YYYY-MM-DD
    recent_price: float
    trend_low: float
    trend_high: float
    asset_class: str


def standardize_date(date_str: str) -> str:
    """Convert M/D/YYYY to YYYY-MM-DD format"""
    dt = datetime.strptime(date_str, "%m/%d/%Y")
    return dt.strftime("%Y-%m-%d")


def parse_price(price_str: str) -> float:
    """Parse price string like '$123.45' to float"""
    # Remove $ and any whitespace
    clean = price_str.replace('$', '').replace(',', '').strip()
    return float(clean)


def parse_eml(filepath: str) -> Tuple[str, List[EtfProPosition]]:
    """
    Parse ETF Pro Plus weekly email file using HTML table structure.

    Returns:
        (report_date, positions)
    """
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        msg = message_from_file(f)

    # Extract report date from email Date header
    date_str = msg.get('Date', '')
    # Parse date from format like: "Sun, 9 Nov 2025 15:39:04 -0500 (EST)"
    dt = datetime.strptime(date_str.split(',')[1].strip().split(' -')[0], "%d %b %Y %H:%M:%S")
    report_date = dt.strftime("%Y-%m-%d")

    # Get HTML body
    html_body = None
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload(decode=True)
                if payload:
                    html_body = payload.decode('utf-8', errors='ignore')
                    break
    
    if not html_body:
        raise ValueError("No HTML body found in email")

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_body, 'html.parser')
    
    # Find the ETF Pro table
    table = soup.find('table', class_='etf-pro-table')
    if not table:
        raise ValueError("Could not find etf-pro-table in HTML")

    positions = []
    current_position_type = None

    # Process all rows
    for row in table.find_all('tr'):
        cells = row.find_all(['td', 'th'])
        if not cells:
            continue

        # Check if this is a header row (BULLISH/BEARISH)
        first_cell_text = cells[0].get_text(strip=True)
        
        if first_cell_text == 'BULLISH':
            current_position_type = 'LONG'
            continue
        elif first_cell_text == 'BEARISH':
            current_position_type = 'SHORT'
            continue
        
        # Skip if we haven't seen a section header yet
        if current_position_type is None:
            continue
        
        # Skip header rows (contain "TICKER", "DATE ADDED", etc.)
        if 'TICKER' in first_cell_text or 'DATE ADDED' in first_cell_text:
            continue

        # Parse data row - should have 7 cells:
        # Description, Ticker, Date Added, Recent Price, Trend Low, Trend High, Asset Class
        if len(cells) < 7:
            continue

        try:
            description = cells[0].get_text(strip=True)
            ticker = cells[1].get_text(strip=True)
            date_added_raw = cells[2].get_text(strip=True)
            recent_price_raw = cells[3].get_text(strip=True)
            trend_low_raw = cells[4].get_text(strip=True)
            trend_high_raw = cells[5].get_text(strip=True)
            asset_class = cells[6].get_text(strip=True)

            # Parse date
            date_added = standardize_date(date_added_raw)

            # Parse prices
            recent_price = parse_price(recent_price_raw)
            trend_low = parse_price(trend_low_raw)
            trend_high = parse_price(trend_high_raw)

            positions.append(EtfProPosition(
                ticker=ticker,
                description=description,
                position_type=current_position_type,
                date_added=date_added,
                recent_price=recent_price,
                trend_low=trend_low,
                trend_high=trend_high,
                asset_class=asset_class
            ))

        except Exception as e:
            cell_texts = [c.get_text(strip=True) for c in cells]
            print(f"  Warning: Could not parse row {cell_texts}: {e}")
            continue

    return report_date, positions


def save_outputs(report_date: str, positions: List[EtfProPosition], output_dir: str = None):
    """
    Save parsed positions to CSV file.

    Args:
        report_date: Report date in YYYY-MM-DD format
        positions: List of EtfProPosition objects
        output_dir: Output directory (defaults to config value)
    """
    if output_dir is None:
        from hedgeye.config_loader import load_config
        config = load_config()
        output_dir = config["paths"]["etf_pro_csv_dir"]

    output_path = Path(output_dir) / f"etf_pro_weekly_{report_date}.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write CSV
    with open(output_path, 'w') as f:
        # Header
        f.write("report_date,position_type,ticker,description,date_added,recent_price,trend_low,trend_high,asset_class\n")

        # Data rows
        for pos in positions:
            f.write(f"{report_date},{pos.position_type},{pos.ticker},{pos.description},"
                   f"{pos.date_added},{pos.recent_price},{pos.trend_low},{pos.trend_high},"
                   f'"{pos.asset_class}"\n')

    print(f"✅ Saved {len(positions)} positions to {output_path}")


def main():
    """Main entry point - finds and parses the latest ETF Pro weekly email"""
    from hedgeye.config_loader import load_config

    config = load_config()
    raw_dir = Path(config["paths"]["etf_pro_raw_eml_dir"])

    # Find latest ETF Pro weekly file
    eml_files = list(raw_dir.glob("etf_pro_weekly_*.eml"))
    if not eml_files:
        print("❌ No ETF Pro weekly files found")
        return

    latest_file = sorted(eml_files)[-1]
    print(f"📂 Parsing: {latest_file.name}")

    # Parse the email
    report_date, positions = parse_eml(str(latest_file))

    print(f"\n📊 Report Date: {report_date}")
    print(f"   Total Positions: {len(positions)}")
    print(f"   LONG: {sum(1 for p in positions if p.position_type == 'LONG')}")
    print(f"   SHORT: {sum(1 for p in positions if p.position_type == 'SHORT')}")

    # Save outputs
    save_outputs(report_date, positions)


if __name__ == "__main__":
    main()
