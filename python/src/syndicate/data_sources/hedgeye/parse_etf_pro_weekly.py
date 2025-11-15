#!/usr/bin/env python3
"""
Parser for Hedgeye ETF Pro Plus weekly emails.

Extracts trend ranges and position information from weekly portfolio snapshots.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Tuple, List, NamedTuple
from email import message_from_file


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


def parse_position_line(line: str) -> EtfProPosition:
    """
    Parse a single position line from the email.

    Example input:
    "Physical GoldAAAU2/28/2025$39.52$38.07$40.86Foreign Currency"

    Pattern: Description + Ticker + Date + Price + TrendLow + TrendHigh + AssetClass
    """
    # Regex pattern to extract components
    # Strategy: Find the date pattern first, then work backwards to find ticker
    # Ticker is 2-5 uppercase letters immediately before the date
    pattern = r'^(.+?)([A-Z]{2,5})(\d{1,2}/\d{1,2}/\d{4})\$(\d+\.\d+)\$(\d+\.\d+)\$(\d+\.\d+)(.+)$'

    match = re.match(pattern, line)
    if not match:
        raise ValueError(f"Could not parse position line: {line}")

    description = match.group(1).strip()
    ticker = match.group(2)
    date_added = standardize_date(match.group(3))
    recent_price = float(match.group(4))
    trend_low = float(match.group(5))
    trend_high = float(match.group(6))
    asset_class = match.group(7).strip()

    # Additional validation: ticker should be 2-4 chars typically
    # If ticker is 5 chars and description ends with uppercase, regex was likely too greedy
    if len(ticker) == 5 and description and description[-1].isupper():
        # Move first char of ticker back to description (e.g., "OCLOX" -> "AAA CLO" + "CLOX")
        description = description + ticker[0]
        ticker = ticker[1:]

    # Position type will be set by caller based on section (BULLISH/BEARISH)
    return EtfProPosition(
        ticker=ticker,
        description=description,
        position_type="",  # Will be set by parse_eml
        date_added=date_added,
        recent_price=recent_price,
        trend_low=trend_low,
        trend_high=trend_high,
        asset_class=asset_class
    )


def parse_eml(filepath: str) -> Tuple[str, List[EtfProPosition]]:
    """
    Parse ETF Pro Plus weekly email file.

    Returns:
        (report_date, positions)
    """
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        msg = message_from_file(f)

    # Extract report date from subject or email date
    # Subject format: "ETF Pro Plus - New Weekly Report"
    # Use email Date header
    date_str = msg.get('Date', '')
    # Parse date from format like: "Sun, 9 Nov 2025 15:39:04 -0500 (EST)"
    dt = datetime.strptime(date_str.split(',')[1].strip().split(' -')[0], "%d %b %Y %H:%M:%S")
    report_date = dt.strftime("%Y-%m-%d")

    # Get email body
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                break
    else:
        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

    # Find BULLISH and BEARISH sections
    # Pattern: "BULLISHTICKERDATE ADDED..." followed by position lines
    bullish_match = re.search(r'BULLISH.*?ASSET CLASS\n(.*?)(?=BEARISH|$)', body, re.DOTALL)
    bearish_match = re.search(r'BEARISH.*?ASSET CLASS\n(.*?)(?=\*All ETF|Trade ::|$)', body, re.DOTALL)

    positions = []

    # Parse BULLISH positions
    if bullish_match:
        bullish_text = bullish_match.group(1).strip()
        for line in bullish_text.split('\n'):
            line = line.strip()
            if not line or 'BEARISH' in line:
                continue
            try:
                pos = parse_position_line(line)
                # Set position type to LONG
                positions.append(pos._replace(position_type='LONG'))
            except ValueError as e:
                print(f"Warning: Could not parse bullish line: {e}")

    # Parse BEARISH positions
    if bearish_match:
        bearish_text = bearish_match.group(1).strip()
        for line in bearish_text.split('\n'):
            line = line.strip()
            if not line or '*All ETF' in line or 'Trade ::' in line:
                continue
            try:
                pos = parse_position_line(line)
                # Set position type to SHORT
                positions.append(pos._replace(position_type='SHORT'))
            except ValueError as e:
                print(f"Warning: Could not parse bearish line: {e}")

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
        from syndicate.data_sources.hedgeye.config_loader import load_config
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
    from syndicate.data_sources.hedgeye.config_loader import load_config

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