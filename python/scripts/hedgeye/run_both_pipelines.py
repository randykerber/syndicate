#!/usr/bin/env python3
"""
Run both RR and CR pipelines sequentially.

This script runs:
1. Risk Range (RR) full pipeline
2. Current Range (CR) full pipeline

The RR pipeline must run first because CR depends on the combined RR data.

Usage:
    uv run python scripts/hedgeye/run_both_pipelines.py
"""

from hedgeye.ds.rr.rr_pipeline import run_full_rr_pipeline
from hedgeye.ds.ep.process_etf_pro_weekly import main as parse_ep
from hedgeye.ds.ps.process_portfolio_solutions import main as parse_ps
from hedgeye.ds.cr.cr_merge_ranges import main as merge_cr
from hedgeye.ds.cr.cr_enrich_ranges import main as enrich_cr
from hedgeye.ds.cr.cr_time_series_plotting import generate_all_cr_time_series_plots


def run_both_pipelines(
    rr_parse_emails: bool = True,
    rr_generate_plots: bool = True,
    cr_parse_emails: bool = True,
    cr_generate_plots: bool = True,
    plot_days_back: int = 30
):
    """
    Run both RR and CR pipelines.

    Args:
        rr_parse_emails: Parse RR emails (default: True)
        rr_generate_plots: Generate RR plots (default: True)
        cr_parse_emails: Parse EP/PS emails (default: True)
        cr_generate_plots: Generate CR plots (default: True)
        plot_days_back: Days to look back for CR plots (default: 30)
    """
    print("=" * 70)
    print("HEDGEYE FULL PIPELINE - RR + CR")
    print("=" * 70)

    # ========== RR Pipeline ==========
    print("\n" + "=" * 70)
    print("RISK RANGE (RR) PIPELINE")
    print("=" * 70)

    run_full_rr_pipeline(
        parse_emails=rr_parse_emails,
        combine_data=True,
        generate_basic_plots=False,
        generate_enhanced_plots=rr_generate_plots
    )

    # ========== CR Pipeline ==========
    print("\n" + "=" * 70)
    print("CURRENT RANGE (CR) PIPELINE")
    print("=" * 70)

    if cr_parse_emails:
        print("\n" + "=" * 70)
        print("Step 1: Parsing ETF Pro Plus Weekly Emails")
        print("=" * 70)
        parse_ep()

        print("\n" + "=" * 70)
        print("Step 2: Parsing Portfolio Solutions Daily Emails")
        print("=" * 70)
        parse_ps()

    print("\n" + "=" * 70)
    print("Step 3: Merging Position Ranges")
    print("=" * 70)
    merge_cr()

    print("\n" + "=" * 70)
    print("Step 4: Enriching with Current Prices")
    print("=" * 70)
    enrich_cr()

    if cr_generate_plots:
        print("\n" + "=" * 70)
        print("Step 5: Generating CR Time-Series Plots")
        print("=" * 70)
        generate_all_cr_time_series_plots(days_back=plot_days_back)

    # ========== Summary ==========
    print("\n" + "=" * 70)
    print("✅ FULL PIPELINE COMPLETE!")
    print("=" * 70)
    print("\nOutputs:")
    print("  RR Data: ~/d/prod/hedgeye/rr/all/csv/combined_risk_range.csv")
    print("  RR Plots: ~/d/view/hedgeye/plots/plots_with_fmp_*/")
    print("  CR Data: ~/d/view/hedgeye/data/cr/position_ranges_enriched.csv")
    print("  CR Plots: ~/d/view/hedgeye/plots/cr_time_series/")
    print("=" * 70)


def main():
    """Main entry point."""
    run_both_pipelines()


if __name__ == "__main__":
    main()
