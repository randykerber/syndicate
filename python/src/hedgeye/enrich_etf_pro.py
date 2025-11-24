#!/usr/bin/env python3
"""
Enrich ETF Pro Plus weekly data with current prices from FMP/Yahoo.

Reads the latest ETF Pro weekly CSV and adds current_price column.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional
from hedgeye.config_loader import load_config
from hedgeye.fmp.price_fetcher import get_prices_for_symbols


def get_latest_etf_pro_file() -> Optional[Path]:
    """Find the most recent ETF Pro weekly CSV file (non-enriched)"""
    config = load_config()
    csv_dir = Path(config["paths"]["etf_pro_csv_dir"])

    if not csv_dir.exists():
        return None

    # Only get base CSV files (not enriched versions)
    csv_files = [f for f in csv_dir.glob("etf_pro_weekly_*.csv")
                 if "_enriched" not in f.name]
    if not csv_files:
        return None

    # Sort by filename (which includes date) and get latest
    return sorted(csv_files)[-1]


def enrich_with_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add current_price column to ETF Pro dataframe.

    Args:
        df: DataFrame with 'ticker' column

    Returns:
        DataFrame with added 'current_price' column
    """
    print(f"Fetching current prices for {df['ticker'].nunique()} symbols...")

    # Get unique tickers - create mappings dataframe
    tickers = df['ticker'].unique()
    mappings = pd.DataFrame({
        'he_symbol': tickers,
        'fmp_symbol': tickers,  # For ETF Pro, symbols are already tradeable
        'fmp_etype': 'etfs'  # Assume all are ETFs for now
    })

    # Fetch latest prices using FMP price fetcher
    try:
        prices_df = get_prices_for_symbols(mappings, latest=True)

        # Create ticker -> price mapping
        price_map = prices_df.set_index('he_symbol')['price'].to_dict()

        # Add current_price column
        df['current_price'] = df['ticker'].map(price_map)

        # Report any missing prices
        missing = df[df['current_price'].isna()]['ticker'].unique()
        if len(missing) > 0:
            print(f"⚠️ Could not fetch prices for: {', '.join(missing)}")

        successful = df['current_price'].notna().sum()
        print(f"✅ Fetched prices for {successful}/{len(df)} positions")

    except Exception as e:
        print(f"❌ Error fetching prices: {e}")
        df['current_price'] = None

    return df


def calculate_range_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add columns showing position relative to trend range.

    Adds:
    - trend_pct: Where current price sits in trend range (0-100%)
    - trend_relative: Same as trend_pct but on 0-10 scale
    - status: BUY/SELL/IN_RANGE based on position
    """
    # Calculate percentage through trend range
    df['trend_pct'] = ((df['current_price'] - df['trend_low']) /
                       (df['trend_high'] - df['trend_low']) * 100)

    # 0-10 scale for easy reading
    df['trend_relative'] = df['trend_pct'] / 10

    # Status flags
    def get_status(row):
        if pd.isna(row['current_price']):
            return 'NO_PRICE'
        if row['current_price'] < row['trend_low']:
            return 'BELOW_TREND'  # 🚨 Sell signal
        if row['current_price'] > row['trend_high']:
            return 'ABOVE_TREND'  # 🚨 Strong signal
        return 'IN_RANGE'

    df['status'] = df.apply(get_status, axis=1)

    return df


def save_enriched(df: pd.DataFrame, output_path: Path):
    """Save enriched dataframe to CSV"""
    # Reorder columns for better readability
    cols = [
        'report_date', 'position_type', 'ticker', 'description',
        'current_price', 'trend_low', 'trend_high',
        'trend_relative', 'status',
        'date_added', 'recent_price', 'asset_class'
    ]

    # Keep only columns that exist
    cols = [c for c in cols if c in df.columns]
    df = df[cols]

    df.to_csv(output_path, index=False)
    print(f"✅ Saved enriched CSV to {output_path}")


def generate_markdown(df: pd.DataFrame, output_path: Path):
    """
    Generate Markdown table for Obsidian viewing.

    Highlights:
    - 🔴 BELOW_TREND (sell signal)
    - 🟢 ABOVE_TREND (strong position)
    - ⚠️ Near edges (trend_relative < 2 or > 8)
    """
    lines = []

    # Header
    lines.append("# ETF Pro Plus Weekly - Enriched with Current Prices\n")
    lines.append(f"**Report Date:** {df['report_date'].iloc[0]}\n")
    lines.append(f"**Positions:** {len(df)} ({df['position_type'].value_counts().to_dict()})\n")

    # Status summary
    lines.append("\n## Status Summary\n")
    status_counts = df['status'].value_counts()
    for status, count in status_counts.items():
        emoji = "🔴" if status == "BELOW_TREND" else "🟢" if status == "ABOVE_TREND" else "⚪"
        lines.append(f"- {emoji} **{status}**: {count}\n")

    # LONG positions
    long_df = df[df['position_type'] == 'LONG'].copy()
    if len(long_df) > 0:
        lines.append("\n## 📈 LONG Positions\n")
        lines.append("| Ticker | Description | Current | Trend Low | Trend High | Relative | Status |\n")
        lines.append("|--------|-------------|---------|-----------|------------|----------|--------|\n")

        for _, row in long_df.iterrows():
            # Determine visual indicator
            if row['status'] == 'BELOW_TREND':
                indicator = "🔴"
            elif row['status'] == 'ABOVE_TREND':
                indicator = "🟢"
            elif row['trend_relative'] < 2:
                indicator = "⚠️"  # Near bottom
            elif row['trend_relative'] > 8:
                indicator = "⚠️"  # Near top
            else:
                indicator = ""

            lines.append(
                f"| {row['ticker']} | {row['description']} | "
                f"${row['current_price']:.2f} | ${row['trend_low']:.2f} | "
                f"${row['trend_high']:.2f} | {row['trend_relative']:.1f}/10 | "
                f"{indicator} {row['status']} |\n"
            )

    # SHORT positions
    short_df = df[df['position_type'] == 'SHORT'].copy()
    if len(short_df) > 0:
        lines.append("\n## 📉 SHORT Positions\n")
        lines.append("| Ticker | Description | Current | Trend Low | Trend High | Relative | Status |\n")
        lines.append("|--------|-------------|---------|-----------|------------|----------|--------|\n")

        for _, row in short_df.iterrows():
            # Determine visual indicator
            if row['status'] == 'ABOVE_TREND':
                indicator = "🔴"  # Bad for short - price too high
            elif row['status'] == 'BELOW_TREND':
                indicator = "🟢"  # Good for short - price dropping
            elif row['trend_relative'] < 2:
                indicator = "⚠️"  # Near bottom
            elif row['trend_relative'] > 8:
                indicator = "⚠️"  # Near top
            else:
                indicator = ""

            lines.append(
                f"| {row['ticker']} | {row['description']} | "
                f"${row['current_price']:.2f} | ${row['trend_low']:.2f} | "
                f"${row['trend_high']:.2f} | {row['trend_relative']:.1f}/10 | "
                f"{indicator} {row['status']} |\n"
            )

    # Write to file
    with open(output_path, 'w') as f:
        f.writelines(lines)

    print(f"✅ Saved markdown to {output_path}")


def main():
    """Main enrichment workflow"""
    # Find latest ETF Pro file (non-enriched base CSV)
    latest_file = get_latest_etf_pro_file()
    if latest_file is None:
        print("❌ No ETF Pro weekly files found")
        return

    print(f"📂 Reading: {latest_file.name}")
    df = pd.read_csv(latest_file)
    print(f"   {len(df)} positions ({df['position_type'].value_counts().to_dict()})")

    # Enrich with current prices
    df = enrich_with_prices(df)

    # Calculate range metrics
    df = calculate_range_metrics(df)

    # Save outputs (overwrite if exists)
    # Extract base name: etf_pro_weekly_2025-11-09.csv -> etf_pro_weekly_2025-11-09
    base_name = latest_file.stem

    # CSV output
    csv_output = latest_file.parent / f"{base_name}_enriched.csv"
    save_enriched(df, csv_output)

    # Markdown output
    md_output = latest_file.parent / f"{base_name}_enriched.md"
    generate_markdown(df, md_output)

    # Print summary
    print("\n📊 Position Status Summary:")
    print(df['status'].value_counts().to_string())

    # Show positions outside trend range (alerts)
    alerts = df[df['status'].isin(['BELOW_TREND', 'ABOVE_TREND'])]
    if len(alerts) > 0:
        print(f"\n🚨 {len(alerts)} positions OUTSIDE trend range:")
        for _, row in alerts.iterrows():
            direction = "↓ BELOW" if row['status'] == 'BELOW_TREND' else "↑ ABOVE"
            print(f"   {row['ticker']:6} ({row['position_type']:5}) {direction} "
                  f"${row['current_price']:.2f} vs ${row['trend_low']:.2f}-${row['trend_high']:.2f}")

    print(f"\n📁 Files saved:")
    print(f"   CSV: {csv_output.name}")
    print(f"   Markdown: {md_output.name}")


if __name__ == "__main__":
    main()
