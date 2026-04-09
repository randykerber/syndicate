"""
Manual IBKR position entry.

For when you can't export a CSV and just want to type in positions.
Produces FidelityPosition-compatible objects for use with Portfolio.

Usage:
    from fin.ds.ibkr.manual import create_ibkr_positions

    positions = create_ibkr_positions(
        equities={
            "NORW": 377,
            "WPM": 43,
        },
        bonds={
            "91282CGW5": 50,  # 50 units = $50k face value
        },
        cash=52000.0,
    )
"""

from fin.ds.fid.parser import FidelityPosition


def _fetch_equity_prices(symbols: list[str]) -> dict[str, float | None]:
    """Look up current prices via yfinance."""
    import yfinance as yf

    prices: dict[str, float | None] = {}
    if not symbols:
        return prices

    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            info = ticker.fast_info
            prices[sym] = float(info.last_price)
        except Exception:
            prices[sym] = None

    return prices


def create_ibkr_positions(
    equities: dict[str, float] | None = None,
    bonds: dict[str, float] | None = None,
    cash: float = 0.0,
    yf_symbol_map: dict[str, str] | None = None,
    bond_price_pct: float = 100.0,
) -> list[FidelityPosition]:
    """
    Create positions from manually entered IBKR data.

    Args:
        equities: {ticker: quantity} for stocks/ETFs.
        bonds: {CUSIP: face_value_units} where 1 unit = $1,000 par.
            face_value_units of 50 means $50,000 face value.
        cash: Cash balance in USD.
        yf_symbol_map: Map from your ticker to yfinance symbol,
            e.g. {"TUF": "TUF.V"} for Canadian tickers.
        bond_price_pct: Assumed bond price as % of par (default 100).

    Returns:
        List of FidelityPosition ready for Portfolio().
    """
    equities = equities or {}
    bonds = bonds or {}
    yf_symbol_map = yf_symbol_map or {}

    positions: list[FidelityPosition] = []

    # Look up equity prices
    yf_symbols = []
    yf_to_ticker: dict[str, str] = {}
    for ticker in equities:
        yf_sym = yf_symbol_map.get(ticker, ticker)
        yf_symbols.append(yf_sym)
        yf_to_ticker[yf_sym] = ticker

    prices = _fetch_equity_prices(yf_symbols)

    # Map prices back to original tickers
    ticker_prices: dict[str, float | None] = {}
    for yf_sym, orig_ticker in yf_to_ticker.items():
        ticker_prices[orig_ticker] = prices.get(yf_sym)

    # Create equity positions
    for ticker, qty in equities.items():
        price = ticker_prices.get(ticker)
        if price is not None:
            value = round(price * qty, 2)
        else:
            value = 0.0
            print(f"  WARNING: No price found for {ticker}, value set to $0")

        positions.append(
            FidelityPosition(
                symbol=ticker,
                description=f"IBKR: {ticker}",
                quantity=qty,
                last_price=price,
                current_value=value,
                total_gain_loss=None,
                cost_basis=None,
                position_type="Cash",
            )
        )

    # Create bond positions (approximate value at par or given %)
    for cusip, units in bonds.items():
        face_value = units * 1000.0
        value = round(face_value * bond_price_pct / 100.0, 2)
        positions.append(
            FidelityPosition(
                symbol=cusip,
                description=f"IBKR Bond: {cusip}",
                quantity=units,
                last_price=None,
                current_value=value,
                total_gain_loss=None,
                cost_basis=None,
                position_type="Cash",
            )
        )

    # Cash position
    if cash > 0:
        positions.append(
            FidelityPosition(
                symbol="IBKR_CASH",
                description="IBKR Cash Balance",
                quantity=cash,
                last_price=1.0,
                current_value=cash,
                total_gain_loss=None,
                cost_basis=None,
                position_type="Cash",
            )
        )

    return positions
