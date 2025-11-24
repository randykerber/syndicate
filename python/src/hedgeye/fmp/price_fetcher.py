#!/usr/bin/env python3
"""
FMP (Financial Modeling Prep) price fetching functions.
Supports getting historical closing prices and latest prices by entity type.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
from pathlib import Path
from hedgeye.yahoo.yahoo_fallback import get_yahoo_price, is_yahoo_fallback_symbol

class FMPPriceFetcher:
    """
    Fetches price data from Financial Modeling Prep API.
    
    Supports different entity types:
    - stocks: Individual stock symbols (AAPL, MSFT, etc.)
    - etfs: Exchange traded funds (SPY, QQQ, etc.)
    - indexes: Market indexes (^SPX, ^VIX, etc.)
    - forex: Currency pairs (EURUSD, GBPUSD, etc.)
    - commodities: Commodity futures (GCUSD, CLUSD, etc.)
    - cryptocurrencies: Crypto pairs (BTCUSD, ETHUSD, etc.)
    - treasury: US Treasury rates (year2, year10, year30, etc.)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with FMP API key."""
        self.api_key = api_key or self._get_api_key()
        self.base_url = "https://financialmodelingprep.com/api/v3"
        self.session = requests.Session()
        
    def _get_api_key(self) -> str:
        """Get API key from environment or config."""
        # Try environment variable first
        api_key = os.getenv('FMP_API_KEY')
        if api_key:
            return api_key
            
        # Try config file
        config_file = Path.home() / '.fmp_api_key'
        if config_file.exists():
            return config_file.read_text().strip()
            
        raise ValueError(
            "FMP API key not found. Set FMP_API_KEY environment variable or "
            "create ~/.fmp_api_key file with your API key"
        )
    
    def get_latest_price(self, symbol: str, etype: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest/current price for a symbol.
        
        Args:
            symbol: FMP symbol (e.g., 'AAPL', 'EURUSD', '^SPX', 'year10')
            etype: Entity type ('stocks', 'forex', 'indexes', 'treasury', etc.)
            
        Returns:
            Dict with price info or None if failed
        """
        try:
            endpoint = self._get_latest_price_endpoint(etype)
            url = f"{self.base_url}{endpoint}"
            
            params = {'apikey': self.api_key}
            
            if etype in ['stocks', 'etfs']:
                # For stocks/ETFs, append symbol to URL
                url = f"{url}/{symbol}"
            elif etype == 'forex':
                # Forex uses different endpoint structure
                url = f"{self.base_url}/fx/{symbol}"
            elif etype == 'indexes':
                # Indexes may need special handling
                url = f"{self.base_url}/quote-short/{symbol}"
            elif etype in ['commodities', 'cryptocurrencies']:
                # Commodities and crypto use stable quote-short endpoint
                url = f"https://financialmodelingprep.com/stable/quote-short"
                params['symbol'] = symbol
            elif etype == 'treasury':
                # Treasury rates use stable endpoint
                url = "https://financialmodelingprep.com/stable/treasury-rates"
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
            
            if isinstance(data, dict):
                # Special handling for treasury rates
                if etype == 'treasury':
                    rate_value = self._extract_treasury_rate(data, symbol)
                    if rate_value is not None:
                        return {
                            'symbol': symbol,
                            'price': rate_value,
                            'timestamp': self._extract_timestamp(data, etype),
                            'etype': etype
                        }
                else:
                    return {
                        'symbol': symbol,
                        'price': self._extract_price(data, etype),
                        'timestamp': self._extract_timestamp(data, etype),
                        'etype': etype
                    }
                
        except Exception as e:
            print(f"Error fetching latest price for {symbol} ({etype}): {e}")
            
            # Try Yahoo Finance fallback for specific symbols
            if is_yahoo_fallback_symbol(symbol):
                print(f"Trying Yahoo Finance fallback for {symbol}...")
                yahoo_result = get_yahoo_price(symbol, latest=True)
                if yahoo_result:
                    print(f"✅ Yahoo fallback successful for {symbol}: ${yahoo_result['price']:.2f}")
                    return yahoo_result
                else:
                    print(f"❌ Yahoo fallback also failed for {symbol}")
            
        return None
    
    def get_historical_price(self, symbol: str, etype: str, date: str) -> Optional[Dict[str, Any]]:
        """
        Get historical closing price for a specific date.
        
        Args:
            symbol: FMP symbol
            etype: Entity type
            date: Date string in YYYY-MM-DD format
            
        Returns:
            Dict with price info or None if failed
        """
        try:
            # Convert date to proper format
            target_date = pd.to_datetime(date).strftime('%Y-%m-%d')
            
            # Get historical data (last 30 days to ensure we have the date)
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            endpoint = self._get_historical_endpoint(etype)
            url = f"{self.base_url}{endpoint}"
            
            params = {
                'apikey': self.api_key,
                'from': start_date,
                'to': end_date
            }
            
            if etype in ['stocks', 'etfs', 'indexes']:
                url = f"{url}/{symbol}"
            elif etype in ['forex', 'commodities', 'cryptocurrencies']:
                url = f"{self.base_url}/historical-chart/1day/{symbol}"
            elif etype == 'treasury':
                # Treasury rates use stable endpoint
                url = "https://financialmodelingprep.com/stable/treasury-rates"
                # For treasury, we'll get current rates (historical treasury rates might not be available)
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Find the specific date
            if etype == 'treasury':
                # Treasury rates: return current rates (historical may not be available)
                if isinstance(data, list) and len(data) > 0:
                    data = data[0]
                if isinstance(data, dict):
                    rate_value = self._extract_treasury_rate(data, symbol)
                    if rate_value is not None:
                        return {
                            'symbol': symbol,
                            'date': target_date,
                            'price': rate_value,
                            'etype': etype
                        }
            elif isinstance(data, list):
                for item in data:
                    item_date = self._extract_date(item, etype)
                    if item_date == target_date:
                        return {
                            'symbol': symbol,
                            'date': target_date,
                            'price': self._extract_historical_price(item, etype),
                            'etype': etype
                        }
                        
        except Exception as e:
            print(f"Error fetching historical price for {symbol} on {date}: {e}")
            
        return None
    
    def _get_latest_price_endpoint(self, etype: str) -> str:
        """Get the appropriate endpoint for latest prices by entity type."""
        endpoints = {
            'stocks': '/quote-short',
            'etfs': '/quote-short', 
            'indexes': '/quote-short',
            'forex': '/fx',
            'commodities': '/fx',
            'cryptocurrencies': '/fx',
            'treasury': '/stable/treasury-rates'
        }
        return endpoints.get(etype, '/quote-short')
    
    def _get_historical_endpoint(self, etype: str) -> str:
        """Get the appropriate endpoint for historical prices by entity type."""
        endpoints = {
            'stocks': '/historical-price-full',
            'etfs': '/historical-price-full',
            'indexes': '/historical-price-full',
            'forex': '/historical-chart/1day',
            'commodities': '/historical-chart/1day', 
            'cryptocurrencies': '/historical-chart/1day',
            'treasury': '/stable/treasury-rates'
        }
        return endpoints.get(etype, '/historical-price-full')
    
    def _extract_price(self, data: Dict, etype: str) -> Optional[float]:
        """Extract current price from API response."""
        price_fields = ['price', 'close', 'last', 'ask', 'bid']
        
        for field in price_fields:
            if field in data and data[field] is not None:
                try:
                    return float(data[field])
                except (ValueError, TypeError):
                    continue
                    
        return None
    
    def _extract_historical_price(self, data: Dict, etype: str) -> Optional[float]:
        """Extract historical closing price from API response."""
        if 'close' in data:
            try:
                return float(data['close'])
            except (ValueError, TypeError):
                pass
                
        return self._extract_price(data, etype)
    
    def _extract_timestamp(self, data: Dict, etype: str) -> Optional[str]:
        """Extract timestamp from API response."""
        timestamp_fields = ['timestamp', 'lastUpdated', 'date']
        
        for field in timestamp_fields:
            if field in data and data[field] is not None:
                return str(data[field])
                
        return datetime.now().isoformat()
    
    def _extract_date(self, data: Dict, etype: str) -> Optional[str]:
        """Extract date from historical data response."""
        if 'date' in data:
            date_str = str(data['date'])
            # Handle datetime format: '2025-06-20 00:00:00' -> '2025-06-20'
            if ' ' in date_str:
                date_str = date_str.split(' ')[0]
            return date_str
        return None
    
    def _extract_treasury_rate(self, data: Dict, symbol: str) -> Optional[float]:
        """
        Extract treasury rate from FMP treasury rates response.
        
        Args:
            data: Treasury rates API response
            symbol: Treasury symbol (year2, year10, year30, etc.)
            
        Returns:
            Treasury rate as float or None if not found
        """
        try:
            # FMP treasury response format: {"date": "2024-02-29", "year2": 4.64, "year10": 4.25, "year30": 4.38}
            if symbol in data and data[symbol] is not None:
                return float(data[symbol])
            
            # Handle alternative symbol names
            symbol_mapping = {
                'year2': ['year2', 'month24'],
                'year10': ['year10'], 
                'year30': ['year30']
            }
            
            for mapped_symbol in symbol_mapping.get(symbol, [symbol]):
                if mapped_symbol in data and data[mapped_symbol] is not None:
                    return float(data[mapped_symbol])
                    
        except (ValueError, TypeError, KeyError) as e:
            print(f"Error extracting treasury rate for {symbol}: {e}")
            
        return None

# Convenience functions
def get_latest_price(symbol: str, etype: str, api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Convenience function to get latest price.
    
    Example:
        price = get_latest_price('AAPL', 'stocks')
        print(f"AAPL current price: ${price['price']}")
    """
    fetcher = FMPPriceFetcher(api_key)
    return fetcher.get_latest_price(symbol, etype)

def get_historical_price(symbol: str, etype: str, date: str, api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Convenience function to get historical price.
    
    Example:
        price = get_historical_price('AAPL', 'stocks', '2025-06-20')
        print(f"AAPL price on 2025-06-20: ${price['price']}")
    """
    fetcher = FMPPriceFetcher(api_key)
    return fetcher.get_historical_price(symbol, etype, date)

def get_prices_for_symbols(symbols_df: pd.DataFrame, latest: bool = True, date: Optional[str] = None) -> pd.DataFrame:
    """
    Get prices for multiple symbols from mapping DataFrame.
    
    Args:
        symbols_df: DataFrame with columns ['he_symbol', 'fmp_etype', 'fmp_symbol']
        latest: If True, get latest prices; if False, get historical for date
        date: Date string for historical prices (required if latest=False)
        
    Returns:
        DataFrame with price information
    """
    fetcher = FMPPriceFetcher()
    results = []
    
    for _, row in symbols_df.iterrows():
        he_symbol = row['he_symbol']
        fmp_symbol = row['fmp_symbol']
        etype = row['fmp_etype']
        
        if latest:
            price_data = fetcher.get_latest_price(fmp_symbol, etype)
        else:
            if not date:
                raise ValueError("Date required for historical prices")
            price_data = fetcher.get_historical_price(fmp_symbol, etype, date)
        
        if price_data:
            results.append({
                'he_symbol': he_symbol,
                'fmp_symbol': fmp_symbol,
                'fmp_etype': etype,
                'price': price_data['price'],
                'timestamp': price_data.get('timestamp', ''),
                'date': price_data.get('date', date if not latest else '')
            })
        else:
            print(f"Failed to get price for {he_symbol} ({fmp_symbol})")
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    # Test the functions
    print("Testing FMP price fetcher...")
    
    # Test with a few symbols
    test_cases = [
        ('AAPL', 'stocks'),
        ('EURUSD', 'forex'),
        ('^SPX', 'indexes')
    ]
    
    for symbol, etype in test_cases:
        print(f"\nTesting {symbol} ({etype}):")
        
        # Latest price
        latest = get_latest_price(symbol, etype)
        if latest:
            print(f"  Latest: ${latest['price']}")
        
        # Historical price (yesterday)
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        historical = get_historical_price(symbol, etype, yesterday)
        if historical:
            print(f"  {yesterday}: ${historical['price']}")