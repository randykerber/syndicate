#!/usr/bin/env python3
"""
Generate enhanced risk range plots with latest FMP prices.
"""
from hedgeye_kb.pipeline import run_enhanced_plots_step

def main():
    """Generate enhanced plots with latest FMP prices."""
    run_enhanced_plots_step()

if __name__ == "__main__":
    main()