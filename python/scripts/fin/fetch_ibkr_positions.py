#!/usr/bin/env python3
"""
Fetch current IBKR portfolio positions and save to CSV.

Prerequisites:
    TWS or IB Gateway must be running with API enabled.

Usage:
    uv run scripts/fin/fetch_ibkr_positions.py                  # defaults: TWS live (7496)
    uv run scripts/fin/fetch_ibkr_positions.py --port 7497       # TWS paper
    uv run scripts/fin/fetch_ibkr_positions.py --port 4001       # Gateway live
    uv run scripts/fin/fetch_ibkr_positions.py -o my_positions.csv
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from fin.ibkr import PORTS, fetch_positions, enrich_with_prices, positions_to_dataframe


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch IBKR portfolio positions to CSV"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="TWS/Gateway host (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=PORTS["tws_live"],
        help=f"Socket port (default: {PORTS['tws_live']} = TWS live). "
        f"Common: TWS live={PORTS['tws_live']}, TWS paper={PORTS['tws_paper']}, "
        f"GW live={PORTS['gw_live']}, GW paper={PORTS['gw_paper']}",
    )
    parser.add_argument(
        "--client-id",
        type=int,
        default=10,
        help="Client ID for IBKR connection (default: 10)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output CSV path (default: output/ibkr_positions_YYYYMMDD_HHMMSS.csv)",
    )
    args = parser.parse_args()

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = Path(__file__).resolve().parent.parent.parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"ibkr_positions_{ts}.csv"

    print(f"Connecting to IBKR at {args.host}:{args.port} ...")

    try:
        positions = fetch_positions(
            host=args.host,
            port=args.port,
            client_id=args.client_id,
        )
    except ConnectionError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print("Fetching market prices ...")
    positions = enrich_with_prices(positions)

    df = positions_to_dataframe(positions)
    df.to_csv(output_path, index=False)

    print(f"\nFetched {len(positions)} positions")
    if not df.empty:
        cols = ["symbol", "quantity", "avg_cost", "market_price", "market_value"]
        print(f"\n{df[cols].to_string(index=False)}")
        if df["market_value"].notna().any():
            total_value = df["market_value"].sum()
            print(f"\nTotal market value: ${total_value:,.2f}")
    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    main()
