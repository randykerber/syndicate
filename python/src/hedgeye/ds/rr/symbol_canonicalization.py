#!/usr/bin/env python3
"""
Symbol canonicalization utilities for handling case/naming inconsistencies.
Addresses issues where symbols like 'Bitcoin' vs 'BITCOIN' cause data fragmentation.
"""

import pandas as pd
from typing import Dict, Optional

# Symbol mapping for known variations to canonical forms
SYMBOL_CANONICALIZATION_MAP = {
    # Case variations - most common issue
    'bitcoin': 'BITCOIN',
    'Bitcoin': 'BITCOIN',
    'copper': 'COPPER',
    'Copper': 'COPPER',
    'silver': 'SILVER',
    'Silver': 'SILVER',
    
    # Known naming variations - NIKK is Hedgeye's current standard
    'NIKKEI': 'NIKK',  # Map legacy to current Hedgeye standard
    'nikkei': 'NIKK',
    'Nikkei': 'NIKK',
    'NIKK': 'NIKK',    # Canonical symbol maps to itself
    
    # Add more mappings as discovered
}

def canonicalize_symbol(symbol: str) -> str:
    """
    Convert symbol to canonical form.
    
    Args:
        symbol: Original symbol from data
        
    Returns:
        Canonical symbol (typically uppercase)
    """
    if not symbol or not isinstance(symbol, str):
        return symbol
    
    # Check explicit mapping first
    if symbol in SYMBOL_CANONICALIZATION_MAP:
        return SYMBOL_CANONICALIZATION_MAP[symbol]
    
    # Default: uppercase
    return symbol.upper()

def canonicalize_dataframe_symbols(df: pd.DataFrame, symbol_column: str = 'index') -> pd.DataFrame:
    """
    Canonicalize all symbols in a dataframe.
    
    Args:
        df: DataFrame containing symbol data
        symbol_column: Name of column containing symbols
        
    Returns:
        DataFrame with canonicalized symbols
    """
    df_copy = df.copy()
    df_copy[symbol_column] = df_copy[symbol_column].apply(canonicalize_symbol)
    return df_copy

def find_symbol_variations(df: pd.DataFrame, symbol_column: str = 'index') -> Dict[str, list]:
    """
    Find all variations of symbols that might be the same.
    
    Args:
        df: DataFrame containing symbol data
        symbol_column: Name of column containing symbols
        
    Returns:
        Dict mapping canonical symbols to list of variations found
    """
    symbols = df[symbol_column].unique()
    variations = {}
    
    for symbol in symbols:
        canonical = canonicalize_symbol(symbol)
        if canonical not in variations:
            variations[canonical] = []
        variations[canonical].append(symbol)
    
    # Only return cases with multiple variations
    return {k: v for k, v in variations.items() if len(v) > 1}

def get_canonical_symbol_for_plotting(df: pd.DataFrame, target_symbol: str, symbol_column: str = 'index') -> Optional[str]:
    """
    Find the best symbol match for plotting, handling case variations.
    
    Args:
        df: DataFrame containing symbol data
        target_symbol: Symbol we want to plot
        symbol_column: Name of column containing symbols
        
    Returns:
        Symbol that exists in the data, or None if no match
    """
    available_symbols = df[symbol_column].unique()
    
    # Try exact match first
    if target_symbol in available_symbols:
        return target_symbol
    
    # Try canonical form of target
    canonical_target = canonicalize_symbol(target_symbol)
    
    # Look for any symbol that canonicalizes to the same form
    for symbol in available_symbols:
        if canonicalize_symbol(symbol) == canonical_target:
            return symbol
    
    return None

def combine_symbol_variations(df: pd.DataFrame, symbol_column: str = 'index') -> pd.DataFrame:
    """
    Combine data for symbols that are variations of the same symbol.
    
    Args:
        df: DataFrame containing symbol data
        symbol_column: Name of column containing symbols
        
    Returns:
        DataFrame with symbols canonicalized and data combined
    """
    return canonicalize_dataframe_symbols(df, symbol_column)