#!/usr/bin/env python3
"""
A small test script to verify the shared config loader.

This script loads the SSS config file and prints the resolved values
for the YouTube directory paths to confirm they are working correctly.
"""
import sys
import os
from pathlib import Path

# Add the src directory to the Python path to allow importing shared
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from shared.config import load_config

def main():
    """Loads config and prints specific resolved paths."""
    print("--- Testing Config Loader ---")
    
    try:
        config_path = Path(__file__).parent.parent / "config" / "sss" / "config.yaml"
        print(f"Loading config from: {config_path}")
        
        config = load_config(config_path)
        
        print("\n--- Resolved Paths ---")
        
        triage_dir = config.get('youtube', {}).get('triage_summaries_dir', 'NOT FOUND')
        extractions_dir = config.get('youtube', {}).get('extractions_dir', 'NOT FOUND')
        
        print(f"youtube.triage_summaries_dir: {triage_dir}")
        print(f"youtube.extractions_dir:      {extractions_dir}")
        
        print("\n--- Test Complete ---")

    except Exception as e:
        print(f"\nAn error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
