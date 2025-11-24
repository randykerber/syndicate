#!/usr/bin/env python3
"""
Generate time series plots for all Risk Range symbols.
"""
from hedgeye.rr_pipeline import run_rr_basic_plots_step

def main():
    run_rr_basic_plots_step()

if __name__ == "__main__":
    main()