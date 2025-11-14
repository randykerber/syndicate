#!/usr/bin/env python3
"""
Core pipeline orchestration functions for Hedgeye Risk Range™ data processing.

This module provides composable pipeline functions that can be run independently
or as part of the full pipeline. All core pipeline logic is centralized here.
"""

import pandas as pd
from typing import Optional, Dict, Any
from pathlib import Path

from syndicate.data_sources.hedgeye.run_parser import main as run_parser_main
from syndicate.data_sources.hedgeye.use_rr import load_all_risk_range_data, save_combined_risk_range_df, generate_all_plots
from syndicate.data_sources.hedgeye.enhanced_plotting import generate_enhanced_plots, create_summary_dashboard
from syndicate.data_sources.hedgeye.symbol_canonicalization import canonicalize_symbol


def run_parsing_step(file_path: Optional[str] = None) -> None:
    """
    Run the email parsing step of the pipeline.
    
    Args:
        file_path: Optional path to specific .eml file. If None, processes all unprocessed files.
    """
    print("=== Step: Parsing emails ===")
    if file_path:
        # TODO: Add single file processing support to run_parser_main
        print(f"Processing single file: {file_path}")
        # For now, just run the main parser
        run_parser_main()
    else:
        run_parser_main()
    print("✅ Email parsing completed")


def run_combine_step() -> pd.DataFrame:
    """
    Run the data combination step with symbol canonicalization.
    
    Returns:
        Combined and canonicalized DataFrame
    """
    print("=== Step: Loading and combining data ===")
    df = load_all_risk_range_data()
    
    print("=== Step: Applying symbol canonicalization ===")
    df['index'] = df['index'].apply(canonicalize_symbol)
    
    print("=== Step: Saving combined dataframe ===")
    save_combined_risk_range_df(df)
    
    print(f"✅ Combined {len(df)} records from {df['index'].nunique()} symbols")
    return df


def run_basic_plots_step(df: Optional[pd.DataFrame] = None) -> None:
    """
    Run basic plotting step.
    
    Args:
        df: Optional DataFrame. If None, loads combined data.
    """
    print("=== Step: Generating basic plots ===")
    if df is None:
        df = load_all_risk_range_data()
        df['index'] = df['index'].apply(canonicalize_symbol)
    
    generate_all_plots(df)
    print("✅ Basic plotting completed")


def run_enhanced_plots_step(df: Optional[pd.DataFrame] = None, **kwargs) -> None:
    """
    Run enhanced plotting step with FMP price integration.
    
    Args:
        df: Optional DataFrame. If None, loads combined data.
        **kwargs: Additional options for enhanced plotting
    """
    print("=== Generating Enhanced Risk Range Plots ===")
    
    if df is None:
        df = load_all_risk_range_data()
        df['index'] = df['index'].apply(canonicalize_symbol)
    
    # Option 1: Generate plots for all symbols with latest prices
    print("\n1. Generating all plots with latest FMP prices...")
    generate_enhanced_plots(df, include_latest_prices=True, **kwargs)
    
    # Option 2: Generate plots for specific symbols only
    print("\n2. Generating plots for select symbols...")
    test_symbols = ['AAPL', 'SPX', 'TSLA', 'EUR/USD', 'GOLD']
    generate_enhanced_plots(df, include_latest_prices=True, symbols_to_plot=test_symbols)

    # Option 3: Create summary dashboard (DISABLED - not useful currently)
    # TODO: Redesign high-utility dashboard later
    # print("\n3. Creating summary dashboard...")
    # summary = create_summary_dashboard()
    #
    # if summary is not None and not summary.empty:
    #     print("\nRisk Range Status Summary:")
    #     status_summary = summary['status'].value_counts()
    #     for status, count in status_summary.items():
    #         print(f"  {status}: {count} symbols")

    print("\n✅ Enhanced plotting complete!")


def run_full_pipeline(
    parse_emails: bool = True,
    combine_data: bool = True, 
    generate_basic_plots: bool = False,
    generate_enhanced_plots: bool = True,
    **kwargs
) -> pd.DataFrame:
    """
    Run the complete Hedgeye Risk Range data pipeline.
    
    Args:
        parse_emails: Whether to run email parsing step
        combine_data: Whether to run data combination step  
        generate_basic_plots: Whether to generate basic plots
        generate_enhanced_plots: Whether to generate enhanced plots
        **kwargs: Additional options passed to plotting functions
        
    Returns:
        Final combined DataFrame
    """
    print("=== Starting Full Pipeline ===")
    
    df = None
    
    if parse_emails:
        run_parsing_step()
    
    if combine_data:
        df = run_combine_step()
    
    if generate_basic_plots:
        run_basic_plots_step(df)
        
    if generate_enhanced_plots:
        run_enhanced_plots_step(df, **kwargs)
    
    print("✅ Full pipeline completed")
    
    # Return final dataframe (load if not already loaded)
    if df is None:
        df = load_all_risk_range_data()
        df['index'] = df['index'].apply(canonicalize_symbol)
    
    return df


# Convenience functions for common pipeline combinations
def run_data_pipeline() -> pd.DataFrame:
    """Run just the data processing pipeline (parse + combine)."""
    return run_full_pipeline(
        parse_emails=True,
        combine_data=True,
        generate_basic_plots=False,
        generate_enhanced_plots=False
    )


def run_plotting_pipeline(df: Optional[pd.DataFrame] = None) -> None:
    """Run just the plotting pipeline (enhanced plots only)."""
    if df is None:
        df = load_all_risk_range_data()
        df['index'] = df['index'].apply(canonicalize_symbol)
    
    run_enhanced_plots_step(df)


def run_refresh_pipeline() -> pd.DataFrame:
    """Run pipeline to refresh plots with latest data (no parsing)."""
    return run_full_pipeline(
        parse_emails=False,
        combine_data=True,
        generate_enhanced_plots=True
    )