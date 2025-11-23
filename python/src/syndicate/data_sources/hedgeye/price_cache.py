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
from typing import List, Optional, Union
import yfinance as yf
from syndicate.data_sources.hedgeye.config_loader import load_config
from syndicate.data_sources.hedgeye.price_utils import (
    is_market_closed_et,
    is_weekend_date,
    should_cache_today,
)


def get_cache_path() -> Path:
    """Get path to price cache CSV file."""
    config = load_config()
    cache_dir = Path(config["paths"]["cache_dir"])
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "daily_prices_cache.csv"


def get_today_date() -> datetime:
    """Get today's date as timezone-naive datetime."""
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


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
    # Normalize dates immediately (remove timezone and time components)
    needed['date'] = pd.to_datetime(needed['date']).dt.normalize()
    
    if use_cache:
        # Load cache
        cache_df = load_cache()
        
        # Get today's date for filtering
        today = get_today_date()
        
        if not cache_df.empty:
            # Ensure cache dates are datetime and normalized
            cache_df['date'] = pd.to_datetime(cache_df['date']).dt.normalize()
            # needed dates are already normalized above
            
            # If markets are still open (weekday before 4pm ET), exclude today's cached prices
            # (force fresh fetch for today)
            # Weekend dates are OK to use from cache (markets closed all day)
            if not should_cache_today():
                cache_df = cache_df[cache_df['date'] != today]
            
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
            # Normalize dates immediately after fetching (remove timezone and time components)
            fetched_df['date'] = pd.to_datetime(fetched_df['date']).dt.normalize()
            
            # Normalize start/end dates for comparison
            start_date_norm = pd.to_datetime(start_date).normalize()
            end_date_norm = pd.to_datetime(end_date).normalize()
            
            # Filter fetched to only dates within our requested range
            fetched_df = fetched_df[
                (fetched_df['date'] >= start_date_norm) & 
                (fetched_df['date'] <= end_date_norm)
            ]
            
            # Filter to only missing dates (avoid duplicates with cache)
            # missing dates are already normalized (from needed)
            if not missing.empty:
                fetched_df = fetched_df.merge(missing, on=['date', 'ticker'], how='inner')
            
            # Combine cached and fetched (no duplicates since we filtered fetched_df)
            if not cached.empty:
                result_df = pd.concat([cached, fetched_df], ignore_index=True)
            else:
                result_df = fetched_df
            
            # Update cache with new prices (only if markets are closed for today's prices)
            if use_cache and not fetched_df.empty:
                today = get_today_date()
                
                # Normalize dates for comparison
                fetched_df['date'] = pd.to_datetime(fetched_df['date']).dt.normalize()
                
                # Separate today's prices from historical prices
                today_prices = fetched_df[fetched_df['date'] == today].copy()
                historical_prices = fetched_df[fetched_df['date'] != today].copy()
                
                # Always cache historical prices
                prices_to_cache = historical_prices.copy() if not historical_prices.empty else pd.DataFrame(columns=['date', 'ticker', 'price'])
                
                # Only cache today's prices if markets are closed
                if not today_prices.empty:
                    if should_cache_today():
                        if prices_to_cache.empty:
                            prices_to_cache = today_prices
                        else:
                            prices_to_cache = pd.concat([prices_to_cache, today_prices], ignore_index=True)
                        print(f"  ℹ️  Markets closed - caching today's prices ({len(today_prices)} prices)")
                    else:
                        print(f"  ℹ️  Markets open - not caching today's prices ({len(today_prices)} prices)")
                
                if not prices_to_cache.empty:
                    # Reload full cache (unfiltered) to get current state
                    current_cache = load_cache()
                    
                    if not current_cache.empty:
                        # Normalize dates
                        current_cache['date'] = pd.to_datetime(current_cache['date']).dt.normalize()
                        
                        # If markets are open, remove today's prices from cache before updating
                        # (they shouldn't be there, but just in case)
                        if not should_cache_today():
                            current_cache = current_cache[current_cache['date'] != today]
                        
                        # Remove old entries for these (date, ticker) pairs and add new ones
                        prices_to_cache_idx = prices_to_cache.set_index(['date', 'ticker']).index
                        cache_idx = current_cache.set_index(['date', 'ticker']).index
                        current_cache = current_cache[~cache_idx.isin(prices_to_cache_idx)]
                        updated_cache = pd.concat([current_cache, prices_to_cache], ignore_index=True)
                    else:
                        updated_cache = prices_to_cache
                    
                    save_cache(updated_cache)
                    print(f"  ✓ Updated cache with {len(prices_to_cache)} new prices")
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


def clear_today_cache() -> None:
    """
    Clear today's prices from the cache (useful for forcing fresh prices during market hours).
    """
    today = get_today_date()
    cache_df = load_cache()
    
    if cache_df.empty:
        print(f"ℹ️  Cache is empty - nothing to clear")
        return
    
    # Count prices before
    before_count = len(cache_df)
    
    # Remove today's prices
    cache_df['date'] = pd.to_datetime(cache_df['date']).dt.normalize()
    today_prices = cache_df[cache_df['date'] == today]
    cache_df = cache_df[cache_df['date'] != today]
    
    removed_count = len(today_prices)
    
    # Save updated cache
    save_cache(cache_df)
    
    print(f"✓ Removed {removed_count} today's prices from cache ({len(cache_df)} prices remaining)")


if __name__ == "__main__":
    # Test
    start = datetime.now() - timedelta(days=30)
    end = datetime.now()
    tickers = ['AAAU', 'QQQ']
    
    print("Testing price cache...")
    prices = get_daily_prices(tickers, start, end)
    print(f"\nResult: {len(prices)} price records")
    print(prices.head(10))

