"""
Parse Fidelity portfolio CSV exports into normalized position records.

Fidelity CSV format (as of 2026):
    Account Number, Account Name, Symbol, Description, Quantity, Last Price,
    Last Price Change, Current Value, Today's Gain/Loss Dollar,
    Today's Gain/Loss Percent, Total Gain/Loss Dollar,
    Total Gain/Loss Percent, Percent Of Account, Cost Basis Total,
    Average Cost Basis, Type

Usage:
    from fin.ds.fid.parser import parse_fidelity_csv
    positions = parse_fidelity_csv("~/Downloads/Portfolio_Positions_Mar-20-2026.csv")
"""

import csv
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FidelityPosition:
    """A single position from a Fidelity CSV export."""

    symbol: str
    description: str
    quantity: float
    last_price: float | None
    current_value: float
    total_gain_loss: float | None
    cost_basis: float | None
    position_type: str  # "Cash", "Margin", "Short"


def _parse_dollar(val: str) -> float | None:
    """Parse Fidelity dollar string like '$1,234.56' or '+$99.00' or '--'."""
    val = val.strip()
    if not val or val == "--":
        return None
    val = val.replace("$", "").replace(",", "").replace("+", "")
    try:
        return float(val)
    except ValueError:
        return None


def _clean_symbol(symbol: str) -> str:
    """Clean up Fidelity symbol quirks (trailing **, leading spaces)."""
    return symbol.strip().rstrip("*")


def _is_option_symbol(symbol: str) -> bool:
    """Detect option symbols like ' -IWM260618C305'."""
    return bool(re.match(r"\s*-?\w+\d{6}[CP]\d+", symbol.strip()))


def parse_fidelity_csv(
    path: str | Path,
    ignore_symbols: set[str] | None = None,
) -> list[FidelityPosition]:
    """
    Parse a Fidelity portfolio CSV into normalized positions.

    Aggregates positions across accounts (same symbol in multiple accounts
    gets summed). Money market symbols are normalized to their base ticker.

    Args:
        path: Path to the Fidelity CSV file.
        ignore_symbols: Symbols to skip entirely (e.g., delisted ETFs with $0 value).

    Returns:
        List of FidelityPosition, one per unique symbol.
    """
    path = Path(path).expanduser()
    ignore_symbols = ignore_symbols or set()

    # First pass: collect raw rows
    raw: dict[str, dict] = {}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol_raw = row.get("Symbol") or ""
            symbol_raw = symbol_raw.strip()
            if not symbol_raw:
                continue

            symbol = _clean_symbol(symbol_raw)
            if not symbol:
                continue

            # Check ignore list (match on cleaned symbol or raw CUSIP-style)
            if symbol in ignore_symbols:
                continue

            description = row.get("Description", "").strip()
            current_value = _parse_dollar(row.get("Current Value", ""))
            if current_value is None:
                # Skip rows with no value (e.g., $0 delisted positions)
                continue

            quantity_str = row.get("Quantity", "").strip().replace(",", "")
            try:
                quantity = float(quantity_str) if quantity_str else 0.0
            except ValueError:
                quantity = 0.0

            last_price = _parse_dollar(row.get("Last Price", ""))
            total_gl = _parse_dollar(row.get("Total Gain/Loss Dollar", ""))
            cost_basis = _parse_dollar(row.get("Cost Basis Total", ""))
            pos_type = row.get("Type", "").strip().rstrip(",")

            # Aggregate by symbol across accounts
            if symbol in raw:
                existing = raw[symbol]
                existing["quantity"] += quantity
                existing["current_value"] += current_value
                if total_gl is not None:
                    existing["total_gain_loss"] = (
                        existing["total_gain_loss"] or 0.0
                    ) + total_gl
                if cost_basis is not None:
                    existing["cost_basis"] = (
                        existing["cost_basis"] or 0.0
                    ) + cost_basis
            else:
                raw[symbol] = {
                    "symbol": symbol,
                    "description": description,
                    "quantity": quantity,
                    "current_value": current_value,
                    "last_price": last_price,
                    "total_gain_loss": total_gl,
                    "cost_basis": cost_basis,
                    "position_type": pos_type,
                }

    positions = []
    for data in raw.values():
        positions.append(
            FidelityPosition(
                symbol=data["symbol"],
                description=data["description"],
                quantity=data["quantity"],
                current_value=data["current_value"],
                last_price=data["last_price"],
                total_gain_loss=data["total_gain_loss"],
                cost_basis=data["cost_basis"],
                position_type=data["position_type"],
            )
        )

    return positions
