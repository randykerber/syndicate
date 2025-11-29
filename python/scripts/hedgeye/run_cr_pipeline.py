#!/usr/bin/env python3
"""
Run the complete Hedgeye Current Range (CR) data pipeline.

This script orchestrates the full CR pipeline:
1. Parse ETF Pro Plus weekly emails
2. Parse Portfolio Solutions daily emails
3. Merge position ranges from all sources
4. Enrich with current prices and proxy calculations
5. Generate CR time-series plots

Usage:
    uv run python scripts/hedgeye/run_cr_pipeline.py
"""

from hedgeye.ds.ep.process_etf_pro_weekly import main as parse_ep
from hedgeye.ds.ps.process_portfolio_solutions import main as parse_ps
from hedgeye.ds.cr.cr_merge_ranges import main as merge_cr
from hedgeye.ds.cr.cr_enrich_ranges import main as enrich_cr
from hedgeye.ds.cr.cr_time_series_plotting import generate_all_cr_time_series_plots


def run_full_cr_pipeline(
    parse_emails: bool = True,
    merge_data: bool = True,
    enrich_data: bool = True,
    generate_plots: bool = True,
    plot_days_back: int = 30
):
    """
    Run the complete CR pipeline.

    Args:
        parse_emails: Parse EP and PS emails (default: True)
        merge_data: Merge position ranges (default: True)
        enrich_data: Enrich with prices (default: True)
        generate_plots: Generate time-series plots (default: True)
        plot_days_back: Days to look back for plots (default: 30)
    """
    print("=" * 70)
    print("Current Range (CR) Full Pipeline")
    print("=" * 70)

    if parse_emails:
        print("\n" + "=" * 70)
        print("Step 1: Parsing ETF Pro Plus Weekly Emails")
        print("=" * 70)
        parse_ep()

        print("\n" + "=" * 70)
        print("Step 2: Parsing Portfolio Solutions Daily Emails")
        print("=" * 70)
        parse_ps()

    if merge_data:
        print("\n" + "=" * 70)
        print("Step 3: Merging Position Ranges")
        print("=" * 70)
        merge_cr()

    if enrich_data:
        print("\n" + "=" * 70)
        print("Step 4: Enriching with Current Prices")
        print("=" * 70)
        enrich_cr()

    if generate_plots:
        print("\n" + "=" * 70)
        print("Step 5: Generating CR Time-Series Plots")
        print("=" * 70)
        generate_all_cr_time_series_plots(days_back=plot_days_back)

    print("\n" + "=" * 70)
    print("✅ Full CR Pipeline Complete!")
    print("=" * 70)


def main():
    """Main entry point."""
    run_full_cr_pipeline()


if __name__ == "__main__":
    main()
