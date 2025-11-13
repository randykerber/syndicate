#!/usr/bin/env python3
"""
Fix incorrect treasury mappings and add treasury rates support.
UST30Y, UST10Y, UST2Y should map to treasury rates, not ETFs.
"""

import pandas as pd
import os
from pathlib import Path

def fix_treasury_mappings():
    """
    Fix the incorrect treasury mappings in the FMP mapping file.
    
    Current issues:
    - UST30Y -> etfs:TLT (WRONG: TLT is ETF, UST30Y is interest rate)
    - UST10Y -> etfs:IEF (WRONG: IEF is ETF, UST10Y is interest rate)  
    - UST2Y -> etfs:SHY (WRONG: SHY is ETF, UST2Y is interest rate)
    
    Correct mappings:
    - UST30Y -> treasury:year30 (30-year treasury rate)
    - UST10Y -> treasury:year10 (10-year treasury rate)
    - UST2Y -> treasury:year2 (2-year treasury rate)
    """
    
    print("=== FIXING TREASURY MAPPINGS ===")
    
    # Load existing mapping
    map_path = os.path.expanduser("~/d/downloads/fmp/he_to_fmp.csv")
    
    if not Path(map_path).exists():
        print(f"ERROR: FMP mapping file not found: {map_path}")
        return
    
    df = pd.read_csv(map_path)
    print(f"Loaded {len(df)} existing mappings")
    
    # Create backup
    backup_path = map_path + f'.backup_treasury_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}'
    df.to_csv(backup_path, index=False)
    print(f"Backup saved: {backup_path}")
    
    # Show current incorrect mappings
    treasury_symbols = ['UST30Y', 'UST10Y', 'UST2Y']
    current_mappings = df[df['he_symbol'].isin(treasury_symbols)]
    
    print(f"\nCurrent INCORRECT mappings:")
    for _, row in current_mappings.iterrows():
        print(f"  {row['he_symbol']} -> {row['fmp_etype']}:{row['fmp_symbol']} ❌")
    
    # Remove old incorrect mappings
    df = df[~df['he_symbol'].isin(treasury_symbols)]
    print(f"\nRemoved {len(treasury_symbols)} incorrect treasury mappings")
    
    # Add correct treasury mappings
    correct_mappings = [
        {'he_symbol': 'UST30Y', 'fmp_etype': 'treasury', 'fmp_symbol': 'year30'},
        {'he_symbol': 'UST10Y', 'fmp_etype': 'treasury', 'fmp_symbol': 'year10'}, 
        {'he_symbol': 'UST2Y', 'fmp_etype': 'treasury', 'fmp_symbol': 'year2'}
    ]
    
    new_df = pd.DataFrame(correct_mappings)
    df = pd.concat([df, new_df], ignore_index=True)
    
    print(f"\nAdded CORRECT mappings:")
    for mapping in correct_mappings:
        print(f"  {mapping['he_symbol']} -> {mapping['fmp_etype']}:{mapping['fmp_symbol']} ✅")
    
    # Sort and save
    df = df.sort_values('he_symbol').reset_index(drop=True)
    df.to_csv(map_path, index=False)
    
    print(f"\nUpdated mapping saved to: {map_path}")
    print(f"Total mappings: {len(df)}")
    
    # Show new entity type distribution
    print(f"\n=== UPDATED ENTITY TYPE DISTRIBUTION ===")
    entity_counts = df['fmp_etype'].value_counts()
    for etype, count in entity_counts.items():
        print(f"  {etype}: {count}")
    
    return df

def validate_treasury_mapping():
    """Validate that treasury mappings are correct."""
    print("\n=== VALIDATING TREASURY MAPPINGS ===")
    
    map_path = os.path.expanduser("~/d/downloads/fmp/he_to_fmp.csv")
    df = pd.read_csv(map_path)
    
    treasury_mappings = df[df['fmp_etype'] == 'treasury']
    
    if treasury_mappings.empty:
        print("❌ No treasury mappings found!")
        return False
    
    print(f"✅ Found {len(treasury_mappings)} treasury mappings:")
    for _, row in treasury_mappings.iterrows():
        print(f"  {row['he_symbol']} -> {row['fmp_etype']}:{row['fmp_symbol']}")
    
    # Check for expected mappings
    expected = {
        'UST30Y': 'year30',
        'UST10Y': 'year10', 
        'UST2Y': 'year2'
    }
    
    all_correct = True
    for he_symbol, expected_fmp in expected.items():
        mapping = treasury_mappings[treasury_mappings['he_symbol'] == he_symbol]
        
        if mapping.empty:
            print(f"❌ Missing mapping for {he_symbol}")
            all_correct = False
        elif mapping.iloc[0]['fmp_symbol'] != expected_fmp:
            print(f"❌ Wrong mapping for {he_symbol}: expected {expected_fmp}, got {mapping.iloc[0]['fmp_symbol']}")
            all_correct = False
        else:
            print(f"✅ Correct mapping for {he_symbol}")
    
    return all_correct

def check_conflicting_etf_mappings():
    """Check if TLT, IEF, SHY are still mapped to other symbols."""
    print("\n=== CHECKING FOR ETF MAPPING CONFLICTS ===")
    
    map_path = os.path.expanduser("~/d/downloads/fmp/he_to_fmp.csv")
    df = pd.read_csv(map_path)
    
    problematic_etfs = ['TLT', 'IEF', 'SHY']
    
    for etf in problematic_etfs:
        mappings = df[df['fmp_symbol'] == etf]
        
        if mappings.empty:
            print(f"✅ {etf}: No longer mapped")
        elif len(mappings) == 1:
            symbol = mappings.iloc[0]['he_symbol']
            if symbol == etf:
                print(f"✅ {etf}: Correctly mapped to itself only")
            else:
                print(f"ℹ️  {etf}: Mapped to {symbol} (check if this is correct)")
        else:
            symbols = mappings['he_symbol'].tolist()
            print(f"⚠️  {etf}: Still has {len(mappings)} mappings: {symbols}")

def main():
    """Fix treasury mappings and validate the changes."""
    print("🏛️  TREASURY MAPPING CORRECTION")
    print("=" * 50)
    
    print("Issues to fix:")
    print("  • UST30Y should be treasury rate, not TLT ETF")  
    print("  • UST10Y should be treasury rate, not IEF ETF")
    print("  • UST2Y should be treasury rate, not SHY ETF")
    print()
    
    # Fix the mappings
    updated_df = fix_treasury_mappings()
    
    # Validate the fixes
    validation_success = validate_treasury_mapping()
    
    # Check for remaining conflicts
    check_conflicting_etf_mappings()
    
    print("\n" + "=" * 50)
    if validation_success:
        print("✅ Treasury mapping correction completed successfully!")
        print("\nNext steps:")
        print("  1. Update price_fetcher.py to support 'treasury' entity type")
        print("  2. Add treasury rates endpoint integration")
        print("  3. Test with corrected mappings")
    else:
        print("❌ Treasury mapping correction had issues. Check the output above.")
    
    return updated_df

if __name__ == "__main__":
    result = main()