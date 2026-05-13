#!/usr/bin/env python3
"""Download the Hedgeye ETF Holdings CSV and persist if changed."""
from pathlib import Path

from hedgeye.config_loader import load_config
from hedgeye.ds.ham.ham_etf_holdings_downloader import download_etf_holdings


def main():
    cfg = load_config()
    output_dir = Path(cfg["paths"]["ham_csv_dir"])
    download_etf_holdings(output_dir)


if __name__ == "__main__":
    main()
