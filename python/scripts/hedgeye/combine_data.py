#!/usr/bin/env python3
"""
Combine individual CSV files into a master dataset.
"""
from syndicate.data_sources.hedgeye.pipeline import run_combine_step

def main():
    run_combine_step()

if __name__ == "__main__":
    main()