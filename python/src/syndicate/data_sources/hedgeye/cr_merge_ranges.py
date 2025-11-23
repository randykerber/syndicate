#!/usr/bin/env python3
"""
Merge position ranges from multiple sources.

This script combines:
1. ETF Pro Plus (EPP) weekly portfolio - trend ranges, LONG/SHORT positions
2. Portfolio Solutions (PS) daily - portfolio ranks
3. Risk Range (RR) combined - trade ranges for reference symbols
4. Symbol mapping table - p_sym to r_sym mappings
5. Live prices - current prices for both p_sym and r_sym

Output: Clean merged CSV with all raw data, no calculations.

Usage:
    uv run python -m syndicate.data_sources.hedgeye.cr_merge_ranges
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from syndicate.data_sources.hedgeye.config_loader import load_config


def get_latest_file(directory: Path, pattern: str) -> Optional[Path]:
    """
    Get the most recent file matching a pattern.

    Sorts by the date embedded in the filename (YYYY-MM-DD), not file mtime.

    Args:
        directory: Directory to search
        pattern: Glob pattern to match

    Returns:
        Path to latest file, or None if no files found
    """
    import re

    files = list(directory.glob(pattern))
    if not files:
        return None

    # Extract date from filename and sort
    # Pattern: *_YYYY-MM-DD.csv
    def extract_date(path: Path) -> str:
        match = re.search(r'(\d{4}-\d{2}-\d{2})', path.name)
        return match.group(1) if match else '0000-00-00'

    return max(files, key=extract_date)


def load_epp_portfolio(csv_path: Path) -> pd.DataFrame:
    """
    Load ETF Pro Plus weekly portfolio.

    Returns DataFrame with columns:
    report_date, position_type, ticker, description, date_added,
    recent_price, trend_low, trend_high, asset_class
    """
    df = pd.read_csv(csv_path)
    print(f"  ✓ Loaded {len(df)} EPP positions from {csv_path.name}")
    return df


def load_ps_portfolio(csv_path: Path) -> pd.DataFrame:
    """
    Load Portfolio Solutions daily rankings.

    Returns DataFrame with columns:
    report_date, rank, ticker, name
    """
    df = pd.read_csv(csv_path)
    print(f"  ✓ Loaded {len(df)} PS positions from {csv_path.name}")
    return df


def load_rr_data(csv_path: Path) -> pd.DataFrame:
    """
    Load Risk Range combined data.

    Returns DataFrame with columns:
    date, index, trend, buy_trade, sell_trade, prev_close, bucket, ...
    """
    df = pd.read_csv(csv_path)
    print(f"  ✓ Loaded {len(df)} RR records")
    return df


def load_mapping_table(mapping_path: Path) -> pd.DataFrame:
    """
    Load p_sym to r_sym mapping table from YAML or CSV file.
    
    Supports both YAML (preferred) and CSV formats for backward compatibility.
    All access to the mapping file should go through this function.

    Args:
        mapping_path: Path to mapping file (.yaml or .csv)

    Returns:
        DataFrame with columns:
        p_sym, r_sym, mapping_type, proxy_type, confidence, notes, inverted
    """
    import yaml
    
    if not mapping_path.exists():
        raise FileNotFoundError(f"Mapping file not found: {mapping_path}")
    
    # Determine file type and load accordingly
    if mapping_path.suffix.lower() in ['.yaml', '.yml']:
        # Load from YAML
        with open(mapping_path, 'r') as f:
            yaml_data = yaml.safe_load(f)
        
        # Convert YAML structure to DataFrame
        mappings = yaml_data.get('mappings', [])
        if not mappings:
            return pd.DataFrame(columns=['p_sym', 'r_sym', 'mapping_type', 'confidence', 'notes', 'proxy_type', 'inverted'])
        
        # Convert list of dicts to DataFrame
        df = pd.DataFrame(mappings)
        
        # Ensure all expected columns exist
        expected_cols = ['p_sym', 'r_sym', 'mapping_type', 'confidence', 'notes', 'proxy_type', 'inverted']
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None
        
        # Convert None/empty r_sym to empty string for consistency
        df['r_sym'] = df['r_sym'].fillna('')
        
        # Ensure inverted is boolean
        df['inverted'] = df['inverted'].fillna(False).astype(bool)
        
    else:
        # Load from CSV (backward compatibility)
        df = pd.read_csv(mapping_path)
        # Fill NaN values for consistency
        df['r_sym'] = df['r_sym'].fillna('')
        if 'inverted' not in df.columns:
            df['inverted'] = False
        df['inverted'] = df['inverted'].fillna(False).astype(bool)
    
    print(f"  ✓ Loaded {len(df)} symbol mappings from {mapping_path.suffix}")
    return df


def get_latest_rr_for_symbol(rr_df: pd.DataFrame, symbol: str) -> Optional[pd.Series]:
    """
    Get the most recent RR data for a symbol.

    Args:
        rr_df: Risk Range DataFrame
        symbol: Symbol to lookup (r_sym)

    Returns:
        Series with latest RR data, or None if not found
    """
    symbol_data = rr_df[rr_df['index'] == symbol]
    if symbol_data.empty:
        return None

    # Sort by date and get latest
    symbol_data = symbol_data.sort_values('date', ascending=False)
    return symbol_data.iloc[0]


def fetch_current_prices(symbols: list) -> Dict[str, float]:
    """
    Fetch current prices for a list of symbols.

    Args:
        symbols: List of symbols to fetch prices for

    Returns:
        Dictionary mapping symbol to current price
    """
    # TODO: Implement actual price fetching from FMP/Yahoo
    # For now, return empty dict - will be filled in later
    print(f"  ⚠️  Price fetching not yet implemented ({len(symbols)} symbols)")
    return {}


def cr_merge_all_sources(
    epp_df: pd.DataFrame,
    ps_df: pd.DataFrame,
    rr_df: pd.DataFrame,
    mapping_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge all data sources into a single DataFrame.

    Strategy:
    1. Start with union of EPP and PS tickers (EPP primary for LONG/SHORT)
    2. Add PS ranks for matching tickers
    3. Add RR data via mapping table
    4. Add current prices

    Returns:
        Merged DataFrame with all raw data
    """
    print("\n=== Merging Data Sources ===")

    # Start with EPP as base (has LONG/SHORT and trend ranges)
    base_df = epp_df.copy()
    base_df = base_df.rename(columns={'ticker': 'p_sym'})
    print(f"  • Starting with {len(base_df)} EPP positions")

    # Add PS data (ranks for matching symbols)
    ps_df = ps_df.rename(columns={'ticker': 'p_sym'})
    base_df = base_df.merge(
        ps_df[['p_sym', 'rank', 'report_date']],
        on='p_sym',
        how='left',
        suffixes=('_epp', '_ps')
    )
    print(f"  • Added PS ranks ({base_df['rank'].notna().sum()} matches)")

    # Add mapping data (p_sym → r_sym)
    base_df = base_df.merge(
        mapping_df[['p_sym', 'r_sym', 'proxy_type']],
        on='p_sym',
        how='left'
    )
    print(f"  • Added symbol mappings ({base_df['r_sym'].notna().sum()} with r_sym)")

    # Add RR data for each r_sym
    rr_data = []
    for idx, row in base_df.iterrows():
        r_sym = row.get('r_sym')
        if pd.notna(r_sym):
            rr_row = get_latest_rr_for_symbol(rr_df, r_sym)
            if rr_row is not None:
                rr_data.append({
                    'p_sym': row['p_sym'],
                    'trade_low': rr_row['buy_trade'],
                    'trade_high': rr_row['sell_trade'],
                    'rr_prev_close': rr_row['prev_close'],
                    'rr_date': rr_row['date'],
                    'rr_trend': rr_row['trend']
                })

    if rr_data:
        rr_enriched = pd.DataFrame(rr_data)
        base_df = base_df.merge(rr_enriched, on='p_sym', how='left')
        print(f"  • Added RR trade ranges ({len(rr_data)} symbols with ranges)")
    else:
        # Add empty columns if no RR data
        base_df['trade_low'] = None
        base_df['trade_high'] = None
        base_df['rr_prev_close'] = None
        base_df['rr_date'] = None
        base_df['rr_trend'] = None

    # Placeholder for current prices (will implement later)
    base_df['p_current'] = None
    base_df['r_current'] = None

    # Reorder columns for clarity
    cols = [
        'p_sym', 'description', 'position_type', 'date_added', 'asset_class',
        'rank', 'p_current', 'trend_low', 'trend_high',
        'r_sym', 'proxy_type', 'r_current', 'trade_low', 'trade_high', 'rr_prev_close', 'rr_trend',
        'report_date_epp', 'report_date_ps', 'rr_date'
    ]

    # Only include columns that exist
    cols = [c for c in cols if c in base_df.columns]
    result_df = base_df[cols]

    print(f"\n  ✓ Merged {len(result_df)} total positions")

    return result_df


def cr_save_merged_data(df: pd.DataFrame, output_path: Path):
    """Save merged DataFrame to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\n💾 Saved merged data to: {output_path}")
    print(f"   Rows: {len(df)}")
    print(f"   Columns: {len(df.columns)}")


def main():
    """Main entry point for merge script."""
    print("=" * 70)
    print("Position Ranges Merge - Combining All Sources")
    print("=" * 70)

    config = load_config()

    # Define paths
    epp_dir = Path(config["paths"]["etf_pro_csv_dir"])
    ps_dir = Path(config["paths"]["portfolio_solutions_csv_dir"])
    rr_path = Path(config["paths"]["combined_csv_output_dir"]) / "combined_risk_range.csv"
    ranges_dir = Path(config["paths"]["ranges_base_dir"])
    mapping_path = Path(config["paths"]["p_to_r_mapping_file"])
    output_path = ranges_dir / "base" / "position_ranges_base.csv"

    # Load latest EPP weekly
    # NOTE: We use the latest EP weekly file to get the current portfolio state
    # (LONG/SHORT positions and trend ranges). Historical tracking of EP/PS
    # positions over time is handled separately at the parsing level.
    print("\n📂 Loading Data Sources...")
    epp_file = get_latest_file(epp_dir, "etf_pro_weekly_*.csv")
    if not epp_file:
        print("❌ No EPP weekly files found")
        return
    epp_df = load_epp_portfolio(epp_file)

    # Load latest PS daily
    # NOTE: We use the latest PS daily file to get the current ranking state.
    # Historical PS rankings are preserved in individual CSV files.
    ps_file = get_latest_file(ps_dir, "ps_daily_*.csv")
    if not ps_file:
        print("❌ No PS daily files found")
        return
    ps_df = load_ps_portfolio(ps_file)

    # Load RR combined
    if not rr_path.exists():
        print(f"❌ RR combined file not found: {rr_path}")
        return
    rr_df = load_rr_data(rr_path)

    # Load mapping table
    if not mapping_path.exists():
        print(f"❌ Mapping table not found: {mapping_path}")
        return
    mapping_df = load_mapping_table(mapping_path)

    # Merge all sources
    merged_df = cr_merge_all_sources(epp_df, ps_df, rr_df, mapping_df)

    # Save merged data
    cr_save_merged_data(merged_df, output_path)

    print("\n" + "=" * 70)
    print("✅ Merge Complete!")
    print("=" * 70)

    # Summary stats
    print("\nSummary:")
    print(f"  Total positions: {len(merged_df)}")
    print(f"  With trend ranges: {merged_df['trend_low'].notna().sum()}")
    print(f"  With trade ranges: {merged_df['trade_low'].notna().sum()}")
    print(f"  With PS ranks: {merged_df['rank'].notna().sum()}")
    print(f"  LONG positions: {(merged_df['position_type'] == 'LONG').sum()}")
    print(f"  SHORT positions: {(merged_df['position_type'] == 'SHORT').sum()}")


if __name__ == "__main__":
    main()