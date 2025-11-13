#!/usr/bin/env python3
"""
Yahoo Finance fallback for commodity symbols that fail on FMP.
Used as a last resort to avoid rate limits on Yahoo.
"""

import yfinance as yf
from typing import Optional, Dict, Any
from datetime import datetime
import pandas as pd

# Yahoo symbol mappings for problematic FMP symbols
YAHOO_FALLBACK_SYMBOLS = {
    'HGUSD': 'HG=F',  # Copper
    'NGUSD': 'NG=F',  # Natural Gas
    'CLUSD': 'CL=F',  # WTI Crude Oil
    'ZBUSD': 'ZB=F',  # 30-Year Treasury Bond Futures (if needed)
    'ZNUSD': 'ZN=F',  # 10-Year Treasury Note Futures (if needed)
}

def get_yahoo_price(fmp_symbol: str, latest: bool = True) -> Optional[Dict[str, Any]]:
    """
    Get price from Yahoo Finance for symbols that fail on FMP.
    
    Args:
        fmp_symbol: The FMP symbol that failed (e.g., 'HGUSD')
        latest: Whether to get latest price (True) or historical (False)
        
    Returns:
        Dict with price data or None if failed
    """
    if fmp_symbol not in YAHOO_FALLBACK_SYMBOLS:
        return None
    
    yahoo_symbol = YAHOO_FALLBACK_SYMBOLS[fmp_symbol]
    
    try:
        ticker = yf.Ticker(yahoo_symbol)
        
        if latest:
            # Get latest price (1 day history)
            data = ticker.history(period='1d')
            if data.empty:
                return None
            
            latest_price = data['Close'].iloc[-1]
            latest_date = data.index[-1].strftime('%Y-%m-%d')
            
            return {
                'symbol': fmp_symbol,
                'price': float(latest_price),
                'date': latest_date,
                'source': 'yahoo_fallback'
            }
        else:
            # For historical data, could implement if needed
            return None
            
    except Exception as e:
        print(f"Yahoo fallback failed for {fmp_symbol} -> {yahoo_symbol}: {e}")
        return None

def is_yahoo_fallback_symbol(fmp_symbol: str) -> bool:
    """Check if symbol should use Yahoo fallback."""
    return fmp_symbol in YAHOO_FALLBACK_SYMBOLS

def get_yahoo_fallback_symbols() -> Dict[str, str]:
    """Get all Yahoo fallback symbol mappings."""
    return YAHOO_FALLBACK_SYMBOLS.copy()