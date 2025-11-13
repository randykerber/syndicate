#!/usr/bin/env python3
"""
Create corrected FMP mappings addressing all identified issues.
Writes proposed corrections to CSV for review before applying.
"""

import pandas as pd
import os
from pathlib import Path
from datetime import datetime

def create_corrected_mappings():
    """Create comprehensive corrections to the FMP mapping file."""
    
    print("=== CREATING CORRECTED FMP MAPPINGS ===")
    
    # Load existing mapping
    map_path = os.path.expanduser("~/d/downloads/fmp/he_to_fmp.csv")
    df = pd.read_csv(map_path)
    
    print(f"Original mappings: {len(df)}")
    
    # Track changes for reporting
    changes = []
    
    def log_change(he_symbol, old_etype, old_fmp, new_etype, new_fmp, reason):
        changes.append({
            'he_symbol': he_symbol,
            'old_mapping': f"{old_etype}:{old_fmp}",
            'new_mapping': f"{new_etype}:{new_fmp}",
            'reason': reason
        })
    
    # 1. FIX TREASURY RATES
    print("\n1. Fixing treasury rates...")
    treasury_fixes = {
        'UST30Y': ('treasury', 'year30', 'Convert from ETF proxy to actual treasury rate'),
        'UST10Y': ('treasury', 'year10', 'Convert from ETF proxy to actual treasury rate'),
        'UST2Y': ('treasury', 'year2', 'Convert from ETF proxy to actual treasury rate')
    }
    
    for he_symbol, (new_etype, new_fmp, reason) in treasury_fixes.items():
        mask = df['he_symbol'] == he_symbol
        if mask.any():
            old_row = df[mask].iloc[0]
            log_change(he_symbol, old_row['fmp_etype'], old_row['fmp_symbol'], new_etype, new_fmp, reason)
            df.loc[mask, 'fmp_etype'] = new_etype
            df.loc[mask, 'fmp_symbol'] = new_fmp
    
    # 2. FIX ETF MISCLASSIFICATIONS  
    print("2. Fixing ETF misclassifications...")
    etf_fixes = {
        # XL sector ETFs
        'XLE': ('etfs', 'XLE', 'Energy sector ETF, not individual stock'),
        'XLF': ('etfs', 'XLF', 'Financial sector ETF, not individual stock'),
        'XLI': ('etfs', 'XLI', 'Industrial sector ETF, not individual stock'),
        'XLK': ('etfs', 'XLK', 'Technology sector ETF, not individual stock'),
        'XLP': ('etfs', 'XLP', 'Consumer staples ETF, not individual stock'),
        'XLRE': ('etfs', 'XLRE', 'Real estate sector ETF, not individual stock'),
        'XLU': ('etfs', 'XLU', 'Utilities sector ETF, not individual stock'),
        'XLY': ('etfs', 'XLY', 'Consumer discretionary ETF, not individual stock'),
        
        # Bond/specialty ETFs
        'GDX': ('etfs', 'GDX', 'Gold miners ETF, not individual stock'),
        'HYG': ('etfs', 'HYG', 'High yield bond ETF, not individual stock'),
        'LQD': ('etfs', 'LQD', 'Investment grade bond ETF, not individual stock'),
    }
    
    for he_symbol, (new_etype, new_fmp, reason) in etf_fixes.items():
        mask = df['he_symbol'] == he_symbol
        if mask.any():
            old_row = df[mask].iloc[0]
            if old_row['fmp_etype'] != new_etype:
                log_change(he_symbol, old_row['fmp_etype'], old_row['fmp_symbol'], new_etype, new_fmp, reason)
                df.loc[mask, 'fmp_etype'] = new_etype
    
    # 3. FIX INDEX MISCLASSIFICATIONS
    print("3. Fixing index misclassifications...")
    index_fixes = {
        'DAX': ('indexes', '^GDAXI', 'German stock index, not individual stock'),
        'USD': ('indexes', 'DXY', 'US Dollar Index (DXY), not individual stock')  # Will need to verify DXY symbol
    }
    
    for he_symbol, (new_etype, new_fmp, reason) in index_fixes.items():
        mask = df['he_symbol'] == he_symbol
        if mask.any():
            old_row = df[mask].iloc[0]
            log_change(he_symbol, old_row['fmp_etype'], old_row['fmp_symbol'], new_etype, new_fmp, reason)
            df.loc[mask, 'fmp_etype'] = new_etype
            df.loc[mask, 'fmp_symbol'] = new_fmp
    
    # 4. FIX COMMODITY MISCLASSIFICATIONS  
    print("4. Fixing commodity misclassifications...")
    commodity_fixes = {
        'GOLD': ('commodities', 'GCUSD', 'Gold commodity futures, not stock ticker')
    }
    
    for he_symbol, (new_etype, new_fmp, reason) in commodity_fixes.items():
        mask = df['he_symbol'] == he_symbol
        if mask.any():
            old_row = df[mask].iloc[0]
            if old_row['fmp_etype'] != new_etype:
                log_change(he_symbol, old_row['fmp_etype'], old_row['fmp_symbol'], new_etype, new_fmp, reason)
                df.loc[mask, 'fmp_etype'] = new_etype
                df.loc[mask, 'fmp_symbol'] = new_fmp
    
    # 5. RESOLVE DUPLICATE CONFLICTS
    print("5. Resolving duplicate conflicts...")
    
    # Remove case/spelling variants (keep the primary)
    duplicates_to_remove = [
        ('Bitcoin', 'Keep BITCOIN, remove case variant'),
        ('Copper', 'Keep COPPER, remove case variant'), 
        ('Silver', 'Keep SILVER, remove case variant'),
        ('YEN/USD', 'Keep USD/YEN, remove alternate spelling'),
        ('NIKKEI', 'Keep NIKK (shorter), remove longer variant'),
        ('OIL', 'Keep WTIC (more specific), remove generic OIL')
    ]
    
    for he_symbol, reason in duplicates_to_remove:
        mask = df['he_symbol'] == he_symbol
        if mask.any():
            old_row = df[mask].iloc[0]
            log_change(he_symbol, old_row['fmp_etype'], old_row['fmp_symbol'], 'REMOVED', 'REMOVED', reason)
            df = df[~mask]
    
    # Handle TLT conflict (already fixed UST30Y above, but TLT itself should remain)
    # TLT -> etfs:TLT is correct for the actual TLT ETF
    
    print(f"After corrections: {len(df)} mappings")
    
    # 6. IDENTIFY REMAINING SUSPICIOUS ITEMS
    print("\n6. Identifying potentially suspicious mappings...")
    suspicious = []
    
    # Check for any remaining stocks that might be misclassified
    remaining_stocks = df[df['fmp_etype'] == 'stocks']['he_symbol'].tolist()
    suspicious_stocks = [s for s in remaining_stocks if 
                        s.startswith('X') or  # X-prefixed symbols often ETFs
                        len(s) <= 3 or       # Very short symbols often indexes
                        s in ['SPMO', 'IAK', 'ITA', 'AMLP']]  # Check these
    
    for stock in suspicious_stocks:
        suspicious.append(f"Stock: {stock} - verify if actually individual stock")
    
    # Check commodities symbols 
    commodity_symbols = df[df['fmp_etype'] == 'commodities']
    for _, row in commodity_symbols.iterrows():
        if not row['fmp_symbol'].endswith('USD'):
            suspicious.append(f"Commodity: {row['he_symbol']} -> {row['fmp_symbol']} - unusual commodity symbol format")
    
    return df, changes, suspicious

def write_corrected_csv(corrected_df, changes, suspicious):
    """Write corrected mappings and change log to files."""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create output directory
    output_dir = Path.home() / "d/downloads/hedgeye/prod/all/mapping_corrections"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Write corrected mappings CSV
    corrected_file = output_dir / f"he_to_fmp_corrected_{timestamp}.csv"
    corrected_df_sorted = corrected_df.sort_values('he_symbol').reset_index(drop=True)
    corrected_df_sorted.to_csv(corrected_file, index=False)
    
    # 2. Write change log
    changes_file = output_dir / f"mapping_changes_{timestamp}.csv"
    changes_df = pd.DataFrame(changes)
    if not changes_df.empty:
        changes_df.to_csv(changes_file, index=False)
    
    # 3. Write suspicious items report
    suspicious_file = output_dir / f"suspicious_mappings_{timestamp}.txt"
    with open(suspicious_file, 'w') as f:
        f.write("POTENTIALLY SUSPICIOUS MAPPINGS FOR REVIEW\n")
        f.write("=" * 50 + "\n\n")
        
        if suspicious:
            for item in suspicious:
                f.write(f"• {item}\n")
        else:
            f.write("No obviously suspicious mappings found.\n")
        
        f.write(f"\nGenerated: {datetime.now().isoformat()}\n")
    
    # 4. Write summary report
    summary_file = output_dir / f"correction_summary_{timestamp}.txt"
    with open(summary_file, 'w') as f:
        f.write("FMP MAPPING CORRECTION SUMMARY\n")
        f.write("=" * 40 + "\n\n")
        
        f.write(f"Total mappings: {len(corrected_df_sorted)}\n")
        f.write(f"Total changes made: {len(changes)}\n\n")
        
        f.write("Entity type distribution:\n")
        entity_counts = corrected_df_sorted['fmp_etype'].value_counts()
        for etype, count in entity_counts.items():
            f.write(f"  {etype}: {count}\n")
        
        f.write(f"\nFiles created:\n")
        f.write(f"  • Corrected mappings: {corrected_file.name}\n")
        f.write(f"  • Change log: {changes_file.name}\n")
        f.write(f"  • Suspicious items: {suspicious_file.name}\n")
        f.write(f"  • This summary: {summary_file.name}\n")
    
    return {
        'corrected_csv': corrected_file,
        'changes_csv': changes_file, 
        'suspicious_txt': suspicious_file,
        'summary_txt': summary_file
    }

def main():
    """Create corrected mappings and write to files for review."""
    
    print("🔧 FMP MAPPING CORRECTION TOOL")
    print("=" * 50)
    
    # Create corrections
    corrected_df, changes, suspicious = create_corrected_mappings()
    
    # Write to files
    files = write_corrected_csv(corrected_df, changes, suspicious)
    
    # Summary
    print(f"\n📊 CORRECTION SUMMARY:")
    print(f"   • Total mappings: {len(corrected_df)}")
    print(f"   • Changes made: {len(changes)}")
    print(f"   • Suspicious items: {len(suspicious)}")
    
    print(f"\n📁 FILES CREATED:")
    for file_type, file_path in files.items():
        print(f"   • {file_type}: {file_path}")
    
    print(f"\n✅ CORRECTED ENTITY DISTRIBUTION:")
    entity_counts = corrected_df['fmp_etype'].value_counts()
    for etype, count in entity_counts.items():
        print(f"   • {etype}: {count}")
    
    if changes:
        print(f"\n🔄 KEY CHANGES MADE:")
        for change in changes[:10]:  # Show first 10 changes
            print(f"   • {change['he_symbol']}: {change['old_mapping']} → {change['new_mapping']}")
        if len(changes) > 10:
            print(f"   ... and {len(changes) - 10} more (see change log)")
    
    if suspicious:
        print(f"\n⚠️  ITEMS NEEDING REVIEW:")
        for item in suspicious[:5]:  # Show first 5
            print(f"   • {item}")
        if len(suspicious) > 5:
            print(f"   ... and {len(suspicious) - 5} more (see suspicious items file)")
    
    print(f"\n📋 NEXT STEPS:")
    print(f"   1. Review the corrected CSV: {files['corrected_csv'].name}")
    print(f"   2. Check suspicious items: {files['suspicious_txt'].name}")
    print(f"   3. If approved, replace original mapping file")
    print(f"   4. Update price_fetcher.py to support 'treasury' entity type")
    
    return corrected_df, files

if __name__ == "__main__":
    result = main()