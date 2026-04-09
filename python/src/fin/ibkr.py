"""
IBKR portfolio access via ib_async.

Connects to Interactive Brokers TWS or IB Gateway to retrieve
current portfolio positions with market values and P&L.

Prerequisites:
    - TWS or IB Gateway must be running and logged in
    - API connections must be enabled in TWS/Gateway settings
    - Default ports: TWS live=7496, paper=7497; Gateway live=4001, paper=4002

Usage:
    from fin.ibkr import fetch_portfolio, portfolio_to_dataframe

    positions = fetch_positions()  # TWS live (port 7496)
    df = positions_to_dataframe(positions)
    df.to_csv("positions.csv", index=False)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pandas as pd
import yfinance as yf
from ib_async import IB


# Common port configurations
PORTS = {
    "tws_live": 7496,
    "tws_paper": 7497,
    "gw_live": 4001,
    "gw_paper": 4002,
}


@dataclass
class PortfolioPosition:
    """A single portfolio position from ib.positions() (read-only API safe)."""

    account: str
    symbol: str
    sec_type: str
    currency: str
    quantity: float
    avg_cost: float
    market_price: Optional[float]
    market_value: Optional[float]
    con_id: int


def fetch_positions(
    host: str = "127.0.0.1",
    port: int = 7496,
    client_id: int = 10,
) -> list[PortfolioPosition]:
    """
    Connect to IBKR and fetch all positions (read-only API compatible).

    Uses ib.positions() which does NOT require write access.

    Args:
        host: TWS/Gateway host address.
        port: Socket port. Defaults to 7496 (TWS live).
        client_id: Unique client ID for this connection.

    Returns:
        List of PortfolioPosition with quantity and average cost.

    Raises:
        ConnectionError: If TWS/Gateway is not running or refuses connection.
    """
    ib = IB()
    try:
        ib.connect(host, port, clientId=client_id, readonly=True)
    except Exception as e:
        raise ConnectionError(
            f"Cannot connect to IBKR at {host}:{port}. "
            f"Is TWS running with API enabled? Error: {e}"
        ) from e

    try:
        items = ib.positions()
        positions = [
            PortfolioPosition(
                account=item.account,
                symbol=item.contract.symbol,
                sec_type=item.contract.secType,
                currency=item.contract.currency,
                quantity=float(item.position),
                avg_cost=float(item.avgCost),
                market_price=None,
                market_value=None,
                con_id=item.contract.conId,
            )
            for item in items
        ]
        return positions
    finally:
        ib.disconnect()


def enrich_with_prices(positions: list[PortfolioPosition]) -> list[PortfolioPosition]:
    """
    Add market prices to positions using yfinance (free, no subscription needed).

    Args:
        positions: List from fetch_positions().

    Returns:
        Same list with market_price and market_value populated where available.
    """
    symbols = list({p.symbol for p in positions if p.sec_type == "STK"})
    if not symbols:
        return positions

    prices: dict[str, Optional[float]] = {}
    try:
        tickers = yf.Tickers(" ".join(symbols))
        for sym in symbols:
            try:
                info = tickers.tickers[sym].fast_info
                prices[sym] = float(info.last_price)
            except Exception:
                prices[sym] = None
    except Exception:
        return positions

    for p in positions:
        price = prices.get(p.symbol)
        if price is not None:
            p.market_price = round(price, 4)
            p.market_value = round(price * p.quantity, 2)

    return positions


def positions_to_dataframe(positions: list[PortfolioPosition]) -> pd.DataFrame:
    """
    Convert portfolio positions to a pandas DataFrame.

    Args:
        positions: List from fetch_positions().

    Returns:
        DataFrame with all position fields plus a timestamp column.
    """
    if not positions:
        return pd.DataFrame(
            columns=[
                "timestamp",
                "account",
                "symbol",
                "sec_type",
                "currency",
                "quantity",
                "avg_cost",
                "market_price",
                "market_value",
                "con_id",
            ]
        )

    now = datetime.now().isoformat(timespec="seconds")
    records = []
    for p in positions:
        records.append(
            {
                "timestamp": now,
                "account": p.account,
                "symbol": p.symbol,
                "sec_type": p.sec_type,
                "currency": p.currency,
                "quantity": p.quantity,
                "avg_cost": round(p.avg_cost, 4),
                "market_price": p.market_price,
                "market_value": p.market_value,
                "con_id": p.con_id,
            }
        )

    return pd.DataFrame(records)
