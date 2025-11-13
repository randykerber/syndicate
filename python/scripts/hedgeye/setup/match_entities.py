#!/usr/bin/env python3
"""
Match Hedgeye Risk Range symbols with FMP entities.

Loads Hedgeye risk range data, extracts unique symbols, and finds matches
in FMP entity data using pandas DataFrames.
"""

import pandas as pd
from pathlib import Path
from hedgeye_kb.config_loader import load_config
from fmp.load_entities import load_fmp_entities

def load_hedgeye_data():
    """Load Hedgeye risk range data from CSV"""
    config = load_config()
    hedgeye_file = Path(config["paths"]["combined_csv_output_dir"]) / "combined_risk_range.csv"
    
    if not hedgeye_file.exists():
        print(f"Hedgeye data file not found: {hedgeye_file}")
        return pd.DataFrame()
    
    print(f"Loading Hedgeye data from: {hedgeye_file}")
    df = pd.read_csv(hedgeye_file)
    print(f"Loaded {len(df)} risk range records")
    print(f"Columns: {list(df.columns)}")
    
    return df

def extract_hedgeye_symbols(df):
    """Extract unique symbols from Hedgeye data"""
    if df.empty:
        return []
    
    symbols = df['index'].unique()
    symbols = sorted(symbols)
    
    print(f"Found {len(symbols)} unique Hedgeye symbols:")
    print(f"Sample symbols: {symbols[:10]}")
    
    return symbols

def match_symbols_with_fmp(hedgeye_symbols):
    """Match Hedgeye symbols with FMP entities"""
    print("\n" + "="*60)
    print("MATCHING SYMBOLS WITH FMP ENTITIES")
    print("="*60)
    
    # Load FMP entities
    stocks = load_fmp_entities("stocks")
    etfs = load_fmp_entities("etfs")
    indexes = load_fmp_entities("indexes")
    cryptocurrencies = load_fmp_entities("cryptocurrencies")
    
    print(f"Loaded FMP data:")
    print(f"  - Stocks: {len(stocks)} records")
    print(f"  - ETFs: {len(etfs)} records") 
    print(f"  - Indexes: {len(indexes)} records")
    print(f"  - Cryptocurrencies: {len(cryptocurrencies)} records")
    
    # Create a combined FMP dataset
    fmp_data = []
    
    # Add stocks
    if not stocks.empty:
        stocks_copy = stocks.copy()
        stocks_copy['entity_type'] = 'stock'
        fmp_data.append(stocks_copy)
    
    # Add ETFs
    if not etfs.empty:
        etfs_copy = etfs.copy()
        etfs_copy['entity_type'] = 'etf'
        fmp_data.append(etfs_copy)
    
    # Add indexes
    if not indexes.empty:
        indexes_copy = indexes.copy()
        indexes_copy['entity_type'] = 'index'
        fmp_data.append(indexes_copy)
    
    # Add cryptocurrencies
    if not cryptocurrencies.empty:
        crypto_copy = cryptocurrencies.copy()
        crypto_copy['entity_type'] = 'cryptocurrency'
        fmp_data.append(crypto_copy)
    
    if not fmp_data:
        print("No FMP data loaded")
        return pd.DataFrame(), []
    
    # Combine all FMP data
    fmp_combined = pd.concat(fmp_data, ignore_index=True)
    print(f"Combined FMP data: {len(fmp_combined)} records")
    
    # Find exact matches
    matches = []
    no_matches = []
    
    for symbol in hedgeye_symbols:
        # Look for exact symbol match
        match = fmp_combined[fmp_combined['symbol'] == symbol]
        
        if not match.empty:
            match_info = match.iloc[0]
            matches.append({
                'hedgeye_symbol': symbol,
                'fmp_symbol': match_info['symbol'],
                'fmp_name': match_info.get('name', match_info.get('companyName', 'N/A')),
                'entity_type': match_info['entity_type'],
                'exchange': match_info.get('exchange', 'N/A'),
                'price': match_info.get('price', 'N/A'),
                'match_type': 'exact'
            })
        else:
            no_matches.append(symbol)
    
    # Create results DataFrame
    matches_df = pd.DataFrame(matches)
    
    print(f"\nMATCHING RESULTS:")
    print(f"✅ Exact matches found: {len(matches)}")
    print(f"❌ No exact matches: {len(no_matches)}")
    
    if not matches_df.empty:
        print(f"\nSample exact matches:")
        print(matches_df.head())
    
    if no_matches:
        print(f"\nSymbols with no FMP match (first 10):")
        print(no_matches[:10])
    
    return matches_df, no_matches

def main():
    """Main function to run the matching process"""
    print("HEDGEYE-FMP ENTITY MATCHING")
    print("="*60)
    
    # Load Hedgeye data
    hedgeye_df = load_hedgeye_data()
    if hedgeye_df.empty:
        return
    
    # Extract unique symbols
    hedgeye_symbols = extract_hedgeye_symbols(hedgeye_df)
    if not hedgeye_symbols:
        return
    
    # Match with FMP entities
    matches_df, no_matches = match_symbols_with_fmp(hedgeye_symbols)
    
    # Summary
    print(f"\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total Hedgeye symbols: {len(hedgeye_symbols)}")
    print(f"Matched with FMP: {len(matches_df)}")
    print(f"Unmatched: {len(no_matches)}")
    print(f"Match rate: {len(matches_df)/len(hedgeye_symbols)*100:.1f}%")
    
    return matches_df, no_matches

if __name__ == "__main__":
    main() 