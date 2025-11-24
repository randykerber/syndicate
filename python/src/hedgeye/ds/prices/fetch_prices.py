#!/usr/bin/env python3
"""
Fetch current prices for symbols with daily caching.

Uses FMP (Financial Modeling Prep) API via he_to_fmp mapping as primary source,
with yfinance fallback for unmapped symbols.
Caches results for the day since markets are closed.

Usage:
    from fetch_prices import fetch_current_prices
    prices = fetch_current_prices(['AAAU', 'QQQ', 'GOLD'])
"""

import os
import json
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from hedgeye.config_loader import load_config
from hedgeye.fmp.price_fetcher import FMPPriceFetcher
from hedgeye.ds.prices.price_utils import (
    should_cache_today,
)

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


def get_cache_path() -> Path:
    """Get path to daily price cache file."""
    config = load_config()
    cache_dir = Path(config["paths"]["cache_dir"])
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Use today's date in cache filename
    today = datetime.now().strftime("%Y-%m-%d")
    return cache_dir / f"prices_{today}.json"


def load_price_cache(include_today: bool = None) -> Dict[str, float]:
    """
    Load cached prices for today if they exist.
    
    Args:
        include_today: If True, include today's cached prices even if market is open.
                      If False, exclude today's cached prices.
                      If None (default), auto-detect based on market close time.
    
    Returns:
        Dictionary of cached prices (excluding today if market is still open)
    """
    cache_path = get_cache_path()
    if not cache_path.exists():
        return {}
    
    with open(cache_path, 'r') as f:
        cached_prices = json.load(f)
    
    # If markets are open and we should exclude today, return empty dict
    # (effectively forcing fresh fetch for today)
    if include_today is None:
        include_today = should_cache_today()
    
    if not include_today:
        # Return empty dict to force fresh fetch (but don't delete cache file yet)
        return {}
    
    return cached_prices


def save_price_cache(prices: Dict[str, float]):
    """Save prices to daily cache."""
    cache_path = get_cache_path()
    with open(cache_path, 'w') as f:
        json.dump(prices, f, indent=2)


def load_he_to_fmp_mapping() -> pd.DataFrame:
    """Load the Hedgeye to FMP symbol mappings."""
    config = load_config()
    fmp_path = Path(config["paths"]["fmp_mapping_file"])

    if not fmp_path.exists():
        print(f"  ⚠️  FMP mapping file not found: {fmp_path}")
        return pd.DataFrame(columns=['he_symbol', 'fmp_etype', 'fmp_symbol'])

    return pd.read_csv(fmp_path)


def fetch_from_fmp_with_mapping(symbols: List[str]) -> Dict[str, float]:
    """
    Fetch prices using the he_to_fmp mapping file.

    Args:
        symbols: List of Hedgeye symbols to fetch

    Returns:
        Dictionary mapping symbol to current price
    """
    # Load mapping
    mapping_df = load_he_to_fmp_mapping()

    if mapping_df.empty:
        return {}

    # Filter to requested symbols
    symbols_to_fetch = mapping_df[mapping_df['he_symbol'].isin(symbols)]

    if symbols_to_fetch.empty:
        return {}

    # Fetch prices using FMPPriceFetcher
    fetcher = FMPPriceFetcher()
    prices = {}

    for _, row in symbols_to_fetch.iterrows():
        he_symbol = row['he_symbol']
        fmp_symbol = row['fmp_symbol']
        etype = row['fmp_etype']

        try:
            price_data = fetcher.get_latest_price(fmp_symbol, etype)
            if price_data and 'price' in price_data:
                prices[he_symbol] = price_data['price']
        except Exception as e:
            # Silently skip - will be reported as missing
            continue

    return prices


def fetch_from_fmp(symbols: List[str]) -> Dict[str, float]:
    """
    Fetch prices from Financial Modeling Prep API.

    Args:
        symbols: List of symbols to fetch

    Returns:
        Dictionary mapping symbol to current price
    """
    api_key = os.getenv('FMP_API_KEY')
    if not api_key:
        print("  ⚠️  FMP_API_KEY not set in environment")
        return {}

    prices = {}

    # FMP batch quote endpoint (max 100 symbols)
    # Split into batches if needed
    batch_size = 100
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i+batch_size]
        symbols_str = ','.join(batch)

        url = f"https://financialmodelingprep.com/api/v3/quote/{symbols_str}"
        params = {'apikey': api_key}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            for quote in data:
                symbol = quote.get('symbol')
                price = quote.get('price')
                if symbol and price is not None:
                    prices[symbol] = price

        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Error fetching batch from FMP: {e}")
            continue

    return prices


def fetch_from_yfinance(symbols: List[str]) -> Dict[str, float]:
    """
    Fetch prices from Yahoo Finance using yfinance.

    Args:
        symbols: List of symbols to fetch

    Returns:
        Dictionary mapping symbol to current price
    """
    if not YFINANCE_AVAILABLE:
        print("  ⚠️  yfinance not installed - pip install yfinance")
        return {}

    prices = {}

    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            # Get most recent price
            hist = ticker.history(period="1d")
            if not hist.empty:
                prices[symbol] = float(hist['Close'].iloc[-1])
        except Exception as e:
            # Silently skip - will report missing at end
            continue

    return prices


def fetch_current_prices(symbols: List[str], use_cache: bool = True) -> Dict[str, float]:
    """
    Fetch current prices for a list of symbols.

    Uses daily cache to avoid repeated API calls for same symbols.
    Tries FMP first, then yfinance for any missing symbols.

    Args:
        symbols: List of symbols to fetch prices for
        use_cache: Whether to use cached prices (default: True)

    Returns:
        Dictionary mapping symbol to current price
    """
    # Remove duplicates and None values
    symbols = [s for s in set(symbols) if s]

    if not symbols:
        return {}

    # Load cache (excludes today if markets are still open)
    if use_cache:
        # Don't use today's cached prices if market is still open
        include_today = should_cache_today()
        cached_prices = load_price_cache(include_today=include_today)
    else:
        cached_prices = {}

    # Identify symbols not in cache
    symbols_to_fetch = [s for s in symbols if s not in cached_prices]

    if symbols_to_fetch:
        print(f"  📊 Fetching prices for {len(symbols_to_fetch)} symbols...")

        # Try FMP with he_to_fmp mapping first (handles special symbols like GOLD, COMPQ, etc.)
        new_prices = fetch_from_fmp_with_mapping(symbols_to_fetch)
        print(f"     FMP (via mapping): {len(new_prices)} symbols")

        # Try direct FMP quote for remaining (standard stocks/ETFs)
        missing = [s for s in symbols_to_fetch if s not in new_prices]
        if missing:
            fmp_direct = fetch_from_fmp(missing)
            new_prices.update(fmp_direct)
            print(f"     FMP (direct): {len(fmp_direct)} symbols")

        # Try yfinance for remaining
        missing = [s for s in symbols_to_fetch if s not in new_prices]
        if missing and YFINANCE_AVAILABLE:
            yf_prices = fetch_from_yfinance(missing)
            new_prices.update(yf_prices)
            print(f"     Yahoo Finance: {len(yf_prices)} symbols")

        # Merge with cache
        all_prices = {**cached_prices, **new_prices}

        # Save updated cache (only if markets are closed, or if explicitly caching)
        if use_cache and new_prices:
            if should_cache_today():
                save_price_cache(all_prices)
                print(f"  ✓ Cached {len(new_prices)} total new prices")
            else:
                # Markets are open - don't cache today's prices
                # But preserve old cache if it exists
                if cached_prices:
                    save_price_cache(cached_prices)
                print(f"  ℹ️  Markets open - not caching today's prices (fetched {len(new_prices)} fresh prices)")
    else:
        print(f"  ✓ Using cached prices for all {len(symbols)} symbols")
        all_prices = cached_prices

    # Return only requested symbols
    result = {s: all_prices[s] for s in symbols if s in all_prices}

    if len(result) < len(symbols):
        missing = set(symbols) - set(result.keys())
        print(f"  ⚠️  Could not fetch prices for {len(missing)} symbols: {', '.join(sorted(missing))}")

    return result


def clear_today_cache() -> None:
    """
    Clear today's price cache file (useful for forcing fresh prices during market hours).
    """
    cache_path = get_cache_path()
    if cache_path.exists():
        cache_path.unlink()
        print(f"✓ Cleared today's price cache: {cache_path.name}")
    else:
        print(f"ℹ️  No cache file found for today: {cache_path.name}")


if __name__ == "__main__":
    # Test with a few symbols
    test_symbols = ['AAAU', 'QQQ', 'GOLD', 'SPY']
    prices = fetch_current_prices(test_symbols)

    print("\nTest Results:")
    for symbol, price in sorted(prices.items()):
        print(f"  {symbol}: ${price:,.2f}")