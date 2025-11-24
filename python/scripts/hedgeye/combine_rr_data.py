#!/usr/bin/env python3
"""
Combine individual CSV files into a master dataset.
"""
from hedgeye.rr_pipeline import run_rr_combine_step

def main():
    run_rr_combine_step()

if __name__ == "__main__":
    main()