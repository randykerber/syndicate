#!/usr/bin/env python3
"""
Create final Hedgeye to FMP symbol mapping table.

Generates a clean 3-column mapping table:
- he_symbol: Hedgeye symbol
- fmp_etype: FMP entity type (stocks, etfs, forex, commodities, indexes, cryptocurrencies)
- fmp_symbol: FMP symbol in that entity type
"""

import pandas as pd
from pathlib import Path
from hedgeye_kb.config_loader import load_config
from .load_entities import load_fmp_entities

def get_exact_matches():
    """Get exact matches from the original matching process"""
    # Load Hedgeye data
    config = load_config()
    hedgeye_file = Path(config["paths"]["combined_csv_output_dir"]) / "combined_risk_range.csv"
    
    if not hedgeye_file.exists():
        print(f"Hedgeye data file not found: {hedgeye_file}")
        return []
    
    hedgeye_df = pd.read_csv(hedgeye_file)
    hedgeye_symbols = hedgeye_df['index'].unique()
    
    # Load FMP entities
    stocks = load_fmp_entities("stocks")
    etfs = load_fmp_entities("etfs")
    indexes = load_fmp_entities("indexes")
    cryptocurrencies = load_fmp_entities("cryptocurrencies")
    
    exact_matches = []
    
    # Check stocks
    for symbol in hedgeye_symbols:
        match = stocks[stocks['symbol'] == symbol]
        if not match.empty:
            exact_matches.append({
                'he_symbol': symbol,
                'fmp_etype': 'stocks',
                'fmp_symbol': symbol
            })
            continue
    
    # Check ETFs
    for symbol in hedgeye_symbols:
        match = etfs[etfs['symbol'] == symbol]
        if not match.empty:
            exact_matches.append({
                'he_symbol': symbol,
                'fmp_etype': 'etfs',
                'fmp_symbol': symbol
            })
            continue
    
    # Check indexes
    for symbol in hedgeye_symbols:
        match = indexes[indexes['symbol'] == symbol]
        if not match.empty:
            exact_matches.append({
                'he_symbol': symbol,
                'fmp_etype': 'indexes',
                'fmp_symbol': symbol
            })
            continue
    
    # Check cryptocurrencies
    for symbol in hedgeye_symbols:
        match = cryptocurrencies[cryptocurrencies['symbol'] == symbol]
        if not match.empty:
            exact_matches.append({
                'he_symbol': symbol,
                'fmp_etype': 'cryptocurrencies',
                'fmp_symbol': symbol
            })
            continue
    
    return exact_matches

def get_manual_matches():
    """Get manual matches from our tracking process"""
    manual_matches = [
        # Cryptocurrencies
        {'he_symbol': 'BITCOIN', 'fmp_etype': 'cryptocurrencies', 'fmp_symbol': 'BTCUSD'},
        {'he_symbol': 'Bitcoin', 'fmp_etype': 'cryptocurrencies', 'fmp_symbol': 'BTCUSD'},
        
        # Commodities
        {'he_symbol': 'BRENT', 'fmp_etype': 'commodities', 'fmp_symbol': 'BZUSD'},
        {'he_symbol': 'COPPER', 'fmp_etype': 'commodities', 'fmp_symbol': 'HGUSD'},
        {'he_symbol': 'Copper', 'fmp_etype': 'commodities', 'fmp_symbol': 'HGUSD'},
        {'he_symbol': 'GOLD', 'fmp_etype': 'commodities', 'fmp_symbol': 'GCUSD'},
        {'he_symbol': 'OIL', 'fmp_etype': 'commodities', 'fmp_symbol': 'CLUSD'},
        {'he_symbol': 'SILVER', 'fmp_etype': 'commodities', 'fmp_symbol': 'SIUSD'},
        {'he_symbol': 'ZN', 'fmp_etype': 'commodities', 'fmp_symbol': 'ZNUSD'},
        {'he_symbol': 'ZB', 'fmp_etype': 'commodities', 'fmp_symbol': 'ZBUSD'},
        
        # Indexes
        {'he_symbol': 'BSE', 'fmp_etype': 'indexes', 'fmp_symbol': '^BSESN'},
        {'he_symbol': 'COMPQ', 'fmp_etype': 'indexes', 'fmp_symbol': '^IXIC'},
        {'he_symbol': 'NIKKEI', 'fmp_etype': 'indexes', 'fmp_symbol': '^N225'},
        {'he_symbol': 'SPX', 'fmp_etype': 'indexes', 'fmp_symbol': '^SPX'},
        {'he_symbol': 'VIX', 'fmp_etype': 'indexes', 'fmp_symbol': '^VIX'},
        
        # ETFs
        {'he_symbol': 'TLT', 'fmp_etype': 'etfs', 'fmp_symbol': 'TLT'},
        {'he_symbol': 'VXX', 'fmp_etype': 'etfs', 'fmp_symbol': 'VXX'},
        {'he_symbol': 'XLE', 'fmp_etype': 'etfs', 'fmp_symbol': 'XLE'},
        {'he_symbol': 'XLF', 'fmp_etype': 'etfs', 'fmp_symbol': 'XLF'},
        {'he_symbol': 'XLI', 'fmp_etype': 'etfs', 'fmp_symbol': 'XLI'},
        {'he_symbol': 'XLK', 'fmp_etype': 'etfs', 'fmp_symbol': 'XLK'},
        {'he_symbol': 'XLV', 'fmp_etype': 'etfs', 'fmp_symbol': 'XLV'},
        {'he_symbol': 'XLY', 'fmp_etype': 'etfs', 'fmp_symbol': 'XLY'},
        {'he_symbol': 'XLP', 'fmp_etype': 'etfs', 'fmp_symbol': 'XLP'},
        {'he_symbol': 'XLU', 'fmp_etype': 'etfs', 'fmp_symbol': 'XLU'},
        {'he_symbol': 'XME', 'fmp_etype': 'etfs', 'fmp_symbol': 'XME'},
        {'he_symbol': 'XOP', 'fmp_etype': 'etfs', 'fmp_symbol': 'XOP'},
        {'he_symbol': 'XRT', 'fmp_etype': 'etfs', 'fmp_symbol': 'XRT'},
        {'he_symbol': 'XTN', 'fmp_etype': 'etfs', 'fmp_symbol': 'XTN'},
        
        # Forex pairs
        {'he_symbol': 'CAD/USD', 'fmp_etype': 'forex', 'fmp_symbol': 'CADUSD'},
        {'he_symbol': 'EUR/USD', 'fmp_etype': 'forex', 'fmp_symbol': 'EURUSD'},
        {'he_symbol': 'GBP/USD', 'fmp_etype': 'forex', 'fmp_symbol': 'GBPUSD'},
        {'he_symbol': 'JPY/USD', 'fmp_etype': 'forex', 'fmp_symbol': 'JPYUSD'},
        {'he_symbol': 'YEN/USD', 'fmp_etype': 'forex', 'fmp_symbol': 'JPYUSD'},
        {'he_symbol': 'YUAN/USD', 'fmp_etype': 'forex', 'fmp_symbol': 'CNYUSD'},
        {'he_symbol': 'ZAR/USD', 'fmp_etype': 'forex', 'fmp_symbol': 'ZARUSD'},
    ]
    
    return manual_matches

def main():
    """Create the final mapping table"""
    print("Creating Hedgeye to FMP mapping table...")
    
    # Get exact matches
    exact_matches = get_exact_matches()
    print(f"Found {len(exact_matches)} exact matches")
    
    # Get manual matches
    manual_matches = get_manual_matches()
    print(f"Found {len(manual_matches)} manual matches")
    
    # Combine all matches
    all_matches = exact_matches + manual_matches
    
    # Create DataFrame
    mapping_df = pd.DataFrame(all_matches)
    
    # Remove duplicates (in case we have both exact and manual matches)
    mapping_df = mapping_df.drop_duplicates(subset=['he_symbol'], keep='first')
    
    # Sort by Hedgeye symbol
    mapping_df = mapping_df.sort_values('he_symbol')
    
    # Save to configured output location
    config = load_config()
    output_dir = Path(config["paths"]["combined_csv_output_dir"])
    output_file = output_dir / "he_to_fmp_mapping.csv"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    mapping_df.to_csv(output_file, index=False)
    
    print(f"\nMapping table saved to: {output_file}")
    print(f"Total mappings: {len(mapping_df)}")
    
    # Summary by entity type
    print("\nSummary by entity type:")
    summary = mapping_df['fmp_etype'].value_counts()
    for etype, count in summary.items():
        print(f"  {etype}: {count}")
    
    # Show sample
    print(f"\nSample mappings:")
    print(mapping_df.head(10).to_string(index=False))
    
    return mapping_df

if __name__ == "__main__":
    main() 