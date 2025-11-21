#!/usr/bin/env python3
"""
Time-series plotting for Combo Ranges (CR).

Combines:
1. Risk Range (RR) trade ranges over time (translated to p_sym coordinates)
2. ETF Pro Plus (EP) trend ranges over time (forward-filled from weekly to daily)
3. Daily price history (fetched fresh from yfinance/FMP, no caching)

Usage:
    from syndicate.data_sources.hedgeye.cr_time_series_plotting import plot_cr_time_series
    plot_cr_time_series("AAAU", days_back=30)
"""

import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import numpy as np

from syndicate.data_sources.hedgeye.config_loader import load_config
from syndicate.data_sources.hedgeye.use_rr import load_all_risk_range_data
from syndicate.data_sources.hedgeye.cr_enrich_ranges import cr_calculate_proxy_trade_ranges
from syndicate.data_sources.hedgeye.price_cache import get_daily_prices

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


def fetch_historical_daily_prices(p_sym: str, start_date: datetime, end_date: datetime, 
                                  use_cache: bool = True) -> pd.Series:
    """
    Fetch historical daily closing prices for a symbol over a date range.
    
    Uses price cache (checks cache first, then fetches from yfinance if missing).
    
    Args:
        p_sym: Symbol to fetch (e.g., "AAAU")
        start_date: Start date (datetime)
        end_date: End date (datetime)
        use_cache: Whether to use cache (default: True)
        
    Returns:
        Series with date index and closing prices
    """
    # Use price cache to get prices
    prices_df = get_daily_prices([p_sym], start_date, end_date, use_cache=use_cache)
    
    if prices_df.empty:
        print(f"  ⚠️  No prices found for {p_sym}")
        return pd.Series(dtype=float)
    
    # Convert to Series with date index
    prices_df = prices_df[prices_df['ticker'] == p_sym]
    if prices_df.empty:
        return pd.Series(dtype=float)
    
    prices_series = prices_df.set_index('date')['price']
    print(f"  ✓ Got {len(prices_series)} daily prices for {p_sym} ({start_date.date()} to {end_date.date()})")
    return prices_series


def load_ep_time_series(p_sym: str, days_back: int = 30) -> pd.DataFrame:
    """
    Load ETF Pro Plus trend range time series for a ticker.
    
    EP data is weekly, so we forward-fill values to create daily time series.
    
    Args:
        p_sym: Portfolio symbol (e.g., "BUXX")
        days_back: Number of days to look back
        
    Returns:
        DataFrame with columns: date, trend_low, trend_high, recent_price
    """
    config = load_config()
    ep_csv_dir = Path(config["paths"]["etf_pro_csv_dir"])
    
    # Find all EP weekly CSV files
    ep_files = sorted(ep_csv_dir.glob("etf_pro_weekly_*.csv"))
    
    if not ep_files:
        print(f"⚠️  No EP weekly files found in {ep_csv_dir}")
        return pd.DataFrame(columns=['date', 'trend_low', 'trend_high', 'recent_price'])
    
    # Load all files and filter for this ticker
    ep_data = []
    for file in ep_files:
        df = pd.read_csv(file)
        ticker_data = df[df['ticker'] == p_sym]
        if not ticker_data.empty:
            row = ticker_data.iloc[0]
            ep_data.append({
                'date': pd.to_datetime(row['report_date']),
                'trend_low': row['trend_low'],
                'trend_high': row['trend_high'],
                'recent_price': row['recent_price']
            })
    
    if not ep_data:
        print(f"⚠️  No EP data found for {p_sym}")
        return pd.DataFrame(columns=['date', 'trend_low', 'trend_high', 'recent_price'])
    
    # Create DataFrame and sort by date
    ep_df = pd.DataFrame(ep_data)
    ep_df = ep_df.sort_values('date').reset_index(drop=True)
    
    # Create daily date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    daily_df = pd.DataFrame({'date': date_range})
    
    # Forward-fill EP weekly values to daily
    # For each date in daily range, use the most recent EP value
    daily_df['trend_low'] = None
    daily_df['trend_high'] = None
    daily_df['recent_price'] = None
    
    for idx, daily_date in enumerate(daily_df['date']):
        # Find most recent EP value on or before this date
        valid_ep = ep_df[ep_df['date'] <= daily_date]
        if not valid_ep.empty:
            latest_ep = valid_ep.iloc[-1]
            daily_df.loc[idx, 'trend_low'] = latest_ep['trend_low']
            daily_df.loc[idx, 'trend_high'] = latest_ep['trend_high']
            daily_df.loc[idx, 'recent_price'] = latest_ep['recent_price']
    
    return daily_df


def load_rr_time_series_with_translation(p_sym: str, mapping_df: pd.DataFrame, 
                                        p_current_series: Optional[pd.Series] = None) -> pd.DataFrame:
    """
    Load Risk Range time series for a ticker, translated to p_sym coordinates.
    
    Args:
        p_sym: Portfolio symbol (e.g., "AAAU")
        mapping_df: DataFrame with p_sym to r_sym mappings
        p_current_series: Series with date index and p_current values (for translation)
        
    Returns:
        DataFrame with columns: date, p_trade_low, p_trade_high, prev_close
    """
    # Find r_sym for this p_sym
    if mapping_df.empty or 'p_sym' not in mapping_df.columns:
        print(f"⚠️  Invalid mapping DataFrame for {p_sym}")
        return pd.DataFrame(columns=['date', 'p_trade_low', 'p_trade_high', 'prev_close'])
    
    mapping = mapping_df[mapping_df['p_sym'] == p_sym]
    if mapping.empty:
        print(f"⚠️  No mapping found for {p_sym}")
        return pd.DataFrame(columns=['date', 'p_trade_low', 'p_trade_high', 'prev_close'])
    
    mapping_row = mapping.iloc[0]
    r_sym = mapping_row['r_sym']
    is_inverted = mapping_row.get('inverted', False) if 'inverted' in mapping_row else False
    
    # Load all RR data
    rr_df = load_all_risk_range_data()
    
    # Filter for r_sym
    rr_symbol = rr_df[rr_df['index'] == r_sym].copy()
    
    if rr_symbol.empty:
        print(f"⚠️  No RR data found for {r_sym} (proxy for {p_sym})")
        return pd.DataFrame(columns=['date', 'p_trade_low', 'p_trade_high', 'prev_close'])
    
    # Convert date and sort
    rr_symbol['date'] = pd.to_datetime(rr_symbol['date'])
    rr_symbol = rr_symbol.sort_values('date').reset_index(drop=True)
    
    # Translate trade ranges to p_sym coordinates
    # Formula: p_trade = p_current * (r_trade / r_current)
    # where r_current is the RR prev_close (proxy price for r_sym)
    
    rr_symbol['r_current'] = rr_symbol['prev_close']  # Use prev_close as proxy for r_current
    
    # Calculate translation factors
    mask = (rr_symbol['r_current'] > 0) & rr_symbol['buy_trade'].notna() & rr_symbol['sell_trade'].notna()
    rr_symbol.loc[mask, 'buy_factor'] = rr_symbol.loc[mask, 'buy_trade'] / rr_symbol.loc[mask, 'r_current']
    rr_symbol.loc[mask, 'sell_factor'] = rr_symbol.loc[mask, 'sell_trade'] / rr_symbol.loc[mask, 'r_current']
    
    # Initialize translated columns
    rr_symbol['p_trade_low'] = None
    rr_symbol['p_trade_high'] = None
    
    # Translate using p_current if available
    if p_current_series is not None and not p_current_series.empty:
        # Merge p_current into rr_symbol by date
        p_current_df = p_current_series.reset_index()
        p_current_df.columns = ['date', 'p_current']
        p_current_df['date'] = pd.to_datetime(p_current_df['date'])
        
        rr_symbol = pd.merge(rr_symbol, p_current_df, on='date', how='left')
        
        # Apply translation
        translation_mask = mask & rr_symbol['p_current'].notna() & (rr_symbol['p_current'] > 0)
        
        if is_inverted:
            # For inverted proxies (e.g., TLT vs UST30Y):
            # When UST30Y goes up, TLT goes down, so we flip the ranges
            # buy_trade (low yield) -> high TLT price (p_trade_high)
            # sell_trade (high yield) -> low TLT price (p_trade_low)
            rr_symbol.loc[translation_mask, 'p_trade_low'] = (
                rr_symbol.loc[translation_mask, 'p_current'] * rr_symbol.loc[translation_mask, 'sell_factor']
            )
            rr_symbol.loc[translation_mask, 'p_trade_high'] = (
                rr_symbol.loc[translation_mask, 'p_current'] * rr_symbol.loc[translation_mask, 'buy_factor']
            )
            print(f"  ✓ Applied inverted translation (flipped low/high)")
        else:
            # Normal translation
            rr_symbol.loc[translation_mask, 'p_trade_low'] = (
                rr_symbol.loc[translation_mask, 'p_current'] * rr_symbol.loc[translation_mask, 'buy_factor']
            )
            rr_symbol.loc[translation_mask, 'p_trade_high'] = (
                rr_symbol.loc[translation_mask, 'p_current'] * rr_symbol.loc[translation_mask, 'sell_factor']
            )
    
    result = pd.DataFrame({
        'date': rr_symbol['date'],
        'p_trade_low': rr_symbol['p_trade_low'],
        'p_trade_high': rr_symbol['p_trade_high'],
        'prev_close': rr_symbol['prev_close']
    })
    
    return result


def plot_cr_time_series(p_sym: str, days_back: int = 30, 
                       mapping_df: Optional[pd.DataFrame] = None,
                       save_path: Optional[Path] = None) -> plt.Figure:
    """
    Plot combo ranges time series for a single ticker.
    
    Shows:
    - Trend ranges (from EP) over time
    - Trade ranges (from RR, translated) over time
    - Price history
    
    Args:
        p_sym: Portfolio symbol to plot
        days_back: Number of days to look back (default: 100)
        mapping_df: p_sym to r_sym mapping DataFrame (loads if None)
        save_path: Optional path to save figure
        
    Returns:
        matplotlib Figure object
    """
    # Load mapping if not provided
    if mapping_df is None:
        config = load_config()
        mapping_path = Path("/Users/rk/d/downloads/hedgeye/prod/ranges/p-to-r-mapping.csv")
        if mapping_path.exists():
            mapping_df = pd.read_csv(mapping_path)
        else:
            print(f"⚠️  Mapping file not found: {mapping_path}")
            mapping_df = pd.DataFrame()
    
    # Determine date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    # Load EP time series (weekly trend ranges, forward-filled to daily)
    print(f"Loading EP trend ranges for {p_sym}...")
    ep_df = load_ep_time_series(p_sym, days_back=days_back)
    
    # Load RR time series (daily trade ranges)
    print(f"Loading RR trade ranges for {p_sym}...")
    rr_df = load_rr_time_series_with_translation(p_sym, mapping_df, p_current_series=None)
    
    # Fetch daily historical prices for the date range (no caching)
    print(f"Fetching daily prices for {p_sym}...")
    daily_prices = fetch_historical_daily_prices(p_sym, start_date, end_date)
    
    # Create p_current series from daily prices (preferred) or EP weekly prices (fallback)
    if not daily_prices.empty:
        p_current_series = daily_prices
        print(f"  Using {len(daily_prices)} daily prices from yfinance")
    elif not ep_df.empty and 'recent_price' in ep_df.columns:
        p_current_series = ep_df.set_index('date')['recent_price']
        print(f"  Using {len(p_current_series)} weekly prices from EP (fallback)")
    else:
        p_current_series = None
        print(f"  ⚠️  No price data available for translation")
    
    # Re-translate RR ranges using daily prices if available
    if p_current_series is not None and not rr_df.empty:
        print(f"Translating RR trade ranges using daily prices...")
        rr_df = load_rr_time_series_with_translation(p_sym, mapping_df, p_current_series=p_current_series)
    
    # Merge EP and RR data by date
    if not ep_df.empty and not rr_df.empty:
        merged_df = pd.merge(ep_df, rr_df, on='date', how='outer', sort=True)
    elif not ep_df.empty:
        merged_df = ep_df.copy()
        merged_df['p_trade_low'] = None
        merged_df['p_trade_high'] = None
        merged_df['prev_close'] = None
    elif not rr_df.empty:
        merged_df = rr_df.copy()
        merged_df['trend_low'] = None
        merged_df['trend_high'] = None
        merged_df['recent_price'] = None
    else:
        print(f"❌ No data found for {p_sym}")
        return plt.figure()
    
    # Sort by date and ensure date is datetime
    merged_df['date'] = pd.to_datetime(merged_df['date'])
    merged_df = merged_df.sort_values('date').reset_index(drop=True)
    
    # Add daily prices to merged dataframe
    if not daily_prices.empty:
        # Merge daily prices by date
        price_df = daily_prices.reset_index()
        price_df.columns = ['date', 'price']
        price_df['date'] = pd.to_datetime(price_df['date'])
        merged_df = pd.merge(merged_df, price_df, on='date', how='outer', sort=True)
    else:
        # Fallback to EP recent_price if no daily prices
        merged_df['price'] = merged_df['recent_price']
    
    # Sort again after merge
    merged_df = merged_df.sort_values('date').reset_index(drop=True)
    
    # Convert numeric columns to float, handling any non-numeric values
    for col in ['trend_low', 'trend_high', 'p_trade_low', 'p_trade_high', 'price', 'recent_price', 'prev_close']:
        if col in merged_df.columns:
            merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce')
    
    # Filter to last N days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    merged_df = merged_df[merged_df['date'] >= start_date]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Plot trend ranges (from EP) - shaded area
    trend_mask = merged_df['trend_low'].notna() & merged_df['trend_high'].notna()
    if trend_mask.any():
        trend_data = merged_df[trend_mask]
        ax.fill_between(trend_data['date'], 
                       trend_data['trend_low'], 
                       trend_data['trend_high'],
                       alpha=0.2, color='blue', label='Trend Range (EP)')
        ax.plot(trend_data['date'], trend_data['trend_low'], 
               color='blue', linestyle='--', linewidth=1.5, alpha=0.7, label='Trend Low')
        ax.plot(trend_data['date'], trend_data['trend_high'], 
               color='blue', linestyle='--', linewidth=1.5, alpha=0.7, label='Trend High')
    
    # Plot trade ranges (from RR, translated) - shaded area
    trade_mask = merged_df['p_trade_low'].notna() & merged_df['p_trade_high'].notna()
    if trade_mask.any():
        trade_data = merged_df[trade_mask]
        ax.fill_between(trade_data['date'], 
                       trade_data['p_trade_low'], 
                       trade_data['p_trade_high'],
                       alpha=0.2, color='green', label='Trade Range (RR, translated)')
        ax.plot(trade_data['date'], trade_data['p_trade_low'], 
               color='green', linestyle='--', linewidth=1.5, alpha=0.7, label='Trade Low')
        ax.plot(trade_data['date'], trade_data['p_trade_high'], 
               color='green', linestyle='--', linewidth=1.5, alpha=0.7, label='Trade High')
    
    # Plot price history
    price_mask = merged_df['price'].notna()
    if price_mask.any():
        price_data = merged_df[price_mask]
        ax.plot(price_data['date'], price_data['price'], 
               color='black', linewidth=2, label='Price', marker='o', markersize=3)
    
    # Formatting
    ax.set_title(f"Combo Ranges Time Series: {p_sym} (Last {days_back} Days)", 
                fontsize=16, fontweight='bold')
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Price ($)", fontsize=12)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Format dates on x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=7))  # Weekly ticks
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"💾 Saved plot to: {save_path}")
    
    return fig


def plot_cr_time_series_test(tickers: list, days_back: int = 30, output_dir: Optional[Path] = None):
    """
    Test plotting function with 1-2 tickers.
    
    Args:
        tickers: List of tickers to plot
        days_back: Number of days to look back
        output_dir: Directory to save plots
    """
    # Load mapping
    mapping_path = Path("/Users/rk/d/downloads/hedgeye/prod/ranges/p-to-r-mapping.csv")
    if mapping_path.exists():
        mapping_df = pd.read_csv(mapping_path)
    else:
        print(f"⚠️  Mapping file not found: {mapping_path}")
        mapping_df = pd.DataFrame()
    
    print(f"🎨 Testing CR time-series plots for {len(tickers)} tickers: {tickers}")
    
    for ticker in tickers:
        print(f"\n  Plotting {ticker}...")
        fig = plot_cr_time_series(ticker, days_back=days_back, mapping_df=mapping_df)
        
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            save_path = output_dir / f"cr_timeseries_{ticker}.png"
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"  💾 Saved: {save_path.name}")
        else:
            plt.show()
        
        plt.close(fig)
    
    print(f"\n✅ Test plotting complete!")


def get_all_ep_tickers() -> List[str]:
    """
    Get all unique tickers from EP weekly CSVs.
    
    Returns:
        Sorted list of unique ticker symbols
    """
    config = load_config()
    ep_csv_dir = Path(config["paths"]["etf_pro_csv_dir"])
    
    ep_files = sorted(ep_csv_dir.glob("etf_pro_weekly_*.csv"))
    if not ep_files:
        return []
    
    all_tickers = set()
    for file in ep_files:
        df = pd.read_csv(file)
        if 'ticker' in df.columns:
            all_tickers.update(df['ticker'].unique())
    
    return sorted(list(all_tickers))


def generate_all_cr_time_series_plots(
    days_back: int = 30,
    output_dir: Optional[Path] = None,
    tickers_filter: Optional[List[str]] = None,
    require_rr_data: bool = False
) -> Dict[str, Any]:
    """
    Generate CR time-series plots for all tickers with EP data.
    
    Args:
        days_back: Number of days to look back (default: 30)
        output_dir: Output directory for plots (default: prod/ranges/plots/cr_timeseries/)
        tickers_filter: Optional list to filter specific tickers
        require_rr_data: If True, skip tickers without RR data (default: False)
        
    Returns:
        Dictionary with statistics
    """
    from datetime import datetime, timedelta
    
    # Set up output directory
    if output_dir is None:
        output_dir = Path("/Users/rk/d/downloads/hedgeye/prod/ranges/plots/cr_timeseries")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load mapping table
    mapping_path = Path("/Users/rk/d/downloads/hedgeye/prod/ranges/p-to-r-mapping.csv")
    if mapping_path.exists():
        mapping_df = pd.read_csv(mapping_path)
    else:
        print(f"⚠️  Mapping file not found: {mapping_path}")
        mapping_df = pd.DataFrame()
    
    # Get all tickers from EP data
    all_tickers = get_all_ep_tickers()
    if not all_tickers:
        print("❌ No tickers found in EP weekly CSVs")
        return {'total': 0, 'successful': 0, 'failed': 0, 'ep_only': 0, 'failed_list': []}
    
    # Apply filter if provided
    if tickers_filter:
        all_tickers = [t for t in all_tickers if t in tickers_filter]
    
    print(f"📊 Generating CR time-series plots for {len(all_tickers)} tickers")
    print(f"   Days back: {days_back}")
    print(f"   Output: {output_dir}")
    
    # Determine date range and pre-fetch all prices
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    print(f"\n💰 Pre-fetching prices for all tickers...")
    from syndicate.data_sources.hedgeye.price_cache import get_daily_prices
    all_prices_df = get_daily_prices(all_tickers, start_date, end_date, use_cache=True)
    print(f"   ✓ Pre-fetched prices for {all_prices_df['ticker'].nunique()} tickers")
    
    # Statistics tracking
    stats = {
        'total': len(all_tickers),
        'successful': 0,
        'failed': 0,
        'ep_only': 0,  # Has EP but no RR
        'failed_list': []
    }
    
    # Process each ticker
    print(f"\n🎨 Generating plots...")
    for i, ticker in enumerate(all_tickers, 1):
        print(f"\n[{i}/{len(all_tickers)}] {ticker}...")
        
        try:
            # Check if has RR data
            has_rr = False
            if not mapping_df.empty and 'p_sym' in mapping_df.columns:
                ticker_mapping = mapping_df[mapping_df['p_sym'] == ticker]
                if not ticker_mapping.empty and pd.notna(ticker_mapping.iloc[0]['r_sym']):
                    r_sym = ticker_mapping.iloc[0]['r_sym']
                    if r_sym and r_sym != 'no_coverage':
                        has_rr = True
            
            # Skip if require_rr_data and no RR
            if require_rr_data and not has_rr:
                print(f"  ⏭️  Skipped (no RR data, require_rr_data=True)")
                stats['ep_only'] += 1
                continue
            
            # Generate plot
            save_path = output_dir / f"cr_timeseries_{ticker}.png"
            fig = plot_cr_time_series(
                ticker, 
                days_back=days_back, 
                mapping_df=mapping_df,
                save_path=save_path
            )
            
            plt.close(fig)
            
            # Track statistics
            if not has_rr:
                stats['ep_only'] += 1
                print(f"  ✅ Saved (EP-only, no RR data)")
            else:
                print(f"  ✅ Saved (EP + RR)")
            stats['successful'] += 1
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            stats['failed'] += 1
            stats['failed_list'].append({
                'ticker': ticker,
                'error': str(e)
            })
            continue
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"📊 Plot Generation Summary")
    print(f"{'='*70}")
    print(f"  Total tickers: {stats['total']}")
    print(f"  ✅ Successful: {stats['successful']}")
    print(f"     - With RR data: {stats['successful'] - stats['ep_only']}")
    print(f"     - EP-only: {stats['ep_only']}")
    print(f"  ❌ Failed: {stats['failed']}")
    print(f"  📁 Output: {output_dir}")
    
    if stats['failed_list']:
        print(f"\n  Failed tickers:")
        for item in stats['failed_list']:
            print(f"    - {item['ticker']}: {item['error']}")
    
    return stats


if __name__ == "__main__":
    # Test with multiple tickers (excluding BUXX - money market, not interesting)
    # Limited to 30 days for debugging
    test_tickers = ["AAAU", "QQQ", "TLT", "UUP"]  # Gold, Nasdaq, Treasuries, Dollar
    config = load_config()
    output_dir = Path("/Users/rk/d/downloads/hedgeye/prod/ranges/plots/cr_timeseries_test")
    
    plot_cr_time_series_test(test_tickers, days_back=30, output_dir=output_dir)

