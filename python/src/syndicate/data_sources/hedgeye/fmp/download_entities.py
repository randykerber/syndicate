#!/usr/bin/env python3
"""
FMP Entity Downloader

Downloads Financial Modeling Prep entity data to CSV files.
Supports both v3 and stable API versions.

Usage:
    python download_entities.py                    # Download all entities
    python download_entities.py --version v3       # Download only v3 entities
    python download_entities.py --version stable   # Download only stable entities
    python download_entities.py --entity stocks    # Download only stocks
"""

import argparse
import requests
import pandas as pd
import os
from pathlib import Path
from hedgeye_kb.config_loader import load_config

# Load configuration
config = load_config()
FMP_DATA_BASE_DIR = Path(config["paths"]["fmp_data_base_dir"])
FMP_DATA_BASE_DIR.mkdir(parents=True, exist_ok=True)

FMP_API_KEY = os.getenv("FMP_API_KEY")
BASE_URL = "https://financialmodelingprep.com"

# Define all available entities
ENTITIES = {
    "api/v3": {
        "stocks": ("stock/list", "stock-list-v3.csv"),
        "etfs": ("etf/list", "etf-list-v3.csv"),
        "countries": ("available-countries", "countries-v3.csv"),
    },
    "stable": {
        "stocks": ("stock-list", "stock-list-stable.csv"),
        "etfs": ("etf-list", "etf-list-stable.csv"),
        "indexes": ("index-list", "index-list-stable.csv"),
        "countries": ("available-countries", "countries-stable.csv"),
        "exchanges": ("available-exchanges", "exchanges.csv"),
        "industries": ("available-industries", "industries.csv"),
        "sectors": ("available-sectors", "sectors.csv"),
        "commodities": ("commodities-list", "commodities.csv"),
        "forex": ("forex-list", "forex.csv"),
        "cryptocurrencies": ("cryptocurrency-list", "cryptocurrencies.csv"),
    }
}

def download_entity(version: str, entity_name: str, endpoint: str, filename: str):
    """Download a single entity"""
    url = f"{BASE_URL}/{version}/{endpoint}?apikey={FMP_API_KEY}"
    print(f"Downloading {entity_name} from {version}...")
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                df = pd.DataFrame(data)
                output_file = FMP_DATA_BASE_DIR / filename
                df.to_csv(output_file, index=False)
                print(f"✅ {filename}: {len(data)} rows")
                return True, len(data)
            else:
                print(f"❌ {filename}: No data returned")
                return False, 0
        else:
            print(f"❌ {filename}: HTTP {response.status_code}")
            return False, 0
    except Exception as e:
        print(f"❌ {filename}: Error - {e}")
        return False, 0

def download_all_entities(version=None):
    """Download entities based on version filter"""
    results = []
    
    for ver, entities in ENTITIES.items():
        if version and ver != version:
            continue
            
        print(f"\n{'='*60}")
        print(f"Downloading {ver.upper()} entities")
        print(f"{'='*60}")
        
        for entity_name, (endpoint, filename) in entities.items():
            success, count = download_entity(ver, entity_name, endpoint, filename)
            results.append({
                'version': ver,
                'entity': entity_name,
                'filename': filename,
                'success': success,
                'count': count
            })
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Download FMP entity data")
    parser.add_argument("--version", choices=["api/v3", "stable"], 
                       help="Download only specific API version")
    parser.add_argument("--entity", choices=["stocks", "etfs", "indexes", "countries", 
                                            "exchanges", "industries", "sectors", 
                                            "commodities", "forex", "cryptocurrencies"],
                       help="Download only specific entity")
    
    args = parser.parse_args()
    
    print("FMP Entity Downloader")
    print(f"Output directory: {FMP_DATA_BASE_DIR}")
    
    if args.entity:
        # Download specific entity from all available versions
        for version, entities in ENTITIES.items():
            if args.entity in entities:
                endpoint, filename = entities[args.entity]
                download_entity(version, args.entity, endpoint, filename)
    else:
        # Download all entities (or filtered by version)
        results = download_all_entities(args.version)
        
        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print(f"✅ Successful: {len(successful)}")
        for r in successful:
            print(f"  - {r['version']}/{r['entity']}: {r['count']} rows")
        
        if failed:
            print(f"❌ Failed: {len(failed)}")
            for r in failed:
                print(f"  - {r['version']}/{r['entity']}")

if __name__ == "__main__":
    main() 