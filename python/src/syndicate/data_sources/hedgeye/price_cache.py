#!/usr/bin/env python3
"""
Simple price cache for daily closing prices.

Cache format: CSV with columns: date, ticker, price
- One row per (date, ticker) combination
- Check cache first, then fetch from API if missing
- Batch fetch all missing prices at once

Usage:
    from syndicate.data_sources.hedgeye.price_cache import get_daily_prices
    
    # Get prices for multiple tickers over date range
    prices_df = get_daily_prices(['AAAU', 'QQQ'], start_date, end_date)
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
import yfinance as yf


def get_cache_path() -> Path:
    """Get path to price cache CSV file."""
    cache_dir = Path("/Users/rk/d/downloads/hedgeye/prod/all/cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "daily_prices_cache.csv"


def load_cache() -> pd.DataFrame:
    """Load price cache from CSV."""
    cache_path = get_cache_path()
    if cache_path.exists():
        df = pd.read_csv(cache_path)
        df['date'] = pd.to_datetime(df['date'])
        return df
    return pd.DataFrame(columns=['date', 'ticker', 'price'])


def save_cache(cache_df: pd.DataFrame):
    """Save price cache to CSV."""
    cache_path = get_cache_path()
    cache_df = cache_df.sort_values(['date', 'ticker']).reset_index(drop=True)
    cache_df.to_csv(cache_path, index=False)


def fetch_prices_from_yfinance(tickers: List[str], start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """
    Fetch daily closing prices from yfinance for multiple tickers.
    
    Args:
        tickers: List of ticker symbols
        start_date: Start date
        end_date: End date
        
    Returns:
        DataFrame with columns: date, ticker, price
    """
    results = []
    
    for ticker in tickers:
        try:
            yf_ticker = yf.Ticker(ticker)
            hist = yf_ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                print(f"  ⚠️  No data for {ticker}")
                continue
            
            # Extract closing prices
            for date, row in hist.iterrows():
                # Convert date to date-only (remove time and timezone)
                if hasattr(date, 'tz_localize'):
                    date_only = pd.to_datetime(date.tz_localize(None).date())
                else:
                    date_only = pd.to_datetime(date.date())
                results.append({
                    'date': date_only,
                    'ticker': ticker,
                    'price': float(row['Close'])
                })
            
            print(f"  ✓ Fetched {len(hist)} days for {ticker}")
            
        except Exception as e:
            print(f"  ⚠️  Error fetching {ticker}: {e}")
            continue
    
    if not results:
        return pd.DataFrame(columns=['date', 'ticker', 'price'])
    
    return pd.DataFrame(results)


def get_daily_prices(tickers: List[str], start_date: datetime, end_date: datetime, 
                     use_cache: bool = True) -> pd.DataFrame:
    """
    Get daily closing prices for tickers over date range.
    
    Checks cache first, then fetches missing prices from yfinance.
    Updates cache with newly fetched prices.
    
    Args:
        tickers: List of ticker symbols
        start_date: Start date
        end_date: End date
        use_cache: Whether to use cache (default: True)
        
    Returns:
        DataFrame with columns: date, ticker, price
    """
    # Generate all (date, ticker) combinations we need
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    needed = pd.DataFrame([
        {'date': date, 'ticker': ticker}
        for date in date_range
        for ticker in tickers
    ])
    
    if use_cache:
        # Load cache
        cache_df = load_cache()
        
        if not cache_df.empty:
            # Ensure dates are datetime and normalized
            cache_df['date'] = pd.to_datetime(cache_df['date']).dt.normalize()
            needed['date'] = pd.to_datetime(needed['date']).dt.normalize()
            
            # Find what we have in cache
            merged = needed.merge(cache_df, on=['date', 'ticker'], how='left')
            cached = merged[merged['price'].notna()].copy()
            missing = merged[merged['price'].isna()][['date', 'ticker']].copy()
            
            print(f"  Cache: {len(cached)} prices found, {len(missing)} missing")
        else:
            cached = pd.DataFrame(columns=['date', 'ticker', 'price'])
            missing = needed.copy()
            print(f"  Cache: empty, fetching {len(missing)} prices")
    else:
        cached = pd.DataFrame(columns=['date', 'ticker', 'price'])
        missing = needed
        print(f"  Cache: disabled, fetching {len(missing)} prices")
    
    # Fetch missing prices
    if not missing.empty:
        # Group by ticker to batch fetch
        unique_tickers = missing['ticker'].unique().tolist()
        fetched_df = fetch_prices_from_yfinance(unique_tickers, start_date, end_date)
        
        if not fetched_df.empty:
            # Filter fetched to only dates within our requested range
            fetched_df = fetched_df[
                (fetched_df['date'] >= start_date) & 
                (fetched_df['date'] <= end_date)
            ]
            
            # Filter to only missing dates (avoid duplicates with cache)
            if not missing.empty:
                fetched_df = fetched_df.merge(missing, on=['date', 'ticker'], how='inner')
            
            # Combine cached and fetched (no duplicates since we filtered fetched_df)
            if not cached.empty:
                result_df = pd.concat([cached, fetched_df], ignore_index=True)
            else:
                result_df = fetched_df
            
            # Update cache with new prices
            if use_cache and not fetched_df.empty:
                if not cache_df.empty:
                    # Remove old entries for these (date, ticker) pairs and add new ones
                    # Create index for comparison
                    fetched_idx = fetched_df.set_index(['date', 'ticker']).index
                    cache_idx = cache_df.set_index(['date', 'ticker']).index
                    cache_df = cache_df[~cache_idx.isin(fetched_idx)]
                    updated_cache = pd.concat([cache_df, fetched_df], ignore_index=True)
                else:
                    updated_cache = fetched_df
                
                save_cache(updated_cache)
                print(f"  ✓ Updated cache with {len(fetched_df)} new prices")
        else:
            result_df = cached if not cached.empty else pd.DataFrame(columns=['date', 'ticker', 'price'])
    else:
        result_df = cached if not cached.empty else pd.DataFrame(columns=['date', 'ticker', 'price'])
        print(f"  ✓ All prices from cache")
    
    # Filter to requested date range and sort
    result_df = result_df[
        (result_df['date'] >= start_date) & 
        (result_df['date'] <= end_date)
    ].sort_values(['date', 'ticker']).reset_index(drop=True)
    
    return result_df


if __name__ == "__main__":
    # Test
    start = datetime.now() - timedelta(days=30)
    end = datetime.now()
    tickers = ['AAAU', 'QQQ']
    
    print("Testing price cache...")
    prices = get_daily_prices(tickers, start, end)
    print(f"\nResult: {len(prices)} price records")
    print(prices.head(10))

