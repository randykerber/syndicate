"""
Seed the fin catalog from FMP entity data.

Usage:
    python -m fin.seed_fmp                    # Seed all
    python -m fin.seed_fmp --stocks           # Seed only stocks
    python -m fin.seed_fmp --etfs             # Seed only ETFs
    python -m fin.seed_fmp --indexes          # Seed only indexes
"""

import argparse
import os
from pathlib import Path

import pandas as pd

from .catalog import TickerCatalog
from .country_codes import EXCHANGE_TO_COUNTRY, SUFFIX_TO_COUNTRY


# Default FMP data location
FMP_DATA_DIR = Path("/Users/rk/d/downloads/fmp/entities")


def load_exchange_country_map(fmp_dir: Path) -> dict[str, str]:
    """
    Load exchange-to-country mapping from FMP exchanges.csv.
    Merges with our built-in mappings.
    """
    exchange_map = EXCHANGE_TO_COUNTRY.copy()
    
    exchanges_file = fmp_dir / "exchanges.csv"
    if exchanges_file.exists():
        df = pd.read_csv(exchanges_file, dtype=str)
        for _, row in df.iterrows():
            exchange = str(row.get("exchange", "") or "").strip()
            country_code = str(row.get("countryCode", "") or "").strip().lower()
            if exchange and country_code and country_code != "nan":
                # Map country codes to our preferred format
                if country_code == "gb":
                    country_code = "uk"  # User preference
                exchange_map[exchange.upper()] = country_code
    
    return exchange_map


def seed_stocks(catalog: TickerCatalog, fmp_dir: Path, exchange_map: dict[str, str], limit: int = None):
    """Seed stocks from FMP stock-list-v3.csv."""
    stocks_file = fmp_dir / "stock-list-v3.csv"
    if not stocks_file.exists():
        print(f"❌ Stock file not found: {stocks_file}")
        return 0
    
    print(f"Loading stocks from {stocks_file}...")
    df = pd.read_csv(stocks_file, dtype=str)
    
    if limit:
        df = df.head(limit)
    
    count = 0
    errors = 0
    
    for _, row in df.iterrows():
        try:
            symbol = row.get("symbol", "").strip()
            name = row.get("name", "").strip()
            exchange = row.get("exchangeShortName", "").strip()
            entity_type = row.get("type", "stock").strip().lower()
            
            if not symbol or not name:
                continue
            
            # Determine country from exchange
            country = exchange_map.get(exchange.upper(), "us")
            
            # Handle symbols with exchange suffix (e.g., "BGP.NZ", "ARX.TO")
            if "." in symbol:
                parts = symbol.split(".")
                base_symbol = parts[0]
                suffix = parts[-1].lower()
                # Map suffix to country using our mapping
                if suffix in SUFFIX_TO_COUNTRY:
                    country = SUFFIX_TO_COUNTRY[suffix]
                elif len(suffix) == 2:
                    # Assume it's already a country code
                    country = suffix
                symbol = base_symbol
            
            # Create cid
            cid = f"{symbol.upper()}.{country}"
            
            # Determine asset class
            asset_class = "stock"
            if entity_type == "etf":
                asset_class = "etf"
            elif entity_type == "trust":
                asset_class = "trust"
            
            # Add to catalog
            catalog.add_entity(
                cid=cid,
                name=name,
                asset_class=asset_class,
                exchange=exchange,
                fmp_symbol=row.get("symbol", "").strip(),
            )
            count += 1
            
            if count % 5000 == 0:
                print(f"  ... {count} stocks processed")
                
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  Error: {e}")
    
    print(f"✅ Stocks: {count} added, {errors} errors")
    return count


def seed_etfs(catalog: TickerCatalog, fmp_dir: Path, exchange_map: dict[str, str], limit: int = None):
    """Seed ETFs from FMP etf-list-stable.csv."""
    etf_file = fmp_dir / "etf-list-stable.csv"
    if not etf_file.exists():
        print(f"❌ ETF file not found: {etf_file}")
        return 0
    
    print(f"Loading ETFs from {etf_file}...")
    df = pd.read_csv(etf_file, dtype=str)
    
    if limit:
        df = df.head(limit)
    
    count = 0
    
    for _, row in df.iterrows():
        symbol = row.get("symbol", "").strip()
        name = row.get("name", "").strip()
        
        if not symbol or not name:
            continue
        
        # Most ETFs in stable list are US
        country = "us"
        if "." in symbol:
            parts = symbol.split(".")
            symbol = parts[0]
            suffix = parts[-1].lower()
            if len(suffix) == 2:
                country = suffix
        
        cid = f"{symbol.upper()}.{country}"
        
        catalog.add_entity(
            cid=cid,
            name=name,
            asset_class="etf",
            is_etf=True,
            fmp_symbol=row.get("symbol", "").strip(),
        )
        count += 1
    
    print(f"✅ ETFs: {count} added")
    return count


def seed_indexes(catalog: TickerCatalog, fmp_dir: Path, limit: int = None):
    """Seed indexes from FMP index-list-stable.csv."""
    index_file = fmp_dir / "index-list-stable.csv"
    if not index_file.exists():
        print(f"❌ Index file not found: {index_file}")
        return 0
    
    print(f"Loading indexes from {index_file}...")
    df = pd.read_csv(index_file, dtype=str)
    
    if limit:
        df = df.head(limit)
    
    count = 0
    
    for _, row in df.iterrows():
        symbol = row.get("symbol", "").strip()
        name = row.get("name", "").strip()
        
        if not symbol or not name:
            continue
        
        # Clean symbol (remove ^ prefix if present)
        clean_symbol = symbol.lstrip("^")
        
        # Indexes are typically US unless specified
        country = "us"
        
        cid = f"{clean_symbol.upper()}.{country}"
        
        catalog.add_entity(
            cid=cid,
            name=name,
            asset_class="index",
            is_index=True,
            fmp_symbol=symbol,
        )
        count += 1
    
    print(f"✅ Indexes: {count} added")
    return count


def seed_commodities(catalog: TickerCatalog, fmp_dir: Path):
    """Seed commodities from FMP commodities.csv."""
    comm_file = fmp_dir / "commodities.csv"
    if not comm_file.exists():
        print(f"❌ Commodities file not found: {comm_file}")
        return 0
    
    print(f"Loading commodities from {comm_file}...")
    df = pd.read_csv(comm_file, dtype=str)
    
    count = 0
    
    for _, row in df.iterrows():
        symbol = row.get("symbol", "").strip()
        name = row.get("name", "").strip()
        
        if not symbol or not name:
            continue
        
        # Commodities don't have a country per se, use "xx" for global
        cid = f"{symbol.upper()}.xx"
        
        catalog.add_entity(
            cid=cid,
            name=name,
            asset_class="commodity",
            fmp_symbol=symbol,
        )
        count += 1
    
    print(f"✅ Commodities: {count} added")
    return count


def seed_all(catalog: TickerCatalog, fmp_dir: Path, limit: int = None):
    """Seed all entity types."""
    exchange_map = load_exchange_country_map(fmp_dir)
    
    total = 0
    total += seed_stocks(catalog, fmp_dir, exchange_map, limit)
    total += seed_etfs(catalog, fmp_dir, exchange_map, limit)
    total += seed_indexes(catalog, fmp_dir, limit)
    total += seed_commodities(catalog, fmp_dir)
    
    return total


def main():
    parser = argparse.ArgumentParser(description="Seed fin catalog from FMP data")
    parser.add_argument("--stocks", action="store_true", help="Seed only stocks")
    parser.add_argument("--etfs", action="store_true", help="Seed only ETFs")
    parser.add_argument("--indexes", action="store_true", help="Seed only indexes")
    parser.add_argument("--commodities", action="store_true", help="Seed only commodities")
    parser.add_argument("--limit", type=int, help="Limit records (for testing)")
    parser.add_argument("--fmp-dir", type=str, default=str(FMP_DATA_DIR), 
                       help="FMP data directory")
    parser.add_argument("--db", type=str, help="Database path (default: data/fin_catalog.db)")
    
    args = parser.parse_args()
    fmp_dir = Path(args.fmp_dir)
    
    print("=" * 60)
    print("FMP → fin catalog seeder")
    print("=" * 60)
    print(f"FMP data dir: {fmp_dir}")
    
    with TickerCatalog(db_path=args.db) as catalog:
        print(f"Database: {catalog.db_path}")
        print()
        
        exchange_map = load_exchange_country_map(fmp_dir)
        
        if args.stocks:
            seed_stocks(catalog, fmp_dir, exchange_map, args.limit)
        elif args.etfs:
            seed_etfs(catalog, fmp_dir, exchange_map, args.limit)
        elif args.indexes:
            seed_indexes(catalog, fmp_dir, args.limit)
        elif args.commodities:
            seed_commodities(catalog, fmp_dir)
        else:
            # Seed all
            seed_all(catalog, fmp_dir, args.limit)
        
        print()
        print("=" * 60)
        print("Catalog stats:")
        stats = catalog.stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()

