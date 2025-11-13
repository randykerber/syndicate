#!/usr/bin/env python3
"""
Run the complete Hedgeye Risk Range data pipeline.
"""
from hedgeye_kb.pipeline import run_full_pipeline

def main():
    run_full_pipeline()

if __name__ == "__main__":
    main()
