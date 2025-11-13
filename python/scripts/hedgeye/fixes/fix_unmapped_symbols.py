#!/usr/bin/env python3
"""
Add mappings for unmapped Hedgeye symbols to FMP entities.
"""

import pandas as pd
import os
from pathlib import Path

def get_unmapped_symbol_mappings():
    """
    Manual mappings for the 11 unmapped symbols identified in analysis.
    Based on financial market knowledge and FMP entity types.
    """
    return [
        # Natural Gas
        {'he_symbol': 'NATGAS', 'fmp_etype': 'commodities', 'fmp_symbol': 'NGUSD'},
        
        # Nikkei (already have NIKKEI, this is alternate spelling)
        {'he_symbol': 'NIKK', 'fmp_etype': 'indexes', 'fmp_symbol': '^N225'},
        
        # REITs ETF
        {'he_symbol': 'REITS', 'fmp_etype': 'etfs', 'fmp_symbol': 'VNQ'},
        
        # Russell 2000
        {'he_symbol': 'RUT', 'fmp_etype': 'indexes', 'fmp_symbol': '^RUT'},
        
        # Shanghai Composite
        {'he_symbol': 'SSEC', 'fmp_etype': 'indexes', 'fmp_symbol': '000001.SS'},
        
        # Silver (commodity, already have SILVER with SIUSD)
        {'he_symbol': 'Silver', 'fmp_etype': 'commodities', 'fmp_symbol': 'SIUSD'},
        
        # USD/YEN (same as existing YEN/USD)
        {'he_symbol': 'USD/YEN', 'fmp_etype': 'forex', 'fmp_symbol': 'USDJPY'},
        
        # US Treasury bonds
        {'he_symbol': 'UST10Y', 'fmp_etype': 'etfs', 'fmp_symbol': 'IEF'},  # 7-10Y Treasury ETF
        {'he_symbol': 'UST2Y', 'fmp_etype': 'etfs', 'fmp_symbol': 'SHY'},   # 1-3Y Treasury ETF
        {'he_symbol': 'UST30Y', 'fmp_etype': 'etfs', 'fmp_symbol': 'TLT'},  # 20+ Year Treasury ETF
        
        # WTI Crude Oil
        {'he_symbol': 'WTIC', 'fmp_etype': 'commodities', 'fmp_symbol': 'CLUSD'},
    ]

def main():
    print("=== FIXING UNMAPPED HEDGEYE SYMBOLS ===")
    
    # Load existing mapping
    map_path = os.path.expanduser("~/d/downloads/fmp/he_to_fmp.csv")
    
    if not Path(map_path).exists():
        print(f"ERROR: FMP mapping file not found: {map_path}")
        return
    
    existing_df = pd.read_csv(map_path)
    print(f"Loaded {len(existing_df)} existing mappings")
    
    # Get new mappings
    new_mappings = get_unmapped_symbol_mappings()
    new_df = pd.DataFrame(new_mappings)
    print(f"Adding {len(new_mappings)} new mappings:")
    
    for mapping in new_mappings:
        print(f"  • {mapping['he_symbol']} -> {mapping['fmp_etype']}:{mapping['fmp_symbol']}")
    
    # Combine mappings
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    print(f"\nTotal mappings after addition: {len(combined_df)}")
    
    # Remove duplicates (keep first occurrence)
    initial_count = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset=['he_symbol'], keep='first')
    final_count = len(combined_df)
    
    if initial_count != final_count:
        print(f"Removed {initial_count - final_count} duplicate mappings")
    
    # Sort by symbol
    combined_df = combined_df.sort_values('he_symbol').reset_index(drop=True)
    
    # Create backup of original
    backup_path = map_path + '.backup'
    existing_df.to_csv(backup_path, index=False)
    print(f"Original mapping saved as backup: {backup_path}")
    
    # Save updated mapping
    combined_df.to_csv(map_path, index=False)
    print(f"Updated mapping saved to: {map_path}")
    
    # Show summary
    print(f"\n=== FINAL MAPPING SUMMARY ===")
    entity_counts = combined_df['fmp_etype'].value_counts()
    for etype, count in entity_counts.items():
        print(f"  {etype}: {count}")
    
    print(f"\nTotal unique Hedgeye symbols mapped: {len(combined_df)}")
    
    # Verify no duplicates
    duplicates = combined_df[combined_df.duplicated(subset=['he_symbol'], keep=False)]
    if duplicates.empty:
        print("✓ No duplicate Hedgeye symbols in final mapping")
    else:
        print(f"⚠️  Found {len(duplicates)} duplicate Hedgeye symbols:")
        for _, row in duplicates.iterrows():
            print(f"  • {row['he_symbol']}")
    
    return combined_df

if __name__ == "__main__":
    result = main()