# FMP (Financial Modeling Prep) API
# https://site.financialmodelingprep.com/developer/docs/
# Functions to load FMP entity data from CSV files.

import pandas as pd
from pathlib import Path
from hedgeye.config_loader import load_config

# Load configuration
config = load_config()
FMP_DATA_BASE_DIR = Path(config["paths"]["fmp_data_base_dir"])

def load_fmp_entities(entity_name: str):
    """
    Load FMP entity data from CSV file.
    
    Args:
        entity_name (str): Name of entity (e.g., 'stocks', 'etfs', 'indexes', 'countries', 'cryptocurrencies')
    
    Returns:
        pd.DataFrame: Entity data loaded from CSV
    
    Example:
        stocks = load_fmp_entities("stocks")
        etfs = load_fmp_entities("etfs")
        cryptocurrencies = load_fmp_entities("cryptocurrencies")
    """
    csv_file = FMP_DATA_BASE_DIR / f"{entity_name}.csv"
    if csv_file.exists():
        return pd.read_csv(csv_file)
    else:
        print(f"CSV file not found: {csv_file}")
        return pd.DataFrame()
