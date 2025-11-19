#!/usr/bin/env python3
"""
Run the complete Hedgeye Risk Range data pipeline.
"""
from syndicate.data_sources.hedgeye.rr_pipeline import run_full_rr_pipeline

def main():
    run_full_rr_pipeline()

if __name__ == "__main__":
    main()
