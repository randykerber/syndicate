#!/usr/bin/env python3
"""
Portfolio categorization and reporting.

Parses Fidelity CSV exports and IBKR manual positions, categorizes into
thematic buckets, and provides query interface.

Usage:
    uv run scripts/fin/portfolio_report.py ~/Downloads/Portfolio_Positions_Mar-20-2026.csv
    uv run scripts/fin/portfolio_report.py path/to/csv --detail Energy
    uv run scripts/fin/portfolio_report.py path/to/csv --detail all
    uv run scripts/fin/portfolio_report.py path/to/csv --nota
    uv run scripts/fin/portfolio_report.py path/to/csv --no-ibkr
"""

import argparse
import sys
from pathlib import Path

from fin.ds.fid.parser import parse_fidelity_csv
from fin.ds.ibkr.manual import create_ibkr_positions
from fin.portfolio import Portfolio


# Symbols to ignore (delisted, $0 value, etc.)
IGNORE_SYMBOLS = {
    "92189F403",  # VanEck Russia ETF (delisted, $0)
}

# IBKR positions (manually entered 2026-03-20)
IBKR_EQUITIES = {
    "NORW": 377,
    "WPM": 43,
    "ELE": 110,
    "FNV": 12,
    "GLNCY": 380,
    "VALE": 150,
    "TIP": 55,
    "COM": 120,
    "TUF": 9500,
}
IBKR_BONDS = {
    "91282CGW5": 50,   # TIPS note, 50 units = $50k face value
    "912810FH6": 20,   # TIPS bond, 20 units = $20k face value
}
IBKR_CASH = 52000.0
IBKR_YF_MAP = {
    "TUF": "TUF.V",  # Honey Badger Silver, TSX Venture
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Categorize and report on portfolio positions"
    )
    parser.add_argument(
        "csv_file",
        help="Path to Fidelity Portfolio_Positions CSV file",
    )
    parser.add_argument(
        "--detail",
        nargs="*",
        metavar="BUCKET",
        help='Show detail for bucket(s). Use "all" for every bucket.',
    )
    parser.add_argument(
        "--nota",
        action="store_true",
        help="Show NOTA (uncategorized) positions",
    )
    parser.add_argument(
        "--shorts",
        action="store_true",
        help="Show all short positions with detail",
    )
    parser.add_argument(
        "--no-ibkr",
        action="store_true",
        help="Exclude IBKR positions (Fidelity only)",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv_file).expanduser()
    if not csv_path.exists():
        print(f"ERROR: File not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    # Load Fidelity positions
    positions = parse_fidelity_csv(csv_path, ignore_symbols=IGNORE_SYMBOLS)
    print(f"Loaded {len(positions)} Fidelity positions")

    # Load IBKR positions
    if not args.no_ibkr:
        print("Fetching IBKR prices via yfinance...")
        ibkr_positions = create_ibkr_positions(
            equities=IBKR_EQUITIES,
            bonds=IBKR_BONDS,
            cash=IBKR_CASH,
            yf_symbol_map=IBKR_YF_MAP,
        )
        print(f"Loaded {len(ibkr_positions)} IBKR positions")
        positions.extend(ibkr_positions)

    pf = Portfolio(positions)

    # Always show summary
    print(pf.summary())

    # Detail views
    if args.detail is not None:
        buckets = args.detail if args.detail else ["all"]
        if "all" in buckets:
            buckets = pf.buckets
        for b in buckets:
            print(pf.bucket_detail(b))

    if args.nota:
        print(pf.bucket_detail("NOTA"))

    if args.shorts:
        print(pf.shorts_detail())

    # Quick stats
    total = pf.total_all()
    shorts_val = sum(p.current_value for p in pf.shorts())
    print(f"\nShorts total: ${shorts_val:,.2f}")
    print(f"Portfolio total: ${total:,.2f}")


if __name__ == "__main__":
    main()
