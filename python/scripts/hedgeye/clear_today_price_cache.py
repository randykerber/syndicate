#!/usr/bin/env python3
"""
Clear today's prices from both price caches.

This forces fresh price fetches for the current day, useful when markets are open
and you want the latest prices instead of cached values from earlier in the day.

Usage:
    uv run python scripts/hedgeye/clear_today_price_cache.py
"""

from hedgeye.fetch_prices import clear_today_cache as clear_daily_cache
from hedgeye.price_cache import clear_today_cache as clear_historical_cache

def main():
    """Clear today's prices from both cache systems."""
    print("=" * 70)
    print("Clearing Today's Price Cache")
    print("=" * 70)
    print()
    
    print("1. Clearing daily price cache (fetch_prices.py)...")
    clear_daily_cache()
    
    print()
    print("2. Clearing today's prices from historical cache (price_cache.py)...")
    clear_historical_cache()
    
    print()
    print("=" * 70)
    print("✅ Cache cleanup complete!")
    print("=" * 70)
    print()
    print("ℹ️  Next pipeline run will fetch fresh prices for today.")

if __name__ == "__main__":
    main()

