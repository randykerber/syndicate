#!/usr/bin/env python3
"""
Enrich position ranges with current prices and proxy-translated trade ranges.

This script:
1. Loads the base merged CSV
2. Fetches current prices for all p_sym and r_sym
3. Calculates proxy-translated trade ranges using the formula:
   - Assume r_current matches p_current conceptually
   - Calculate m = trade_low / r_current, n = trade_high / r_current
   - Then p_trade_low = p_current * m, p_trade_high = p_current * n
4. Saves enriched CSV with additional calculated fields

Usage:
    uv run python -m syndicate.data_sources.hedgeye.cr_enrich_ranges
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List
from syndicate.data_sources.hedgeye.config_loader import load_config
from syndicate.data_sources.hedgeye.fetch_prices import fetch_current_prices


def cr_load_base_merged(csv_path: Path) -> pd.DataFrame:
    """Load the base merged position ranges CSV."""
    df = pd.read_csv(csv_path)
    print(f"  ✓ Loaded {len(df)} positions from base merge")
    return df


def cr_add_current_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add current prices for both p_sym and r_sym.

    Falls back to rr_prev_close for r_sym if live price unavailable.

    Args:
        df: DataFrame with p_sym and r_sym columns

    Returns:
        DataFrame with p_current and r_current columns filled
    """
    # Collect all unique symbols to fetch
    p_symbols = df['p_sym'].dropna().unique().tolist()
    r_symbols = df['r_sym'].dropna().unique().tolist()

    all_symbols = list(set(p_symbols + r_symbols))

    # Fetch all prices at once
    prices = fetch_current_prices(all_symbols)

    # Map prices to columns
    df['p_current'] = df['p_sym'].map(prices)
    df['r_current'] = df['r_sym'].map(prices)

    # Use rr_prev_close as fallback for r_current if available
    if 'rr_prev_close' in df.columns:
        missing_r = df['r_current'].isna() & df['rr_prev_close'].notna()
        if missing_r.sum() > 0:
            df.loc[missing_r, 'r_current'] = df.loc[missing_r, 'rr_prev_close']
            print(f"  ✓ Used rr_prev_close fallback for {missing_r.sum()} r_sym")

    p_filled = df['p_current'].notna().sum()
    r_filled = df['r_current'].notna().sum()

    print(f"  ✓ Added current prices ({p_filled} p_sym, {r_filled} r_sym)")

    return df


def cr_calculate_proxy_trade_ranges(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate proxy-translated trade ranges.

    For positions with r_sym (proxy), translate RR trade ranges to p_sym coordinates.

    Formula:
    - m = trade_low / r_current
    - n = trade_high / r_current
    - p_trade_low = p_current * m
    - p_trade_high = p_current * n

    Args:
        df: DataFrame with trade_low, trade_high, p_current, r_current

    Returns:
        DataFrame with p_trade_low and p_trade_high columns added
    """
    # Initialize new columns
    df['p_trade_low'] = None
    df['p_trade_high'] = None

    # Only calculate for rows with all required data
    mask = (
        df['trade_low'].notna() &
        df['trade_high'].notna() &
        df['p_current'].notna() &
        df['r_current'].notna() &
        (df['r_current'] > 0)  # Avoid division by zero
    )

    if mask.sum() > 0:
        # Calculate multipliers
        df.loc[mask, 'm'] = df.loc[mask, 'trade_low'] / df.loc[mask, 'r_current']
        df.loc[mask, 'n'] = df.loc[mask, 'trade_high'] / df.loc[mask, 'r_current']

        # Apply to p_current
        df.loc[mask, 'p_trade_low'] = df.loc[mask, 'p_current'] * df.loc[mask, 'm']
        df.loc[mask, 'p_trade_high'] = df.loc[mask, 'p_current'] * df.loc[mask, 'n']

        # Drop temporary m, n columns
        df = df.drop(columns=['m', 'n'])

        print(f"  ✓ Calculated proxy trade ranges for {mask.sum()} positions")
    else:
        print("  ⚠️  No positions with complete data for proxy calculation")

    return df


def cr_add_interpretability_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add calculated fields to aid interpretation.

    Fields added:
    - trend_pct_from_low: % distance from trend low to current price
    - trend_pct_from_high: % distance from trend high to current price
    - trade_pct_from_low: % distance from trade low to current price
    - trade_pct_from_high: % distance from trade high to current price
    - p_trade_pct_from_low: % distance from p_trade_low to current price
    - p_trade_pct_from_high: % distance from p_trade_high to current price
    """
    # Trend ranges (from EPP)
    mask = df['trend_low'].notna() & df['trend_high'].notna() & df['p_current'].notna()
    if mask.sum() > 0:
        df.loc[mask, 'trend_pct_from_low'] = (
            (df.loc[mask, 'p_current'] - df.loc[mask, 'trend_low']) /
            df.loc[mask, 'trend_low'] * 100
        )
        df.loc[mask, 'trend_pct_from_high'] = (
            (df.loc[mask, 'p_current'] - df.loc[mask, 'trend_high']) /
            df.loc[mask, 'trend_high'] * 100
        )

    # RR trade ranges (original r_sym coordinates)
    mask = df['trade_low'].notna() & df['trade_high'].notna() & df['r_current'].notna()
    if mask.sum() > 0:
        df.loc[mask, 'trade_pct_from_low'] = (
            (df.loc[mask, 'r_current'] - df.loc[mask, 'trade_low']) /
            df.loc[mask, 'trade_low'] * 100
        )
        df.loc[mask, 'trade_pct_from_high'] = (
            (df.loc[mask, 'r_current'] - df.loc[mask, 'trade_high']) /
            df.loc[mask, 'trade_high'] * 100
        )

    # Proxy-translated trade ranges (p_sym coordinates)
    mask = df['p_trade_low'].notna() & df['p_trade_high'].notna() & df['p_current'].notna()
    if mask.sum() > 0:
        df.loc[mask, 'p_trade_pct_from_low'] = (
            (df.loc[mask, 'p_current'] - df.loc[mask, 'p_trade_low']) /
            df.loc[mask, 'p_trade_low'] * 100
        )
        df.loc[mask, 'p_trade_pct_from_high'] = (
            (df.loc[mask, 'p_current'] - df.loc[mask, 'p_trade_high']) /
            df.loc[mask, 'p_trade_high'] * 100
        )

    print("  ✓ Added interpretability percentage fields")

    return df


def cr_save_enriched_data(df: pd.DataFrame, output_path: Path):
    """Save enriched DataFrame to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\n💾 Saved enriched data to: {output_path}")
    print(f"   Rows: {len(df)}")
    print(f"   Columns: {len(df.columns)}")


def cr_create_formatted_text(df: pd.DataFrame, output_path: Path):
    """Create formatted text file with aligned columns."""
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 250)
    pd.set_option('display.max_colwidth', 30)

    output = df.to_string(index=False)
    txt_path = output_path.parent / output_path.name.replace('.csv', '.txt')
    txt_path.write_text(output)
    print(f"📄 Created formatted text file: {txt_path}")


def main():
    """Main entry point for enrichment script."""
    print("=" * 70)
    print("Position Ranges Enrichment - Adding Prices & Proxy Calculations")
    print("=" * 70)

    config = load_config()
    ranges_dir = Path("/Users/rk/d/downloads/hedgeye/prod/ranges")

    base_csv = ranges_dir / "base" / "position_ranges_base.csv"
    output_csv = ranges_dir / "enriched" / "position_ranges_enriched.csv"

    print("\n📂 Loading Base Data...")
    df = cr_load_base_merged(base_csv)

    print("\n💰 Fetching Current Prices...")
    df = cr_add_current_prices(df)

    print("\n🔢 Calculating Proxy Trade Ranges...")
    df = cr_calculate_proxy_trade_ranges(df)

    print("\n📊 Adding Interpretability Fields...")
    df = cr_add_interpretability_fields(df)

    # Reorder columns for clarity
    base_cols = [
        'p_sym', 'description', 'position_type', 'date_added', 'asset_class', 'rank'
    ]
    price_cols = [
        'p_current', 'trend_low', 'trend_high',
        'trend_pct_from_low', 'trend_pct_from_high'
    ]
    proxy_cols = [
        'r_sym', 'proxy_type', 'r_current',
        'trade_low', 'trade_high', 'trade_pct_from_low', 'trade_pct_from_high',
        'p_trade_low', 'p_trade_high', 'p_trade_pct_from_low', 'p_trade_pct_from_high',
        'rr_trend'
    ]
    date_cols = ['report_date_epp', 'report_date_ps', 'rr_date']

    all_cols = base_cols + price_cols + proxy_cols + date_cols
    existing_cols = [c for c in all_cols if c in df.columns]
    df = df[existing_cols]

    # Save enriched data
    cr_save_enriched_data(df, output_csv)
    cr_create_formatted_text(df, output_csv)

    print("\n" + "=" * 70)
    print("✅ Enrichment Complete!")
    print("=" * 70)

    # Summary stats
    print("\nSummary:")
    print(f"  Total positions: {len(df)}")
    print(f"  With p_current: {df['p_current'].notna().sum()}")
    print(f"  With r_current: {df['r_current'].notna().sum()}")
    print(f"  With proxy trade ranges: {df['p_trade_low'].notna().sum()}")
    print(f"  LONG positions: {(df['position_type'] == 'LONG').sum()}")
    print(f"  SHORT positions: {(df['position_type'] == 'SHORT').sum()}")


if __name__ == "__main__":
    main()
