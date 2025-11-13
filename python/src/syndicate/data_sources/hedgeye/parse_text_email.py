#!/usr/bin/env python3
"""
Simple text parser for Hedgeye Risk Range emails when HTML parsing fails.
Handles plain text format from iCloud Mail copy-paste.
"""

import re
from datetime import datetime
from typing import List, Tuple, Optional
from hedgeye_kb.models import RiskRangeEntry, ChangeEvent, Trend, Bucket
from hedgeye_kb.symbol_canonicalization import canonicalize_symbol

def standardize_date(date_str: str) -> str:
    """Convert date string to ISO format."""
    try:
        date_obj = datetime.strptime(date_str, "%B %d, %Y")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        try:
            date_obj = datetime.strptime(date_str, "%b %d, %Y")
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            return date_str

def parse_text_email(file_path: str) -> Tuple[Optional[str], List[RiskRangeEntry], List[ChangeEvent]]:
    """
    Parse Risk Range data from plain text email format.
    
    Args:
        file_path: Path to text file containing email content
        
    Returns:
        Tuple of (report_date, entries, changes)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    
    # Extract date
    report_date = None
    for line in lines:
        # Look for date pattern like "RISK RANGE™ SIGNALS: June 26, 2025"
        date_match = re.search(r"RISK RANGE™ SIGNALS:\s*(\w+ \d{1,2}, \d{4})", line)
        if date_match:
            report_date = standardize_date(date_match.group(1))
            break
        # Alternative: look for timestamp pattern "06/26/2025 07:58 AM EDT"
        date_match = re.search(r"(\d{2}/\d{2}/\d{4})", line)
        if date_match:
            try:
                date_obj = datetime.strptime(date_match.group(1), "%m/%d/%Y")
                report_date = date_obj.strftime("%Y-%m-%d")
                break
            except ValueError:
                continue
    
    if not report_date:
        raise ValueError("Could not find date in text content")
    
    # Extract trend changes
    changes = []
    trend_section = False
    for line in lines:
        if "TREND CHANGE:" in line:
            trend_section = True
            continue
        if trend_section and line.startswith(("Bullish", "Bearish", "Neutral", "INDEX")):
            trend_section = False
            break
        if trend_section:
            # Parse trend changes like "USD/YEN changed from NEUTRAL to BEARISH"
            change_match = re.search(r"(\w+(?:/\w+)?)\s+changed from\s+(\w+)\s+to\s+(\w+)", line)
            if change_match:
                symbol = canonicalize_symbol(change_match.group(1))
                old_trend = change_match.group(2)
                new_trend = change_match.group(3)
                changes.append(ChangeEvent(
                    date=report_date or "2025-06-26",  # Use parsed date or fallback
                    index=symbol,
                    trend_from=Trend(old_trend),
                    trend_to=Trend(new_trend)
                ))
            # Parse additions like "XLE added back to Risk Ranges"
            elif "added" in line.lower():
                add_match = re.search(r"(\w+)\s+added", line)
                if add_match:
                    symbol = canonicalize_symbol(add_match.group(1))
                    changes.append(ChangeEvent(
                        date=report_date or "2025-06-26",
                        index=symbol,
                        bucket_from=Bucket.OUT,
                        bucket_to=Bucket.IN
                    ))
    
    # Extract Risk Range entries
    entries = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for pattern: SYMBOL (TREND)
        symbol_match = re.match(r"^(\w+(?:/\w+)?)\s*\((\w+)\)$", line)
        if symbol_match and i + 1 < len(lines):
            symbol = canonicalize_symbol(symbol_match.group(1))
            trend = symbol_match.group(2)
            
            # Next line should have: Description BUY_TRADE SELL_TRADE PREV_CLOSE
            next_line = lines[i + 1]
            
            # Split by whitespace and take last 3 elements as numbers
            parts = next_line.split()
            if len(parts) >= 3:
                try:
                    # Extract numeric values - they're the last 3 elements
                    prev_close = float(parts[-1].replace(',', ''))
                    sell_trade = float(parts[-2].replace(',', ''))
                    buy_trade = float(parts[-3].replace(',', ''))
                    
                    # Description is everything except the last 3 numeric parts
                    description = ' '.join(parts[:-3])
                    
                    entries.append(RiskRangeEntry(
                        date=report_date or "2025-06-26",
                        index=symbol,
                        trend=Trend(trend),
                        buy_trade=buy_trade,
                        sell_trade=sell_trade,
                        prev_close=prev_close
                    ))
                    
                    i += 2  # Skip both lines
                    continue
                except (ValueError, IndexError):
                    pass
        
        i += 1
    
    return report_date, entries, changes

def test_parse_text_email():
    """Test function for the text parser."""
    test_file = "/Users/rk/d/downloads/hedgeye/raw/eml/abcxyz.eml"
    try:
        date, entries, changes = parse_text_email(test_file)
        print(f"Date: {date}")
        print(f"Found {len(entries)} entries and {len(changes)} changes")
        
        print("\nChanges:")
        for change in changes:
            print(f"  {change.symbol}: {change.event_type} ({change.old_value} -> {change.new_value})")
        
        print("\nFirst few entries:")
        for entry in entries[:5]:
            print(f"  {entry.index} ({entry.trend}): {entry.buy_trade} - {entry.sell_trade} | {entry.prev_close}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_parse_text_email()