#!/usr/bin/env python3
"""
Shared utility functions for price fetching and caching.

This module provides common logic for:
- Market hours detection (US Eastern Time)
- Weekend date detection
- Caching decision logic (when to cache today's prices)
"""

from datetime import datetime
from typing import Optional
import pytz


def is_market_closed_et(check_date: Optional[datetime] = None) -> bool:
    """
    Check if US markets are closed for the given date/time.
    
    Markets are closed:
    - All weekend days (Saturday, Sunday) - markets closed all day
    - Weekdays before 4pm ET - markets open, don't cache
    - Weekdays after 4pm ET - markets closed, safe to cache
    
    Note: yfinance/FMP don't return prices for weekend dates (they skip non-trading days).
    This function is mainly for determining if we should cache weekday prices.
    
    Args:
        check_date: Datetime to check (default: now in ET)
    
    Returns:
        True if markets are closed (safe to cache), False otherwise
    """
    et_tz = pytz.timezone('US/Eastern')
    if check_date is None:
        now_et = datetime.now(et_tz)
    else:
        # Convert to ET if needed
        if check_date.tzinfo is None:
            now_et = et_tz.localize(check_date)
        else:
            now_et = check_date.astimezone(et_tz)
    
    # Weekend: markets closed all day (but yfinance won't return prices for these dates anyway)
    if now_et.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return True
    
    # Weekday: market closes at 4:00 PM ET
    market_close_hour = 16
    return now_et.hour >= market_close_hour


def is_weekend_date(date: datetime) -> bool:
    """
    Check if a date falls on a weekend (Saturday or Sunday).
    
    Args:
        date: Datetime to check (timezone-naive or aware)
    
    Returns:
        True if weekend, False otherwise
    """
    # Convert to ET for consistency
    et_tz = pytz.timezone('US/Eastern')
    if date.tzinfo is None:
        date_et = et_tz.localize(date)
    else:
        date_et = date.astimezone(et_tz)
    
    return date_et.weekday() >= 5  # Saturday = 5, Sunday = 6


def should_cache_today() -> bool:
    """
    Determine if today's prices should be cached.
    
    Returns:
        True if markets are closed (weekend or after 4pm ET on weekdays), False otherwise
    """
    return is_market_closed_et()

