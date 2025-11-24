#!/usr/bin/env python3
"""
Generate CR time-series plots for all tickers.

Usage:
    uv run python scripts/hedgeye/generate_cr_time_series_plots.py
"""

from hedgeye.ds.cr.cr_time_series_plotting import generate_all_cr_time_series_plots

def main():
    """Generate CR time-series plots for all tickers."""
    stats = generate_all_cr_time_series_plots(
        days_back=30,
        require_rr_data=False  # Include EP-only tickers
    )
    
    return stats

if __name__ == "__main__":
    main()

