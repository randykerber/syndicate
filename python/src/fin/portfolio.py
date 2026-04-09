"""
Portfolio categorization and querying.

Assigns positions to thematic buckets and provides query methods
for totals, filtering, and reporting.

Usage:
    from fin.ds.fid.parser import parse_fidelity_csv
    from fin.portfolio import Portfolio

    positions = parse_fidelity_csv("path/to/csv")
    pf = Portfolio(positions)
    pf.summary()
    pf.bucket_detail("Energy")
    pf.total("Shorts")
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from fin.ds.fid.parser import FidelityPosition


# ---------------------------------------------------------------------------
# Bucket definitions
# ---------------------------------------------------------------------------
# Each bucket has a set of explicit ticker symbols. Positions not matching
# any bucket fall into NOTA. Order matters for precedence when a ticker
# could match multiple rules (first match wins).

BUCKET_TICKERS: dict[str, set[str]] = {
    "Cash": {
        "FDRXX", "SPAXX", "CORE", "FZFXX", "FZDXX", "BUXX", "IBKR_CASH",
    },
    "TIPS": {
        # ETFs
        "TIP",
        # TIPS CUSIPs (from Scala categorization)
        "91282CFR7", "91282CGW5", "912810FH6", "91282CEZ0", "91282CGK1",
        "91282CLE9", "91282CNB3", "912810QV3", "91282CJH5", "91282CJY8",
        "91282CKL4", "91282CLV1", "91282CML2", "91282CNS6",
    },
    "Treasuries": set(),  # matched by CUSIP pattern, see _classify()
    "Other Bonds": {
        "MTBA", "EMB",
    },
    "Precious Metals": {
        "PHYS", "AAAU",
    },
    "PM Miners": {
        "AEM", "AGI", "HYMC", "ZPHYF", "TUF",
    },
    "PM Royalties": {
        "FNV", "ELE", "EMPYF", "WPM",
    },
    "Energy": {
        # E&P
        "AR", "AETUF", "BTE", "CNQ", "CRGY", "EC", "FANG", "MTDR",
        "PBR", "PEYUF", "SHEL", "SM", "TRMLF", "VG", "VIST", "VLO",
        # Midstream / Infrastructure
        "AMLP", "ENFR", "ET", "GEL", "TPYP", "TGS",
        # Services / ETFs
        "FCG", "OIH", "XOP",
        # Oil commodity trackers
        "BNO", "USO",
        # Coal
        "BTU", "COAL",
        # Energy royalties
        "KRP", "VNOM",
    },
    "Ag / Food Commodities": {
        "CORN", "WEAT", "VEGI", "UAN", "DAR",
    },
    "Currency": {
        "UUP", "FXB",
    },
    "Geo ETFs": {
        "NORW", "EWG", "EWP", "IDX", "COLO", "KWT",
    },
    "Diversified Miners": {
        "GLNCY", "VALE",
    },
    "Broad Commodities": {
        "COM",
    },
    "Defense": {
        "LMT", "RTX", "HII",
    },
    "Consumer": {
        "CASY", "MUSA", "MCD", "PEP", "HSY", "FRPT", "CAVA", "PRMB", "TJX", "NFLX",
        "WING", "CPB", "HELE", "ADDYY", "OLLI", "DDS", "LULU", "ANF", "BRBR", "KSS",
        "EXPE", "XLY", "GRNY",
    },
    "Healthcare": {
        "ACHC", "THC", "ELV", "MOH", "USPH", "IHF", "PSCH", "SGRY",
    },
    "Managed Futures": {
        "CTA",
    },
    "Shipping": {
        "ODFL",
    },
    "Financials": {
        "JPM", "XLF", "IAK", "SPGI", "WAL", "TRU", "FISV", "ROP",
    },
    "Tech": {
        "POET", "FSLY",
        "FICO", "MNDY", "CRWV", "RBLX", "AFRM", "TSLA", "SKYY", "ORCL",
        "IVES", "PATH", "PI", "BITS", "AMZN", "MAGS", "XLK", "MSFO", "MSTY",
    },
}

# Options are detected by symbol pattern, not explicit ticker list.
# Shorts are detected by negative quantity (except those explicitly
# assigned to a thematic bucket like FXB in Currency).


@dataclass
class CategorizedPosition:
    """A position with its assigned bucket."""

    symbol: str
    description: str
    quantity: float
    current_value: float
    total_gain_loss: float | None
    cost_basis: float | None
    bucket: str
    is_short: bool = False
    is_option: bool = False


@dataclass
class Portfolio:
    """
    A portfolio of categorized positions with query methods.

    Construct from a list of FidelityPosition (or any source that
    produces the same shape).
    """

    positions: list[CategorizedPosition] = field(default_factory=list)
    _by_bucket: dict[str, list[CategorizedPosition]] = field(
        default_factory=dict, repr=False
    )

    def __init__(self, raw_positions: list[FidelityPosition]) -> None:
        self.positions = [_classify(p) for p in raw_positions]
        self._rebuild_index()

    def _rebuild_index(self) -> None:
        self._by_bucket = {}
        for p in self.positions:
            self._by_bucket.setdefault(p.bucket, []).append(p)

    # -- Queries -----------------------------------------------------------

    @property
    def buckets(self) -> list[str]:
        """All bucket names that have at least one position, sorted."""
        return sorted(self._by_bucket.keys())

    def bucket_positions(self, bucket: str) -> list[CategorizedPosition]:
        """Get all positions in a bucket."""
        return self._by_bucket.get(bucket, [])

    def total(self, bucket: str) -> float:
        """Total current value of a bucket."""
        return sum(p.current_value for p in self.bucket_positions(bucket))

    def total_all(self) -> float:
        """Total current value of the entire portfolio."""
        return sum(p.current_value for p in self.positions)

    def bucket_detail(self, bucket: str) -> str:
        """Formatted detail for a single bucket: ticker, value, gain/loss."""
        positions = sorted(
            self.bucket_positions(bucket),
            key=lambda p: abs(p.current_value),
            reverse=True,
        )
        if not positions:
            return f"{bucket}: (empty)"

        lines = [f"\n{'='*60}", f"  {bucket}", f"{'='*60}"]
        lines.append(f"  {'Symbol':<12} {'Value':>14} {'Gain/Loss':>14}")
        lines.append(f"  {'-'*12} {'-'*14} {'-'*14}")
        for p in positions:
            gl_str = f"${p.total_gain_loss:>+,.2f}" if p.total_gain_loss is not None else "--"
            lines.append(f"  {p.symbol:<12} ${p.current_value:>13,.2f} {gl_str:>14}")
        bucket_total = sum(p.current_value for p in positions)
        lines.append(f"  {'-'*12} {'-'*14}")
        lines.append(f"  {'TOTAL':<12} ${bucket_total:>13,.2f}")
        return "\n".join(lines)

    def shorts(self) -> list[CategorizedPosition]:
        """All short positions across all buckets."""
        return [p for p in self.positions if p.is_short]

    def shorts_detail(self) -> str:
        """Formatted detail for all short positions, grouped by bucket."""
        shorts = sorted(self.shorts(), key=lambda p: (p.bucket, p.current_value))
        if not shorts:
            return "No short positions."

        lines = [f"\n{'='*60}", f"  ALL SHORT POSITIONS", f"{'='*60}"]
        lines.append(f"  {'Symbol':<12} {'Bucket':<20} {'Value':>14}")
        lines.append(f"  {'-'*12} {'-'*20} {'-'*14}")
        for p in shorts:
            lines.append(f"  {p.symbol:<12} {p.bucket:<20} ${p.current_value:>13,.2f}")
        total = sum(p.current_value for p in shorts)
        lines.append(f"  {'-'*12} {'-'*20} {'-'*14}")
        lines.append(f"  {'TOTAL':<12} {'':<20} ${total:>13,.2f}")
        return "\n".join(lines)

    def summary(self) -> str:
        """Summary table: bucket name, position count (long/short), total value."""
        total = self.total_all()
        lines = [
            f"\n{'='*70}",
            f"  PORTFOLIO SUMMARY",
            f"{'='*70}",
            f"  {'Bucket':<24} {'Long':>4} {'Short':>5} {'Value':>14} {'%':>7}",
            f"  {'-'*24} {'-'*4} {'-'*5} {'-'*14} {'-'*7}",
        ]
        for bucket in self.buckets:
            positions = self.bucket_positions(bucket)
            n_long = sum(1 for p in positions if not p.is_short)
            n_short = sum(1 for p in positions if p.is_short)
            bucket_val = sum(p.current_value for p in positions)
            pct = (bucket_val / total * 100) if total else 0
            short_str = str(n_short) if n_short else ""
            lines.append(
                f"  {bucket:<24} {n_long:>4} {short_str:>5} ${bucket_val:>13,.2f} {pct:>6.1f}%"
            )
        n_total_long = sum(1 for p in self.positions if not p.is_short)
        n_total_short = sum(1 for p in self.positions if p.is_short)
        lines.append(f"  {'-'*24} {'-'*4} {'-'*5} {'-'*14} {'-'*7}")
        lines.append(
            f"  {'TOTAL':<24} {n_total_long:>4} {n_total_short:>5} ${total:>13,.2f} {100.0:>6.1f}%"
        )
        return "\n".join(lines)

    def query(
        self,
        buckets: list[str] | None = None,
        exclude_buckets: list[str] | None = None,
        shorts_only: bool = False,
        longs_only: bool = False,
    ) -> list[CategorizedPosition]:
        """
        Flexible query across positions.

        Args:
            buckets: Include only these buckets (None = all).
            exclude_buckets: Exclude these buckets.
            shorts_only: Only short positions.
            longs_only: Only long positions.
        """
        result = self.positions
        if buckets:
            bucket_set = set(buckets)
            result = [p for p in result if p.bucket in bucket_set]
        if exclude_buckets:
            exc_set = set(exclude_buckets)
            result = [p for p in result if p.bucket not in exc_set]
        if shorts_only:
            result = [p for p in result if p.is_short]
        if longs_only:
            result = [p for p in result if not p.is_short]
        return result

    def query_total(self, **kwargs) -> float:
        """Total value of positions matching query()."""
        return sum(p.current_value for p in self.query(**kwargs))

    def __repr__(self) -> str:
        return f"Portfolio({len(self.positions)} positions, {len(self.buckets)} buckets)"


# ---------------------------------------------------------------------------
# Classification logic
# ---------------------------------------------------------------------------

# CUSIP patterns for treasuries
_TBILL_CUSIP = re.compile(r"^912797")  # T-Bills
_TNOTE_CUSIP = re.compile(r"^91282C")  # T-Notes
_TBOND_CUSIP = re.compile(r"^912810")  # T-Bonds (includes TIPS)

# Option symbol pattern: e.g., "-IWM260618C305"
_OPTION_RE = re.compile(r"^-?\w+\d{6}[CP]\d+$")


def _classify(pos: FidelityPosition) -> CategorizedPosition:
    """Assign a position to a bucket."""
    sym = pos.symbol
    desc_upper = pos.description.upper()
    is_short = pos.quantity < 0 or pos.position_type == "Short"
    is_option = bool(_OPTION_RE.match(sym.lstrip()))

    # Options bucket
    if is_option:
        return _make(pos, "Options", is_short=is_short, is_option=True)

    # Check explicit ticker lists (first match wins)
    for bucket, tickers in BUCKET_TICKERS.items():
        if sym in tickers:
            return _make(pos, bucket, is_short=is_short)

    # CUSIP-based treasury detection
    if _TBILL_CUSIP.match(sym) or _TNOTE_CUSIP.match(sym):
        if "TIPS" in desc_upper:
            return _make(pos, "TIPS", is_short=is_short)
        return _make(pos, "Treasuries", is_short=is_short)

    if _TBOND_CUSIP.match(sym):
        if "TIPS" in desc_upper:
            return _make(pos, "TIPS", is_short=is_short)
        return _make(pos, "Treasuries", is_short=is_short)

    # Everything else (long or short)
    return _make(pos, "NOTA", is_short=is_short)


def _make(
    pos: FidelityPosition,
    bucket: str,
    is_short: bool = False,
    is_option: bool = False,
) -> CategorizedPosition:
    return CategorizedPosition(
        symbol=pos.symbol,
        description=pos.description,
        quantity=pos.quantity,
        current_value=pos.current_value,
        total_gain_loss=pos.total_gain_loss,
        cost_basis=pos.cost_basis,
        bucket=bucket,
        is_short=is_short,
        is_option=is_option,
    )
