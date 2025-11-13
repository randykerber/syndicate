#!/usr/bin/env python3
"""
Analyze Hedgeye to FMP symbol mappings and identify next steps.
"""

import pandas as pd
import os
from pathlib import Path

def main():
    print("=== HEDGEYE-FMP MAPPING ANALYSIS ===")
    
    # Load Hedgeye combined risk range data
    print("\n1. Loading Hedgeye Risk Range data...")
    csv_path = os.path.expanduser("~/d/downloads/hedgeye/prod/all/csv/combined_risk_range.csv")
    
    if not Path(csv_path).exists():
        print(f"ERROR: Hedgeye data file not found: {csv_path}")
        return
    
    he_df = pd.read_csv(csv_path)
    print(f"   Loaded {len(he_df)} rows, {len(he_df.columns)} columns")
    print(f"   Date range: {he_df['date'].min()} to {he_df['date'].max()}")
    
    # Get unique Hedgeye symbols
    he_unique_symbols = set(he_df['index'].unique())
    print(f"   Unique Hedgeye symbols: {len(he_unique_symbols)}")
    
    # Load FMP mapping data
    print("\n2. Loading FMP mapping data...")
    map_path = os.path.expanduser("~/d/downloads/fmp/he_to_fmp.csv")
    
    if not Path(map_path).exists():
        print(f"ERROR: FMP mapping file not found: {map_path}")
        return
    
    map_df = pd.read_csv(map_path)
    print(f"   Loaded {len(map_df)} mappings")
    
    # Get mapped symbols
    he_mapped_symbols = set(map_df['he_symbol'].unique())
    print(f"   Hedgeye symbols in mapping: {len(he_mapped_symbols)}")
    
    # Analyze mapping coverage
    print("\n3. MAPPING COVERAGE ANALYSIS")
    unmapped_symbols = he_unique_symbols - he_mapped_symbols
    extra_mapped_symbols = he_mapped_symbols - he_unique_symbols
    
    total_he_symbols = len(he_unique_symbols)
    mapped_count = len(he_unique_symbols & he_mapped_symbols)
    coverage_pct = (mapped_count / total_he_symbols) * 100
    
    print(f"   Total Hedgeye symbols: {total_he_symbols}")
    print(f"   Successfully mapped: {mapped_count}")
    print(f"   Coverage: {coverage_pct:.1f}%")
    
    print(f"\n   Unmapped symbols ({len(unmapped_symbols)}):")
    for symbol in sorted(unmapped_symbols):
        print(f"     • {symbol}")
    
    if extra_mapped_symbols:
        print(f"\n   Extra mapped symbols not in current data ({len(extra_mapped_symbols)}):")
        for symbol in sorted(extra_mapped_symbols):
            print(f"     • {symbol}")
    
    # Entity type distribution
    print("\n4. FMP ENTITY TYPE DISTRIBUTION")
    entity_counts = map_df['fmp_etype'].value_counts()
    for etype, count in entity_counts.items():
        print(f"   {etype}: {count}")
    
    # Data quality checks
    print("\n5. DATA QUALITY CHECKS")
    
    # Check for duplicate mappings
    duplicates = map_df[map_df.duplicated(subset=['he_symbol'], keep=False)]
    if not duplicates.empty:
        print(f"   ⚠️  Duplicate Hedgeye symbol mappings: {len(duplicates)}")
        for _, row in duplicates.iterrows():
            print(f"     • {row['he_symbol']} -> {row['fmp_etype']}:{row['fmp_symbol']}")
    else:
        print("   ✓ No duplicate Hedgeye symbol mappings")
    
    # Check FMP symbol reuse
    fmp_symbol_counts = map_df['fmp_symbol'].value_counts()
    reused_fmp_symbols = fmp_symbol_counts[fmp_symbol_counts > 1]
    if not reused_fmp_symbols.empty:
        print(f"   ⚠️  FMP symbols mapped to multiple Hedgeye symbols:")
        for fmp_symbol, count in reused_fmp_symbols.items():
            mappings = map_df[map_df['fmp_symbol'] == fmp_symbol]['he_symbol'].tolist()
            print(f"     • {fmp_symbol} <- {mappings}")
    
    # Data density analysis
    print("\n6. DATA DENSITY ANALYSIS")
    symbol_counts = he_df['index'].value_counts()
    print(f"   Most active symbols (top 5):")
    for symbol, count in symbol_counts.head(5).items():
        print(f"     • {symbol}: {count} observations")
    
    print(f"   Least active symbols (bottom 5):")
    for symbol, count in symbol_counts.tail(5).items():
        print(f"     • {symbol}: {count} observations")
    
    # Generate action items
    print("\n" + "="*60)
    print("RECOMMENDED NEXT STEPS")
    print("="*60)
    
    print("\n🔥 IMMEDIATE PRIORITIES:")
    print("   1. Add FMP mappings for unmapped symbols")
    print("   2. Validate entity type classifications")
    print("   3. Resolve duplicate/conflicting mappings")
    
    print("\n📈 DATA ENHANCEMENT:")
    print("   1. Integrate FMP price data for mapped symbols")
    print("   2. Add symbol metadata (company names, sectors)")
    print("   3. Historical price vs risk range correlation analysis")
    
    print("\n🔍 ANALYSIS CAPABILITIES:")
    print("   1. Time series analysis of risk range changes")
    print("   2. Cross-asset correlation analysis")
    print("   3. Trend persistence and reversal patterns")
    print("   4. Risk range effectiveness backtesting")
    
    print("\n⚙️  OPERATIONAL IMPROVEMENTS:")
    print("   1. Daily data quality monitoring")
    print("   2. Automated mapping validation")
    print("   3. Alert system for range breaches")
    print("   4. Performance dashboard")
    
    # Create action items CSV
    actions = [
        {"Priority": "High", "Task": "Map unmapped symbols", "Category": "Data", "Effort": "Medium", "Timeline": "1-2 days"},
        {"Priority": "High", "Task": "Add FMP price integration", "Category": "Enhancement", "Effort": "High", "Timeline": "1 week"},
        {"Priority": "Medium", "Task": "Build quality dashboard", "Category": "Operations", "Effort": "Medium", "Timeline": "3-5 days"},
        {"Priority": "Medium", "Task": "Correlation analysis", "Category": "Analysis", "Effort": "Low", "Timeline": "1-2 days"},
        {"Priority": "Low", "Task": "Portfolio risk integration", "Category": "Enhancement", "Effort": "High", "Timeline": "2-3 weeks"}
    ]
    
    action_df = pd.DataFrame(actions)
    action_file = os.path.expanduser("~/d/downloads/hedgeye/prod/all/csv/action_items.csv")
    action_df.to_csv(action_file, index=False)
    print(f"\n📋 Action items saved to: {action_file}")
    
    return {
        'unmapped_symbols': unmapped_symbols,
        'coverage_pct': coverage_pct,
        'entity_distribution': entity_counts.to_dict(),
        'total_symbols': total_he_symbols
    }

if __name__ == "__main__":
    result = main()