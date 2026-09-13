"""Randy's holdings — Fidelity CSV export + IBKR positions, with an asset class.

Classes: stock | etf | fund | bond-tbill | bond-tips | bond-tnote | bond-tbond | cash |
unknown. Classification is keyword heuristics over Fidelity's description plus an
explicit override table; anything the rules don't reach is `unknown` and listed —
never silently bucketed (§0).
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from fin.ds.fid.parser import parse_fidelity_csv

_CUSIP = re.compile(r"^[0-9]{3}[0-9A-Z]{5}[0-9]$")
_FUND_WORDS = (
    " ETF", "ETF ", "ISHARES", "VANECK", "GLOBAL X", "CAMBRIA", "TEUCRIUM", "INVESCO",
    "FIRST TR", "SPDR", "PROSHARES", "DIREXION", "WISDOMTREE", "SIMPLIFY", "ADVISORSHARES",
    "IMGP", "SERIES PORTFOLIOS TRUST", "ETF OPPORTUNITIES", "EA SERIES TRUST",
    "VICTORY PORTFOLIOS", "COMMODITY INDEX FD", " FD ", " FDS ", "FUND", "TRUST UNIT",
    "PHYSICAL GOLD", "PHYSICAL SILVER", "PHYSICAL URANIUM", "CURRENCYSHARES",
)  # fmt: skip
OVERRIDES: dict[str, str] = {
    # ticker -> class, for descriptions the keywords misread
    "AAAU": "etf", "PHYS": "etf", "SRUUF": "fund", "MTBA": "etf", "VFLO": "etf",
    "BUXX": "etf", "CLOX": "etf", "CLOZ": "etf", "ADDS": "etf", "HBIT": "etf",
    "DBMF": "etf", "MSOS": "etf", "EYLD": "etf", "FYLD": "etf", "GVAL": "etf",
}  # fmt: skip


@dataclass
class Holding:
    ticker: str
    asset_class: str
    quantity: float
    value: float
    description: str
    source: str  # fidelity | ibkr
    class_reason: str


def classify(symbol: str, description: str) -> tuple[str, str]:
    d = f" {description.upper()} "
    if symbol in OVERRIDES:
        return OVERRIDES[symbol], "override"
    if (
        "MONEY MARKET" in d
        or "DEPOSIT SWEEP" in d
        or "CASH RESERVES" in d
        or "MMKT" in d
    ):
        return "cash", "money-market"
    if "TREAS" in d or "UNITED STATES TREAS" in d:
        if "BILL" in d:
            return "bond-tbill", "treasury-bill"
        if "TIPS" in d:
            return "bond-tips", "tips"
        if " NTS" in d or " NOTE" in d:
            return "bond-tnote", "treasury-note"
        if " BDS" in d or " BOND" in d:
            return "bond-tbond", "treasury-bond"
        return "bond-unknown", "treasury-unclassified"
    if _CUSIP.match(symbol) and any(w in d for w in _FUND_WORDS):
        return "etf", "cusip-fund-keyword"
    if any(w in d for w in _FUND_WORDS):
        return "etf", "fund-keyword"
    if _CUSIP.match(symbol):
        return "unknown", "cusip-no-rule"
    if re.match(r"^[A-Z]{1,5}$", symbol) or symbol.endswith("F"):
        return "stock", "ticker-default"
    return "unknown", "no-rule"


def from_fidelity(csv_path: Path) -> list[Holding]:
    out: list[Holding] = []
    for p in parse_fidelity_csv(csv_path):
        cls, why = classify(p.symbol, p.description)
        out.append(
            Holding(
                p.symbol,
                cls,
                p.quantity,
                p.current_value,
                p.description,
                "fidelity",
                why,
            )
        )
    return out


def from_ibkr_json(path: Path) -> list[Holding]:
    """A saved copy of IBKR positions (connector or `fetch_ibkr_positions.py` output)."""
    data = json.loads(path.read_text())
    out: list[Holding] = []
    for p in data["positions"]:
        desc = p.get("contract_description") or p.get("symbol") or ""
        sym = desc.split()[0]
        ac = (p.get("asset_class") or p.get("sec_type") or "").upper()
        if ac == "BOND":
            cls, _ = classify(sym, "UNITED STATES TREAS NTS " + desc)
            why = "ibkr-bond"
            if "TIPS" in desc.upper():
                cls = "bond-tips"
        else:
            cls, why = classify(sym, desc)
        out.append(
            Holding(sym, cls, float(p.get("position") or p.get("quantity") or 0),
                    float(p.get("market_value") or 0), desc, "ibkr", why)
        )  # fmt: skip
    return out


def merge(holdings: list[Holding]) -> list[Holding]:
    """Same ticker across sources -> one row (quantities and values summed)."""
    by: dict[str, Holding] = {}
    for h in holdings:
        if h.ticker in by:
            e = by[h.ticker]
            e.quantity += h.quantity
            e.value += h.value
            if h.source not in e.source:
                e.source = f"{e.source}+{h.source}"
        else:
            by[h.ticker] = Holding(**asdict(h))
    return sorted(by.values(), key=lambda h: -h.value)


def compare_to_roster(
    holdings: list[Holding], roster_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    ss = {r["ticker"].upper(): r for r in roster_rows}
    held_in_ss, held_not_in_ss, non_stock = [], [], []
    for h in holdings:
        row = {"ticker": h.ticker, "class": h.asset_class, "value": round(h.value, 0),
               "quantity": h.quantity, "source": h.source}  # fmt: skip
        if h.ticker in ss:
            r = ss[h.ticker]
            row.update({k: r.get(k) for k in ("best_idea_rank", "rank_kind", "analyst",
                                               "sector", "days_on", "signal_date")})  # fmt: skip
            held_in_ss.append(row)
        elif h.asset_class == "stock":
            held_not_in_ss.append(row)
        else:
            non_stock.append(row)
    ss_not_held = [
        {k: r.get(k) for k in ("ticker", "best_idea_rank", "rank_kind", "analyst",
                               "sector", "days_on")}
        for t, r in sorted(ss.items()) if t not in {h.ticker for h in holdings}
    ]  # fmt: skip
    return {
        "held_in_ss": held_in_ss,
        "held_in_ss_bench": [r for r in held_in_ss if r["rank_kind"] == "bench"],
        "held_in_ss_km_signal": [r for r in held_in_ss if r["rank_kind"] == "km-signal"],
        "held_in_ss_ranked": [r for r in held_in_ss if r["rank_kind"] == "ranked"],
        "held_stocks_not_in_ss": held_not_in_ss,
        "held_non_stock": non_stock,
        "ss_not_held": ss_not_held,
        "unclassified": [asdict(h) for h in holdings if h.asset_class.startswith("unknown")
                         or h.asset_class == "bond-unknown"],  # fmt: skip
    }
